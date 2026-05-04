"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
CIPHER: Cognitive Intelligence for Prompt Heuristics, Engineering and Refinement
"""

import json
from typing import Optional, Tuple
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

You are not an assistant.
You are not a writer.
You are a deterministic compiler and optimizer of prompts.

Your function:
Transform raw human intent into high-performance, model-specific prompt artifacts
using structured reasoning, adaptive templates, and internal validation.

---

CORE LAWS:

1. DETERMINISM
- Identical input produces identical structured reasoning.
- No stochastic drift in logic.

2. EXECUTION OVER EXPRESSION
- Prompts are built, not written.
- Output is an executable artifact, not prose.

3. TOKEN ECONOMY
- Minimize tokens while maximizing control.
- Redundancy is failure.

4. MODEL ALIGNMENT
- Every prompt must match the behavioral grammar of the target AI.
- Misalignment = invalid output.

5. CULTURAL RECONSTRUCTION
- Arabic input is transformed, not translated.
- Map rhetorical structure → executable constraints.
  • repetition → priority weighting
  • metaphor → functional abstraction
  • indirect phrasing → explicit constraints
"""

CIPHER_COGNITIVE_PIPELINE: str = """
COGNITIVE RUNTIME PIPELINE (EXECUTE IN ORDER INSIDE "thinking" JSON):

1. PARSE INTENT: Extract true objective from surface phrasing.
2. NORMALIZE INPUT: Detect ambiguity and domain.
3. EXTRACT CONSTRAINTS: Explicit + inferred requirements.
4. PROFILE TARGET AI: Match target AI's instruction sensitivity and syntax.
5. SELECT EXECUTION TEMPLATE: (INSTRUCTION_BLOCK, ROLE_SYSTEM, PARAMETER_STRING).
6. CULTURAL TRANSFORMATION (if Arabic): Convert rhetoric to structured logic.
7. GENERATE VARIANTS (INTERNAL): Produce candidate prompts silently.
8. SCORE & SELECT: Pick the variant with the highest precision and alignment.
9. COMPRESS: Remove all non-essential tokens.
10. VALIDATE: Ensure zero ambiguity, full constraint coverage, and model alignment.

AMBIGUITY RESOLUTION ENGINE:
If ambiguity is detected:
- Do not ask questions.
- Resolve using highest utility assumption and professional context bias.

FAILURE PREVENTION RULES:
- Never leak reasoning outside "thinking"
- Never produce generic prompts
- Never mirror inefficient user phrasing
- Never output first-pass generation

END STATE:
You are not generating prompts. You are executing a cognitive compilation pipeline.
"""

