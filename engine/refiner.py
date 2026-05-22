"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
v5.0: Pattern Learning + Meta-Audit Integration.
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

_PATTERN_THRESHOLD = 85
_FAILURE_THRESHOLD = 60

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
            if escape:       escape = False
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
    if "[CLARIFICATION_REQUIRED]" in refined:
        return True, ""
    text = refined.strip()
    if len(text) < 100:
        return False, "Output density insufficient — prompt is too short."
    target = str(target or "")

    if "Claude" in target:
        if not re.search(r"<(?:role|task|constraints|output_format)>", text, re.IGNORECASE):
            return False, "Claude requires XML-structured output with <role>, <task>, <constraints>, <output_format> tags."
        for tag in ("edge_cases", "quality_bar"):
            if not re.search(rf"<{tag}>\s*.+?\s*</{tag}>", text, re.IGNORECASE | re.DOTALL):
                return False, f"Claude output must include a non-empty <{tag}>...</{tag}> block."
        if re.search(r"^you\s+are\s+", text[:80], re.IGNORECASE):
            return False, "Claude output must NOT open with 'You are a...'. Use <role> XML tag."
        return True, ""

    if "Midjourney" in target or "midjourney" in target.lower() or "flux" in target.lower():
        if not re.search(r"^/imagine\s+prompt\s*:", text, re.IGNORECASE):
            return False, "Midjourney/Flux prompts must start with '/imagine prompt:'."
        return True, ""

    if "Stable" in target or "stable diffusion" in target.lower():
        if re.search(r"^you\s+are\s+", text, re.IGNORECASE):
            return False, "Stable Diffusion prompts must be comma-separated keyword tags."
        if "Negative prompt:" not in text:
            return False, "Stable Diffusion output must include a 'Negative prompt:' section."
        return True, ""

    if "DALL" in target or "dall" in target.lower():
        if re.search(r"^you\s+are\s+", text, re.IGNORECASE):
            return False, "DALL-E prompts must be descriptive prose."
        if re.search(r"^/imagine", text, re.IGNORECASE):
            return False, "DALL-E prompts must be prose paragraphs, not /imagine syntax."
        return True, ""

    if "Gemini" in target:
        if re.search(r"^you\s+are\s+a?\s+", text[:80], re.IGNORECASE):
            return False, "Gemini prompts must open with 'Context:' label."
        return True, ""

    if "Perplexity" in target:
        if re.search(r"^you\s+are\s+", text, re.IGNORECASE):
            return False, "Perplexity prompts must be research questions."
        return True, ""

    if "Copilot" in target:
        if re.search(r"^you\s+are\s+", text, re.IGNORECASE):
            return False, "Copilot prompts must open with an action verb."
        return True, ""

    if "GPT" in target or "ChatGPT" in target:
        if not re.search(r"^you\s+are\s+a?\s*\w", text[:100], re.IGNORECASE):
            return False, "ChatGPT prompt requires 'You are a [role]' identity opener."
        return True, ""

    return True, ""


def _extract_key_instruction(refined: str) -> str:
    if not refined:
        return ""
    role_match = re.search(r"<role>(.*?)</role>", refined, re.IGNORECASE | re.DOTALL)
    if role_match:
        return role_match.group(1).strip()[:500]
    subject_match = re.search(r"\[SUBJECT:?(.*?)\]::", refined, re.IGNORECASE | re.DOTALL)
    if subject_match:
        return subject_match.group(1).strip()[:500]
    paragraphs = [p.strip() for p in refined.split("\n\n") if p.strip()]
    return paragraphs[0][:500] if paragraphs else refined[:500]


def _store_pattern_if_worthy(target: str, framework: str, score: int, refined: str, critique: str) -> None:
    try:
        from state import store_cipher_pattern, store_cipher_failure
        if score >= _PATTERN_THRESHOLD:
            store_cipher_pattern(target, framework, score, _extract_key_instruction(refined))
        elif score < _FAILURE_THRESHOLD:
            store_cipher_failure(target, critique, score)
    except Exception:
        pass


def _run_meta_audit_async(intent: str, target: str, refined: str, score: int, critique: str) -> None:
    try:
        from engine.meta_auditor import run_meta_audit
        from state import store_meta_insight
        insight = run_meta_audit(intent, target, refined, score, critique)
        if insight:
            store_meta_insight(insight)
    except Exception:
        pass


