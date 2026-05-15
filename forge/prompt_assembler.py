"""
forge/prompt_assembler.py — Neural Prompt Assembler
=====================================================
Phase 3 + Hotfix:

  ARC-2: DnaContext TypedDict.
  ARC-3: Token budget guard.

  HOTFIX — Per-model format directives:
    Previously every target model received the same generic instruction,
    so the LLM defaulted to ChatGPT "You are..." style for everything.

    Fix: _TARGET_FORMAT_DIRECTIVES maps every supported model to its
    correct prompt structure. Injected into the payload as a hard contract
    block that overrides the LLM default behaviour.

    ChatGPT        → "You are a [role]..." persona opener
    Claude         → <role><task><context><constraints><output_format>
                     <edge_cases><quality_bar> XML blocks
    Gemini         → ## Objective / ## Context / ## Instructions headers
    Midjourney     → Comma-separated descriptor chains + --param flags
    DALL-E         → Rich single-paragraph visual description prose
    Stable Diffusion → (tag:weight) positive + negative prompt blocks
    Perplexity     → Direct research question + scope + source prefs
    Grok           → Concise direct task, minimal preamble
"""

from __future__ import annotations

import textwrap
from typing import Optional, TypedDict

from forge.persona_engine import inject_persona
from config.prompts import CIPHER_IDENTITY

_PAYLOAD_SOFT_WARN   = 12_000
_USER_INPUT_HARD_CAP = 48_000


class DnaContext(TypedDict):
    ink:    str
    intel:  str
    hikmah: str


def make_dna_context(ink="", intel="", hikmah="") -> DnaContext:
    return DnaContext(
        ink    = str(ink    or "").strip(),
        intel  = str(intel  or "").strip(),
        hikmah = str(hikmah or "").strip(),
    )


def _dna_from_legacy(raw: dict) -> DnaContext:
    if "ink" in raw or "intel" in raw or "hikmah" in raw:
        return make_dna_context(raw.get("ink",""), raw.get("intel",""), raw.get("hikmah",""))
    return make_dna_context(raw.get("ink_dna",""), raw.get("intel_dna",""), raw.get("hikmah_dna",""))


_TARGET_FORMAT_DIRECTIVES: dict[str, str] = {

    "ChatGPT": """STRUCTURE : Role > Context > Task > Constraints > Output format
OPENER    : Begin with "You are a [specific role with expertise]..."
STYLE     : Direct persona assignment. Conversational but precise.
FORBIDDEN : XML tags, markdown section headers""",

    "Claude": """STRUCTURE : XML blocks in this exact order:
            <role>, <task>, <context>, <constraints>,
            <output_format>, <edge_cases>, <quality_bar>
OPENER    : Begin directly with <role>...</role>
            Do NOT write "You are" before or instead of the XML tags.
REQUIRED  : <edge_cases> and <quality_bar> must be non-empty
FORBIDDEN : "You are a...", markdown headers, unstructured paragraphs
EXAMPLE   : <role>Expert curriculum designer specialising in adult learning...</role>
            <task>Design a 4-week programme covering...</task>""",

    "Gemini": """STRUCTURE : Markdown headers: ## Objective, ## Context, ## Instructions,
            ## Constraints, ## Output Format
OPENER    : Begin with "## Objective" — state the goal as a task, not a persona
STYLE     : Task-oriented. What should be done, not who the AI is.
REQUIRED  : At least 4 of the 5 header sections
FORBIDDEN : "You are a...", XML tags, unstructured prose
EXAMPLE   : ## Objective
            Generate a comprehensive market analysis of renewable energy...""",

    "Midjourney": """STRUCTURE : [Subject], [Art style], [Lighting], [Mood], [Camera], [Params]
OPENER    : Start directly with the visual subject — NO sentences, NO "You are"
STYLE     : Comma-separated visual descriptor chains ONLY.
            End with parameter flags: --ar 16:9 --v 6.1 --style raw
REQUIRED  : Subject + style reference + at least one technical param
FORBIDDEN : Full sentences, "You are", "Please generate", instruction language
EXAMPLE   : ancient Arabic library at golden hour, god rays through stained glass,
            orientalist oil painting style, cinematic atmosphere, ultra-detailed
            architecture, 8k --ar 16:9 --v 6.1 --style raw""",

    "DALL-E": """STRUCTURE : Single descriptive paragraph — Subject + Style + Lighting +
            Mood + Technical quality + Color palette + Composition
OPENER    : Begin with "A [adjective] [subject]..." — pure visual description
STYLE     : Prose only. Write what the IMAGE looks like. No instructions.
FORBIDDEN : "You are", headers, bullet lists, meta-instruction language
EXAMPLE   : A photorealistic aerial view of a futuristic Arabian city at dusk,
            warm amber streetlights against a deep violet sky, hyper-detailed
            Islamic geometric architecture fused with glass towers, 8k.""",

    "Stable Diffusion": """STRUCTURE : POSITIVE PROMPT block then NEGATIVE PROMPT: block
OPENER    : Start positive prompt with quality boosters
STYLE     : Weighted tag syntax: (tag:weight). Comma-separated concepts.
BOOSTERS  : (masterpiece:1.4), (best quality:1.3), (8k:1.2)
REQUIRED  : Both positive AND negative prompt sections
FORBIDDEN : Full sentences, "You are", markdown headers
EXAMPLE   : (masterpiece:1.4), (best quality:1.3), arabic calligrapher, dramatic
            studio lighting, (detailed hands:1.2), ink on parchment
            NEGATIVE PROMPT: (low quality:1.4), blurry, watermark, deformed""",

    "Perplexity": """STRUCTURE : Research question + Context + Scope + Source preferences
OPENER    : State the research question directly — no persona framing
STYLE     : Research mode. Specify recency, source types, depth required.
REQUIRED  : Clear scope and any recency constraints
FORBIDDEN : "You are a researcher", roleplay framing, vague questions
EXAMPLE   : What are the most recent peer-reviewed findings on LLM reasoning?
            Focus on 2024-2025 papers. Prioritise academic sources.""",

    "Grok": """STRUCTURE : Direct task statement + Brief context + Tone (optional)
OPENER    : State the task directly. Minimal preamble.
STYLE     : Concise. Grok reasons natively — do not over-specify.
FORBIDDEN : Long persona setups, excessive constraint lists, "You are" openers
EXAMPLE   : Analyse the latest EU AI regulation announcements.
            Focus on practical developer impact. Be direct and opinionated.""",
}

