"""
forge/prompt_assembler.py — Neural Prompt Assembler
=====================================================
Phase 3 Architecture (DnaContext, token budget guard) — fully retained.

Hotfix-C: TARGET FORMAT ENFORCEMENT
─────────────────────────────────────
Root cause of the "You are..." bug:
  CIPHER received the target model name but had no explicit format
  contract per model. With no clear structural rule, it defaulted
  to the ChatGPT "You are a [role]..." pattern for everything.

Fix:
  TARGET_FORMAT_RULES maps every supported model to a precise,
  non-negotiable format contract injected into the payload as a
  [ ⚠ CRITICAL FORMAT DIRECTIVE ] block. CIPHER must follow it
  or the output structure validation will reject the response.

Format contracts by model:
  Claude           → XML tags: <role> <task> <constraints>
                     <output_format> <edge_cases> <quality_bar>
  ChatGPT / GPT-4  → "You are a [role]." system prompt opener
  Gemini           → Context-first, objective-led, no "You are"
  Midjourney       → /imagine prompt: ... --ar --v 6 --style raw
  DALL-E           → Visual description paragraph, no instructions
  Stable Diffusion → Comma-separated weighted tags, no sentences
  Perplexity       → Research question framing, factual directives
  Llama / Mistral  → [INST] ... [/INST] instruction wrapper
  Default          → Clear task-first structure, no model assumptions
"""

from __future__ import annotations

import sys
import textwrap
from typing import Optional, TypedDict

from forge.persona_engine import inject_persona
from config.prompts import CIPHER_IDENTITY

# ── SOFT / HARD LIMITS ────────────────────────────────────────────────────────
_PAYLOAD_SOFT_WARN   = 12_000
_USER_INPUT_HARD_CAP = 48_000


# ── TYPED DNA INTERFACE (Phase 3) ─────────────────────────────────────────────

class DnaContext(TypedDict):
    ink:    str
    intel:  str
    hikmah: str


def make_dna_context(
    ink:    str = "",
    intel:  str = "",
    hikmah: str = "",
) -> DnaContext:
    return DnaContext(
        ink    = str(ink    or "").strip(),
        intel  = str(intel  or "").strip(),
        hikmah = str(hikmah or "").strip(),
    )


def _dna_from_legacy(raw: dict) -> DnaContext:
    if "ink" in raw or "intel" in raw or "hikmah" in raw:
        return make_dna_context(
            ink    = raw.get("ink",    ""),
            intel  = raw.get("intel",  ""),
            hikmah = raw.get("hikmah", ""),
        )
    return make_dna_context(
        ink    = raw.get("ink_dna",    ""),
        intel  = raw.get("intel_dna",  ""),
        hikmah = raw.get("hikmah_dna", ""),
    )


# ── TARGET FORMAT RULES (Hotfix-C) ────────────────────────────────────────────

