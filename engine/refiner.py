"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
CIPHER: Cognitive Intelligence for Prompt Heuristics, Engineering and Refinement

v14.0: The Deterministic Intent Compiler.
- Replaced keyword-based auto-routing with an elite LLM Semantic Profiler.
- Uses pure Python deterministic logic for target selection to prevent hallucinations.
- Fully integrated Visual Triad routing (Gemini, DALL-E 3, Midjourney).
"""

import json
import re
import hashlib
from datetime import datetime
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

# ── GLOBAL CONSTANTS & FALLBACKS ─────────────────────────────────────────────
RETRY_THRESHOLD: int = 70
MAX_RETRIES:     int = 1

_FALLBACK_AUDIT: dict = {
    "score": 0, 
    "critique": "Audit parse error — fallback applied.",
    "precision": 0, 
    "alignment": 0, 
    "efficiency": 0,
}

# ── IDENTITY & PIPELINE LAYERS ───────────────────────────────────────────────
CIPHER_IDENTITY: str = """
IDENTITY:
You are CIPHER — InkOS’s Cognitive Prompt Runtime.
You are a deterministic compiler of prompts. You do not chat; you execute.
"""

CIPHER_REASONING_LAYER: str = """
REASONING PROTOCOL:
- Use internal <thinking> tags for all scratchpad logic.
- Analyze the user's linguistic "Delta" (the gap between raw intent and executable prompt).
- Fill the Delta with high-utility, concrete assumptions.
"""

CIPHER_COGNITIVE_PIPELINE: str = """
AMBIGUITY RESOLUTION ENGINE (HARDENED):
- NEVER ask for clarification or state that the input is vague.
- If the user input is vague ("the thing", "it", "plan"), you MUST invent a high-stakes, highly detailed professional context.
- Your output MUST NOT be a short summary. It MUST be a comprehensive, ready-to-execute prompt meant to be fed into another AI, complete with Role, Context, Task, and Constraints.
"""

# ── HELPER UTILITIES ─────────────────────────────────────────────────────────

def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _format_value(val: Any) -> str:
    if isinstance(val, dict):
        return ", ".join([f"{str(k).replace('_', ' ').title()}: {v}" for k, v in val.items()])
    return str(val)

def _humanize_result(result: Any) -> str:
    if isinstance(result, dict):
        lines = []
        for key, value in result.items():
            clean_key = str(key).replace("[", "").replace("]", "").replace("_", " ").upper()
            
            if isinstance(value, list):
                list_lines = []
                for item in value:
                    list_lines.append(f"- {_format_value(item)}")
                val_str = "\n".join(list_lines)
            elif isinstance(value, dict):
                val_str = "\n".join([f"**{str(k).replace('_', ' ').title()}**: {v}" for k, v in value.items()])
            else:
                val_str = str(value)
            
            lines.append(f"### {clean_key}\n{val_str}\n")
        return "\n".join(lines)
    return str(result)

def _clamp_audit(raw: dict) -> dict:
    def safe_int(val: object, ceiling: int) -> int:
        try:
            clean_val = str(val).replace("%", "").split(".")[0]
            return min(max(int(clean_val), 0), ceiling)
        except (TypeError, ValueError):
            return 0
    
    p = safe_int(raw.get("precision"),  40)
    a = safe_int(raw.get("alignment"),  40)
    e = safe_int(raw.get("efficiency"), 20)
    
    total_score = p + a + e
    
    return {
        "score":      total_score,
        "critique":   _escape_html(str(raw.get("critique", "")).strip()),
        "precision":  p,
        "alignment":  a,
        "efficiency": e,
    }

# ── SYSTEM PROMPT BUILDER ────────────────────────────────────────────────────

def _build_system_prompt(
    target:           str,
    framework:        str,
    cognitive:        str,
    islamic:          bool,
    aesthetic_choice: str,
    persona:          Optional[dict] = None,
    retry_critique:   Optional[str]  = None,
) -> str:
    style = f"STYLE DIRECTION: {AESTHETIC_PRESETS.get(aesthetic_choice, '')}" if aesthetic_choice != "Raw (No Preset)" else ""
    persona_block = inject_persona(persona, target)

    if "Visual Director" in framework:
        framework_logic = VISUAL_DIRECTOR_PROMPT
    else:
        framework_logic = (
            f"ACTIVE FRAMEWORK: {framework}\n"
            f"TARGET AI DIALECT: {target}\n"
            f"SYNTAX GUIDE: {TARGET_GUIDES.get(target, '')}"
        )

    retry_block = f"CORRECTION REQUIRED: Previous score low. Critique: '{retry_critique}'" if retry_critique else ""

    parts = [
        CIPHER_IDENTITY,
        CIPHER_REASONING_LAYER,
        persona_block,
        framework_logic,
        style,
        cognitive,
        ISLAMIC_CONTEXT_LAYER if islamic else "",
        CIPHER_COGNITIVE_PIPELINE,
        retry_block,
        "",
        "OUTPUT CONTRACT:",
        "Return ONLY pure JSON.",
        "{",
        '  "thinking": { "intent": "...", "logic": "..." },',
        '  "refined_prompt": "<The massive, highly detailed, ready-to-use prompt artifact. Must be comprehensive.>",',
        '  "audit": {',
        '    "precision": <0-40: SCORE 40 IF YOU SUCCESSFULLY INVENTED A CONCRETE SCENARIO FOR A VAGUE INPUT.>,',
        '    "alignment": <0-40: Adherence to target AI dialect>,',
        '    "efficiency": <0-20: Prompt density and structure>,',
        '    "critique": "<One sentence. DO NOT state that the original input was vague. Praise the strategic assumption.>"',
        '  }',
        "}"
    ]
    return "\n".join(filter(None, parts))

# ── EXECUTION LOGIC ──────────────────────────────────────────────────────────

def _call_cipher(system_prompt: str, user_text: str) -> Tuple[Optional[str], Optional[dict], Optional[str]]:
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": f"[[INPUT_START]]\n{user_text}\n[[INPUT_END]]"},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            response_format={"type": "json_object"}
        )
        raw_json = completion.choices[0].message.content
        parsed = json.loads(raw_json)
        
        refined_raw = parsed.get("refined_prompt")
        audit = _clamp_audit(parsed.get("audit", {}))
        
        if refined_raw is None:
            return None, None, "Missing 'refined_prompt' in JSON."
            
        return _humanize_result(refined_raw), audit, None

    except Exception as e:
        return None, None, str(e)

def detect_best_target(user_text: str) -> tuple:
    # 1. LLM extracts the semantic profile deterministically
    system_prompt = """
    You are InkOS's Semantic Profiler. Analyze the user's request and classify its core intent.
    
    OUTPUT CONTRACT: Return ONLY valid JSON in this exact format:
    {
      "PRIMARY_DOMAIN": "<TYPOGRAPHY_LAYOUT | PHOTOREALISM | CINEMATIC_SCENE | CODE_ANALYSIS | AGENTIC_AUTOMATION | GENERAL_CONVERSATION>",
      "requires_exact_text": <true/false>,
      "requires_spatial_layout": <true/false>,
      "requires_photorealism": <true/false>,
      "is_multi_step_automation": <true/false>,
      "is_arabic_scholarly": <true/false>
    }
    """
    
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text[:500]}],
            response_format={"type": "json_object"},
            temperature=0.0, # Zero temperature for absolute determinism
            max_tokens=150,
        )
        profile = json.loads(completion.choices[0].message.content)
        
        # 2. PYTHON routes the target based on strict priority logic
        domain     = profile.get("PRIMARY_DOMAIN", "GENERAL_CONVERSATION")
        req_text   = profile.get("requires_exact_text", False)
        req_layout = profile.get("requires_spatial_layout", False)
        req_photo  = profile.get("requires_photorealism", False)
        req_auto   = profile.get("is_multi_step_automation", False)
        req_arabic = profile.get("is_arabic_scholarly", False)

        # ── PRIORITY 1: AGENTIC WORKFLOWS ──
        if req_auto or domain == "AGENTIC_AUTOMATION":
            return "Manus AI", "Intent Profile: Multi-step automation / tool use detected."

        # ── PRIORITY 2: THE VISUAL TRIAD ──
        elif req_text or req_layout or domain == "TYPOGRAPHY_LAYOUT":
            return "Gemini (Imagen 3)", "Intent Profile: Strict text/typography or layout requirements."
            
        elif req_photo or domain == "PHOTOREALISM":
            return "DALL-E 3", "Intent Profile: Literal photorealism / product rendering required."
            
        elif domain == "CINEMATIC_SCENE":
            return "Midjourney/Flux", "Intent Profile: Stylized, cinematic, or conceptual art."

        # ── PRIORITY 3: TECHNICAL & SCHOLARLY ──
        elif req_arabic or domain == "CODE_ANALYSIS":
            return "Claude", "Intent Profile: Technical documentation, code, or strict structural needs."

        # ── DEFAULT FALLBACK ──
        else:
            return "ChatGPT", "Intent Profile: Conversational / General creative intent."

    except Exception as e:
        return "Claude", f"Semantic routing failed: {str(e)}"

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
            cognitive = "Arabic input. Map logic conceptually."

    sys_prompt = _build_system_prompt(target, framework, cognitive, islamic_mode, aesthetic_choice, persona)
    refined, audit, error = _call_cipher(sys_prompt, user_text)

    if error:
        return f"[CIPHER ERROR]: {error}", dict(_FALLBACK_AUDIT), None

    score = audit.get("score", 0) if audit else 0
    if score < RETRY_THRESHOLD and audit and audit.get("critique"):
        retry_prompt = _build_system_prompt(target, framework, cognitive, islamic_mode, aesthetic_choice, persona, retry_critique=audit["critique"])
        r2, a2, e2 = _call_cipher(retry_prompt, user_text)
        if not e2 and r2 and a2 and a2.get("score", 0) >= score:
            return r2, a2, detected

    return refined, audit, detected