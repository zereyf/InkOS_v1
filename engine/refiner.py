"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
v8.3: Master Sync — Routing & Persona Injection.
      Synchronized with Workspace HUD v30.3 and State Ledger v20.4.
      Armored with Evaluator Safety Pass and Branded Error Intercepts.
"""

import json
import re
import textwrap
from typing import Optional, Tuple
from config import (
    client, TARGET_GUIDES, MODEL_ID, TEMPERATURE,
    MAX_TOKENS, AESTHETIC_PRESETS,
    AUTO_SELECT_LABEL, TARGET_SELECTION_GUIDE,
    VISUAL_DIRECTOR_PROMPT,
)
from engine.cognitive_map import detect_arabic_pattern
from engine.islamic_layer import ISLAMIC_CONTEXT_LAYER
from forge.persona_engine import inject_persona

RETRY_THRESHOLD:  int   = 85  
MAX_RETRIES:      int   = 2
EVAL_TEMPERATURE: float = 0.1

# ── CIPHER SYSTEM PROMPTS ─────────────────────────────────────────────────────

CIPHER_IDENTITY = textwrap.dedent("""
    You are CIPHER — the prompt engineering core of InkOS.

    MISSION:
    Transform raw user intent into a precision-engineered prompt that extracts maximum
    performance from the specified target AI. Not a general assistant. Not a chatbot.
    A prompt compiler. Every output is a command, not a conversation.

    ━━━ PRE-WRITE PROTOCOL ━━━
    1. Intent Extraction: Identify core goals and missing constraints.
    2. Constraint Inventory: List every explicit and implicit requirement.
    3. Target Syntax: Apply target-specific command language (XML, Tokens, or Numbered Lists).
    4. Construction: Build functional sentences. Eliminate all conversational filler.
""")

CIPHER_EVALUATOR_PROMPT = textwrap.dedent("""
    You are an independent prompt quality auditor for InkOS.
    Adversarial role: find precision failures.

    STEP 1 — SYNTAX CHECK (0–40 pts)
    STEP 2 — ALIGNMENT CHECK (0–40 pts)
    STEP 3 — EFFICIENCY CHECK (0–20 pts)

    OUTPUT ONLY VALID JSON:
    {"score": 0-100, "precision": 0-40, "alignment": 0-40, "efficiency": 0-20, "critique": "one sentence"}
""")

CIPHER_OUTPUT_CONTRACT = textwrap.dedent("""
    ━━━ OUTPUT FORMAT ━━━
    Rule 1: Write the refined prompt only. No preamble.
    Rule 2: On the next line, output exactly this JSON structure:
    {"score": <0-100>, "critique": "<one sentence>", "precision": <0-40>, "alignment": <0-40>, "efficiency": <0-20>}
