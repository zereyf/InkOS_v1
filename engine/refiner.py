"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
Phase 3 Architecture Upgrade:

  ARC-4: Groq streaming added.

  Architecture decision
  ─────────────────────
  The refiner has two jobs that pull in opposite directions:

    1. Stream tokens to the UI so the user sees progress immediately.
    2. Parse the JSON audit block that appears at the END of the response,
       then optionally retry if the score is below threshold.

  We solve this with two separate functions:

    stream_refinement(payload, ...) → Generator[str, None, None]
      ∙ Yields raw text chunks to the Streamlit UI via st.write_stream().
      ∙ Accumulates the full response internally.
      ∙ After the stream finishes, parses the audit from the accumulated text.
      ∙ Stores the final (refined, audit) in a mutable result dict passed in
        by the caller so the workspace can read them after streaming ends.
      ∙ Does NOT retry — streaming + retry would require buffering the full
        response before showing anything, which defeats the purpose.

    run_refinement_and_audit(payload, ...) → (str, dict, error)
      ∙ The original non-streaming pipeline. Unchanged.
      ∙ Used by: retry logic, test suite, any caller that needs a full result
        before proceeding (e.g. batch processing, the Forge tab).

  Workspace usage
  ───────────────
    result_container = {}
    st.write_stream(
        stream_refinement(payload, target, ..., result=result_container)
    )
    refined = result_container.get("refined", "")
    audit   = result_container.get("audit", {})