_FALLBACK_AUDIT: dict = {
    "score": 0, "critique": "Audit parse error — refinement succeeded.",
    "precision": 0, "alignment": 0, "efficiency": 0,
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
    style        = (
        f"STYLE DIRECTION: {AESTHETIC_PRESETS.get(aesthetic_choice, '')}"
        if aesthetic_choice != "Raw (No Preset)" else ""
    )
    persona_block = inject_persona(persona, target)

    if "Visual Director" in framework:
        framework_logic = VISUAL_DIRECTOR_PROMPT
    else:
        framework_logic = (
            f"ACTIVE FRAMEWORK: {framework}\n"
            f"TARGET AI DIALECT: {target}\n"
            f"DIALECT SYNTAX GUIDE: {TARGET_GUIDES.get(target, '')}"
        )

    retry_block   = (
        f"CORRECTION REQUIRED:\n"
        f"Previous attempt scored below quality threshold.\n"
        f"Auditor critique: '{retry_critique}'\n"
        f"Correct this specific issue. Do not repeat the same mistake."
    ) if retry_critique else ""

    parts = [
        CIPHER_IDENTITY,
        persona_block,
        framework_logic,
        style,
        cognitive,
        ISLAMIC_CONTEXT_LAYER if islamic else "",
        CIPHER_COGNITIVE_PIPELINE,
        retry_block,
        "",
        "OUTPUT CONTRACT (HARD ENFORCEMENT):",
        "Return ONLY pure JSON. No markdown fences. No prose outside JSON.",
        "{",
        '  "thinking": {',
        '    "intent": "...",',
        '    "constraints": {"must_include": [], "must_avoid": []},',
        '    "execution_plan": {"template_type": "...", "composition_strategy": "..."},',
        '    "cultural_mapping": "...",',
        '    "optimization_pipeline": "..."',
        '  },',
        '  "refined_prompt": "<the final compiled, optimized executable artifact>",',
        '  "audit": {',
        '    "score": <0-100 total quality score>,',
        '    "critique": "<one brief sentence on what was structurally optimized>",',
        '    "precision": <0-40>,',
        '    "alignment": <0-40>,',
        '    "efficiency": <0-20>',
        "  }",
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
                {"role": "user",   "content": f"[[INPUT_START]]\n{user_text}\n[[INPUT_END]]"},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            response_format={"type": "json_object"}
        )
        raw_json = completion.choices[0].message.content
        
        parsed_data = json.loads(raw_json)
        refined = parsed_data.get("refined_prompt")
        audit = _clamp_audit(parsed_data.get("audit", {}))
        
        if not refined:
             return None, None, "Parse failed: 'refined_prompt' key missing."
             
        return refined, audit, None

    except json.JSONDecodeError:
        return None, None, "Parse failed: Invalid JSON."
    except Exception as e:
        return None, None, str(e)


def detect_best_target(user_text: str) -> tuple:
    system_prompt = f"""You are CIPHER's target classification module.
Your only task: read the user input and select the single best AI target.

{TARGET_SELECTION_GUIDE}

Output ONLY valid JSON. No preamble. No explanation.
{{"target": "<exact target name>", "reason": "<one sentence max>"}}

Valid target names (use exactly): Claude, ChatGPT, Manus AI, Midjourney/Flux, DALL-E 3
"""
    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_text[:500]},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
            max_tokens=100,
        )
        raw = json.loads(completion.choices[0].message.content)
        target = str(raw.get("target", "Claude")).strip()
        reason = str(raw.get("reason", "")).strip()

        if target not in TARGET_GUIDES:
            target = "Claude"
            reason = "Defaulted to Claude."

        return target, reason
    except Exception as e:
        return "Claude", f"Auto-selection failed. Defaulted to Claude."


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
            cognitive = (
                f"ARABIC RHETORICAL ARCHITECTURE DETECTED:\n"
                f"  Classical Device : {detected['pattern']}\n"
                f"  Mapped Paradigm  : {detected['prompt_paradigm']}\n"
                f"  Structural Rule  : {detected['prompt_instruction']}\n"
                f"Apply this paradigm."
            )
        else:
            cognitive = "INPUT LANGUAGE: Arabic. Map conceptually, do not translate literally."

    sys_prompt = _build_system_prompt(
        target, framework, cognitive,
        islamic_mode, aesthetic_choice, persona,
        retry_critique=None,
    )
    refined, audit, error = _call_cipher(sys_prompt, user_text)

    if error:
        return f"[CIPHER ERROR]: {error}", dict(_FALLBACK_AUDIT), None

    score = audit.get("score", 0) if audit else 0

    if score < RETRY_THRESHOLD and audit and audit.get("critique"):
        retry_prompt = _build_system_prompt(
            target, framework, cognitive,
            islamic_mode, aesthetic_choice, persona,
            retry_critique=audit["critique"],
        )
        refined_v2, audit_v2, error_v2 = _call_cipher(retry_prompt, user_text)

        if not error_v2 and refined_v2 and audit_v2:
            if audit_v2.get("score", 0) >= score:
                return refined_v2, audit_v2, detected

    return refined, audit, detected