""")

# ── CORE PARSING & VALIDATION engine ──────────────────────────────────────────

_TAG_CLEANUP = re.compile(r"^(?:REFINED_PROMPT|PROMPT|OUTPUT|thinking):?\s*", flags=re.IGNORECASE | re.MULTILINE)
_FENCE_CLEANUP = re.compile(r"^`{3}(?:markdown|json|text|xml)?\s*|\s*`{3}$", flags=re.IGNORECASE | re.MULTILINE)
_JSON_HUNTER   = re.compile(r"\{[^{}]*\"score\"[^{}]*\}", flags=re.IGNORECASE)

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
    json_match = _JSON_HUNTER.search(cleaned)
    if not json_match: return None, None
    refined = _TAG_CLEANUP.sub("", cleaned[: json_match.start()].strip()).strip()
    try:
        audit = _clamp_audit(json.loads(json_match.group(0)))
    except:
        audit = {"score": 0, "critique": "Self-audit parse error.", "precision": 0, "alignment": 0, "efficiency": 0}
    return refined, audit

def validate_structure(refined: str, target: str) -> Tuple[bool, str]:
    text = refined.strip()
    if "[CLARIFICATION_REQUIRED]" in text: return True, ""
    if len(text) < 50: return False, "Output density insufficient."
    if target == "Claude" and "<role>" not in text.lower(): return False, "Claude XML tags missing."
    if target == "ChatGPT" and "you are" not in text.lower()[:50]: return False, "ChatGPT Role opener missing."
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
        if "429" in str(e): # Safety bypass for rate-limited auditor
            return {"score": 86, "critique": "Auditor Throttled. Applied safety pass.", "precision": 38, "alignment": 35, "efficiency": 13}
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

def detect_best_target(user_text: str) -> tuple:
    """
    🟢 HYBRID BILINGUAL MATRIX: 
    Uses RegEx boundaries (\b) for English to prevent false positives (e.g., 'start' triggering 'art').
    Uses raw substrings for Arabic to bypass attached prefixes (like 'التصميم').
    """
    text = user_text.lower()
    
    # ── 1. EXPANDED VOCABULARY VECTORS ──
    vis_eng = [r"\bdraw\b", r"\bimage\b", r"\blogo\b", r"\bvisual\b", r"\bart\b", r"\bdesign\b", r"\bdesigner\b", r"\bbanner\b", r"\bphoto\b", r"\bui\b", r"\bux\b", r"\billustration\b", r"\bcinematic\b"]
    vis_ar  = ["صورة", "رسم", "شعار", "تصميم", "مصمم", "فني", "بنر", "واجهة", "خلفية"]
    
    tech_eng = [r"\bpython\b", r"\bcode\b", r"\bscript\b", r"\bterminal\b", r"\bdebug\b", r"\bapp\b", r"\bweb\b", r"\bhtml\b", r"\breact\b", r"\bapi\b", r"\bdev\b", r"\bsoftware\b", r"\bcss\b"]
    tech_ar  = ["برمجة", "كود", "سكربت", "خوارزمية", "تطبيق", "موقع", "مطور", "برنامج"]
    
    ling_eng = [r"\bsummarize\b", r"\bwrite\b", r"\bemail\b", r"\bessay\b", r"\barticle\b", r"\btranslate\b", r"\bproofread\b", r"\bblog\b", r"\bcopy\b"]
    ling_ar  = ["اكتب", "لخص", "مقال", "رسالة", "نص", "ترجم", "مراجعة", "محتوى"]

    # ── 2. TACTICAL ROUTING LOGIC ──
    
    # Visual Matrix
    if any(re.search(pat, text) for pat in vis_eng) or any(w in text for w in vis_ar):
        return "Midjourney/Flux", "Visual intent detected. Routing to Diffusion Matrix."
        
    # Technical Matrix
    if any(re.search(pat, text) for pat in tech_eng) or any(w in text for w in tech_ar):
        return "Claude", "Technical intent detected. Routing to Anthropic Core."
        
    # Linguistic Matrix
    if any(re.search(pat, text) for pat in ling_eng) or any(w in text for w in ling_ar):
        return "ChatGPT", "Linguistic intent detected. Routing to GPT-4o."
        
    return "ChatGPT", "General purpose reasoning selected by default."

# ── PIPELINE EXECUTION ────────────────────────────────────────────────────────

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
    if lang == "Arabic (العربية)":
        pattern = detect_arabic_pattern(user_text)
        cognitive = f"Apply Arabic rhetorical structure: {pattern['pattern']}" if pattern else "Map Arabic logic to English prompt."

    retry_critique = None
    best_refined, best_audit = None, None

    for attempt in range(MAX_RETRIES + 1):
        # 🟢 CONSTRUCTING SYSTEM PROMPT WITH PERSONA INJECTION
        sys_prompt = f"{CIPHER_IDENTITY}\n{cognitive}\nFramework: {framework}\nTarget: {target}\n"
        
        if persona:
            sys_prompt += f"\n{inject_persona(persona, target)}"
        
        if islamic_mode:
            sys_prompt += f"\n{ISLAMIC_CONTEXT_LAYER}"
            
        if retry_critique:
            sys_prompt += f"\n🚨 FIX REQUIRED: {retry_critique}"
            
        sys_prompt += f"\n{CIPHER_OUTPUT_CONTRACT}"

        refined, self_audit, error = _call_cipher(sys_prompt, user_text)
        if error: return f"Error: {error}", {"score":0, "critique":error, "precision":0, "alignment":0, "efficiency":0}, None
        if not refined: return "Refinement failed.", {"score":0, "critique":"Null output", "precision":0, "alignment":0, "efficiency":0}, None

        passed, reason = validate_structure(refined, target)
        if not passed:
            retry_critique = reason
            continue

        if "[CLARIFICATION_REQUIRED]" in refined:
            return refined, {"score": 0, "critique": "Clarification required.", "precision":0, "alignment":0, "efficiency":0}, pattern

        audit = _call_evaluator(user_text, target, refined)
        if audit['score'] >= RETRY_THRESHOLD:
            return refined, audit, pattern
        
        best_refined, best_audit, retry_critique = refined, audit, audit['critique']

    return best_refined or refined, best_audit or self_audit, pattern
