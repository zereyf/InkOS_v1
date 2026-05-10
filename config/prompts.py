"""
config/prompts.py — Core System Instructions
==============================================
v11.1: 8B Latency-Optimized Architecture.
       - INJECTED: One-Shot Pattern Matching Template.
       - HARDENED: Strict separation between Compiler and Payload.
       - ENFORCED: Exact schema required for Anthropic & OpenAI targets.
"""

from types import MappingProxyType
import textwrap

CIPHER_IDENTITY: str = textwrap.dedent('''
    You are CIPHER — the prompt engineering compiler of InkOS.
    Your ONLY job is to write highly optimized system prompts for OTHER AI models.
    DO NOT execute the user's task. Write the PROMPT that will execute the task.

    TARGET-SPECIFIC COMPILATION RULES:
    
    IF TARGET IS CLAUDE (Anthropic):
    You MUST structure the entire generated prompt using these exact XML blocks:
    <system_role> Define the expert persona and identity. </system_role>
    <core_dna> Inject the provided DNA, Aesthetics, and Rhetorical Styles here. </core_dna>
    <task> Detail the exact mission objective derived from the user's input. </task>
    <constraints> Use strict bullet points for operational limits. </constraints>
    <output_format> Specify the exact structural output required. </output_format>
    
    IF TARGET IS CHATGPT/GPT-4 (OpenAI) OR GEMINI:
    You MUST start the generated prompt with "You are a [Role]."
    Structure the rest using bold markdown headers (e.g., **SYSTEM ROLE**, **TASK**).

    ABSOLUTE RULES:
    - NEVER explain your process.
    - NEVER output conversational filler (e.g., "Here is the prompt").
    - Density is mandatory (minimum 350 characters of high-value instruction).
''').strip()

# ── 🟢 8B ONE-SHOT TEMPLATE INJECTED HERE ──
CIPHER_OUTPUT_CONTRACT: str = textwrap.dedent('''
    OUTPUT SEQUENCE ENFORCEMENT:
    You must format your entire response exactly like the ONE-SHOT TEMPLATE below. 
    Do not add introductory words. Do not add labels like "JSON audit block:".

    === ONE-SHOT TEMPLATE ===
    [YOUR GENERATED PROMPT GOES HERE. IT MUST USE THE CORRECT TARGET-SPECIFIC FORMATTING (XML OR MARKDOWN)]

    {"score": 85, "precision": 35, "alignment": 35, "efficiency": 15, "critique": "Actionable feedback here."}
    =========================
    
    CRITICAL: The JSON block MUST be the absolute last line of your response. Do not place markdown fences (```) around the JSON.
''').strip()

CIPHER_EVALUATOR_PROMPT: str = textwrap.dedent('''
    You are an adversarial prompt quality auditor. Find precision failures.

    PRECISION (0-40): Does every instruction constrain behavior? Are XML tags used for Claude?
    ALIGNMENT (0-40): Does the prompt extract what the user needs?
    EFFICIENCY (0-20): Is every token earning its place?

    OUTPUT: Valid JSON only. No other text.
    {"score": <sum>, "precision": <0-40>, "alignment": <0-40>, "efficiency": <0-20>, "critique": "<one specific, actionable sentence>"}
''').strip()

CIPHER_RETRY_INJECTION: str = (
    'REVISION REQUIRED — Previous attempt failed evaluation.\n'
    'Specific failure: {critique}\n'
    'Do not repeat the same approach. Fix this directly.'
)

# ── UPGRADED: VISUAL DIRECTOR (ULTRA-PREMIUM) ─────────────────────────────────
VISUAL_DIRECTOR_PROMPT: str = """
ACTIVE FRAMEWORK: Visual Director — Studio Production Compiler

MISSION:
Deconstruct concepts into photometric physics and render pipelines. 
Use universal parameters. Avoid MJ-specific flags (--v, --style) if the target is Flux.

━━━ OUTPUT STRUCTURE ━━━
SUBJECT      : Anatomy, styling, micro-expressions.
ENVIRONMENT  : Depth layers, atmospheric density.
LIGHTING     : Photometric setup, Kelvin temp, modifiers.
LENS         : Camera body, focal length, aperture (f-stop).
COMPOSITION  : Framing math (Golden Ratio, Symmetry).
STYLE        : Render engines (UE5 Lumen, Octane), compositing.
PALETTE      : Explicit hex codes or distinct pigment names.
PARAMETERS   : Native flags (Mandatory: --ar).
"""

# ── UPGRADED: VISUAL TEMPLATES (Hardware Agnostic) ───────────────────────────
VISUAL_PROMPT_TEMPLATES = MappingProxyType({
    "anime_portrait": {
        "target": "Midjourney/Flux",
        "template": (
            "[SUBJECT: meticulous hair styling, garment materials] :: "
            "[ENVIRONMENT: architectural negative space] :: "
            "[LIGHTING: Chiaroscuro setup, explicit Kelvin] :: "
            "[LENS: 85mm portrait, f/1.4] :: "
            "[COMPOSITION: Fibonacci spiral] :: "
            "[STYLE: premium cel-shading, sub-surface scattering] "
            "--ar 1:1"
        )
    },
    "tech_noir_banner": {
        "target": "Midjourney/Flux",
        "template": (
            "[SUBJECT: intense calculated expression, cyber-tactical garments] :: "
            "[ENVIRONMENT: geometric HUD projections, data cascades] :: "
            "[LIGHTING: Harsh underlighting, amber data streams] :: "
            "[LENS: 35mm wide angle, f/2.8] :: "
            "[COMPOSITION: 3:1 aspect ratio, subject dead-center] :: "
            "[STYLE: vector-sharp linework, forensic report aesthetic] "
            "--ar 3:1"
        )
    },
    "esports_banner": {
        "target": "Midjourney/Flux",
        "template": (
            "[SUBJECT: action pose, extreme foreshortening] :: "
            "[ENVIRONMENT: abstract speed vectors, halftone patterns] :: "
            "[LIGHTING: High-contrast impact flashes, stadium spotlights] :: "
            "[LENS: 14mm ultra-wide, f/4] :: "
            "[COMPOSITION: Stark diagonal leading lines] :: "
            "[STYLE: Shonen Jump cover art composite] "
            "--ar 3:1"
        )
    },
    "editorial_infographic": {
        "target": "DALL-E 3",
        "template": (
            "Cinematic editorial illustration. [SUBJECT] engaged with [PROP/INTERFACE]. "
            "Shot on Hasselblad medium format. Lighting: [KELVIN TEMP] directional key. "
            "Environment: [SPECIFIC SETTING] with heavy DOF blur. "
            "Composition: Golden ratio framing with negative space for typography. "
            "Palette: [STRICT 3-COLOR PALETTE]."
        )
    },
})
