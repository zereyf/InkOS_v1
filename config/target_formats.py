"""
config/target_formats.py — Target Model Format Contracts
==========================================================
Each AI model expects a fundamentally different prompt structure.
CIPHER must know the correct format BEFORE generating, not after.

This module defines:
  TARGET_FORMAT_CONTRACTS — the authoritative format instruction
    injected into the assembled payload for each target model.
    Written as direct compiler directives to CIPHER.

  OPENING_PATTERNS — regex patterns used by _validate_structure()
    in refiner.py to confirm the output opens correctly.

  get_format_contract(target) — clean accessor used by assembler.
"""

from __future__ import annotations
import re

# ── FORMAT CONTRACTS ──────────────────────────────────────────────────────────
# Each string is injected verbatim into the system payload as a
# FORMAT_DIRECTIVE block. Written as firm instructions to CIPHER.

TARGET_FORMAT_CONTRACTS: dict[str, str] = {

    "ChatGPT": """
[ FORMAT_DIRECTIVE: TARGET = ChatGPT / GPT-4 ]
REQUIRED STRUCTURE:
  - Open with: "You are a [specific role]." — first sentence, no exceptions.
  - Follow with clear task description in second person ("Your task is to...").
  - Use numbered steps or bullet sections for complex tasks.
  - End with an explicit output format instruction ("Respond with...", "Return a...").
  - Tone: direct, conversational, instructional.
  - DO NOT use XML tags. DO NOT use markdown headers inside the prompt itself.
EXAMPLE OPENER: "You are a senior data analyst specializing in growth metrics..."
""".strip(),

    "Claude": """
[ FORMAT_DIRECTIVE: TARGET = Claude (Anthropic) ]
REQUIRED STRUCTURE:
  - Use XML tags for every structural section. This is mandatory, not optional.
  - Required tags: <role>, <task>, <constraints>, <output_format>
  - Required tags: <edge_cases>, <quality_bar>
  - Each tag must contain substantive content — no empty tags.
  - Open with <role> block defining the assistant's identity and expertise.
  - Use <thinking> tag guidance where step-by-step reasoning is needed.
  - Tone: precise, analytical, thorough. Claude responds best to explicit constraints.
  - DO NOT use "You are a..." opener. Use <role> tag instead.
EXAMPLE OPENER: "<role>You are an expert technical writer with 10 years..."
""".strip(),

    "Gemini": """
[ FORMAT_DIRECTIVE: TARGET = Gemini (Google) ]
REQUIRED STRUCTURE:
  - Open with a clear CONTEXT block: "Context: [background the model needs]"
  - Follow with TASK: "Task: [what to do, specific and measurable]"
  - Include CONSTRAINTS: "Constraints: [boundaries, format, length, style]"
  - End with OUTPUT: "Output format: [exactly what the response should look like]"
  - Gemini handles multimodal context well — specify if input includes images/data.
  - Tone: structured but natural. Gemini responds well to labelled sections.
  - DO NOT use "You are a..." opener. DO NOT use XML tags.
EXAMPLE OPENER: "Context: You are helping a marketing team analyze campaign data..."
""".strip(),

    "Midjourney": """
[ FORMAT_DIRECTIVE: TARGET = Midjourney (Image Generation) ]
REQUIRED STRUCTURE:
  - Start with: /imagine prompt:
  - Structure: [subject], [environment/setting], [lighting], [style/medium],
    [artist references if relevant], [technical parameters]
  - End with Midjourney parameters: --ar [ratio] --v 6 --style raw --q 2
  - Common ratios: --ar 16:9 (wide), --ar 1:1 (square), --ar 9:16 (portrait)
  - Style keywords: photorealistic, cinematic, oil painting, concept art,
    hyperdetailed, octane render, 8k, golden hour, dramatic lighting
  - Negative prompts go after --no: --no blur, text, watermark
  - DO NOT write sentences or paragraphs. This is a comma-separated tag list.
  - DO NOT include "You are..." or any role-play framing.
EXAMPLE: /imagine prompt: ancient Arabic library interior, golden manuscripts,
  shafts of light through arched windows, cinematic lighting, hyperdetailed,
  concept art, --ar 16:9 --v 6 --style raw --q 2
""".strip(),

    "DALL-E": """
[ FORMAT_DIRECTIVE: TARGET = DALL-E (OpenAI Image Generation) ]
REQUIRED STRUCTURE:
  - Write a single descriptive paragraph — no slashes, no parameters.
  - Structure: [subject + action], [setting/environment], [style/medium],
    [lighting and mood], [color palette], [level of detail]
  - DALL-E responds best to natural descriptive English sentences.
  - Specify art style explicitly: "in the style of [movement/medium]"
  - Include camera/perspective details for photorealistic images.
  - Avoid copyrighted artist names — describe the style instead.
  - DO NOT use /imagine. DO NOT use parameter flags. DO NOT use "You are...".
EXAMPLE: "A detailed oil painting of a futuristic Arabic city at dusk, minarets
  blending with glass skyscrapers, warm amber and deep purple tones, soft
  volumetric lighting, in the style of concept art, highly detailed."
""".strip(),

    "Stable Diffusion": """
[ FORMAT_DIRECTIVE: TARGET = Stable Diffusion ]
REQUIRED STRUCTURE:
  - POSITIVE PROMPT: comma-separated keywords describing what you WANT.
    Start with subject, then style, then quality boosters.
    Quality boosters: masterpiece, best quality, highly detailed, 8k, sharp focus
  - NEGATIVE PROMPT: on a new line starting with "Negative prompt:"
    Common negatives: ugly, blurry, low quality, watermark, text, deformed,
    extra limbs, bad anatomy, bad hands, cropped
  - Optional: add LoRA weights in angle brackets <lora:name:weight>
  - DO NOT write sentences. This is keyword/tag syntax only.
  - DO NOT use "You are..." or any conversational framing.
EXAMPLE:
  ancient Arabic library, golden hour lighting, hyperdetailed architecture,
  ornate manuscripts, volumetric light rays, masterpiece, best quality, 8k
  Negative prompt: blurry, low quality, watermark, modern furniture, text
""".strip(),

    "Perplexity": """
[ FORMAT_DIRECTIVE: TARGET = Perplexity AI ]
REQUIRED STRUCTURE:
  - Perplexity is a research/search AI — prompts should be research queries
    or analytical questions, not role-play instructions.
  - Open with a clear, specific question or research directive.
  - Specify: scope ("focus on events after 2023"), sources ("cite academic
    papers"), format ("summarize in 3 bullet points"), depth ("beginner level").
  - Use follow-up constraints: "Do not include [X]", "Prioritize [Y]".
  - Tone: academic, inquisitive. Perplexity rewards precise question framing.
  - DO NOT use "You are a..." role assignments.
  - DO NOT use XML tags or image generation syntax.
EXAMPLE OPENER: "Research and explain the latest developments in [topic],
  focusing on peer-reviewed sources from 2023–2025. Summarize key findings..."
""".strip(),

    "Copilot": """
[ FORMAT_DIRECTIVE: TARGET = Microsoft Copilot ]
REQUIRED STRUCTURE:
  - Copilot is task/productivity-oriented. Prompts should be action-focused.
  - Open with the action verb directly: "Write...", "Create...", "Summarize...",
    "Draft...", "Analyze...", "Generate..."
  - Specify context: "Based on [document/data/meeting]..."
  - Specify output format explicitly: "as a bulleted list", "in table format",
    "as a professional email", "in 3 paragraphs"
  - Include tone/audience: "for a C-suite audience", "in a formal tone"
  - Copilot integrates with Office — reference document types where relevant.
  - DO NOT use "You are a..." opener. Keep it direct and task-first.
EXAMPLE OPENER: "Summarize the following meeting notes into 5 key action items..."
""".strip(),

}

