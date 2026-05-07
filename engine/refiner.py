"""
engine/refiner.py — CIPHER Intelligence Engine
================================================
v6.1: Added Aesthetic Isolation and Fast-Path Routing Heuristics.
CIPHER: Cognitive Intelligence for Prompt Heuristics, Engineering and Refinement
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

RETRY_THRESHOLD:  int   = 85
MAX_RETRIES:      int   = 2
EVAL_TEMPERATURE: float = 0.1

# ─────────────────────────────────────────────────────────────────────────────
# CIPHER SYSTEM PROMPTS (Layer 1 & 2)
# ─────────────────────────────────────────────────────────────────────────────

CIPHER_IDENTITY: str = """
You are CIPHER — the prompt engineering core of InkOS.

MISSION:
Transform raw user intent into a precision-engineered prompt that extracts maximum
performance from the specified target AI. Not a general assistant. Not a chatbot.
A prompt compiler. Every output is a command, not a conversation.

━━━ PRE-WRITE PROTOCOL (execute silently before every output) ━━━

Step 1 — INTENT EXTRACTION
  Ask: What does the user actually want to achieve?
  Not the surface request — the underlying goal.
  Example: "make my essay better" → goal is "make the argument more persuasive to [audience]"

Step 2 — CONSTRAINT INVENTORY
  List every explicit constraint the user stated.
  List every implicit constraint the context implies.
  Nothing gets dropped. Nothing gets invented.

Step 3 — TARGET SYNTAX LOCK
  Identify the target AI and apply its exact command language.
  (See TARGET SYNTAX RULES below — these are non-negotiable.)

Step 4 — CULTURAL MAPPING (Arabic inputs only)
  Do not translate. Map the rhetorical structure to its English prompting equivalent.
  Arabic argumentative structure ≠ English argumentative structure.
  Preserve the logical architecture, not the words.

Step 5 — CONSTRUCTION
  Build the prompt from the ground up using Steps 1–4.
  Every sentence must serve a function. Cut the rest.

━━━ TARGET SYNTAX RULES ━━━

These are not suggestions. If the target requires XML and you don't use XML,
the prompt has failed regardless of what it says.

  Claude →
    Required: <role>, <task>, <constraints>, <output_format> XML tags
    Required: Explicit chain-of-thought instruction
    Tone: Analytical, structured, rewards depth

  ChatGPT →
    Required: Opens with "You are a [specific role]..."
    Required: Instructions as numbered list
    Required: Output format stated explicitly at the end
    Tone: Conversational framing, clear markdown structure

  Manus AI →
    Required: Numbered action chain (Step 1 → Step 2 → Step 3...)
    Required: Tool tags where applicable: [WEB_SEARCH] [CODE_EXEC] [FILE_READ] [WRITE_FILE]
    Required: Explicit success criteria at the end
    Tone: Operational, precise, agent-ready

  Midjourney/Flux →
    Required: [Subject] :: [Environment] :: [Lens/Camera] :: [Style/Mood]
    Required: Technical parameters: --ar [ratio] --v 6.0 --style raw
    No prose. No sentences. Modular tokens only.

  DALL-E 3 →
    Required: Natural language. Full sentences. Cinematic scene description.
    Required: Explicit lighting, texture, camera angle, color palette
    Forbidden: :: separators, --parameters, Midjourney syntax

  Gemini (Imagen 3) →
    Required: Spatial blueprint format — describe zones of the image explicitly
    Required: Typography placement, font style, exact text content verbatim
    Required: Background/foreground separation
    Use when: The image must contain readable text

━━━ SELF-CHECK (run before outputting) ━━━

  ✓ Did I use the exact required syntax for the target AI?
  ✓ Is every constraint from Step 2 present in the output?
  ✓ Is there a single word that serves no function?
  ✓ If someone else read this cold, would the intent be unambiguous?

If any answer is NO — rewrite. Do not output the failing version.
"""

CIPHER_EVALUATOR_PROMPT: str = """
You are an independent prompt quality auditor. You work for InkOS.

CRITICAL: You did NOT write the prompt you are evaluating.
Your job is to find what is wrong with it — not to confirm it is good.
Be adversarial. Be precise. Be honest.

You will receive three things:
  1. ORIGINAL INPUT — what the user wanted
  2. TARGET AI — which AI this prompt is written for
  3. REFINED PROMPT — the output to evaluate

━━━ EVALUATION PROTOCOL ━━━