TARGET_FORMAT_RULES: dict[str, str] = {

    "Claude": textwrap.dedent("""
        OUTPUT FORMAT CONTRACT — TARGET: CLAUDE (Anthropic)
        ─────────────────────────────────────────────────────
        Claude uses XML-structured prompts. You MUST produce the
        following tags in this exact order. No "You are" opener.
        No system-prompt style. Only these XML blocks:

        <role>
        [Define the assistant persona and domain expertise]
        </role>

        <task>
        [The specific task to perform, broken into numbered steps
        if multi-part]
        </task>

        <constraints>
        [Hard rules the response must follow — format, length,
        language, things to avoid]
        </constraints>

        <output_format>
        [Exact structure of the expected output — sections,
        headers, length, code blocks if needed]
        </output_format>

        <edge_cases>
        [How to handle ambiguity, missing info, or out-of-scope
        requests]
        </edge_cases>

        <quality_bar>
        [What a perfect response looks like — the standard
        CIPHER is holding the output to]
        </quality_bar>

        CRITICAL: Do NOT start with "You are". Do NOT use markdown
        headers. XML tags only.
    """).strip(),

    "ChatGPT": textwrap.dedent("""
        OUTPUT FORMAT CONTRACT — TARGET: CHATGPT / GPT-4 (OpenAI)
        ────────────────────────────────────────────────────────────
        ChatGPT uses system-prompt style. You MUST open with:
        "You are a [specific role description]."

        Then follow with these sections in plain prose or
        markdown — NOT XML tags:

        1. Role definition ("You are a...")
        2. Context or background the model needs
        3. The specific task or question
        4. Constraints and rules
        5. Output format specification

        CRITICAL: Must start with "You are a". No XML tags.
    """).strip(),

    "Gemini": textwrap.dedent("""
        OUTPUT FORMAT CONTRACT — TARGET: GEMINI (Google DeepMind)
        ────────────────────────────────────────────────────────────
        Gemini responds best to context-first, objective-led prompts.
        Do NOT start with "You are". Do NOT use XML tags.

        Structure:
        1. CONTEXT: [Background information and situation]
        2. OBJECTIVE: [What needs to be accomplished — specific
           and measurable]
        3. REQUIREMENTS: [Bullet list of must-haves]
        4. OUTPUT SPECIFICATION: [Exact format, length, structure
           of the expected response]
        5. CONSTRAINTS: [What to avoid or exclude]

        CRITICAL: Context before task. No "You are" opener.
        No XML. Use clear section labels.
    """).strip(),

    "Midjourney": textwrap.dedent("""
        OUTPUT FORMAT CONTRACT — TARGET: MIDJOURNEY (Image AI)
        ────────────────────────────────────────────────────────────
        Midjourney is an image generation model. Prompts are NOT
        instructions — they are visual descriptions fed directly
        to the model. You MUST produce ONLY this structure:

        /imagine prompt: [main subject and action], [art style
        and medium], [lighting description], [color palette],
        [mood and atmosphere], [camera angle or perspective if
        relevant], [any specific artist style references]
        --ar [aspect ratio e.g. 16:9 or 1:1] --v 6 --style raw
        --q 2

        EXAMPLE:
        /imagine prompt: a lone astronaut standing on a red desert
        planet at dusk, cinematic concept art, golden hour rim
        lighting, deep crimson and burnt orange palette, epic and
        solitary mood, wide-angle low shot, Greg Rutkowski style
        --ar 16:9 --v 6 --style raw --q 2

        CRITICAL: Output ONLY the /imagine command. No explanations.
        No "You are". No prose. Just the prompt string.
    """).strip(),

    "DALL-E": textwrap.dedent("""
        OUTPUT FORMAT CONTRACT — TARGET: DALL-E (OpenAI Image AI)
        ────────────────────────────────────────────────────────────
        DALL-E takes natural language visual descriptions.
        Output a single descriptive paragraph — NOT instructions,
        NOT a command, NOT "You are".

        Structure the description as:
        [Subject and action] + [Setting and environment] +
        [Art style or medium] + [Lighting] + [Color palette] +
        [Mood] + [Camera perspective or composition detail]

        Write in plain descriptive prose. Be specific and visual.
        Do not include meta-instructions or explanations.

        CRITICAL: One descriptive paragraph only. No slashes,
        no parameters, no "You are", no XML.
    """).strip(),

    "Stable Diffusion": textwrap.dedent("""
        OUTPUT FORMAT CONTRACT — TARGET: STABLE DIFFUSION
        ────────────────────────────────────────────────────────────
        Stable Diffusion uses weighted tag-based prompts.
        You MUST produce two blocks:

        POSITIVE PROMPT:
        [subject:1.4], [art style:1.3], [lighting type], [color
        palette], [mood keywords], [detail tags], [quality boosters
        like "masterpiece, best quality, ultra detailed"],
        [artist style reference if needed]

        NEGATIVE PROMPT:
        [unwanted elements — e.g. "blurry, watermark, text,
        deformed hands, extra limbs, low quality, jpeg artifacts"]

        Use commas between tags. Use (word:weight) syntax for
        emphasis. No sentences. No "You are". No XML.

        CRITICAL: Two labeled blocks only — POSITIVE and NEGATIVE.
    """).strip(),

    "Perplexity": textwrap.dedent("""
        OUTPUT FORMAT CONTRACT — TARGET: PERPLEXITY AI
        ────────────────────────────────────────────────────────────
        Perplexity is a research and search AI. Prompts should be
        framed as precise research questions or investigation briefs.
        Do NOT use "You are". Do NOT use XML.

        Structure:
        1. PRIMARY QUESTION: [The main research question, specific
           and answerable]
        2. CONTEXT: [Why this is being researched, what is
           already known]
        3. SCOPE: [Time range, geography, or domain to focus on]
        4. REQUIRED SOURCES: [Types of sources preferred —
           academic, news, official, etc.]
        5. OUTPUT FORMAT: [How the answer should be structured —
           summary, bullet points, comparison table, etc.]

        CRITICAL: Question-first framing. Factual and specific.
        No instruction-following prompts — Perplexity researches,
        it doesn't role-play.
    """).strip(),

    "Llama": textwrap.dedent("""
        OUTPUT FORMAT CONTRACT — TARGET: LLAMA / MISTRAL
        (Open-source LLM)
        ────────────────────────────────────────────────────────────
        Llama and Mistral models use instruction-tuned format.
        You MUST wrap the prompt in [INST] tags:

        [INST]
        [Clear, direct task description in one or two sentences.
        Include role context inline if needed.
        Specify output format explicitly within the instruction.]
        [/INST]

        Keep it concise. Llama performs best with direct,
        unambiguous instructions. No lengthy preamble.
        No XML structural tags. No "You are a" system-prompt style.

        CRITICAL: [INST] ... [/INST] wrapper required.
        Task description inside must be direct and complete.
    """).strip(),
}