"""

from __future__ import annotations

import json
import re
import textwrap
from typing import Optional, Tuple, Any, Generator

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
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return None


def _extract_json(text: str) -> Optional[str]:
    decoder   = json.JSONDecoder()
    starts    = [m.start() for m in re.finditer(r"\{", text)]
    # Prefer objects that look like the audit contract
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
        "score":      safe_int(raw.get("score"), 100),
        "critique":   str(raw.get("critique", "Audit complete.")).strip(),
        "precision":  safe_int(raw.get("precision"), 40),
        "alignment":  safe_int(raw.get("alignment"), 40),
        "efficiency": safe_int(raw.get("efficiency"), 20),
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
    if "[CLARIFICATION_REQUIRED]" in refined:
        return True, ""
    text = refined.strip()
    if len(text) < 100:
        return False, "Output density insufficient. Prompt is too short."
    target = str(target or "")
    if "Claude" in target:
        if not re.search(r"<(?:role|task|constraints|output_format)>", text, re.IGNORECASE):
            return False, "Claude requires XML-structured blocks (<role>, <task>, etc.)."
        for tag in ("edge_cases", "quality_bar"):
            if not re.search(rf"<{tag}>\s*.+?\s*</{tag}>", text, re.IGNORECASE | re.DOTALL):
                return False, f"Claude output must include a non-empty <{tag}>...</{tag}> block."
    if "GPT" in target or "ChatGPT" in target:
        if not re.search(r"^you\s+are\s+a?\s+\w", text[:100], re.IGNORECASE):
            return False, "Prompt requires 'You are a [role]' identity opener."
    return True, ""


# ── LLM CALLS ────────────────────────────────────────────────────────────────

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
    """Non-streaming LLM call. Used by the retry pipeline."""
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


# ── STREAMING PIPELINE (ARC-4) ────────────────────────────────────────────────

def stream_refinement(
    master_payload: str,
    target:         str,
    framework:      str,
    lang:           str,
    aesthetic_choice: str = "Default",
    hikmah_style:   str   = "None",
    skip_security:  bool  = False,
    result:         dict  = None,          # mutable container — caller reads after stream ends
) -> Generator[str, None, None]:
    """
    Streaming generator. Yields text chunks for st.write_stream().

    After the stream finishes the full response is parsed. The caller
    receives (refined, audit) via the `result` dict:
        result["refined"] = str
        result["audit"]   = dict
        result["error"]   = Optional[str]

    Usage in workspace.py:
        result = {}
        st.write_stream(stream_refinement(payload, ..., result=result))
        clean  = extract_clean_output(result.get("refined", ""))
        audit  = result.get("audit", {})
    """
    if result is None:
        result = {}

    # Security gate
    if not skip_security:
        _, violations = sanitize_input(master_payload)
        if violations:
            sig = " | ".join(violations)
            result["error"]   = f"SECURITY_BREACH: {sig}"
            result["refined"] = f"🛑 OVERWATCH INTERCEPT: Hostile patterns detected.\nSIGNATURE: {sig}"
            result["audit"]   = {"score": 0, "critique": f"SECURITY_BREACH: {sig}"}
            yield result["refined"]
            return

    if not client:
        result["error"]   = "Client Offline"
        result["refined"] = "System Fault: Groq client not initialised."
        result["audit"]   = {"score": 0, "critique": "Client Offline"}
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
            stream      = True,     # ← streaming enabled
        )

        for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                accumulated += delta
                yield delta

    except Exception as e:
        error_msg = f"System Fault: {str(e)}"
        result["error"]   = error_msg
        result["refined"] = error_msg
        result["audit"]   = {"score": 0, "critique": str(e)[:80]}
        yield error_msg
        return

    # Parse the accumulated response after streaming completes
    refined, audit = _parse_output(accumulated)
    result["refined"] = refined or accumulated
    result["audit"]   = audit or {"score": 0, "critique": "Audit parse failed."}
    result["error"]   = None


# ── NON-STREAMING PIPELINE (unchanged — used by retry loop & tests) ───────────

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
    Full non-streaming refinement pipeline with retry logic.
    Unchanged from Phase 1 except for import alignment.
    Used by tests and any caller needing a complete result before proceeding.
    """
    if not skip_security:
        _, violations = sanitize_input(master_payload)
        if violations:
            sig = " | ".join(violations)
            return (
                f"🛑 OVERWATCH INTERCEPT: Hostile patterns detected.\nSIGNATURE: {sig}",
                {"score": 0, "critique": f"SECURITY_BREACH: {sig}"},
                None,
            )

    retry_critique              = None
    best_refined, best_audit    = None, None

    for attempt in range(MAX_RETRIES + 1):
        final_system_prompt = f"{master_payload}\n\n{CIPHER_OUTPUT_CONTRACT}"
        if retry_critique:
            final_system_prompt += f"\n\n[ RETRY_CORRECTION_DIRECTIVE ]\n{retry_critique}"

        refined, self_audit, error = _call_cipher(final_system_prompt)

        if error:
            return f"System Fault: {error}", {"score": 0, "critique": error}, None
        if not refined:
            return "Neural refraction failed.", {"score": 0, "critique": "Empty response from LLM."}, None

        passed, reason = _validate_structure(refined, target)
        if not passed:
            retry_critique = f"Structural Failure: {reason}"
            if self_audit and (not best_audit or self_audit.get("score", 0) > best_audit.get("score", 0)):
                best_refined, best_audit = refined, self_audit
            continue

        if self_audit.get("score", 0) >= RETRY_THRESHOLD:
            audit = _call_evaluator(master_payload, target, refined, hikmah_style)
            if audit["score"] >= RETRY_THRESHOLD:
                return refined, audit, None
            retry_critique = audit["critique"]
            if not best_audit or audit.get("score", 0) > best_audit.get("score", 0):
                best_refined, best_audit = refined, audit
        else:
            retry_critique = self_audit.get("critique", "Score below threshold.")
            if self_audit and (not best_audit or self_audit.get("score", 0) > best_audit.get("score", 0)):
                best_refined, best_audit = refined, self_audit

    final_audit = best_audit or self_audit or {
        "score": 0, "critique": retry_critique or "Refinement exhausted retries.",
    }
    return best_refined or refined, final_audit, None
