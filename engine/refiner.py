"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
v10.0: Zenith Neural Handshake.
      - INTEGRATED: 3-Layer Master Payload (Persona + Rhetoric + DNA).
      - REFACTORED: Replaced 'islamic_mode' with 'hikmah_style' profiles.
      - OPTIMIZED: Removed redundant prompt construction; payload-driven execution.
"""

import json
import re
import textwrap
import time
from typing import Optional, Tuple, Any

from config import (
    client, MODEL_ID, TEMPERATURE, MAX_TOKENS, 
    RETRY_THRESHOLD, MAX_RETRIES, EVAL_TEMPERATURE,
    CIPHER_EVALUATOR_PROMPT, CIPHER_OUTPUT_CONTRACT, 
    CIPHER_RETRY_INJECTION
)

from engine.cognitive_map import detect_arabic_pattern
from security.sanitizer import sanitize_input

# ── 🟢 PARSING & UTILITIES ───────────────────────────────────────────────────

_TAG_CLEANUP = re.compile(r"^(?:REFINED_PROMPT|PROMPT|OUTPUT|thinking):?\s*", flags=re.IGNORECASE | re.MULTILINE)
_FENCE_CLEANUP = re.compile("\x60\x60\x60(?:markdown|json|text|xml)?|\x60\x60\x60", flags=re.IGNORECASE)

def _extract_json(text: str) -> Optional[str]:
    match = re.search(r'\{\s*"?score"?\s*:', text)
    if not match:
        start = text.rfind('{')
        if start == -1: return None
    else:
        start = match.start()
    count, end_pos = 0, -1
    for i in range(start, len(text)):
        if text[i] == '{': count += 1
        elif text[i] == '}': count -= 1
        if count == 0:
            end_pos = i + 1
            break
    return text[start:end_pos] if end_pos != -1 else None

def _clamp_audit(raw: dict) -> dict:
    def safe_int(val, ceiling):
        try: return min(max(int(val), 0), ceiling)
        except: return 0
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
        return cleaned, {"score": 0, "critique": "JSON not found."}
    
    json_start_pos = cleaned.rfind(json_str)
    refined = _TAG_CLEANUP.sub("", cleaned[:json_start_pos].strip()).strip()
    try:
        audit = _clamp_audit(json.loads(json_str))
    except:
        audit = {"score": 0, "critique": "JSON parse error."}
    return refined, audit

def _validate_structure(refined: str, target: str) -> Tuple[bool, str]:
    if "[CLARIFICATION_REQUIRED]" in refined: return True, ""
    text = refined.strip()
    if len(text) < 200: return False, "Output density insufficient."
    
    # Target-specific structure validation
    if 'Claude' in target:
        if not re.search(r'<(?:role|task|constraints|output_format)>', text, re.IGNORECASE):
            return False, 'Claude requires XML-structured blocks.'
    if 'GPT' in target:
        if not re.search(r'^you\s+are\s+a?\s+\w', text[:100], re.IGNORECASE):
            return False, "Prompt requires 'You are a [role]' identity opener."
    return True, ""

# ── 🟢 LLM API HANDSHAKES ─────────────────────────────────────────────────────

def _call_evaluator(master_payload: str, target: str, refined_prompt: str, hikmah_style: str) -> dict:
    """External audit with Rhetoric awareness."""
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
        )
        return _clamp_audit(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return {"score": 0, "critique": f"Audit Error: {str(e)[:40]}"}

def _call_cipher(system_prompt: str) -> Tuple[Optional[str], Optional[dict], Optional[str]]:
    """Executes the neural refraction. Master Payload acts as the System Instruction."""
    if not client: return None, None, "Client Offline"
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "EXECUTE_REFINEMENT_NODE: Process the mission objective within the provided system constraints."}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        refined, audit = _parse_output(completion.choices[0].message.content)
        return refined, audit, None
    except Exception as e:
        return None, None, str(e)

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
    """
    Main Neural Refinement Loop.
    Converts a 3-layer Master Payload into a verified refined asset.
    """
    
    # 🛡️ THE OVERWATCH SHIELD
    if not skip_security:
        _, violations = sanitize_input(master_payload)
        if violations:
            threat_sig = " | ".join(violations)
            return (
                f"🛑 OVERWATCH INTERCEPT: Hostile patterns detected in mission payload.\n"
                f"SIGNATURE: {threat_sig}\n"
                f"ACTION: UPLINK TERMINATED.",
                {"score": 0, "critique": f"SECURITY_BREACH: {threat_sig}"},
                None
            )

    retry_critique = None
    best_refined, best_audit = None, {"score": 0}

    for attempt in range(MAX_RETRIES + 1):
        # 🟢 CONSTRUCT FINAL UPLINK
        # We append the mandatory output contract to the master_payload
        final_system_prompt = f"{master_payload}\n\n{CIPHER_OUTPUT_CONTRACT}"
        
        if retry_critique:
            final_system_prompt += f"\n\n[ RETRY_CORRECTION_DIRECTIVE ]\n{retry_critique}"

        # UPLINK
        refined, self_audit, error = _call_cipher(final_system_prompt)
        
        if error: return f"System Fault: {error}", {"score":0, "critique":error}, None
        if not refined: return "Neural refraction failed.", {"score":0}, None

        # STRUCTURE VALIDATION
        passed, reason = _validate_structure(refined, target)
        if not passed:
            retry_critique = f"Structural Failure: {reason}. Ensure output matches model-specific requirements."
            continue

        # EVALUATION (Self-Audit vs External Audit)
        if self_audit.get('score', 0) >= RETRY_THRESHOLD:
            # External verification for high-score confidence
            audit = _call_evaluator(master_payload, target, refined, hikmah_style)
            if audit['score'] >= RETRY_THRESHOLD:
                return refined, audit, None
            
            # If external audit disagrees, use it as a critique for retry
            retry_critique = audit['critique']
            if audit.get('score', 0) > best_audit.get('score', 0):
                best_refined, best_audit = refined, audit
        else:
            retry_critique = self_audit.get('critique', 'Score below threshold.')

    return best_refined or refined, best_audit or self_audit, None
