"""
config/target_formats.py — v3.0 — Creative Director Standard
==============================================================
Upgraded to match CIPHER v15.0.

Every FORMAT_DIRECTIVE now:
  - Requires 3 named background zones for image targets
  - Requires per-region style assignment for character images
  - Requires Layer 10 Narrative Logic to appear in output
  - Explicitly states which targets use "You are a..." and which never do
  - Includes elite example openers at creative director standard
"""

from __future__ import annotations
import re

TARGET_FORMAT_CONTRACTS: dict[str, str] = {

    "ChatGPT": """
[ FORMAT_DIRECTIVE: TARGET = ChatGPT / GPT-4o ]
ChatGPT is the ONLY target in this system that uses a "You are a..." opener.
All other targets explicitly prohibit it.

REQUIRED STRUCTURE:
  Line 1:  "You are a [specific expert identity]."
           NEVER: "You are a helpful assistant."
           ALWAYS: title + years of experience + domain + institutional context.
           Example: "You are a principal product strategist with 11 years building
           B2B SaaS products at Amplitude, Mixpanel, and two seed-stage startups."

  Line 2:  Task description in second person.
           "Your task is to..." or "You will..." — specific and measurable.

  Body:    Minimum 2 prohibition clauses.
           Measurable output specs (numbers, not adjectives).
           Edge case handling.

  End:     Explicit output format: structure, length, tone — all as numbers or rules.

ELITE REQUIREMENTS:
  - Role: title + years + domain + institution (all four, always)
  - Prohibitions: minimum 2, each targeting a specific failure mode
  - Specs: word counts, section counts, binary rules — never "medium length"
  - No filler: "please", "try to", "make sure to" are banned from the prompt

EXAMPLE OPENER (copy this structure, not this content):
  "You are a senior data journalist with 9 years covering technology policy
   for The Guardian and MIT Technology Review, specializing in AI regulation
   and algorithmic accountability investigations."
""".strip(),

    "Claude": """
[ FORMAT_DIRECTIVE: TARGET = Claude (Anthropic) ]
Claude requires XML-structured output.
DO NOT open with "You are a..." — that is ChatGPT format.
DO NOT open with "Context:" — that is Gemini format.
Missing <role> tag = automatic format failure. Alignment score = 0.

REQUIRED XML STRUCTURE (all six tags mandatory):

  <role>
    Specific expert identity: title + years + domain + institutional context.
    Character traits that directly affect output style and decisions.
    Not generic. Never "helpful assistant." Always a named expert type.
  </role>

  <task>
    Specific measurable task. What the output IS, not what it should feel like.
    Numbers only for length and structure specs.
  </task>

  <constraints>
    Minimum 3 items. All enforceable and testable.
    At least 2 prohibition clauses: "Do not...", "Never...", "Avoid..."
    All format specs as numbers or binary rules.
  </constraints>

  <edge_cases>
    Minimum 2 specific edge cases for this exact task domain.
    Not generic "if unclear ask" — domain-specific failure scenarios.
  </edge_cases>

  <output_format>
    Exact structure: section names, heading levels, word counts per section.
    Binary rules only. No adjectives. No "approximately."
  </output_format>

  <quality_bar>
    Name a specific human reviewer in a specific role who would approve this.
    "A [role] at [institution] would [approve / publish / ship] this without
    [requesting clarification / structural revision / fact-checking concerns]."
  </quality_bar>

EXAMPLE OPENER:
  <role>
  You are a principal security architect with 14 years in enterprise
  infrastructure, previously at Cloudflare and Fastly...
  </role>

DO NOT write anything before the opening <role> tag.
""".strip(),

    "Gemini": """
[ FORMAT_DIRECTIVE: TARGET = Gemini (Google) ]
Gemini uses labelled section format.
DO NOT open with "You are a..." — that is ChatGPT format.
DO NOT use XML tags — that is Claude format.
Missing "Context:" opener = format failure.

REQUIRED STRUCTURE:
  Context:     Expert framing without "You are a..." syntax.
               "Acting as a [expert type] with [years] in [domain]..."
               Or: "From the perspective of a [expert type]..."

  Task:        Specific, measurable. Numbers not adjectives.
               Include multimodal context note if input contains images or data.

  Constraints: Minimum 2 prohibition clauses.
               All specs measurable.

  Output:      Exact format — section names, word counts, heading levels.
               State if response should include citations, tables, or code.

ELITE REQUIREMENTS:
  - Context establishes expert framing without role-play syntax
  - Handles multimodal input explicitly when relevant
  - All output specs are numbers or binary rules

EXAMPLE OPENER:
  "Context: Acting as a senior UX researcher with 10 years in enterprise
   software, having led 200+ usability studies across B2B SaaS products..."
""".strip(),

    "Midjourney": """
[ FORMAT_DIRECTIVE: TARGET = Midjourney v6 ]
Midjourney uses /imagine prompt: syntax with :: weighted layer separators.
DO NOT open with "You are a..." — immediate format failure, alignment = 0.
DO NOT write prose sentences — Midjourney is not a prose model.
DO NOT use a flat tag list without :: separators — precision failure.
Missing /imagine prompt: opener = automatic format failure, alignment = 0.
Missing :: separators = precision capped at 15/40.

REQUIRED LAYER ORDER (each separated by ::):
  1. SUBJECT      — anatomy, joint angles, expression in behavioral terms
  2. ZONE 1       — immediate background: color + opacity + role
  3. ZONE 2       — mid background: specific location + depth structure
  4. ZONE 3       — far background: depth elements + opacity range
  5. LIGHTING     — Kelvin temp for each source, key/fill/rim, shadow quality
  6. LENS         — focal length, aperture, camera height, angle in degrees
  7. COMPOSITION  — named framing rule, subject position, negative space location
  8. FACE         — specific render treatment for face/skin only
  9. CLOTHING     — specific render treatment for clothing only
  10. HANDS       — specific render treatment for hands only
  11. PALETTE     — hex codes, max 4 colors, role of each, discipline statement
  12. NARRATIVE   — WHY the key elements work (one sentence each)

PARAMETERS (always at end, all required):
  --ar [ratio]    16:9 / 3:2 / 1:1 / 9:16 / 3:1
  --v 6
  --style raw     (for realism or anime)
  --q 2
  --no [list]     specific named tropes being excluded, not generic "bad stuff"

HARD RULES:
  PALETTE: Never "vibrant" or "neon." Always hex codes with use-case stated.
  LIGHTING: Never "cinematic." Always Kelvin temperature.
  STYLE: Never studio name alone. Always studio + specific work + director name.
  GLITCH: If present, each effect needs location + pixel magnitude + narrative purpose.
  ZONES: All three zones mandatory. Each gets its own :: block.
  PER-REGION: Face, clothing, hands each get their own :: block.

EXAMPLE OPENER:
  "/imagine prompt: [SUBJECT: single male figure, seated upright...] :: ..."
""".strip(),

    "FLUX": """
[ FORMAT_DIRECTIVE: TARGET = FLUX ]
FLUX uses layered natural language — NOT /imagine syntax.
DO NOT use :: separators.
DO NOT open with "You are a..."
DO NOT use /imagine prefix.
FLUX handles typography and text better than any other diffusion model — exploit this.

REQUIRED STRUCTURE (prose paragraphs, one per layer):
  Paragraph 1: Subject with anatomy-level specificity and behavioral expression.
  Paragraph 2: ZONE 1 (immediate) + ZONE 2 (mid) + ZONE 3 (far) — named explicitly.
  Paragraph 3: Lighting — Kelvin temps, source names, shadow quality.
  Paragraph 4: Lens — focal length, aperture, angle, depth of field behavior.
  Paragraph 5: Per-region style — face treatment, clothing treatment, hands treatment.
  Paragraph 6: Palette — hex codes, role of each color, discipline statement.
  Paragraph 7: Narrative Logic — WHY each major element works.
  Final line:  "Avoid: [specific comma-separated list]."

FLUX STRENGTHS TO EXPLOIT:
  - Text and typography within the image: specify exactly
  - Fine structural detail: exploit at Layer 1 and Layer 6
  - Natural language understanding: write complete sentences, not keyword fragments

EXAMPLE OPENER:
  "Single male figure seated in a minimal dark chair, posture completely relaxed..."
""".strip(),

    "DALL-E": """
[ FORMAT_DIRECTIVE: TARGET = DALL-E 3 ]
DALL-E 3 requires descriptive prose paragraphs.
DO NOT use /imagine syntax — immediate format failure.
DO NOT use :: separators.
DO NOT use XML tags.
DO NOT open with "You are a..."
Missing closing "Avoid:" sentence = precision failure.

REQUIRED PARAGRAPH STRUCTURE:
  P1: Subject — anatomy, pose angles in degrees, behavioral expression (not emotional adjectives).
  P2: Background — ZONE 1 immediate + ZONE 2 mid + ZONE 3 far. Name each zone explicitly.
  P3: Lighting — Kelvin temps required. Source names. Shadow quality. What each light illuminates.
  P4: Per-region style — face treatment separately from clothing separately from hands.
      State the mixed media logic if multiple render modes are used.
  P5: Palette — hex codes for all dominant colors, role of each, maximum 4 colors stated.
  P6: Composition — framing rule, subject placement, negative space location and purpose,
      eye movement path through the composition.
  P7: Narrative Logic — WHY the major elements work. The theory of the composition.
      "The single cable is powerful because there is only one."
      This paragraph gives the model the reasoning to handle unspecified details correctly.
  Final: "Avoid: [specific list of named aesthetic tropes, not generic terms]."

HARD RULES:
  PALETTE: Never "warm tones." Always "#ff6b2b for skin tones and warm practicals."
  LIGHTING: Never "cinematic." Always "5600K key from low-left horizon."
  STYLE: Never "anime style." Always specific work + director + render treatment.
  ZONES: All three background zones must be named and described.
  PER-REGION: Face, clothing, hands described separately.
  NARRATIVE: Layer 10 Narrative Logic paragraph is mandatory.
  AVOID: Final "Avoid:" sentence is mandatory and must name specific tropes.

EXAMPLE OPENER:
  "Premium mixed media cyberpunk editorial poster. Square 1:1 format.
   SUBJECT: Young male figure seated in a sleek minimal dark chair..."
""".strip(),

    "Stable Diffusion": """
[ FORMAT_DIRECTIVE: TARGET = Stable Diffusion ]
Stable Diffusion uses comma-separated keyword tags — NOT prose sentences.
DO NOT write paragraph sentences.
DO NOT open with "You are a..."
Missing "Negative prompt:" block = automatic format failure, alignment = 0.

REQUIRED STRUCTURE:

  POSITIVE TAGS (ordered by importance, comma-separated):
    [subject tags] → [zone/environment tags] → [lighting tags] →
    [per-region style tags] → [palette tags] → [quality boosters]

  Quality boosters (always include at end of positive):
    masterpiece, best quality, highly detailed, sharp focus, 8k

  [blank line]

  Negative prompt: [comma-separated exclusion tags]

  Standard negatives (always include):
    ugly, blurry, low quality, watermark, text, signature,
    deformed, extra limbs, bad anatomy, bad hands, cropped,
    worst quality, jpeg artifacts, motion blur

ADVANCED SYNTAX (use when relevant):
  Token emphasis:   (term:1.4) to boost, (term:0.7) to reduce
  LoRA weights:     <lora:model_name:0.8>
  Embeddings:       embedding:bad_prompt_version2 in negative

HARD RULES:
  ZONES: Include zone-specific tags for immediate / mid / far background.
  PER-REGION: Use separate style tags for face, clothing, hands.
  PALETTE: Include hex code color reference tags.
  NEGATIVES: Name specific aesthetic tropes, not just generic quality terms.
  GLITCH: If applicable, include specific glitch effect tags.

EXAMPLE OPENER:
  "premium editorial poster, young male seated minimal chair,
   eyes closed faint smirk, single emerald cable from head,..."
  Negative prompt: ugly, blurry, watermark, text,...
""".strip(),

    "Perplexity": """
[ FORMAT_DIRECTIVE: TARGET = Perplexity AI ]
Perplexity is a research model. DO NOT use "You are a..." opener.
DO NOT use XML tags or /imagine syntax.
Missing research question opener = format failure.

REQUIRED STRUCTURE:
  Line 1:   Clear, specific research question or directive.
  Scope:    Time period, geography, domain constraints.
  Sources:  "Prioritize peer-reviewed / institutional / primary sources."
  Format:   "Summarize in [N bullet points / N paragraphs / table format]."
  Depth:    State target audience knowledge level explicitly.
  Exclude:  "Do not include [X]. Avoid [Y]."

EXAMPLE OPENER:
  "Research and synthesize peer-reviewed findings published after 2022 on..."
""".strip(),

    "Copilot": """
[ FORMAT_DIRECTIVE: TARGET = Microsoft Copilot ]
Copilot is productivity-oriented. DO NOT use "You are a..." opener.
Open with an action verb. No role-play framing. No XML tags.
Missing action verb opener = format failure.

REQUIRED STRUCTURE:
  Line 1:   Action verb: Write, Create, Summarize, Draft, Analyze, Generate, List.
  Context:  "Based on [document / data / meeting notes / context]..."
  Format:   Exact output structure — "as a bulleted list", "in table format",
            "as a professional email", "in exactly N paragraphs."
  Audience: Specific audience in specific context + tone.
  Length:   Word count or paragraph count — numbers only.

EXAMPLE OPENER:
  "Summarize the following meeting transcript into 5 key action items,
   formatted as a bulleted list for a VP-level audience..."
""".strip(),

    "Manus AI": """
[ FORMAT_DIRECTIVE: TARGET = Manus AI ]
Manus handles agentic multi-step workflows.
Structure as explicit sequential steps with tool references.
DO NOT use "You are a..." opener.

REQUIRED STRUCTURE:
  OBJECTIVE:  Single clear goal statement.
  STEPS:      Numbered sequential actions. Each step names the tool or action.
  TOOLS:      List tools Manus should use (browser, code, files, APIs).
  OUTPUT:     Exact deliverable format and location.
  FALLBACK:   What to do if a step fails.

EXAMPLE OPENER:
  "OBJECTIVE: Research, compile, and format a competitive analysis report..."
""".strip(),

}

