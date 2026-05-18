"""
config/target_formats.py — Target Model Format Contracts
==========================================================
v2.0: Upgraded to match elite compilation standards from CIPHER v14.0.

Each FORMAT_DIRECTIVE is injected verbatim into the assembled payload.
These are the authoritative structural instructions CIPHER reads before
generating any output. They must be specific enough that no default
"You are a..." behavior can slip through.

Changes from v1.0:
  - Midjourney: added mandatory :: separator requirement and layer order
  - DALL-E 3: added mandatory Avoid: closing sentence
  - Stable Diffusion: strengthened Negative prompt: requirement
  - Claude: added explicit anti "You are a..." prohibition
  - ChatGPT: clarified it is the ONLY target that uses "You are a..."
  - Gemini/Perplexity/Copilot: added explicit anti "You are a..." prohibition
  - All: added example openers matching elite standard format
"""

from __future__ import annotations
import re

TARGET_FORMAT_CONTRACTS: dict[str, str] = {

    "ChatGPT": """
[ FORMAT_DIRECTIVE: TARGET = ChatGPT / GPT-4 ]
ChatGPT is the ONLY target that uses "You are a..." opener. All others do not.

REQUIRED STRUCTURE:
  Line 1:  "You are a [specific expert identity with domain + years + institution]."
           NEVER generic: "You are a helpful assistant."
           ALWAYS specific: "You are a senior data scientist at a Series B fintech
           startup with 8 years building fraud detection models in Python and SQL."
  Line 2:  Task description in second person ("Your task is to...", "You will...").
  Body:    Prohibition clauses (minimum 2). Measurable output specs (numbers not adjectives).
  End:     Explicit output format instruction ("Respond with...", "Return a...").

ELITE REQUIREMENTS:
  - Role must include: title + years + domain + institutional context
  - Minimum 2 prohibition clauses ("Do not...", "Never...", "Avoid...")
  - All output specs must be numbers or binary rules, never adjectives
  - No hedging in the prompt itself ("please", "try to", "make sure to")

EXAMPLE OPENER:
  "You are a principal product manager at a Series B SaaS company with 9 years
   building B2B analytics products, previously at Amplitude and Mixpanel."
""".strip(),

    "Claude": """
[ FORMAT_DIRECTIVE: TARGET = Claude (Anthropic) ]
Claude requires XML-structured output. DO NOT use "You are a..." opener.
The absence of a <role> tag is an automatic format failure.

REQUIRED STRUCTURE:
  <role>
    Expert identity: title + years + domain + institutional context.
    Character traits that affect output style.
    Never generic. Always specific.
  </role>

  <task>
    Specific, measurable task description.
    What the output is, not what it should feel like.
  </task>

  <constraints>
    Minimum 3 items. Each must be enforceable and testable.
    Include at least 2 prohibition clauses ("Do not...", "Never...").
    All format specs must be numbers or binary rules.
  </constraints>

  <edge_cases>
    At least 2 specific edge cases the model must handle correctly.
    Not generic ("if unclear, ask") but specific to this task domain.
  </edge_cases>

  <output_format>
    Exact structure: section names, word counts, heading levels.
    Binary rules only. No adjectives.
  </output_format>

  <quality_bar>
    Name a specific human reviewer in a specific role who would approve this.
    "A senior editor at [publication] would publish this without structural revision."
  </quality_bar>

EXAMPLE OPENER: "<role>\\nYou are a principal security architect..."
DO NOT open with "You are a..." outside of XML tags.
""".strip(),

    "Gemini": """
[ FORMAT_DIRECTIVE: TARGET = Gemini (Google) ]
Gemini uses labelled sections. DO NOT use "You are a..." opener.
DO NOT use XML tags. The absence of "Context:" opener is a format failure.

REQUIRED STRUCTURE:
  Context: [Background, expert framing, what this model is being asked to be]
  Task: [Specific, measurable instruction — numbers not adjectives]
  Constraints: [Minimum 2 prohibition clauses + measurable output specs]
  Output: [Exact format: section names, word counts, heading levels]

ELITE REQUIREMENTS:
  - Context must establish expert framing without "You are a..." syntax
  - All specs must be measurable: word counts, section counts, binary rules
  - Include data/multimodal context if input contains images or structured data

EXAMPLE OPENER:
  "Context: Acting as a senior UX researcher with 10 years in enterprise software..."
""".strip(),

    "Midjourney": """
[ FORMAT_DIRECTIVE: TARGET = Midjourney ]
Midjourney requires /imagine prompt: syntax with :: weighted separators.
DO NOT use "You are a..." opener. DO NOT use prose sentences.
DO NOT use a single continuous tag list without :: separators.
Missing /imagine prompt: opener is an automatic format failure.
Missing :: separators is an automatic precision failure.

REQUIRED STRUCTURE:
  /imagine prompt: [SUBJECT layer] :: [ENVIRONMENT layer] :: [LIGHTING layer] :: [LENS layer] :: [COMPOSITION layer] :: [STYLE layer] :: [PALETTE layer] [parameters]

LAYER ORDER (mandatory):
  1. SUBJECT      — anatomy, pose angles, expression, materials
  2. ENVIRONMENT  — location + time of day + depth planes
  3. LIGHTING     — Kelvin temp + key/fill/rim + shadow quality
  4. LENS         — focal length + aperture + camera angle in degrees
  5. COMPOSITION  — framing rule + subject placement + negative space location
  6. STYLE        — specific studio + specific work/arc + specific director
  7. PALETTE      — hex codes or named pigments, max 3 dominant, with use-case

PARAMETERS (always at end):
  --ar [ratio]     (required: 16:9 / 3:2 / 1:1 / 9:16 / 3:1)
  --v 6            (required)
  --style raw      (required for realism/anime)
  --q 2            (required for max quality)
  --no [list]      (required: specific exclusions, not generic "bad stuff")

PALETTE RULE: Never use "vibrant", "neon", "colorful". Always hex codes.
LIGHTING RULE: Never use "cinematic". Always Kelvin temperature.
STYLE RULE: Never just studio name. Always studio + specific work + director.

EXAMPLE OPENER:
  "/imagine prompt: protagonist mid-sprint 30deg forward :: rain-slicked Shibuya..."
""".strip(),

    "DALL-E": """
[ FORMAT_DIRECTIVE: TARGET = DALL-E 3 ]
DALL-E 3 requires descriptive prose. DO NOT use /imagine syntax.
DO NOT use :: separators. DO NOT use "You are a..." opener.
DO NOT use XML tags. Prose paragraph format only.

REQUIRED STRUCTURE:
  Paragraph 1: Subject + action + exact pose description.
  Paragraph 2: Environment + time of day + atmospheric conditions.
  Paragraph 3: Lighting (Kelvin temps) + color palette (hex codes) + lens.
  Paragraph 4: Style reference (specific work, not just genre) + composition.
  Final line:  "Avoid: [specific comma-separated exclusion list]."

ELITE REQUIREMENTS:
  - Color palette: max 3 colors, all as hex codes, each with stated use-case
  - Lighting: must include Kelvin temperature, not just quality adjectives
  - Style: specific work + director, not just genre label
  - Negative space: state location and purpose if banner/title format
  - Closing Avoid: sentence is mandatory

PALETTE RULE: Never "warm tones" or "vibrant". Always "#ff6b2b for skin tones".
LIGHTING RULE: Never "cinematic lighting". Always "5600K key from low-left horizon".
STYLE RULE: Never "anime style". Always "Makoto Shinkai background density + clean cel-shading".

EXAMPLE OPENER:
  "Cinematic anime illustration of three teenage characters mid-sprint..."
""".strip(),

    "Stable Diffusion": """
[ FORMAT_DIRECTIVE: TARGET = Stable Diffusion ]
Stable Diffusion requires comma-separated keyword tags, NOT sentences.
A "Negative prompt:" block is mandatory. Its absence is an automatic format failure.
DO NOT use "You are a..." opener. DO NOT write prose sentences.

REQUIRED STRUCTURE:
  Line 1+:  Positive tags — comma-separated, ordered by importance:
            [subject tags], [environment tags], [lighting tags],
            [style tags], [quality boosters]

  Quality boosters (always include these):
            masterpiece, best quality, highly detailed, sharp focus, 8k

  Blank line, then:
  Negative prompt: [comma-separated exclusion tags]

  Standard negative tags (always include):
            ugly, blurry, low quality, watermark, text, signature,
            deformed, extra limbs, bad anatomy, bad hands, cropped,
            worst quality, jpeg artifacts, motion blur

ADVANCED FEATURES (include when relevant):
  LoRA weights: <lora:model_name:weight>
  Token emphasis: (term:1.3) for boost, (term:0.7) for reduce
  Embedding: embedding:bad_prompt_version2

PALETTE RULE: Use hex codes as color reference tags: "electric blue #00cfff"
STYLE RULE: Specific aesthetic + artist + quality context

EXAMPLE OPENER:
  "anime banner, three characters diagonal sprint, Shibuya rain night..."
  Negative prompt: ugly, blurry, watermark, text...
""".strip(),

    "Perplexity": """
[ FORMAT_DIRECTIVE: TARGET = Perplexity AI ]
Perplexity is a research AI. DO NOT use "You are a..." opener.
DO NOT use XML tags or /imagine syntax.
The absence of a clear research question opener is a format failure.

REQUIRED STRUCTURE:
  Line 1:    Clear, specific research question or directive.
  Scope:     "Focus on [time period / geography / domain]"
  Sources:   "Prioritize [peer-reviewed / institutional / primary sources]"
  Format:    "Summarize in [N bullet points / N paragraphs / table]"
  Exclusions: "Do not include [X]. Avoid [Y]."
  Depth:     State the target audience knowledge level explicitly.

EXAMPLE OPENER:
  "Research and explain the latest peer-reviewed findings on [topic]..."
""".strip(),

    "Copilot": """
[ FORMAT_DIRECTIVE: TARGET = Microsoft Copilot ]
Copilot is task/productivity-oriented. DO NOT use "You are a..." opener.
Open directly with an action verb. No role-play framing.

REQUIRED STRUCTURE:
  Line 1:    Action verb opener: "Write...", "Create...", "Summarize...",
             "Draft...", "Analyze...", "Generate...", "List..."
  Context:   "Based on [document/data/meeting/context]..."
  Format:    Exact output format: "as a bulleted list", "in table format",
             "as a professional email", "in exactly N paragraphs"
  Audience:  "for a [specific audience] in a [formal/informal] tone"
  Length:    Word count or paragraph count — numbers only.

EXAMPLE OPENER:
  "Summarize the following meeting transcript into 5 key action items..."
""".strip(),

}

