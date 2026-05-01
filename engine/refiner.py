"""
engine/refiner.py — Hardened Prompt Refinement + Audit Engine
"""

import json
import re
from typing import Optional, Tuple
from config import client, TARGET_GUIDES, MODEL_ID, TEMPERATURE, MAX_TOKENS, AESTHETIC_PRESETS
from engine.cognitive_map import detect_arabic_pattern
from engine.islamic_layer import ISLAMIC_CONTEXT_LAYER

_FALLBACK_AUDIT: dict = {
    "score":     0,
    "critique":  "Audit parse error — refinement succeeded.",
    "precision": 0,
    "alignment": 0,
    "efficiency":0,
}

def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _clamp_audit(raw: dict) -> dict:
    def safe_int(val: object, ceiling: int) -> int:
        try:
            return min(max(int(val), 0), ceiling)
        except (TypeError, ValueError):
            return 0
    return {
        "score":     safe_int(raw.get("score"),     100),
        "critique":  _escape_html(str(raw.get("critique", "")).strip()),
        "precision": safe_int(raw.get("precision"),  40),
        "alignment": safe_int(raw.get("alignment"),  40),
        "efficiency":safe_int(raw.get("efficiency"), 20),
    }

def _build_system_prompt(target, framework, cognitive, islamic, aesthetic_choice):
    style = f"STYLE DIRECTION: {AESTHETIC_PRESETS.get(aesthetic_choice, '')}" if aesthetic_choice != "Raw (No Preset)" else ""
    parts = [
        "You are a Senior Prompt Architect. Your objective is a 100/100 score on the VelvetCodex Audit.",
        f"FRAMEWORK: {framework}",
        f"TARGET AI: {target}",
        f"DIALECT GUIDE: {TARGET_GUIDES.get(target, '')}",
        style,
        cognitive,
        ISLAMIC_CONTEXT_LAYER if islamic else "",
        "",
        "=== MANDATORY AUDIT RUBRIC ===",
        "1. PRECISION (40pts): Use strict target-specific syntax (XML for Claude, Agent-steps for Manus).",
        "2. ALIGNMENT (40pts): Every user constraint must be explicitly preserved in the refined asset.",
        "3. EFFICIENCY (20pts): Zero conversational filler. No preamble. No introductory politeness.",
        "CRITICAL: If the output scores below 95/100, you must self-correct and rewrite before responding.",
        "",
        "=== OUTPUT FORMAT ===",
        "Return exact delimiters. No markdown fences. No preamble.",
        "===REFINED===",
        "<refined_prompt_text>",
        "===AUDIT===",
        '{"score": <points>, "critique": "<reason>", "precision": <0-40>, "alignment": <0-40>, "efficiency": <0-20>}'
    ]
    return "\n".join(filter(None, parts))

def run_refinement_and_audit(user_text, target, framework, lang, aesthetic_choice, islamic_mode=False):
    detected: Optional[dict] = None
    cognitive: str = ""
    if lang == "Arabic (العربية)":
        detected = detect_arabic_pattern(user_text)
        cognitive = f"PATTERN: {detected['pattern']}" if detected else "Input is Arabic. Map core intent."

    sys_prompt = _build_system_prompt(target, framework, cognitive, islamic_mode, aesthetic_choice)
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": sys_prompt}, 
                {"role": "user", "content": f"[[INPUT_START]]\n{user_text}\n[[INPUT_END]]"}
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
        )
        raw = completion.choices[0].message.content

      # --- BULLETPROOF PARSING ENGINE ---
        
        # 1. Strip out markdown fences (Added 'xml' to the strip list)
        raw_clean = re.sub(r"```(markdown|json|text|xml)?", "", raw, flags=re.IGNORECASE).strip()

        # 2. Ultra-Flexible regex search (Handles ===AUDIT===, <AUDIT>, or [AUDIT])
        audit_pattern = r"(?:===|<|\[)\s*AUDIT\s*(?:===|>|\])"
        
        if not re.search(audit_pattern, raw_clean, flags=re.IGNORECASE):
            return f"[REFINEMENT ERROR] AI ignored delimiters. Raw Output:\n\n{raw}", _FALLBACK_AUDIT, None

        # 3. Split using the flexible pattern
        parts = re.split(audit_pattern, raw_clean, flags=re.IGNORECASE)
        
        # 4. Clean up the refined section (Handles ===REFINED=== or <refined_prompt_text>)
        refined = parts[0]
        refined_pattern = r"(?:===|<|\[)\s*REFINED(?:_PROMPT_TEXT)?\s*(?:===|>|\])"
        refined = re.sub(refined_pattern, "", refined, flags=re.IGNORECASE).strip()
        
        # 5. Extract and parse the JSON safely
        audit_raw = parts[1].strip()
        # --- THE ULTIMATE PARSER (JSON HUNTER) ---
        
        # 1. Strip markdown fences
        raw_clean = re.sub(r"```(markdown|json|text|xml)?", "", raw, flags=re.IGNORECASE).strip()

        # 2. Hunt directly for the JSON dictionary (Looks for a { block containing "score" )
        json_match = re.search(r"\{[^{}]*\"score\"[^{}]*\}", raw_clean, flags=re.IGNORECASE)
        
        if not json_match:
            # If we literally cannot find a JSON object, the AI totally failed.
            return f"[REFINEMENT ERROR] AI failed to output JSON. Raw:\n\n{raw}", _FALLBACK_AUDIT, None

        # 3. Extract the JSON payload
        audit_raw = json_match.group(0)
        
        # 4. Extract the prompt (Everything BEFORE the JSON)
        refined_raw = raw_clean[:json_match.start()].strip()
        
        # 5. Clean up any hallucinated tags from the prompt text (===REFINED===, <refined>, **AUDIT**, etc.)
        cleanup_pattern = r"(?:===|<|\[|\*\*|###)\s*(?:REFINED(?:_PROMPT(?:_TEXT)?)?|AUDIT)\s*(?:===|>|\]|\*\*|###)?"
        refined = re.sub(cleanup_pattern, "", refined_raw, flags=re.IGNORECASE).strip()
        
        # 6. Parse JSON
        try:
            audit = _clamp_audit(json.loads(audit_raw))
        except Exception:
            audit = dict(_FALLBACK_AUDIT)
            audit["critique"] = "Refinement succeeded, but JSON was scrambled."

        return refined, audit, detected

    except Exception as e:
        return f"[REFINEMENT ERROR]: {str(e)}", _FALLBACK_AUDIT, None