_DEFAULT_CONTRACT = """
[ FORMAT_DIRECTIVE: TARGET = {target} ]
Apply the correct prompt format for {target} specifically.
Do NOT default to ChatGPT "You are a..." style unless {target} explicitly uses it.
Apply ELITE COMPILATION STANDARDS: role specificity, prohibition clauses,
measurable output specs, quality bar definition.
For image targets: use 3 named background zones, per-region style assignment,
and Layer 10 Narrative Logic.
Output must be immediately usable with {target} without modification.
""".strip()


OPENING_PATTERNS: dict[str, tuple[str, str]] = {
    "ChatGPT":          (r"^you\s+are\s+a?\s*\w",
                         "Must open with 'You are a [specific expert role]'"),
    "Claude":           (r"^<role>",
                         "Must open with <role> XML tag — no text before it"),
    "Gemini":           (r"^context\s*:",
                         "Must open with 'Context:' label"),
    "Midjourney":       (r"^/imagine\s+prompt\s*:",
                         "Must open with '/imagine prompt:'"),
    "FLUX":             (r"^[A-Z][a-z]",
                         "Must open with a capitalized prose sentence"),
    "DALL-E":           (r"^[A-Z\"]",
                         "Must open with a capitalized descriptive sentence"),
    "Stable Diffusion": (r"^\w[\w\s,]+,",
                         "Must open with comma-separated keyword tags"),
    "Perplexity":       (r"^(research|explain|what|how|why|find|analyze|compare|synthesize)\b",
                         "Must open with a research directive or question"),
    "Copilot":          (r"^(write|create|summarize|draft|analyze|generate|list|make|compile)\b",
                         "Must open with an action verb"),
    "Manus AI":         (r"^OBJECTIVE\s*:",
                         "Must open with 'OBJECTIVE:' statement"),
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