_DEFAULT_CONTRACT = """
[ FORMAT_DIRECTIVE: TARGET = {target} ]
REQUIRED STRUCTURE:
  Research and apply the correct prompt format for {target} specifically.
  Do NOT default to ChatGPT "You are a..." style unless {target} explicitly uses it.
  Match the structural conventions and opener style for {target}.
  Apply ELITE COMPILATION STANDARDS: role specificity, prohibition clauses,
  measurable output specs, quality bar.
  The output must be immediately usable with {target} without modification.
""".strip()


OPENING_PATTERNS: dict[str, tuple[str, str]] = {
    "ChatGPT":          (r"^you\s+are\s+a?\s*\w",           "Must open with 'You are a [specific role]'"),
    "Claude":           (r"^<role>",                          "Must open with <role> XML tag"),
    "Gemini":           (r"^context\s*:",                     "Must open with 'Context:' label"),
    "Midjourney":       (r"^/imagine\s+prompt\s*:",           "Must open with '/imagine prompt:'"),
    "DALL-E":           (r"^[A-Z\"]",                         "Must open with descriptive sentence"),
    "Stable Diffusion": (r"^\w[\w\s,]+,",                     "Must open with comma-separated tags"),
    "Perplexity":       (r"^(research|explain|what|how|why|find|analyze|compare)\b", "Must open with a research directive"),
    "Copilot":          (r"^(write|create|summarize|draft|analyze|generate|list|make)\b", "Must open with an action verb"),
}


def get_format_contract(target: str) -> str:
    if not target:
        return ""
    if target in TARGET_FORMAT_CONTRACTS:
        return TARGET_FORMAT_CONTRACTS[target]
    target_lower = target.lower()
    for key, contract in TARGET_FORMAT_CONTRACTS.items():
        if key.lower() in target_lower or target_lower in key.lower():
            return contract
    return _DEFAULT_CONTRACT.format(target=target)


def get_opening_pattern(target: str) -> tuple[str, str] | None:
    if not target:
        return None
    if target in OPENING_PATTERNS:
        return OPENING_PATTERNS[target]
    target_lower = target.lower()
    for key, pattern in OPENING_PATTERNS.items():
        if key.lower() in target_lower or target_lower in key.lower():
            return pattern
    return None