def _call_evaluator(master_payload: str, target: str, refined_prompt: str, hikmah_style: str) -> dict:
    if not client:
        return {"score": 0, "critique": "Offline"}
    rhetoric_note = f"\nRHETORIC_EXPECTATION: {hikmah_style}" if hikmah_style != "None" else ""
    try:
        completion = client.chat.completions.create(
            model    = MODEL_ID,
            messages = [
                {"role": "system", "content": f"{CIPHER_EVALUATOR_PROMPT}{rhetoric_note}"},
                {"role": "user",   "content": f"TARGET_NODE: {target}\nMASTER_PAYLOAD: {master_payload}\nREFINED_OUTPUT: {refined_prompt}"},
            ],
            response_format = {"type": "json_object"},
            temperature     = EVAL_TEMPERATURE,
            max_tokens      = 300,
            timeout         = REQUEST_TIMEOUT_SECONDS,
        )
        return _clamp_audit(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return {"score": 0, "critique": f"Audit Error: {str(e)[:40]}"}


def _call_cipher(system_prompt: str) -> Tuple[Optional[str], Optional[dict], Optional[str]]:
    if not client:
        return None, None, "Client Offline"
    last_error = None
    for model_id in dict.fromkeys((*(MODEL_PRIORITY or ()), MODEL_ID)):
        try:
            completion = client.chat.completions.create(
                model    = model_id,
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user",   "content": "EXECUTE_REFINEMENT_NODE: Transform the provided intent into a highly optimised, model-specific prompt. DO NOT execute the user's task. Generate the PROMPT for the task, followed strictly by the JSON evaluation block."},
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


def stream_refinement(
    master_payload:   str,
    intent:           str,
    target:           str,
    framework:        str,
    lang:             str,
    aesthetic_choice: str  = "Default",
    hikmah_style:     str  = "None",
    skip_security:    bool = False,
    result:           dict = None,
):
    if result is None:
        result = {}

    if not skip_security:
        _, violations = sanitize_input(master_payload)
        if violations:
            sig = " | ".join(violations)
            result.update({"error": f"SECURITY_BREACH: {sig}",
                           "refined": f"OVERWATCH INTERCEPT: Hostile patterns detected.\nSIGNATURE: {sig}",
                           "audit": {"score": 0, "critique": f"SECURITY_BREACH: {sig}"},
                           "corrected": False})
            yield result["refined"]
            return

    if not client:
        result.update({"error": "Client Offline", "refined": "System Fault: Groq client not initialised.",
                       "audit": {"score": 0, "critique": "Client Offline"}, "corrected": False})
        yield result["refined"]
        return

    final_system_prompt = f"{master_payload}\n\n{CIPHER_OUTPUT_CONTRACT}"
    accumulated = ""

    try:
        stream = client.chat.completions.create(
            model    = MODEL_PRIORITY[0] if MODEL_PRIORITY else MODEL_ID,
            messages = [
                {"role": "system", "content": final_system_prompt},
                {"role": "user",   "content": "EXECUTE_REFINEMENT_NODE: Transform the provided intent into a highly optimised, model-specific prompt. DO NOT execute the user's task. Generate the PROMPT for the task, followed strictly by the JSON evaluation block."},
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
        result.update({"error": error_msg, "refined": error_msg,
                       "audit": {"score": 0, "critique": str(e)[:80]}, "corrected": False})
        yield error_msg
        return

    refined, audit = _parse_output(accumulated)
    refined = refined or accumulated
    passed, reason = _validate_structure(refined, target)

    if not passed:
        retry_prompt = (
            f"{final_system_prompt}\n\n[ CORRECTION_REQUIRED ]\n"
            + CIPHER_RETRY_INJECTION.format(critique=reason)
        )
        corrected_refined, corrected_audit, correction_error = _call_cipher(retry_prompt)
        if corrected_refined and not correction_error:
            result.update({"refined": corrected_refined, "audit": corrected_audit or audit or {},
                           "error": None, "corrected": True})
            final_audit = corrected_audit or {}
            _store_pattern_if_worthy(target, framework, final_audit.get("score", 0),
                                     corrected_refined, final_audit.get("critique", ""))
        else:
            if audit:
                audit["alignment"] = 0
                audit["score"]     = max(0, audit.get("score", 0) - 40)
                audit["critique"]  = f"FORMAT ERROR: {reason}"
            result.update({"refined": refined, "audit": audit or {"score": 0, "critique": f"FORMAT ERROR: {reason}"},
                           "error": None, "corrected": False})
            _store_pattern_if_worthy(target, framework, result["audit"].get("score", 0),
                                     refined, result["audit"].get("critique", ""))
    else:
        result.update({"refined": refined, "audit": audit or {"score": 0, "critique": "Audit parse failed."},
                       "error": None, "corrected": False})
        final_score    = result["audit"].get("score", 0)
        final_critique = result["audit"].get("critique", "")
        _store_pattern_if_worthy(target, framework, final_score, refined, final_critique)
        intent_snippet = intent[:300].strip() if intent else master_payload.split("[MISSION_PAYLOAD]")[-1][:300].strip()
        _run_meta_audit_async(intent_snippet, target, refined, final_score, final_critique)
        
        # Uses the clean intent variable directly instead of parsing the payload
        intent_snippet = intent[:300].strip() if intent else master_payload.split("[MISSION_PAYLOAD]")[-1][:300].strip()
        _run_meta_audit_async(intent_snippet, target, refined, final_score, final_critique)

    final_system_prompt = f"{master_payload}\n\n{CIPHER_OUTPUT_CONTRACT}"
    accumulated = ""

    try:
        stream = client.chat.completions.create(
            model    = MODEL_PRIORITY[0] if MODEL_PRIORITY else MODEL_ID,
            messages = [
                {"role": "system", "content": final_system_prompt},
                {"role": "user",   "content": "EXECUTE_REFINEMENT_NODE: Transform the provided intent into a highly optimised, model-specific prompt. DO NOT execute the user's task. Generate the PROMPT for the task, followed strictly by the JSON evaluation block."},
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
        result.update({"error": error_msg, "refined": error_msg,
                       "audit": {"score": 0, "critique": str(e)[:80]}, "corrected": False})
        yield error_msg
        return

    refined, audit = _parse_output(accumulated)
    refined = refined or accumulated
    passed, reason = _validate_structure(refined, target)

    if not passed:
        retry_prompt = (
            f"{final_system_prompt}\n\n[ CORRECTION_REQUIRED ]\n"
            + CIPHER_RETRY_INJECTION.format(critique=reason)
        )
        corrected_refined, corrected_audit, correction_error = _call_cipher(retry_prompt)
        if corrected_refined and not correction_error:
            result.update({"refined": corrected_refined, "audit": corrected_audit or audit or {},
                           "error": None, "corrected": True})
            final_audit = corrected_audit or {}
            _store_pattern_if_worthy(target, framework, final_audit.get("score", 0),
                                     corrected_refined, final_audit.get("critique", ""))
        else:
            if audit:
                audit["alignment"] = 0
                audit["score"]     = max(0, audit.get("score", 0) - 40)
                audit["critique"]  = f"FORMAT ERROR: {reason}"
            result.update({"refined": refined, "audit": audit or {"score": 0, "critique": f"FORMAT ERROR: {reason}"},
                           "error": None, "corrected": False})
            _store_pattern_if_worthy(target, framework, result["audit"].get("score", 0),
                                     refined, result["audit"].get("critique", ""))
    else:
        result.update({"refined": refined, "audit": audit or {"score": 0, "critique": "Audit parse failed."},
                       "error": None, "corrected": False})
        final_score    = result["audit"].get("score", 0)
        final_critique = result["audit"].get("critique", "")
        _store_pattern_if_worthy(target, framework, final_score, refined, final_critique)
        intent_snippet = master_payload.split("[MISSION_PAYLOAD]")[-1][:300].strip()
        _run_meta_audit_async(intent_snippet, target, refined, final_score, final_critique)


def run_refinement_and_audit(
    master_payload:   str,
    target:           str,
    framework:        str,
    lang:             str,
    aesthetic_choice: str  = "Default",
    hikmah_style:     str  = "None",
    skip_security:    bool = False,
) -> Tuple[str, dict, Optional[Any]]:

    if not skip_security:
        _, violations = sanitize_input(master_payload)
        if violations:
            sig = " | ".join(violations)
            return (f"OVERWATCH INTERCEPT: Hostile patterns detected.\nSIGNATURE: {sig}",
                    {"score": 0, "critique": f"SECURITY_BREACH: {sig}"}, None)

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
            if self_audit and (not best_audit or self_audit.get("score", 0) > best_audit.get("score", 0)):
                best_refined, best_audit = refined, self_audit
            continue

        if self_audit and self_audit.get("score", 0) >= RETRY_THRESHOLD:
            audit = _call_evaluator(master_payload, target, refined, hikmah_style)
            if audit["score"] >= RETRY_THRESHOLD:
                _store_pattern_if_worthy(target, framework, audit["score"], refined, audit.get("critique", ""))
                intent_snippet = master_payload.split("[MISSION_PAYLOAD]")[-1][:300].strip()
                _run_meta_audit_async(intent_snippet, target, refined, audit["score"], audit.get("critique", ""))
                return refined, audit, None
            retry_critique = audit["critique"]
            if not best_audit or audit.get("score", 0) > best_audit.get("score", 0):
                best_refined, best_audit = refined, audit
        else:
            retry_critique = (self_audit or {}).get("critique", "Score below threshold.")
            if self_audit and (not best_audit or self_audit.get("score", 0) > best_audit.get("score", 0)):
                best_refined, best_audit = refined, self_audit

    final_audit = best_audit or self_audit or {"score": 0, "critique": retry_critique or "Retries exhausted."}
    _store_pattern_if_worthy(target, framework, final_audit.get("score", 0),
                             best_refined or refined, final_audit.get("critique", ""))
    return best_refined or refined, final_audit, None