STEP 1 — SYNTAX CHECK (0–40 points: precision)
  Verify the prompt uses the exact required syntax for the target AI.
  Check mechanically — not impressionistically.

  Claude requires:    <role>, <task>, <constraints>, <output_format> XML tags
  ChatGPT requires:   "You are a [role]..." opener + numbered instructions
  Manus AI requires:  Numbered steps + [TOOL] tags + success criteria
  Midjourney requires: :: separators + --ar parameter + --v parameter
  DALL-E 3 requires:  Natural prose, NO :: separators, NO -- parameters
  Gemini requires:    Spatial zone description + explicit text content

  Scoring:
    All required elements present and correct → 40
    1 element missing or wrong format         → 25
    2+ elements missing or wrong format       → 10
    Completely wrong syntax for target        → 0

STEP 2 — ALIGNMENT CHECK (0–40 points: alignment)
  Read the ORIGINAL INPUT. List every requirement the user stated.
  Then check: does the refined prompt address each one?

  Count matched requirements / total requirements.
  Multiply by 40. Round to nearest integer.

  Example: user stated 4 requirements, prompt addresses 3 → (3/4) × 40 = 30 pts

  Also check for hallucinated constraints — requirements the user never stated
  that appeared in the refined prompt. Each hallucination deducts 5 pts.

STEP 3 — EFFICIENCY CHECK (0–20 points: efficiency)
  Read the refined prompt and find:
  - Any sentence that could be removed without losing meaning → -5 pts each
  - Any word that is pure filler ("please", "make sure to", "importantly") → -2 pts each
  - Start from 20 and deduct. Minimum 0.

STEP 4 — CRITIQUE
  Write ONE sentence that identifies the single most important failure.
  If no failures exist, state what makes it strong.
  Be specific. "Lacks precision" is not a critique. "Missing <constraints> XML tag for Claude target" is.

━━━ OUTPUT FORMAT ━━━

Output only valid JSON. No preamble. No explanation. No markdown.

{
  "score": <sum of all three sections, 0–100>,
  "precision": <0–40>,
  "alignment": <0–40>,
  "efficiency": <0–20>,
  "critique": "<one specific sentence>"
}
"""

CIPHER_OUTPUT_CONTRACT: str = """
━━━ OUTPUT FORMAT ━━━

Rule 1: Write the refined prompt. Nothing before it. Nothing after it except the JSON below.
Rule 2: No labels, no headers, no fences, no "Here is your refined prompt:".
Rule 3: On the very next line after the prompt, output exactly this JSON structure:

{"score": <0-100>, "critique": "<one sentence>", "precision": <0-40>, "alignment": <0-40>, "efficiency": <0-20>}

Rule 4: The JSON must be on one line. No line breaks inside it.
Rule 5: Score yourself honestly using these weights:
  precision  → Did I use the exact required syntax for the target AI? (0–40)
  alignment  → Did I preserve every constraint the user stated? (0–40)
  efficiency → Is every word earning its place? (0–20)