# Normalize key variants to canonical names
_TARGET_ALIASES: dict[str, str] = {
    "claude":             "Claude",
    "claude 3":           "Claude",
    "claude-3":           "Claude",
    "claude sonnet":      "Claude",
    "claude opus":        "Claude",
    "chatgpt":            "ChatGPT",
    "gpt-4":              "ChatGPT",
    "gpt4":               "ChatGPT",
    "gpt-3.5":            "ChatGPT",
    "openai":             "ChatGPT",
    "gemini":             "Gemini",
    "gemini pro":         "Gemini",
    "gemini ultra":       "Gemini",
    "google gemini":      "Gemini",
    "midjourney":         "Midjourney",
    "mj":                 "Midjourney",
    "dall-e":             "DALL-E",
    "dalle":              "DALL-E",
    "dall-e 3":           "DALL-E",
    "stable diffusion":   "Stable Diffusion",
    "sd":                 "Stable Diffusion",
    "sdxl":               "Stable Diffusion",
    "perplexity":         "Perplexity",
    "perplexity ai":      "Perplexity",
    "llama":              "Llama",
    "llama 2":            "Llama",
    "llama 3":            "Llama",
    "mistral":            "Llama",
    "mixtral":            "Llama",
}


def _get_format_rule(target: str) -> str:
    """
    Return the format contract for a given target model.
    Normalises aliases (e.g. 'claude sonnet' → 'Claude').
    Returns a generic contract if the target is unrecognised.
    """
    if not target:
        return ""

    canonical = _TARGET_ALIASES.get(target.lower().strip())
    if not canonical:
        # Try direct match
        for key in TARGET_FORMAT_RULES:
            if key.lower() in target.lower():
                canonical = key
                break

    if canonical and canonical in TARGET_FORMAT_RULES:
        return TARGET_FORMAT_RULES[canonical]

    # Generic fallback for unknown targets
    return textwrap.dedent(f"""
        OUTPUT FORMAT CONTRACT — TARGET: {target.upper()}
        ─────────────────────────────────────────────────
        Produce a well-structured prompt optimised for {target}.
        Lead with the task objective. Specify constraints clearly.
        Define the expected output format explicitly.
        Do not assume ChatGPT formatting conventions.
    """).strip()


