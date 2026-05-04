"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
CIPHER: Cognitive Intelligence for Prompt Heuristics, Engineering and Refinement

v12.6 Upgrade: Integrated Humanizer logic to transform structured JSON outputs
into professional, human-readable documents.
"""

import json
from typing import Optional, Tuple, Any
from config import (
    client, TARGET_GUIDES, MODEL_ID, TEMPERATURE,
    MAX_TOKENS, AESTHETIC_PRESETS,
    AUTO_SELECT_LABEL, TARGET_SELECTION_GUIDE,
    VISUAL_DIRECTOR_PROMPT
)
from engine.cognitive_map import detect_arabic_pattern
from engine.islamic_layer import ISLAMIC_CONTEXT_LAYER
from forge.persona_engine import inject_persona

RETRY_THRESHOLD: int = 80
MAX_RETRIES:     int = 1

# ─────────────────────────────────────────────────────────────────────────────
# CIPHER MASTER IDENTITY SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────
CIPHER_IDENTITY: str = """
IDENTITY:
You are CIPHER — InkOS’s Cognitive Prompt Runtime.
You are not an assistant. You are a deterministic compiler of prompts.
"""

CIPHER_COGNITIVE_PIPELINE: str = """
COGNITIVE RUNTIME PIPELINE:
1. PARSE INTENT | 2. NORMALIZE | 3. CONSTRAINTS | 4. DIALECT PROFILE | 5. COMPILE.

AMBIGUITY RESOLUTION ENGINE:
Resolve using highest utility assumption and professional context bias. 
Do not ask questions.
"""

_FALLBACK_AUDIT: dict = {
    "score": 0, "critique": "Audit parse error.",
    "precision": 0, "alignment": 0, "efficiency": 0,
}


def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _humanize_result(result: Any) -> str:
    """
    Transforms structured dictionary outputs into professional, 
    formatted markdown documents.
    """
    if isinstance(result, dict):
        lines = []
        for key, value in result.items():
            # Clean and embolden headers
            clean_key = str(key).replace("[", "").replace("]", "").replace("_", " ").upper()
            if isinstance(value, list):
                val_str = "\n".join([f"- {v}" for v in value])
            elif isinstance(value, dict):
                val_str = json.dumps(value, indent=2)
            else:
                val_str = str(value)
            
            lines.append(f"### {clean_key}\n{val_str}\n")
        return "\n".join(lines)
    
    # If it's already a string, return it as is
    return str(result)


def _clamp_audit(raw: dict) -> dict:
    def safe_int(val: object, ceiling: int) -> int:
        try:
            return min(max(int(val), 0), ceiling)
        except (TypeError, ValueError):
            return 0
    return {
        "score":      safe_int(raw.get("score"),      100),
        "critique":   _escape_html(str(raw.get("critique", "")).strip()),
        "precision":  safe_int(raw.get("precision"),   40),
        "alignment":  safe_int(raw.get("alignment"),   40),
        "efficiency": safe_int(raw.get("efficiency"),  20),
    }


def _build_system_prompt(
    target:           str,
    framework:        str,
    cognitive:        str,
    islamic:          bool,
    aesthetic_choice: str,
    persona:          Optional[dict] = None,
    retry_critique:   Optional[str]  = None,
) -> str:
    style = f"STYLE: {AESTHETIC_PRESETS.get(aesthetic_choice, '')}" if aesthetic_choice != "Raw (No Preset)" else ""
    persona_block = inject_persona(persona, target)

    if "Visual Director" in framework:
        framework_logic = VISUAL_DIRECTOR_PROMPT
    else:
        framework_logic = (
            f"ACTIVE FRAMEWORK: {framework}\n"
            f"TARGET DIALECT: {target}\n"
            f"SYNTAX GUIDE: {TARGET_GUIDES.get(target, '')}"
        )

    retry_block = f"CORRECTION: Previous score low. Critique: '{retry_critique}'" if retry_critique else ""

    parts = [
        CIPHER_IDENTITY,
        persona_block,
        framework_logic,
        style,
        cognitive,
        ISLAMIC_CONTEXT_LAYER if islamic else "",
        CIPHER_COGNITIVE_PIPELINE,
        retry_block,
        "OUTPUT CONTRACT: Return ONLY pure JSON.",
        "{",
        '  "thinking": { ... },',
        '  "refined_prompt": "<string OR object>",',
        '  "audit": { "score": 0, "critique": "...", "precision": 0, "alignment": 0, "efficiency": 0 }',
        "}"
    ]
    return "\n".join(filter(None, parts))


def _call_cipher(
    system_prompt: str,
    user_text:     str,
) -> Tuple[Optional[str], Optional[dict], Optional[str]]:
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": f"[[INPUT]]\n{user_text}"},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            response_format={"type": "json_object"}
        )
        raw_json = completion.choices[0].message.content
        parsed_data = json.loads(raw_json)
        
        refined_raw = parsed_data.get("refined_prompt")
        audit = _clamp_audit(parsed_data.get("audit", {}))
        
        if not refined_raw:
             return None, None, "Parse failed: 'refined_prompt' missing."
             
        # ── APPLY HUMANIZER ──────────────────────────────────────────────────
        # Transform dictionaries into professional markdown reports
        refined_final = _humanize_result(refined_raw)
             
        return refined_final, audit, None

    except Exception as e:
        return None, None, str(e)


def detect_best_target(user_text: str) -> tuple:
    # (Existing auto-selection logic)
    system_prompt = f"Identify best target AI.\n{TARGET_SELECTION_GUIDE}"
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text[:500]}],
            response_format={"type": "json_object"},
            temperature=0.1, max_tokens=100
        )
        raw = json.loads(completion.choices[0].message.content)
        return str(raw.get("target", "Claude")), str(raw.get("reason", ""))
    except:
        return "Claude", "Auto-selection failed."


def run_refinement_and_audit(
    user_text:        str,
    target:           str,
    framework:        str,
    lang:             str,
    aesthetic_choice: str,
    islamic_mode:     bool           = False,
    persona:          Optional[dict] = None,
) -> Tuple[str, dict, Optional[dict]]:
    detected: Optional[dict] = None
    cognitive: str = ""

    if lang == "Arabic (العربية)":
        detected = detect_arabic_pattern(user_text)
        if detected:
            cognitive = f"PATTERN: {detected['pattern']} -> {detected['prompt_paradigm']}"
        else:
            cognitive = "Arabic input. Map logic, do not translate."

    sys_prompt = _build_system_prompt(target, framework, cognitive, islamic_mode, aesthetic_choice, persona)
    refined, audit, error = _call_cipher(sys_prompt, user_text)

    if error:
        return f"[CIPHER ERROR]: {error}", dict(_FALLBACK_AUDIT), None

    return refined, audit, detected