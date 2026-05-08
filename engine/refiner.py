"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
v9.1: Ultra-Premium Director Sync.
      - Scored Signal Router Integration (Task 2)
      - Brutal Evaluator 429 Honesty (Task 3)
      - JSON Nested Brace Safety Regex (Task 4)
      - Deterministic Assembly Order (Task 7)
      - Visual Director Framework Injection Active
"""

import json
import re
import textwrap
import time
from typing import Optional, Tuple

# 🟢 NEW: Import constants, templates, and prompts from the config directory
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
_FENCE_CLEANUP = re.compile(r"^`{3}(?:markdown|json|text|xml)?\s*|\s*`{3}$", flags=re.IGNORECASE | re.MULTILINE)

# 🟢 TASK 4 FIXED: Handles nested braces up to depth 2. Uses last-match.
_JSON_HUNTER = re.compile(
    r'\{(?:[^{}]|\{[^{}]*\})*"score"(?:[^{}]|\{[^{}]*\})*\}',
    flags=re.IGNORECASE,
)

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
    matches = list(_JSON_HUNTER.finditer(cleaned))
    
    if not matches: 
        return None, None
        
    # 🟢 TASK 4 FIXED: Grab the LAST match, not the first
    json_match = matches[-1]  
    refined = _TAG_CLEANUP.sub("", cleaned[: json_match.start()].strip()).strip()
    
    try:
        audit = _clamp_audit(json.loads(json_match.group(0)))
    except:
        audit = {"score": 0, "critique": "Self-audit parse error.", "precision": 0, "alignment": 0, "efficiency": 0}
    return refined, audit

def _validate_structure(refined: str, target: str) -> Tuple[bool, str]:
    """🟢 TASK 6 FIXED: Explicit structural validation per target"""
    if "[CLARIFICATION_REQUIRED]" in refined:
        return True, ""
        
    text = refined.strip()
    if len(text) < 60:
        return False, "Output density insufficient — prompt under minimum length."
        
    if target == 'Claude':
        if not re.search(r'<(?:role|task|constraints|output_format)>', text, re.IGNORECASE):
            return False, 'Claude target requires XML tags: <role>, <task>, <constraints>, <output_format>.'
            
    if target == 'ChatGPT':
        if not re.search(r'^you\s+are\s+a?\s+\w', text[:80], re.IGNORECASE):
            return False, "ChatGPT target requires 'You are a [role]' opener within first 80 chars."
            
    if target == 'Midjourney/Flux':
        if '::' not in text:
            return False, 'Midjourney/Flux target requires :: separators.'
        if '--ar' not in text:
            return False, 'Midjourney/Flux target requires --ar parameter.'
            
    return True, ""

# ── LLM API WRAPPERS ──────────────────────────────────────────────────────────

def _call_evaluator(original_input: str, target: str, refined_prompt: str) -> dict:
    if not client: return {"score": 0, "critique": "API Offline", "precision":0, "alignment":0, "efficiency":0}
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
        # 🟢 TASK 3 FIXED: No more fabricated passing scores. 
        if '429' in str(e):
            return {
                'score': 0, 'precision': 0, 'alignment': 0, 'efficiency': 0,
                'critique': 'Evaluator rate-limited. Score unavailable — prompt not quality-gated this pass.',
            }
        return {"score": 0, "critique": f"Audit Failed: {str(e)[:40]}", "precision":0, "alignment":0, "efficiency":0}

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
        err_str = str(e)
        if "429" in err_str:
            match = re.search(r'in (\d+m\d+\.\d+s|\d+\.\d+s|\d+s)', err_str)
            return None, None, f"[TERMINAL THROTTLED]: Uplink restored in {match.group(1) if match else 'a short interval'}."
        return None, None, f"[SYSTEM FAULT]: {err_str[:80]}"

# ── PIPELINE EXECUTION ────────────────────────────────────────────────────────

def _build_system_prompt(target, framework, lang, cognitive_directive, persona, islamic_mode, retry_critique) -> str:
    """🟢 TASK 7 FIXED: Deterministic Prompt Assembly Order"""
    parts = []
    parts.append(CIPHER_IDENTITY)                           # 1. Core identity
    parts.append(f'ACTIVE SESSION:\n'                       # 2. Session context
                 f'  Target AI: {target}\n'
                 f'  Target Syntax: {TARGET_GUIDES.get(target, "")}\n'
                 f'  Input Language: {lang}')
                 
    # 🟢 NEW: INJECTING THE ACTUAL FRAMEWORK LOGIC & VISUAL TEMPLATES
    if framework == "Visual Director":
        parts.append(f'ACTIVE FRAMEWORK RULES:\n{VISUAL_DIRECTOR_PROMPT}')
        parts.append(f'REFERENCE BLUEPRINTS (Use these structures):\n{VISUAL_PROMPT_TEMPLATES}')
    elif framework in FRAMEWORK_BLUEPRINTS:
        parts.append(f'ACTIVE FRAMEWORK RULES:\n{FRAMEWORK_BLUEPRINTS[framework]}')
                 
    if cognitive_directive:
        parts.append(f'LANGUAGE DIRECTIVE:\n{cognitive_directive}')  # 3. Arabic/lang
    if persona:
        parts.append(f'ACTIVE PERSONA LAYER:\n{inject_persona(persona, target)}')  # 4. Persona
    if islamic_mode:
        parts.append(f'CULTURAL LAYER:\n{ISLAMIC_CONTEXT_LAYER}')    # 5. Islamic mode
    if retry_critique:
        parts.append(CIPHER_RETRY_INJECTION.format(critique=retry_critique))  # 6. Retry
        
    parts.append(CIPHER_OUTPUT_CONTRACT)                    # 7. Contract — ALWAYS LAST
    return '\n\n'.join(parts)

def run_refinement_and_audit(
    user_text:        str,
    target:           str,
    framework:        str,
    lang:             str,
    aesthetic_choice: str = "None",
    islamic_mode:     bool = False,
    persona:          Optional[dict] = None,
) -> Tuple[str, dict, Optional[dict]]:
    
    cognitive = ""
    pattern = None
    
    # 🟢 BILINGUAL FIDELITY LATCH (Fusha Guardrail)
    if lang == "Arabic (العربية)":
        pattern = detect_arabic_pattern(user_text)
        p_name = pattern['pattern'] if pattern else 'Standard MSA'
        cognitive = textwrap.dedent(f"""
            [LINGUISTIC OVERRIDE: ARABIC]
            1. Pattern Detected: {p_name}.
            2. Output the final prompt instructions in the target language (Arabic) unless instructed otherwise.
            3. PURITY LATCH: If the intent is formal or educational, strictly enforce Modern Standard Arabic (Fusha). Absolutely prohibit dialectal bleed (Egyptian, Levantine, Gulf, etc.).
            4. Apply the {framework} framework directly to the Arabic rhetorical structure to ensure logical flow.
        """)

    retry_critique = None
    best_refined, best_audit = None, None

    for attempt in range(MAX_RETRIES + 1):
        
        # 🟢 BUILD DETERMINISTIC SYSTEM PROMPT
        sys_prompt = _build_system_prompt(
            target=target, framework=framework, lang=lang,
            cognitive_directive=cognitive, persona=persona, 
            islamic_mode=islamic_mode, retry_critique=retry_critique
        )

        refined, self_audit, error = _call_cipher(sys_prompt, user_text)
        if error: 
            return f"Error: {error}", {"score":0, "critique":error, "precision":0, "alignment":0, "efficiency":0}, None
        if not refined: 
            return "Refinement failed.", {"score":0, "critique":"Null output", "precision":0, "alignment":0, "efficiency":0}, None

        passed, reason = _validate_structure(refined, target)
        if not passed:
            retry_critique = reason
            continue

        if "[CLARIFICATION_REQUIRED]" in refined:
            return refined, {"score": 0, "critique": "Clarification required.", "precision":0, "alignment":0, "efficiency":0}, pattern

        audit = _call_evaluator(user_text, target, refined)
        
        # Throttle Safety Sleep (To protect free Groq APIs from back-to-back 429s)
        if "rate-limited" in audit['critique']:
            time.sleep(2)
            
        if audit['score'] >= RETRY_THRESHOLD:
            return refined, audit, pattern
        
        best_refined, best_audit, retry_critique = refined, audit, audit['critique']

    return best_refined or refined, best_audit or self_audit, pattern