# ── ASSEMBLY ──────────────────────────────────────────────────────────────────

def assemble_master_payload(
    user_input: str,
    config:     dict,
    dna:        Optional[DnaContext | dict] = None,
) -> str:
    """
    Synthesise Identity, Format Contract, Rhetoric, DNA, and user
    intent into a single master compiler instruction for CIPHER.

    Hotfix-C: TARGET_FORMAT_RULES block is now injected as a
    critical directive — CIPHER must follow it or the response
    fails structural validation.
    """

    # ── Normalise DNA ─────────────────────────────────────────────────────
    if dna is None:
        dna_ctx = make_dna_context()
    elif isinstance(dna, dict):
        dna_ctx = _dna_from_legacy(dna)
    else:
        dna_ctx = dna

    # ── Token budget guard (Phase 3) ──────────────────────────────────────
    if len(user_input) > _USER_INPUT_HARD_CAP:
        user_input = user_input[:_USER_INPUT_HARD_CAP]
        user_input += (
            "\n\n[SYSTEM NOTE: Input truncated at token budget limit. "
            "Ask the user to shorten their input.]"
        )

    # ── Specialist layer ──────────────────────────────────────────────────
    system_base = inject_persona(
        persona_input = config.get("active_persona"),
        target        = config.get("target_model", "ChatGPT"),
        hikmah_style  = config.get("hikmah_style", "None"),
    )

    # ── DNA layer ─────────────────────────────────────────────────────────
    dna_block = ""
    has_dna   = any([dna_ctx["ink"], dna_ctx["intel"], dna_ctx["hikmah"]])
    if has_dna:
        dna_block = textwrap.dedent(f"""
            [ ⚠ CRITICAL COMPILER DIRECTIVE: BRAND DNA INJECTION ]
            Embed the following values directly into the generated prompt.
            Do NOT use abstract placeholders. Expand them fully:

            - VISUAL_AESTHETIC:      {dna_ctx['ink']    or 'Default Obsidian & Gold'}
            - STRATEGIC_FOCUS:       {dna_ctx['intel']  or 'Default AI & Cyber'}
            - PHILOSOPHICAL_BOUNDS:  {dna_ctx['hikmah'] or 'Default Academic Arabic'}
        """).strip()

    # ── Hotfix-C: Target format contract ─────────────────────────────────
    target       = config.get("target_model", "ChatGPT")
    format_block = _get_format_rule(target)

    format_directive = textwrap.dedent(f"""
        [ ⚠ CRITICAL FORMAT DIRECTIVE — NON-NEGOTIABLE ]
        The refined prompt MUST be formatted EXCLUSIVELY for: {target}
        Ignore all default formatting assumptions.
        Follow the contract below with zero deviation:

        {format_block}
    """).strip()

    # ── Assemble ──────────────────────────────────────────────────────────
    parts = [
        CIPHER_IDENTITY,
        "[PERSONA_AND_POLICY_LAYER]",
        system_base,
        format_directive,        # ← Hotfix-C: injected here, before DNA
    ]
    if dna_block:
        parts.append(dna_block)
    parts.append(f"[MISSION_PAYLOAD]\n{user_input}")

    payload = "\n\n".join(parts)

    if len(payload) > _PAYLOAD_SOFT_WARN:
        print(
            f"[InkOS WARNING] Assembled payload is {len(payload):,} chars "
            f"(>{_PAYLOAD_SOFT_WARN:,} soft limit).",
            file=sys.stderr,
        )

    return payload
