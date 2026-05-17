"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
v4.1: Post-Stream Validation Fix.

STREAM-2 FIXED: stream_refinement() previously bypassed _validate_structure()
entirely. Non-streaming path had retry logic; streaming path had none.
Result: "You are..." output for Claude, Midjourney, DALL-E — every time.

Fix: After stream completes and output is accumulated, _validate_structure()
runs on the full text. If it fails, a single non-streaming correction call
fires using _call_cipher() with an explicit retry injection. The corrected
output replaces the streamed draft in the result dict. The user sees the
streamed draft first (for perceived performance) then the corrected version
is committed to session state.

This means:
  - Streaming UX is preserved — tokens appear immediately.
  - Format correctness is enforced — wrong openers get corrected silently.
  - One correction attempt maximum — no infinite loops in streaming context.
"""

from __future__ import annotations

import json
import re
import textwrap
from typing import Optional, Tuple, Any, Generator

from config.target_formats import get_opening_pattern
from config import (
    client, MODEL_ID, MODEL_PRIORITY, TEMPERATURE, MAX_TOKENS,
    RETRY_THRESHOLD, MAX_RETRIES, EVAL_TEMPERATURE,
    CIPHER_EVALUATOR_PROMPT, CIPHER_OUTPUT_CONTRACT,
    CIPHER_RETRY_INJECTION, REQUEST_TIMEOUT_SECONDS,
)
from security.sanitizer import sanitize_input


# ── PARSING UTILITIES ─────────────────────────────────────────────────────────

_TAG_CLEANUP   = re.compile(
    r"^(?:REFINED_PROMPT|PROMPT|OUTPUT|thinking):?\s*",
    flags=re.IGNORECASE | re.MULTILINE,
)
_FENCE_CLEANUP = re.compile(
    "\x60\x60\x60(?:markdown|json|text|xml)?|\x60\x60\x60",
    flags=re.IGNORECASE,
)


def _find_balanced_json_object(text: str, start: int) -> Optional[str]:
    depth, in_string, escape = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:      escape = False
            elif ch == "\\": escape = True
            elif ch == '"':  in_string = False
            continue
        if ch == '"':    in_string = True
        elif ch == "{":  depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start: i + 1]
    return None


def _extract_json(text: str) -> Optional[str]:
    decoder = json.JSONDecoder()
    starts  = [m.start() for m in re.finditer(r"\{", text)]
    starts.sort(
        key=lambda pos: (0 if re.match(r'\{\s*"?score"?\s*:', text[pos:]) else 1, -pos)
    )
    for start in starts:
        balanced = _find_balanced_json_object(text, start)
        if not balanced:
            continue
        try:
            parsed, end = decoder.raw_decode(balanced)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict) and end == len(balanced):
            return balanced
    return None


def _clamp_audit(raw: dict) -> dict:
    raw = raw if isinstance(raw, dict) else {}

    def safe_int(val, ceiling):
        try:
            return min(max(int(val), 0), ceiling)
        except (TypeError, ValueError):
            return 0

    return {
        "score":      safe_int(raw.get("score"),      100),
        "critique":   str(raw.get("critique", "Audit complete.")).strip(),
        "precision":  safe_int(raw.get("precision"),   40),
        "alignment":  safe_int(raw.get("alignment"),   40),
        "efficiency": safe_int(raw.get("efficiency"),  20),
    }


def _parse_output(raw: str) -> Tuple[Optional[str], Optional[dict]]:
    cleaned  = _FENCE_CLEANUP.sub("", raw).strip()
    json_str = _extract_json(cleaned)

    if not json_str:
        return cleaned, {
            "score":    0,
            "critique": "CRITICAL FAULT: LLM failed to append the JSON evaluation block.",
        }

    json_start = cleaned.rfind(json_str)
    refined    = _TAG_CLEANUP.sub("", cleaned[:json_start].strip()).strip()

    try:
        audit = _clamp_audit(json.loads(json_str))
    except json.JSONDecodeError:
        audit = {"score": 0, "critique": "CRITICAL FAULT: Generated JSON was malformed."}

    return refined, audit


def _validate_structure(refined: str, target: str) -> Tuple[bool, str]:
    """
    Validates that the refined output uses the correct format for the target.

    Returns (passed: bool, failure_reason: str).
    Empty failure_reason means passed.
    """
    if "[CLARIFICATION_REQUIRED]" in refined:
        return True, ""

    text = refined.strip()
    if len(text) < 100:
        return False, "Output density insufficient — prompt is too short."

    target = str(target or "")

    # ── Claude ────────────────────────────────────────────────────────────────
    if "Claude" in target:
        if not re.search(r"<(?:role|task|constraints|output_format)>", text, re.IGNORECASE):
            return False, (
                "Claude requires XML-structured output. "
                "Must contain <role>, <task>, <constraints>, <output_format> tags. "
                "Do NOT start with 'You are a...'."
            )
        for tag in ("edge_cases", "quality_bar"):
            if not re.search(rf"<{tag}>\s*.+?\s*</{tag}>", text, re.IGNORECASE | re.DOTALL):
                return False, f"Claude output must include a non-empty <{tag}>...</{tag}> block."
        # Reject "You are" openers for Claude
        if re.search(r"^you\s+are\s+", text[:80], re.IGNORECASE):
            return False, (
                "Claude output must NOT open with 'You are a...'. "
                "Use <role> XML tag instead."
            )
        return True, ""

    # ── Midjourney / Flux ─────────────────────────────────────────────────────
    if "Midjourney" in target or "midjourney" in target.lower() or "flux" in target.lower():
        if not re.search(r"^/imagine\s+prompt\s*:", text, re.IGNORECASE):
            return False, (
                "Midjourney/Flux prompts must start with '/imagine prompt:'. "
                "Do NOT start with 'You are a...' or any role-play opener."
            )
        return True, ""

    # ── Stable Diffusion ──────────────────────────────────────────────────────
    if "Stable" in target or "stable diffusion" in target.lower():
        if re.search(r"^you\s+are\s+", text, re.IGNORECASE):
            return False, (
                "Stable Diffusion prompts must be comma-separated keyword tags. "
                "Do NOT start with 'You are a...'."
            )
        if "Negative prompt:" not in text:
            return False, "Stable Diffusion output must include a 'Negative prompt:' section."
        return True, ""

    # ── DALL-E ────────────────────────────────────────────────────────────────
    if "DALL" in target or "dall" in target.lower():
        if re.search(r"^you\s+are\s+", text, re.IGNORECASE):
            return False, (
                "DALL-E prompts must be descriptive prose. "
                "Do NOT start with 'You are a...'."
            )
        if re.search(r"^/imagine", text, re.IGNORECASE):
            return False, "DALL-E prompts must be prose paragraphs, not /imagine syntax."
        return True, ""

    # ── Gemini ────────────────────────────────────────────────────────────────
    if "Gemini" in target:
        if re.search(r"^you\s+are\s+a?\s+", text[:80], re.IGNORECASE):
            return False, (
                "Gemini prompts must open with 'Context:' label. "
                "Do NOT start with 'You are a...'."
            )
        return True, ""

    # ── Perplexity ────────────────────────────────────────────────────────────
    if "Perplexity" in target:
        if re.search(r"^you\s+are\s+", text, re.IGNORECASE):
            return False, (
                "Perplexity prompts must be research questions. "
                "Do NOT start with 'You are a...'."
            )
        return True, ""

    # ── Copilot ───────────────────────────────────────────────────────────────
    if "Copilot" in target:
        if re.search(r"^you\s+are\s+", text, re.IGNORECASE):
            return False, (
                "Copilot prompts must open with an action verb (Write, Create, Summarize...). "
                "Do NOT start with 'You are a...'."
            )
        return True, ""

    # ── ChatGPT / GPT — only target that REQUIRES "You are a..." ─────────────
    if "GPT" in target or "ChatGPT" in target:
        if not re.search(r"^you\s+are\s+a?\s*\w", text[:100], re.IGNORECASE):
            return False, "ChatGPT prompt requires 'You are a [role]' identity opener."
        return True, ""

    # ── Manus AI ──────────────────────────────────────────────────────────────
    if "Manus" in target:
        return True, ""

    # ── Unknown target — pass through, warn ───────────────────────────────────
    return True, ""


def _call_evaluator(
    master_payload: str,
    target:         str,
    refined_prompt: str,
    hikmah_style:   str,
) -> dict:
    if not client:
        return {"score": 0, "critique": "Offline"}

    rhetoric_note = f"\nRHETORIC_EXPECTATION: {hikmah_style}" if hikmah_style != "None" else ""

    try:
        completion = client.chat.completions.create(
            model    = MODEL_ID,
            messages = [
                {"role": "system", "content": f"{CIPHER_EVALUATOR_PROMPT}{rhetoric_note}"},
                {
                    "role":    "user",
                    "content": (
                        f"TARGET_NODE: {target}\n"
                        f"MASTER_PAYLOAD: {master_payload}\n"
                        f"REFINED_OUTPUT: {refined_prompt}"
                    ),
                },
            ],
            response_format = {"type": "json_object"},
            temperature     = EVAL_TEMPERATURE,
            max_tokens      = 300,
            timeout         = REQUEST_TIMEOUT_SECONDS,
        )
        return _clamp_audit(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return {"score": 0, "critique": f"Audit Error: {str(e)[:40]}"}


def _call_cipher(
    system_prompt: str,
) -> Tuple[Optional[str], Optional[dict], Optional[str]]:
    """Non-streaming LLM call. Used by retry pipeline and post-stream correction."""
    if not client:
        return None, None, "Client Offline"

    last_error = None
    for model_id in dict.fromkeys((*(MODEL_PRIORITY or ()), MODEL_ID)):
        try:
            completion = client.chat.completions.create(
                model    = model_id,
                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role":    "user",
                        "content": (
                            "EXECUTE_REFINEMENT_NODE: Transform the provided intent into a "
                            "highly optimised, model-specific prompt. "
                            "DO NOT execute the user's task. "
                            "Generate the PROMPT for the task, followed strictly by the "
                            "JSON evaluation block."
                        ),
                    },
                ],
                temperature = TEMPERATURE,
                max_tokens  = MAX_TOKENS,
                timeout     = REQUEST_TIMEOUT_SECONDS,
            )
            refined, audit = _parse_output(completion.choices[0].message.content)
            return refined, audit, None
        except Exception as e:
            last_error = str(e)
            continue

    return None, None, last_error or "Unknown model uplink error"


# ── STREAMING PIPELINE ────────────────────────────────────────────────────────

def stream_refinement(
    master_payload:  str,
    target:          str,
    framework:       str,
    lang:            str,
    aesthetic_choice: str  = "Default",
    hikmah_style:    str   = "None",
    skip_security:   bool  = False,
    result:          dict  = None,
) -> Generator[str, None, None]:
    """
    Streaming generator. Yields text chunks for st.write_stream().

    STREAM-2 FIX: After accumulation, _validate_structure() runs on the
    full output. If format is wrong (e.g. "You are..." for Midjourney),
    a single non-streaming correction call fires and the corrected output
    is stored in result["refined"]. The streamed draft is what the user
    sees live; the corrected version is what gets committed to session state.

    Caller reads results via the `result` dict after streaming ends:
        result["refined"] = str   — format-validated output
        result["audit"]   = dict
        result["error"]   = Optional[str]
        result["corrected"] = bool  — True if post-stream correction fired
    """
    if result is None:
        result = {}

    if not skip_security:
        _, violations = sanitize_input(master_payload)
        if violations:
            sig = " | ".join(violations)
            result["error"]   = f"SECURITY_BREACH: {sig}"
            result["refined"] = f"OVERWATCH INTERCEPT: Hostile patterns detected.\nSIGNATURE: {sig}"
            result["audit"]   = {"score": 0, "critique": f"SECURITY_BREACH: {sig}"}
            result["corrected"] = False
            yield result["refined"]
            return

    if not client:
        result["error"]   = "Client Offline"
        result["refined"] = "System Fault: Groq client not initialised."
        result["audit"]   = {"score": 0, "critique": "Client Offline"}
        result["corrected"] = False
        yield result["refined"]
        return

    final_system_prompt = f"{master_payload}\n\n{CIPHER_OUTPUT_CONTRACT}"
    accumulated         = ""

    try:
        stream = client.chat.completions.create(
            model    = MODEL_PRIORITY[0] if MODEL_PRIORITY else MODEL_ID,
            messages = [
                {"role": "system", "content": final_system_prompt},
                {
                    "role":    "user",
                    "content": (
                        "EXECUTE_REFINEMENT_NODE: Transform the provided intent into a "
                        "highly optimised, model-specific prompt. "
                        "DO NOT execute the user's task. "
                        "Generate the PROMPT for the task, followed strictly by the "
                        "JSON evaluation block."
                    ),
                },
            ],
            temperature = TEMPERATURE,
            max_tokens  = MAX_TOKENS,
            timeout     = REQUEST_TIMEOUT_SECONDS,
            stream      = True,
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                accumulated += delta
                yield delta

    except Exception as e:
        error_msg = f"System Fault: {str(e)}"
        result["error"]     = error_msg
        result["refined"]   = error_msg
        result["audit"]     = {"score": 0, "critique": str(e)[:80]}
        result["corrected"] = False
        yield error_msg
        return

    # ── Post-stream parse ─────────────────────────────────────────────────────
    refined, audit = _parse_output(accumulated)
    refined = refined or accumulated

    # ── STREAM-2 FIX: validate format, correct if wrong ───────────────────────
    passed, reason = _validate_structure(refined, target)

    if not passed:
        # Format is wrong — fire a single non-streaming correction call
        critique      = reason
        retry_prompt  = (
            f"{final_system_prompt}\n\n"
            f"[ CORRECTION_REQUIRED ]\n"
            + CIPHER_RETRY_INJECTION.format(critique=critique)
        )
        corrected_refined, corrected_audit, correction_error = _call_cipher(retry_prompt)

        if corrected_refined and not correction_error:
            # Use the corrected output
            result["refined"]   = corrected_refined
            result["audit"]     = corrected_audit or audit or {}
            result["error"]     = None
            result["corrected"] = True
        else:
            # Correction also failed — use original with a low score
            if audit:
                audit["alignment"] = 0
                audit["score"]     = max(0, audit.get("score", 0) - 40)
                audit["critique"]  = f"FORMAT ERROR: {reason}"
            result["refined"]   = refined
            result["audit"]     = audit or {"score": 0, "critique": f"FORMAT ERROR: {reason}"}
            result["error"]     = None
            result["corrected"] = False
    else:
        result["refined"]   = refined
        result["audit"]     = audit or {"score": 0, "critique": "Audit parse failed."}
        result["error"]     = None
        result["corrected"] = False


# ── NON-STREAMING PIPELINE ────────────────────────────────────────────────────

def run_refinement_and_audit(
    master_payload:   str,
    target:           str,
    framework:        str,
    lang:             str,
    aesthetic_choice: str  = "Default",
    hikmah_style:     str  = "None",
    skip_security:    bool = False,
) -> Tuple[str, dict, Optional[Any]]:
    """
    Full non-streaming pipeline with retry logic.
    Used by: tests, batch processing, Forge tab, any caller needing a
    complete result before proceeding.
    """
    if not skip_security:
        _, violations = sanitize_input(master_payload)
        if violations:
            sig = " | ".join(violations)
            return (
                f"OVERWATCH INTERCEPT: Hostile patterns detected.\nSIGNATURE: {sig}",
                {"score": 0, "critique": f"SECURITY_BREACH: {sig}"},
                None,
            )

    retry_critique           = None
    best_refined, best_audit = None, None

    for attempt in range(MAX_RETRIES + 1):
        final_system_prompt = f"{master_payload}\n\n{CIPHER_OUTPUT_CONTRACT}"
        if retry_critique:
            final_system_prompt += (
                f"\n\n[ RETRY_CORRECTION_DIRECTIVE ]\n"
                + CIPHER_RETRY_INJECTION.format(critique=retry_critique)
            )

        refined, self_audit, error = _call_cipher(final_system_prompt)

        if error:
            return f"System Fault: {error}", {"score": 0, "critique": error}, None
        if not refined:
            return "Neural refraction failed.", {"score": 0, "critique": "Empty response."}, None

        passed, reason = _validate_structure(refined, target)
        if not passed:
            retry_critique = f"FORMAT FAILURE: {reason}"
            if self_audit and (
                not best_audit or self_audit.get("score", 0) > best_audit.get("score", 0)
            ):
                best_refined, best_audit = refined, self_audit
            continue

        if self_audit and self_audit.get("score", 0) >= RETRY_THRESHOLD:
            audit = _call_evaluator(master_payload, target, refined, hikmah_style)
            if audit["score"] >= RETRY_THRESHOLD:
                return refined, audit, None
            retry_critique = audit["critique"]
            if not best_audit or audit.get("score", 0) > best_audit.get("score", 0):
                best_refined, best_audit = refined, audit
        else:
            retry_critique = (self_audit or {}).get("critique", "Score below threshold.")
            if self_audit and (
                not best_audit or self_audit.get("score", 0) > best_audit.get("score", 0)
            ):
                best_refined, best_audit = refined, self_audit

    final_audit = best_audit or self_audit or {
        "score": 0, "critique": retry_critique or "Refinement exhausted retries.",
    }
    return best_refined or refined, final_audit, None
