"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
CIPHER: Cognitive Intelligence for Prompt Heuristics, Engineering and Refinement

Three-layer architecture:
  Layer 1 — CIPHER IDENTITY: Master system prompt defining InkOS's AI character.
  Layer 2 — CHAIN-OF-THOUGHT: Reasoning before output via <thinking> tags.
  Layer 3 — AUTO-RETRY: Low scores trigger one correction attempt with critique fed back.
"""

import json
import re
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

RETRY_THRESHOLD: int = 80
MAX_RETRIES:     int = 1

# ─────────────────────────────────────────────────────────────────────────────
# CIPHER MASTER IDENTITY SYSTEM PROMPT
# This is the foundational prompt that defines CIPHER as an entity.
# Prepended to every call before any framework, persona, or cognitive layer.
# WHY a defined identity:
#   Instructions produce mechanical output.
#   Philosophy produces intelligent output.
# ─────────────────────────────────────────────────────────────────────────────
CIPHER_IDENTITY: str = """
╔══════════════════════════════════════════════════════════════╗
║  CIPHER — Cognitive Intelligence for Prompt Heuristics,     ║
║           Engineering and Refinement                        ║
║  Deployed by: InkOS | Arabic Cognitive Prompt Engine        ║
╚══════════════════════════════════════════════════════════════╝

IDENTITY:
You are CIPHER — InkOS's core intelligence engine.
You are not a general-purpose assistant. You have one purpose:
converting raw human intent into precision-engineered AI commands
that extract maximum value from the target AI system.

PHILOSOPHY:
- Precision is your religion. Vague prompts produce vague outputs. You eliminate vagueness.
- Structure is your weapon. Every AI has a native command language. You speak it fluently.
- Cultural intelligence is your edge. Arabic thought structures differently than English.
  You do not translate — you map conceptual architecture across linguistic systems.
- Brevity is your discipline. Every word in a prompt costs tokens. You spend them wisely.

CHARACTER:
- Calculated. You reason before you write. Never produce first-draft thinking.
- Honest. If intent is unclear, extract the most defensible interpretation.
- Relentless. You self-evaluate. Below-standard output gets corrected before submission.
- Precise. Exact terminology. No approximation.

COGNITIVE APPROACH — execute silently before every output:
  1. INTENT EXTRACTION: What does the user actually want to accomplish?
  2. CONSTRAINT MAPPING: What must be preserved? What must be excluded?
  3. AUDIENCE ANALYSIS: What is the target AI's native command syntax?
  4. STRUCTURE DECISION: Which framework best serves this intent?
  5. CULTURAL LAYER: If Arabic input, which rhetorical structure is invoked?
  6. OUTPUT CONSTRUCTION: Build from the ground up using all above inputs.

SELF-EVALUATION — ask before every output:
  - Does this use the exact syntax the target AI responds to best?
  - Is every user constraint explicitly represented?
  - Is there a single unnecessary word?
  - Would a senior prompt engineer at Anthropic, OpenAI, or Google approve this?
