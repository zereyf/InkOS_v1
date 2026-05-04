"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
CIPHER: Cognitive Intelligence for Prompt Heuristics, Engineering and Refinement

v1 Upgrade: Deterministic Scoring Logic.
Forces total score calculation in Python to prevent LLM mathematical hallucinations.
Reduced RETRY_THRESHOLD to 70 for optimized performance.
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

# Optimized for deterministic scoring
RETRY_THRESHOLD: int = 70
MAX_RETRIES:     int = 1

# ─────────────────────────────────────────────────────────────────────────────
# IDENTITY & LOGIC BLOCKS
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
    """Transforms structured dictionary outputs into formatted markdown reports."""
    if isinstance(result, dict):
        lines = []
        for key, value in result.items():
            clean_key = str(key).replace("[", "").replace("]", "").replace("_", " ").upper()
            if isinstance(value, list):
                val_str = "\n".join([f"- {v}" for v in value])
            elif isinstance(value, dict):
                val_str = json.dumps(value, indent=2)
            else:
                val_str = str(value)
            lines.append(f"### {clean_key}\n{val_str}\n")
        return "\n".join(lines)
    return str(result)


def _clamp_audit(raw: dict) -> dict:
    """
    Ensures the audit metrics are within bounds and 
    deterministically calculates the total score in Python.
    """
    def safe_int(val: object, ceiling: int) -> int:
        try:
            # Strip % and handle floats/strings
            clean_val = str(val).replace("%", "").split(".")[0]
            return min(max(int(clean_val), 0), ceiling)
        except (TypeError, ValueError):
            return 0
    
    # Extract components
    p = safe_int(raw.get("precision"),  40)
    a = safe_int(raw.get("alignment"),  40)
    e = safe_int(raw.get("efficiency"), 20)
    
    # ── DETERMINISTIC MATH ──────────────────────────────────────────────────
    # Python handles the addition to prevent LLM hallucinations.
    total_score = p + a + e
    
    return {
        "score":      total_score,
        "critique":   _escape_html(str(raw.get("critique", "")).strip()),
        "precision":  p,
        "alignment":  a,
        "efficiency": e,
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
        '  "audit": {',
        '    "precision": <0-40: technical detail>,',
        '    "alignment": <0-40: dialect adherence>,',
        '    "efficiency": <0-20: token economy>,',
        '    "critique": "<one brief sentence on optimization>"',
        '  }',
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
        
        # Calculate score deterministically using our clamping function
        audit = _clamp_audit(parsed_data.get("audit", {}))
        
        if not refined_raw:
             return None, None, "Parse failed: 'refined_prompt' missing."
             
        refined_final = _humanize_result(refined_raw)
        return refined_final, audit, None

    except Exception as e:
        return None, None, str(e)


def detect_best_target(user_text: str) -> tuple:
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