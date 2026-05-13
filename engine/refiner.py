"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
v10.1: Zenith Neural Handshake (Telemetry Patch).
      - FIXED: "Zero Score Ghost" bug masking retry critiques.
      - HARDENED: Ironclad prompt generator directive to prevent Instruction Override.
      - INTEGRATED: 3-Layer Master Payload (Persona + Rhetoric + DNA).
"""

import json
import re
import textwrap
from typing import Optional, Tuple, Any

from config import (
    client, MODEL_ID, MODEL_PRIORITY, TEMPERATURE, MAX_TOKENS, 
    RETRY_THRESHOLD, MAX_RETRIES, EVAL_TEMPERATURE,
    CIPHER_EVALUATOR_PROMPT, CIPHER_OUTPUT_CONTRACT, 
    CIPHER_RETRY_INJECTION, REQUEST_TIMEOUT_SECONDS
)

from security.sanitizer import sanitize_input

# ── 🟢 PARSING & UTILITIES ───────────────────────────────────────────────────

_TAG_CLEANUP = re.compile(r"^(?:REFINED_PROMPT|PROMPT|OUTPUT|thinking):?\s*", flags=re.IGNORECASE | re.MULTILINE)
_FENCE_CLEANUP = re.compile("\x60\x60\x60(?:markdown|json|text|xml)?|\x60\x60\x60", flags=re.IGNORECASE)

def _find_balanced_json_object(text: str, start: int) -> Optional[str]:
    depth = 0
    in_string = False
    escape = False

    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start:index + 1]

    return None


def _extract_json(text: str) -> Optional[str]:
    decoder = json.JSONDecoder()
    candidate_starts = [m.start() for m in re.finditer(r"\{", text)]

    # Prefer objects that look like the audit contract, but fall back to any
    # decodable JSON object to preserve compatibility with imperfect models.
    candidate_starts.sort(key=lambda pos: (0 if re.match(r'\{\s*"?score"?\s*:', text[pos:]) else 1, -pos))

    for start in candidate_starts:
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
        "score": safe_int(raw.get("score"), 100),
        "critique": str(raw.get("critique", "Audit complete.")).strip(),
        "precision": safe_int(raw.get("precision"), 40),
        "alignment": safe_int(raw.get("alignment"), 40),
        "efficiency": safe_int(raw.get("efficiency"), 20),
    }

def _parse_output(raw: str) -> Tuple[Optional[str], Optional[dict]]:
    cleaned = _FENCE_CLEANUP.sub("", raw).strip()
    json_str = _extract_json(cleaned)
    if not json_str: 
        return cleaned, {"score": 0, "critique": "CRITICAL FAULT: LLM failed to append the JSON evaluation block."}
    
    json_start_pos = cleaned.rfind(json_str)
    refined = _TAG_CLEANUP.sub("", cleaned[:json_start_pos].strip()).strip()
    try:
        audit = _clamp_audit(json.loads(json_str))
    except json.JSONDecodeError:
        audit = {"score": 0, "critique": "CRITICAL FAULT: Generated JSON was malformed and could not be parsed."}
    return refined, audit

def _validate_structure(refined: str, target: str) -> Tuple[bool, str]:
    if "[CLARIFICATION_REQUIRED]" in refined: return True, ""
    text = refined.strip()
    if len(text) < 100: return False, "Output density insufficient. Prompt is too short."
    
    # Target-specific structure validation
    target = str(target or "")
    if 'Claude' in target:
        if not re.search(r'<(?:role|task|constraints|output_format)>', text, re.IGNORECASE):
            return False, 'Claude requires XML-structured blocks (<role>, <task>, etc.).'

        required_xml_tags = ('edge_cases', 'quality_bar')
        for tag in required_xml_tags:
            pattern = rf'<{tag}>\s*.+?\s*</{tag}>'
            if not re.search(pattern, text, re.IGNORECASE | re.DOTALL):
                return False, f'Claude output must include a non-empty <{tag}>...</{tag}> block.'
    if 'GPT' in target or 'ChatGPT' in target:
        if not re.search(r'^you\s+are\s+a?\s+\w', text[:100], re.IGNORECASE):
            return False, "Prompt requires 'You are a [role]' identity opener."
    return True, ""

# ── 🟢 LLM API HANDSHAKES ─────────────────────────────────────────────────────

def _call_evaluator(master_payload: str, target: str, refined_prompt: str, hikmah_style: str) -> dict:
    if not client: return {"score": 0, "critique": "Offline"}
    
    rhetoric_note = f"\nRHETORIC_EXPECTATION: {hikmah_style}" if hikmah_style != "None" else ""
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": f"{CIPHER_EVALUATOR_PROMPT}{rhetoric_note}"},
                {"role": "user",   "content": f"TARGET_NODE: {target}\nMASTER_PAYLOAD: {master_payload}\nREFINED_OUTPUT: {refined_prompt}"},
            ],
            response_format={"type": "json_object"},
            temperature=EVAL_TEMPERATURE,
            max_tokens=300,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        return _clamp_audit(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return {"score": 0, "critique": f"Audit Error: {str(e)[:40]}"}

def _call_cipher(system_prompt: str) -> Tuple[Optional[str], Optional[dict], Optional[str]]:
    if not client: return None, None, "Client Offline"
    last_error = None
    for model_id in dict.fromkeys((*(MODEL_PRIORITY or ()), MODEL_ID)):
        try:
            completion = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    # 🟢 IRONCLAD DIRECTIVE: Forces prompt generation, preventing DNA override.
                    {"role": "user", "content": "EXECUTE_REFINEMENT_NODE: Transform the provided intent into a highly optimized, model-specific prompt. DO NOT execute the user's task. Generate the PROMPT for the task, followed strictly by the JSON evaluation block."}
                ],
                temperature=TEMPERATURE,
                max_tokens=MAX_TOKENS,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            refined, audit = _parse_output(completion.choices[0].message.content)
            return refined, audit, None
        except Exception as e:
            last_error = str(e)
            continue
    return None, None, last_error or "Unknown model uplink error"

# ── 🟢 PIPELINE EXECUTION ─────────────────────────────────────────────────────

def run_refinement_and_audit(
    master_payload: str, 
    target: str, 
    framework: str, 
    lang: str, 
    aesthetic_choice: str = "Default", 
    hikmah_style: str = "None", 
    skip_security: bool = False
) -> Tuple[str, dict, Optional[Any]]:
    
    if not skip_security:
        _, violations = sanitize_input(master_payload)
        if violations:
            threat_sig = " | ".join(violations)
            return (
                f"🛑 OVERWATCH INTERCEPT: Hostile patterns detected in mission payload.\nSIGNATURE: {threat_sig}",
                {"score": 0, "critique": f"SECURITY_BREACH: {threat_sig}"},
                None
            )

    retry_critique = None
    # 🟢 FIXED: Initialized as None to prevent truthiness bugs hiding errors
    best_refined, best_audit = None, None 

    for attempt in range(MAX_RETRIES + 1):
        final_system_prompt = f"{master_payload}\n\n{CIPHER_OUTPUT_CONTRACT}"
        
        if retry_critique:
            final_system_prompt += f"\n\n[ RETRY_CORRECTION_DIRECTIVE ]\n{retry_critique}"

        refined, self_audit, error = _call_cipher(final_system_prompt)
        
        if error: return f"System Fault: {error}", {"score":0, "critique":error}, None
        if not refined: return "Neural refraction failed.", {"score":0, "critique": "Empty response from LLM."}, None

        passed, reason = _validate_structure(refined, target)
        if not passed:
            retry_critique = f"Structural Failure: {reason}"
            # Save the highest scoring failed attempt just in case
            if self_audit and (not best_audit or self_audit.get('score', 0) > best_audit.get('score', 0)):
                best_refined, best_audit = refined, self_audit
            continue

        if self_audit.get('score', 0) >= RETRY_THRESHOLD:
            audit = _call_evaluator(master_payload, target, refined, hikmah_style)
            if audit['score'] >= RETRY_THRESHOLD:
                return refined, audit, None
            
            retry_critique = audit['critique']
            if not best_audit or audit.get('score', 0) > best_audit.get('score', 0):
                best_refined, best_audit = refined, audit
        else:
            retry_critique = self_audit.get('critique', 'Score below threshold.')
            if self_audit and (not best_audit or self_audit.get('score', 0) > best_audit.get('score', 0)):
                best_refined, best_audit = refined, self_audit

    # 🟢 FIXED: Final fallback guarantees a critique is passed to the UI
    final_audit = best_audit or self_audit or {"score": 0, "critique": retry_critique or "Refinement exhausted retries."}
    return best_refined or refined, final_audit, None