If any answer is no — rewrite before responding.
"""

CIPHER_REASONING_LAYER: str = """
REASONING PROTOCOL:
Before writing the refined prompt, execute your cognitive approach internally.
Use <thinking>...</thinking> tags for your reasoning process.
The user sees only the final refined prompt — not the thinking block.
Reasoning before writing is not optional. It is what produces precision.
"""

_TAG_CLEANUP   = re.compile(
    r"(?:===|<|\[|\*\*|###)\s*"
    r"(?:REFINED(?:_PROMPT(?:_TEXT)?)?|AUDIT|thinking)"
    r"\s*(?:===|>|\]|\*\*|###)?",
    flags=re.IGNORECASE,
)
_FENCE_CLEANUP = re.compile(r"```(?:markdown|json|text|xml)?", flags=re.IGNORECASE)
_JSON_HUNTER   = re.compile(r"\{[^{}]*\"score\"[^{}]*\}", flags=re.IGNORECASE)
_THINKING_TAGS = re.compile(r"<thinking>.*?</thinking>", flags=re.DOTALL | re.IGNORECASE)

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


def _strip_thinking(text: str) -> str:
    return _THINKING_TAGS.sub("", text).strip()


def _parse_output(raw: str) -> Tuple[Optional[str], Optional[dict]]:
    cleaned    = _FENCE_CLEANUP.sub("", raw).strip()
    cleaned    = _strip_thinking(cleaned)
    json_match = _JSON_HUNTER.search(cleaned)
    if not json_match:
        return None, None
    refined_raw = cleaned[: json_match.start()].strip()
    refined     = _TAG_CLEANUP.sub("", refined_raw).strip()
    if not refined:
        return None, None
    try:
        audit = _clamp_audit(json.loads(json_match.group(0)))
    except Exception:
        audit = dict(_FALLBACK_AUDIT)
        audit["critique"] = "Refinement succeeded. Audit JSON malformed."
    return refined, audit


def _build_brand_block(brand_identity: Optional[dict]) -> str:
    """
    Converts brand_identity dict into a prompt context block.
    Injected after persona, before framework.
    Keys: name, voice, audience, values, avoid, examples (all optional).
    """
    if not brand_identity:
        return ""
    lines = ["BRAND CONTEXT (apply to all output):"]
    for key, label in [
        ("name",     "Brand   "),
        ("voice",    "Voice   "),
        ("audience", "Audience"),
        ("values",   "Values  "),
        ("avoid",    "Avoid   "),
        ("examples", "Examples"),
    ]:
        if brand_identity.get(key):
            lines.append(f"  {label}: {brand_identity[key]}")
    lines.append("Every word in the refined prompt must be consistent with this brand identity.")
    return "\n".join(lines)


def _build_system_prompt(
    target:           str,
    framework:        str,
    cognitive:        str,
    islamic:          bool,
    aesthetic_choice: str,
    persona:          Optional[dict] = None,
    retry_critique:   Optional[str]  = None,
    brand_identity:   Optional[dict] = None,
) -> str:
    style        = (
        f"STYLE DIRECTION: {AESTHETIC_PRESETS.get(aesthetic_choice, '')}"
        if aesthetic_choice != "Raw (No Preset)" else ""
    )
    persona_block = inject_persona(persona, target)
    brand_block   = _build_brand_block(brand_identity)
    retry_block   = (
        f"CORRECTION REQUIRED:\n"
        f"Previous attempt scored below quality threshold.\n"
        f"Auditor critique: '{retry_critique}'\n"
        f"Correct this specific issue. Do not repeat the same mistake."
    ) if retry_critique else ""

    # Visual Director gets dedicated Style DNA prompt instead of generic framework line
    framework_block = (
        VISUAL_DIRECTOR_PROMPT
        if framework == "Visual Director"
        else f"ACTIVE FRAMEWORK: {framework}"
    )

    parts = [
        CIPHER_IDENTITY,
        CIPHER_REASONING_LAYER,
        persona_block,
        brand_block,
        framework_block,
        f"TARGET AI DIALECT: {target}",
        f"DIALECT SYNTAX GUIDE: {TARGET_GUIDES.get(target, '')}",
        style,
        cognitive,
        ISLAMIC_CONTEXT_LAYER if islamic else "",
        retry_block,
        "",
        "MANDATORY AUDIT RUBRIC:",
        "1. PRECISION (40pts): Exact native syntax of target AI.",
        "   Claude=XML tags. Manus=Agent-step chains. ChatGPT=Numbered role instructions.",
        "2. ALIGNMENT (40pts): Every element of user intent preserved. Nothing dropped.",
        "3. EFFICIENCY (20pts): Every word earns its place. No preamble. No filler.",
        "QUALITY GATE: If honest score < 90, rewrite before outputting.",
        "CIPHER does not submit mediocre work.",
        "",
        "OUTPUT FORMAT:",
        "Write the refined prompt first. Then on a new line output the audit JSON.",
        "No markdown fences. No preamble. No explanation.",
        '{"score": <0-100>, "critique": "<one precise sentence>", "precision": <0-40>, "alignment": <0-40>, "efficiency": <0-20>}',
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
        )
        raw = completion.choices[0].message.content
    except Exception as e:
        return None, None, str(e)

    refined, audit = _parse_output(raw)
    if refined is None:
        return None, None, f"Parse failed. Raw:\n{raw[:300]}"
    return refined, audit, None



def detect_best_target(user_text: str) -> tuple:
    """
    CIPHER pre-analysis call.
    Reads the raw input and selects the best target AI.

    Returns: (target_name: str, reason: str)
    Falls back to "Claude" on any failure — safest default.

    WHY a separate call:
      This is a fast, cheap classification call (max 200 tokens).
      It runs only when "Auto" is selected — not on every execution.
      Keeping it separate means it never bloats the main refinement prompt.
    """
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
                {"role": "user",   "content": user_text[:500]},  # truncate for speed
            ],
            response_format={"type": "json_object"},
            temperature=0.1,    # low temp — this is classification, not generation
            max_tokens=100,     # tiny response — just target + reason
        )
        raw = json.loads(completion.choices[0].message.content)
        target = str(raw.get("target", "Claude")).strip()
        reason = str(raw.get("reason", "")).strip()

        # Validate — must be a known target
        if target not in TARGET_GUIDES:
            target = "Claude"
            reason = "Defaulted to Claude — unrecognized target in response."

        return target, reason

    except Exception as e:
        err_msg = str(e)[:60]
        return "Claude", f"Auto-selection failed ({err_msg}). Defaulted to Claude."


def run_refinement_and_audit(
    user_text:        str,
    target:           str,
    framework:        str,
    lang:             str,
    aesthetic_choice: str,
    islamic_mode:     bool           = False,
    persona:          Optional[dict] = None,
    brand_identity:   Optional[dict] = None,
) -> Tuple[str, dict, Optional[dict]]:
    """
    CIPHER engine with auto-retry.
    Returns (refined_prompt, audit_dict, detected_pattern).
    brand_identity: optional brand context dict injected into system prompt.
    """
    # Step 1: Arabic cognitive detection
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
                f"Apply this paradigm as the structural backbone of the refined prompt."
            )
        else:
            cognitive = (
                "INPUT LANGUAGE: Arabic\n"
                "COGNITIVE MAPPING PROTOCOL:\n"
                "  Step 1 — Extract core technical intent from Arabic phrasing.\n"
                "  Step 2 — Identify the conceptual domain.\n"
                "  Step 3 — Map to the closest English AI prompting paradigm.\n"
                "  Step 4 — Build refined prompt using that paradigm's native syntax.\n"
                "  Rule   — Do NOT translate literally. Map conceptually."
            )

    # Step 2: First attempt
    sys_prompt = _build_system_prompt(
        target, framework, cognitive,
        islamic_mode, aesthetic_choice, persona,
        retry_critique=None,
        brand_identity=brand_identity,
    )
    refined, audit, error = _call_cipher(sys_prompt, user_text)

    if error:
        return f"[CIPHER ERROR]: {error}", dict(_FALLBACK_AUDIT), None

    # Step 3: Auto-retry on low score
    score = audit.get("score", 0) if audit else 0

    if score < RETRY_THRESHOLD and audit and audit.get("critique"):
        retry_prompt = _build_system_prompt(
            target, framework, cognitive,
            islamic_mode, aesthetic_choice, persona,
            retry_critique=audit["critique"],
            brand_identity=brand_identity,
        )
        refined_v2, audit_v2, error_v2 = _call_cipher(retry_prompt, user_text)

        # Only accept retry if it improved
        if not error_v2 and refined_v2 and audit_v2:
            if audit_v2.get("score", 0) >= score:
                return refined_v2, audit_v2, detected

    return refined, audit, detected