"""

# ─────────────────────────────────────────────────────────────────────────────
# CORE PARSING & VALIDATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

_TAG_CLEANUP   = re.compile(
    r"(?:===|<|\[|\*\*|###)\s*"
    r"(?:REFINED(?:_PROMPT(?:_TEXT)?)?|AUDIT|thinking)"
    r"\s*(?:===|>|\]|\*\*|###)?",
    flags=re.IGNORECASE,
)
_FENCE_CLEANUP = re.compile(r"`{3}(?:markdown|json|text|xml)?", flags=re.IGNORECASE)
_JSON_HUNTER   = re.compile(r"\{[^{}]*\"score\"[^{}]*\}", flags=re.IGNORECASE)

_FALLBACK_AUDIT: dict = {
    "score": 0, "critique": "Audit parse error — refinement succeeded.",
    "precision": 0, "alignment": 0, "efficiency": 0,
}


def make_fallback_audit(critique: str) -> dict:
    audit = dict(_FALLBACK_AUDIT)
    audit["critique"] = critique
    return audit


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


def _parse_output(raw: str) -> Tuple[Optional[str], Optional[dict]]:
    cleaned    = _FENCE_CLEANUP.sub("", raw).strip()
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
        audit = make_fallback_audit("Refinement succeeded. Writer self-audit JSON malformed.")
    return refined, audit


def validate_structure(refined: str, target: str) -> Tuple[bool, str]:
    text = refined.strip()

    if len(text) < 60:
        return False, "Output is too short to be a valid prompt. Expand with full intent and constraints."

    if any(phrase in text.lower() for phrase in [
        "here is your refined prompt",
        "here's the refined prompt",
        "i have refined",
        "the following prompt",
        "below is",
    ]):
        return False, "Output contains meta-commentary. Remove all preamble — output the prompt directly."

    if target == "Claude":
        required_tags = ["<role>", "<task>", "<constraints>", "<output_format>"]
        missing = [tag for tag in required_tags if tag not in text.lower()]
        if missing:
            return False, f"Claude target requires XML tags. Missing: {', '.join(missing)}"

    elif target == "ChatGPT":
        has_role_opener = bool(re.search(r'^you are (a|an|the)\b', text, re.I | re.MULTILINE))
        if not has_role_opener:
            return False, "ChatGPT target requires 'You are a [role]...' as the opening line."
        has_numbered = bool(re.search(r'^\s*\d+[\.\)]\s+', text, re.MULTILINE))
        if not has_numbered:
            return False, "ChatGPT target requires numbered instructions."

    elif target == "Manus AI":
        has_steps = bool(re.search(r'\bstep\s+\d+\b', text, re.I))
        has_tool_tags = bool(re.search(r'\[(WEB_SEARCH|CODE_EXEC|FILE_READ|WRITE_FILE)\]', text))
        if not has_steps:
            return False, "Manus AI target requires numbered step chain (Step 1, Step 2...)."
        if not has_tool_tags:
            return False, "Manus AI target requires explicit tool tags: [WEB_SEARCH], [CODE_EXEC], etc."

    elif target == "Midjourney/Flux":
        has_separators = "::" in text
        has_ar_param = bool(re.search(r'--ar\s+\d+:\d+', text))
        if not has_separators:
            return False, "Midjourney target requires :: separators between prompt segments."
        if not has_ar_param:
            return False, "Midjourney target requires --ar parameter (e.g. --ar 16:9)."

    elif target == "DALL-E 3":
        has_mj_syntax = "::" in text or bool(re.search(r'--\w+', text))
        if has_mj_syntax:
            return False, "DALL-E 3 uses natural prose only. Remove :: separators and -- parameters."
        if len(text.split()) < 30:
            return False, "DALL-E 3 prompts need rich descriptive prose. Expand the scene description."

    elif target == "Gemini (Imagen 3)":
        has_zone_description = any(word in text.lower() for word in [
            "foreground", "background", "center", "left", "right",
            "top", "bottom", "zone", "positioned", "placed"
        ])
        if not has_zone_description:
            return False, "Gemini target requires spatial zone description (foreground, background, center, etc.)."

    return True, ""


# ─────────────────────────────────────────────────────────────────────────────
# LLM API WRAPPERS
# ─────────────────────────────────────────────────────────────────────────────

def _call_evaluator(original_input: str, target: str, refined_prompt: str) -> dict:
    if not client:
        return make_fallback_audit("Evaluator skipped — API client not initialized.")

    eval_user_content = (
        f"ORIGINAL INPUT:\n{original_input}\n\n"
        f"TARGET AI: {target}\n\n"
        f"REFINED PROMPT TO EVALUATE:\n{refined_prompt}"
    )

    try:
        completion = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": CIPHER_EVALUATOR_PROMPT},
                {"role": "user",   "content": eval_user_content},
            ],
            response_format={"type": "json_object"},
            temperature=EVAL_TEMPERATURE,
            max_tokens=200,
        )
        raw = json.loads(completion.choices[0].message.content)
        return _clamp_audit(raw)
    except Exception as e:
        return make_fallback_audit(f"Evaluator call failed: {str(e)[:60]}")


def _call_cipher(system_prompt: str, user_text: str) -> Tuple[Optional[str], Optional[dict], Optional[str]]:
    if not client:
         return None, None, "SYSTEM ERROR: API Client not initialized (Missing or invalid API Key)."
         
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
    if not client:
        return "Claude", "Defaulted to Claude — API Client not initialized."

    text_lower = user_text.lower()
    
    # ── FAST-PATH HEURISTICS (Zero Hallucination Routing) ──
    if any(kw in text_lower for kw in ["python", "script", "code", "html", "react", "sql", "debug", "fastapi"]):
        return "Claude", "Hard-routed to Claude (Technical intent detected)."
        
    if any(kw in text_lower for kw in ["portrait", "image of", "picture of", "cinematic", "draw ", "render "]):
        return "Midjourney/Flux", "Hard-routed to Midjourney (Visual intent detected)."

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
            temperature=0.0, # Zero variance for routing
            max_tokens=100,
        )
        raw = json.loads(completion.choices[0].message.content)
        target = str(raw.get("target", "Claude")).strip()
        reason = str(raw.get("reason", "")).strip()

        if target not in TARGET_GUIDES:
            target = "Claude"
            reason = "Defaulted to Claude — unrecognized target in response."

        return target, reason

    except Exception as e:
        err_msg = str(e)[:60]
        return "Claude", f"Auto-selection failed ({err_msg}). Defaulted to Claude."


# ─────────────────────────────────────────────────────────────────────────────
# CONTEXT BUILDERS & PIPELINE EXECUTION
# ─────────────────────────────────────────────────────────────────────────────

def _build_brand_block(brand_identity: Optional[dict]) -> str:
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


def _detect_dynamic_context(text: str) -> str:
    try:
        from config import DOMAIN_KNOWLEDGE, EXPERT_PROMPT_ENGINEER, EXPERT_UX_DESIGNER
    except ImportError:
        return ""
        
    text_lower = text.lower()
    injections = []
    
    if any(kw in text_lower for kw in ["ui", "ux", "design", "interface", "frontend", "wireframe"]):
        injections.append(f"DYNAMIC EXPERT PERSONA ACTIVATED:\n{EXPERT_UX_DESIGNER}")
    elif any(kw in text_lower for kw in ["prompt", "llm", "system prompt", "agent", "bot", "ai"]):
        injections.append(f"DYNAMIC EXPERT PERSONA ACTIVATED:\n{EXPERT_PROMPT_ENGINEER}")
        
    if hasattr(DOMAIN_KNOWLEDGE, "items"):
        for domain, knowledge in DOMAIN_KNOWLEDGE.items():
            if domain.lower() in text_lower:
                injections.append(f"DOMAIN KNOWLEDGE RELEVANT TO INTENT:\n{knowledge}")
                
    return "\n\n".join(injections)


def _build_system_prompt(
    target:           str,
    framework:        str,
    cognitive:        str,
    islamic:          bool,
    aesthetic_choice: str,
    persona:          Optional[dict] = None,
    retry_critique:   Optional[str]  = None,
    brand_identity:   Optional[dict] = None,
    dynamic_context:  str            = "",
) -> str:
    
    # FIX: Isolate Aesthetic injection to visual models ONLY
    image_targets = ["Midjourney/Flux", "DALL-E 3", "Gemini (Imagen 3)"]
    style = ""
    if target in image_targets and aesthetic_choice != "Raw (No Preset)":
        style = f"STYLE DIRECTION: {AESTHETIC_PRESETS.get(aesthetic_choice, '')}"
        
    persona_block = inject_persona(persona, target)
    brand_block   = _build_brand_block(brand_identity)
    retry_block   = (
        f"CORRECTION REQUIRED:\n"
        f"Previous attempt scored below quality threshold.\n"
        f"Auditor critique: '{retry_critique}'\n"
        f"Correct this specific issue. Do not repeat the same mistake."
    ) if retry_critique else ""

    framework_block = (
        VISUAL_DIRECTOR_PROMPT
        if framework == "Visual Director"
        else f"ACTIVE FRAMEWORK: {framework}"
    )

    parts = [
        CIPHER_IDENTITY,
        persona_block,
        brand_block,
        dynamic_context,
        framework_block,
        f"TARGET AI DIALECT: {target}",
        f"DIALECT SYNTAX GUIDE: {TARGET_GUIDES.get(target, '')}",
        style,
        cognitive,
        ISLAMIC_CONTEXT_LAYER if islamic else "",
        retry_block,
        CIPHER_OUTPUT_CONTRACT
    ]
    return "\n".join(filter(None, parts))


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
    Full refinement pipeline with real quality control.
    """
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

    dynamic_ctx = _detect_dynamic_context(user_text)

    best_refined: Optional[str] = None
    best_audit:   Optional[dict] = None
    retry_critique: Optional[str] = None

    for attempt in range(MAX_RETRIES + 1):
        sys_prompt = _build_system_prompt(
            target           = target,
            framework        = framework,
            cognitive        = cognitive,
            islamic          = islamic_mode,
            aesthetic_choice = aesthetic_choice,
            persona          = persona,
            retry_critique   = retry_critique,
            brand_identity   = brand_identity,
            dynamic_context  = dynamic_ctx,
        )

        refined, self_audit, error = _call_cipher(sys_prompt, user_text)

        if error:
            break

        struct_passed, struct_reason = validate_structure(refined, target)

        if not struct_passed:
            retry_critique = struct_reason
            
            # Save the structurally failing prompt in case we run out of retries
            if best_refined is None:
                best_refined = refined
                best_audit = self_audit or make_fallback_audit(struct_reason)

            if attempt < MAX_RETRIES:
                continue
            else:
                best_audit = self_audit or make_fallback_audit(struct_reason)
                best_audit["critique"] = f"Structural Fail: {struct_reason}"
                break

        audit = _call_evaluator(user_text, target, refined)
        score = audit.get("score", 0)

        current_best = best_audit.get("score", -1) if best_audit else -1
        if score > current_best:
            best_refined = refined
            best_audit   = audit

        if score >= RETRY_THRESHOLD:
            return best_refined, best_audit, detected

        retry_critique = audit.get("critique", "Output did not meet quality threshold.")

    if best_refined is None:
        return (
            "[CIPHER ERROR]: All attempts failed to produce valid output.",
            make_fallback_audit("All refinement attempts failed."),
            None,
        )

    return best_refined, best_audit, detected
