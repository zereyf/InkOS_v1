
"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
v9.4: Production-Grade Hardened Build.
      - 350-char validation (Sync with 60-word Identity).
      - Unicode-Hex backtick escapes (Streamlit safety).
      - Mathematical Brace-Balancing JSON Recovery.
      - Best-Effort Historical Fallback.
"""

import json
import re
import textwrap
import time
from typing import Optional, Tuple

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

# 🟢 FIXED: Unicode-Hex (\x60 = `) ensures Streamlit deployment doesn't snap the string
_FENCE_CLEANUP = re.compile("\x60\x60\x60(?:markdown|json|text|xml)?|\x60\x60\x60", flags=re.IGNORECASE)

def _extract_json(text: str) -> Optional[str]:
    """Surgical JSON Recovery via mathematical brace-balancing."""
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
        audit = {"score": 0, "critique": "JSON structural failure.", "precision": 0, "alignment": 0, "efficiency": 0}
    return refined, audit

def _validate_structure(refined: str, target: str) -> Tuple[bool, str]:
    """Structural validation synced with Identity word-count requirements."""
    if "[CLARIFICATION_REQUIRED]" in refined:
        return True, ""
        
    text = refined.strip()
    # 🟢 SYNCED: 350 chars approximates the 60-word requirement in Identity
    if len(text) < 350:
        return False, "Output density insufficient — prompt under 350 char minimum."
        
    if target == 'Claude':
        if not re.search(r'<(?:role|task|constraints|output_format)>', text, re.IGNORECASE):
            return False, 'Claude target requires XML tags: <role>, <task>, <constraints>, <output_format>.'
            
    if target == 'ChatGPT':
        if not re.search(r'^you\s+are\s+a?\s+\w', text[:80], re.IGNORECASE):
            return False, "ChatGPT target requires 'You are a [role]' opener."
            
    if target == 'Midjourney/Flux':
        if '::' not in text:
            return False, 'Midjourney/Flux target requires :: separators.'
            
    return True, ""

# ── API WRAPPERS & EXECUTION ──────────────────────────────────────────────────

def _call_evaluator(original_input: str, target: str, refined_prompt: str) -> dict:
    if not client: return {"score": 0, "critique": "API Offline"}
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
        return {"score": 0, "critique": "Evaluator rate-limited or offline." if '429' in str(e) else str(e)}

def _call_cipher(system_prompt: str, user_text: str) -> Tuple[Optional[str], Optional[dict], Optional[str]]:
    if not client: return None, None, "Client Offline"
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        refined, audit = _parse_output(completion.choices[0].message.content)
        return refined, audit, None
    except Exception as e:
        return None, None, f"[FAULT]: {str(e)[:80]}"

def _build_system_prompt(target, framework, lang, cognitive_directive, persona, islamic_mode, retry_critique) -> str:
    parts = [CIPHER_IDENTITY]
    parts.append(f'ACTIVE SESSION:\n  Target AI: {target}\n  Input Language: {lang}')
    
    if framework == "Visual Director":
        parts.append(f'ACTIVE FRAMEWORK RULES:\n{VISUAL_DIRECTOR_PROMPT}\n{VISUAL_PROMPT_TEMPLATES}')
    elif framework in FRAMEWORK_BLUEPRINTS:
        parts.append(f'ACTIVE FRAMEWORK RULES:\n{FRAMEWORK_BLUEPRINTS[framework]}')
                 
    if cognitive_directive: parts.append(cognitive_directive)
    if persona: parts.append(inject_persona(persona, target))
    if islamic_mode: parts.append(ISLAMIC_CONTEXT_LAYER)
    if retry_critique: parts.append(CIPHER_RETRY_INJECTION.format(critique=retry_critique))
        
    parts.append(CIPHER_OUTPUT_CONTRACT)
    return '\n\n'.join(parts)

def run_refinement_and_audit(
    user_text, target, framework, lang, aesthetic_choice="None", islamic_mode=False, persona=None
) -> Tuple[str, dict, Optional[dict]]:
    
    cognitive, pattern = "", None
    if lang == "Arabic (العربية)":
        pattern = detect_arabic_pattern(user_text)
        cognitive = "[LINGUISTIC OVERRIDE: ARABIC] Strictly enforce Fusha. No dialectal bleed."

    retry_critique = None
    best_refined, best_audit = None, {"score": 0}

    for attempt in range(MAX_RETRIES + 1):
        sys_prompt = _build_system_prompt(target, framework, lang, cognitive, persona, islamic_mode, retry_critique)
        refined, self_audit, error = _call_cipher(sys_prompt, user_text)
        
        if error or not refined: return error or "Refinement failed.", {"score": 0}, None

        passed, reason = _validate_structure(refined, target)
        if not passed:
            retry_critique = reason
            best_refined, best_audit = refined, self_audit
            continue

        audit = _call_evaluator(user_text, target, refined)
        
        if "rate-limited" in audit['critique'] and best_refined:
            return best_refined, best_audit, pattern
            
        if audit['score'] >= RETRY_THRESHOLD:
            return refined, audit, pattern
        
        if audit.get('score', 0) > best_audit.get('score', 0):
            best_refined, best_audit = refined, audit
            
        retry_critique = audit['critique']
        time.sleep(1)

    return best_refined or refined, best_audit, pattern
