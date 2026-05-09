"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
v9.4.3: Structural & Cognitive Sync Build.
      - Integrated Arabic Pattern Negation instructions.
      - Synchronized with forge/persona_engine.py v9.2.
      - Hardened JSON recovery & structural validation.
"""

import json
import re
import textwrap
import time
from typing import Optional, Tuple

# 🟢 Import constants and prompts
from config import (
    client, MODEL_ID, TEMPERATURE, MAX_TOKENS, 
    RETRY_THRESHOLD, MAX_RETRIES, EVAL_TEMPERATURE,
    TARGET_GUIDES, CIPHER_IDENTITY, CIPHER_EVALUATOR_PROMPT, 
    CIPHER_OUTPUT_CONTRACT, CIPHER_RETRY_INJECTION,
    VISUAL_DIRECTOR_PROMPT, VISUAL_PROMPT_TEMPLATES, FRAMEWORK_BLUEPRINTS
)

from engine.router import route_to_target
from engine.cognitive_map import detect_arabic_pattern
from engine.islamic_layer import ISLAMIC_CONTEXT_LAYER
from forge.persona_engine import inject_persona

# ── CORE PARSING & VALIDATION ENGINE ──────────────────────────────────────────

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
    if not json_str: return None, None
    json_start_pos = cleaned.rfind(json_str)
    refined = _TAG_CLEANUP.sub("", cleaned[:json_start_pos].strip()).strip()
    try:
        audit = _clamp_audit(json.loads(json_str))
    except:
        audit = {"score": 0, "critique": "JSON failure.", "precision": 0, "alignment": 0, "efficiency": 0}
    return refined, audit

def _validate_structure(refined: str, target: str) -> Tuple[bool, str]:
    if "[CLARIFICATION_REQUIRED]" in refined: return True, ""
    text = refined.strip()
    if len(text) < 350:
        return False, "Output density insufficient (< 350 chars)."
    if target == 'Claude':
        if not re.search(r'<(?:role|task|constraints|output_format)>', text, re.IGNORECASE):
            return False, 'Claude requires XML: <role>, <task>, <constraints>.'
    if target == 'ChatGPT':
        if not re.search(r'^you\s+are\s+a?\s+\w', text[:80], re.IGNORECASE):
            return False, "ChatGPT requires 'You are a [role]' opener."
    return True, ""

# ── LLM API WRAPPERS ──────────────────────────────────────────────────────────

def _call_evaluator(original_input: str, target: str, refined_prompt: str) -> dict:
    if not client: return {"score": 0, "critique": "Offline"}
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": CIPHER_EVALUATOR_PROMPT},
                {"role": "user",   "content": f"INPUT: {original_input}\nTARGET: {target}\nPROMPT: {refined_prompt}"},
            ],
            response_format={"type": "json_object"},
            temperature=EVAL_TEMPERATURE,
            max_tokens=250,
        )
        return _clamp_audit(json.loads(completion.choices[0].message.content))
    except Exception as e:
        return {"score": 0, "critique": f"Audit Failed: {str(e)[:40]}"}

def _call_cipher(system_prompt: str, user_text: str) -> Tuple[Optional[str], Optional[dict], Optional[str]]:
    if not client: return None, None, "Offline"
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        return _parse_output(completion.choices[0].message.content)
    except Exception as e:
        return None, None, f"[FAULT]: {str(e)[:80]}"

# ── PIPELINE EXECUTION ────────────────────────────────────────────────────────

def _build_system_prompt(target, framework, lang, cognitive_directive, persona, islamic_mode, retry_critique) -> str:
    parts = [CIPHER_IDENTITY]
    parts.append(f'SESSION: Target={target} | Lang={lang}')
    
    if framework in FRAMEWORK_BLUEPRINTS:
        parts.append(f'FRAMEWORK:\n{FRAMEWORK_BLUEPRINTS[framework]}')
    
    if cognitive_directive:
        parts.append(f'COGNITIVE_DIRECTIVE:\n{cognitive_directive}')
    
    # 🟢 SYNCED: Passes persona dict to the forge engine
    if persona:
        # Note: persona here is the dict from st.session_state[K.ACTIVE_PERSONA]
        # In forge/persona_engine.py, ensure inject_persona handles the dict.
        parts.append(f'ACTIVE PERSONA LAYER:\n{inject_persona(persona.get("name") if isinstance(persona, dict) else persona, target)}')
    
    if islamic_mode:
        parts.append(f'CULTURAL LAYER:\n{ISLAMIC_CONTEXT_LAYER}')
    
    if retry_critique:
        parts.append(CIPHER_RETRY_INJECTION.format(critique=retry_critique))
        
    parts.append(CIPHER_OUTPUT_CONTRACT)
    return '\n\n'.join(parts)

def run_refinement_and_audit(
    user_text: str, target: str, framework: str, lang: str, 
    aesthetic_choice: str = "None", islamic_mode: bool = False, 
    persona: Optional[dict] = None
) -> Tuple[str, dict, Optional[dict]]:
    
    cognitive = ""
    pattern_data = None
    
    if lang == "Arabic (العربية)":
        # 🟢 SYNCED: Extract pattern negation logic
        pattern_data = detect_arabic_pattern(user_text)
        if pattern_data:
            cognitive = f"[PATTERN: {pattern_data['pattern']}] {pattern_data['prompt_instruction']}"
        else:
            cognitive = "[LINGUISTIC OVERRIDE] Enforce Fusha. No dialect bleed."

    retry_critique = None
    best_refined, best_audit = None, {"score": 0}

    for attempt in range(MAX_RETRIES + 1):
        sys_prompt = _build_system_prompt(
            target, framework, lang, cognitive, persona, islamic_mode, retry_critique
        )
        refined, self_audit, error = _call_cipher(sys_prompt, user_text)
        
        if error or not refined: 
            return error or "Failed", {"score":0, "critique":error}, None

        passed, reason = _validate_structure(refined, target)
        if not passed:
            retry_critique = reason
            best_refined, best_audit = refined, self_audit
            continue

        if "[CLARIFICATION_REQUIRED]" in refined:
            return refined, {"score": 0, "critique": "Clarification needed."}, pattern_data

        audit = _call_evaluator(user_text, target, refined)
        
        if audit['score'] >= RETRY_THRESHOLD:
            return refined, audit, pattern_data
        
        if audit.get('score', 0) > best_audit.get('score', 0):
            best_refined, best_audit = refined, audit
            
        retry_critique = audit['critique']
        time.sleep(1)

    return best_refined or refined, best_audit or self_audit, pattern_data