# Default for unrecognised targets — safe fallback
_DEFAULT_CONTRACT = """
[ FORMAT_DIRECTIVE: TARGET = {target} ]
REQUIRED STRUCTURE:
  - Research and apply the correct prompt format for {target} specifically.
  - Do NOT default to ChatGPT "You are a..." style unless {target} explicitly
    requires it.
  - Match the structural conventions, opener style, and parameter syntax
    that {target} is documented to respond best to.
  - The output must be immediately usable with {target} without modification.
""".strip()


# ── OPENING VALIDATION PATTERNS ───────────────────────────────────────────────
# Used by _validate_structure() in refiner.py to confirm the prompt
# opens with the correct pattern for each target.
# Value: (regex_pattern, description_of_rule)

OPENING_PATTERNS: dict[str, tuple[str, str]] = {
    "ChatGPT":          (r"^you\s+are\s+a?\s*\w",           "Must open with 'You are a [role]'"),
    "Claude":           (r"^<role>",                          "Must open with <role> XML tag"),
    "Gemini":           (r"^context\s*:",                     "Must open with 'Context:' label"),
    "Midjourney":       (r"^/imagine\s+prompt\s*:",           "Must open with '/imagine prompt:'"),
    "DALL-E":           (r"^[A-Z\"]",                         "Must open with descriptive sentence"),
    "Stable Diffusion": (r"^\w[\w\s,]+,",                     "Must open with comma-separated tags"),
    "Perplexity":       (r"^(research|explain|what|how|why|find|analyze|compare)\b", "Must open with a research question or directive"),
    "Copilot":          (r"^(write|create|summarize|draft|analyze|generate|list|make)\b", "Must open with an action verb"),
}


# ── ACCESSOR ──────────────────────────────────────────────────────────────────

def get_format_contract(target: str) -> str:
    """
    Returns the format contract string for a given target model.
    Falls back to a generic directive for unknown targets.
    """
    if not target:
        return ""
    # Exact match first
    if target in TARGET_FORMAT_CONTRACTS:
        return TARGET_FORMAT_CONTRACTS[target]
    # Partial match (e.g. "GPT-4" matches "ChatGPT")
    target_lower = target.lower()
    for key, contract in TARGET_FORMAT_CONTRACTS.items():
        if key.lower() in target_lower or target_lower in key.lower():
            return contract
    # Unknown target — use generic directive
    return _DEFAULT_CONTRACT.format(target=target)


def get_opening_pattern(target: str) -> tuple[str, str] | None:
    """
    Returns (regex_pattern, rule_description) for validation,
    or None if no strict opener is required for this target.
    """
    if not target:
        return None
    if target in OPENING_PATTERNS:
        return OPENING_PATTERNS[target]
    target_lower = target.lower()
    for key, pattern in OPENING_PATTERNS.items():
        if key.lower() in target_lower or target_lower in key.lower():
            return pattern
    return None