_DEFAULT_FORMAT_DIRECTIVE = """STRUCTURE : Role > Context > Task > Constraints > Output
OPENER    : Use the conventional prompt structure for this specific AI model.
CRITICAL  : Do NOT default to ChatGPT "You are..." style for non-ChatGPT targets.
            Research what format this model expects and use that."""


def _get_format_directive(target: str) -> str:
    if not target:
        return _DEFAULT_FORMAT_DIRECTIVE
    if target in _TARGET_FORMAT_DIRECTIVES:
        return _TARGET_FORMAT_DIRECTIVES[target]
    for key in _TARGET_FORMAT_DIRECTIVES:
        if key.lower() in target.lower() or target.lower() in key.lower():
            return _TARGET_FORMAT_DIRECTIVES[key]
    return _DEFAULT_FORMAT_DIRECTIVE


def assemble_master_payload(
    user_input: str,
    config:     dict,
    dna:        "Optional[DnaContext | dict]" = None,
) -> str:
    if dna is None:
        dna_ctx = make_dna_context()
    elif isinstance(dna, dict):
        dna_ctx = _dna_from_legacy(dna)
    else:
        dna_ctx = dna

    if len(user_input) > _USER_INPUT_HARD_CAP:
        user_input = user_input[:_USER_INPUT_HARD_CAP]
        user_input += (
            "\n\n[SYSTEM NOTE: Input truncated at the token budget limit. "
            "Ask the user to shorten their input.]"
        )

    system_base = inject_persona(
        persona_input = config.get("active_persona"),
        target        = config.get("target_model", "ChatGPT"),
        hikmah_style  = config.get("hikmah_style", "None"),
    )

    dna_block = ""
    has_dna   = any([dna_ctx["ink"], dna_ctx["intel"], dna_ctx["hikmah"]])
    if has_dna:
        dna_block = textwrap.dedent(f"""
            [ BRAND DNA INJECTION ]
            - VISUAL_AESTHETIC:      {dna_ctx["ink"]   or "Default Obsidian & Gold"}
            - STRATEGIC_FOCUS:       {dna_ctx["intel"] or "Default AI & Cyber"}
            - PHILOSOPHICAL_BOUNDS:  {dna_ctx["hikmah"]or "Default Academic Arabic"}
        """).strip()

    target_name      = config.get("target_model", "ChatGPT") or "ChatGPT"
    format_directive = _get_format_directive(target_name)

    format_block = (
        f"[ CRITICAL FORMAT CONTRACT — TARGET: {target_name.upper()} ]\n"
        f"The refined prompt MUST follow these rules EXACTLY.\n"
        f"This overrides any default formatting tendency.\n"
        f"DO NOT use \"You are...\" unless the contract below explicitly requires it.\n\n"
        f"{format_directive.strip()}"
    )

    parts = [
        CIPHER_IDENTITY,
        "[PERSONA_AND_POLICY_LAYER]",
        system_base,
        format_block,
    ]
    if dna_block:
        parts.append(dna_block)
    parts.append(f"[MISSION_PAYLOAD]\n{user_input}")

    payload = "\n\n".join(parts)

    if len(payload) > _PAYLOAD_SOFT_WARN:
        import sys
        print(
            f"[InkOS WARNING] Assembled payload is {len(payload):,} chars "
            f"(>{_PAYLOAD_SOFT_WARN:,} soft limit).",
            file=sys.stderr,
        )

    return payload
