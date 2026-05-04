"""
config.py — Environment Bootstrap & Application Constants
==========================================================
Updated v1.3: Visual Triad Complete (Gemini Imagen 3 added).
Restored missing LOGIC_FRAMEWORKS variable to prevent sidebar crash.
Injected Elite Aesthetic Enhancer into Visual Director.
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# ── API CLIENT ────────────────────────────────────────────────────────────────
_api_key: str = os.getenv("GROQ_API_KEY", "")
client: Groq = Groq(api_key=_api_key) if _api_key else None  # type: ignore
API_KEY_MISSING: bool = not bool(_api_key)

# ── MODEL CONFIG ──────────────────────────────────────────────────────────────
MODEL_ID:    str = "llama-3.3-70b-versatile"
TEMPERATURE: float = 0.3
MAX_TOKENS:  int   = 1536

# ── RATE LIMITING ─────────────────────────────────────────────────────────────
# Required by security/rate_limiter.py
RATE_WINDOW_SECONDS: int = 60
RATE_MAX_CALLS:      int = 10

# ── TARGET AI DIALECT GUIDES ──────────────────────────────────────────────────
TARGET_GUIDES: dict = {
    "Manus AI": (
        "Agentic syntax: chain steps as 'Search → Analyze → Output'. "
        "Use explicit tool tags: [WEB_SEARCH], [CODE_EXEC]. "
        "End with explicit success criteria."
    ),
    "Claude": (
        "Structural syntax: wrap all sections in XML tags "
        "<role>, <task>, <constraints>, <output_format>."
    ),
    "ChatGPT": (
        "Conversational syntax: open with 'You are a...', "
        "use numbered instructions and markdown headers."
    ),
    "Midjourney/Flux": (
        "Structure prompts using modular visual syntax optimized for both Midjourney and Flux: "
        "[Primary Subject] :: [Environment/Scene] :: [Composition/Lens/Camera Specs] :: "
        "[Lighting/Rendering/Material Detail] :: [Aesthetic/Reference Style]. Use weighted tokens (::) "
        "to prioritize critical visual elements, append negative prompting for exclusion control where relevant "
        "(e.g. '--no cartoon, illustration, low detail, deformed anatomy'), and always inject elite aesthetic "
        "reference cues sourced from ArtStation, Vogue Italia editorials, Shotdeck cinematic grading, luxury "
        "commercial photography, and premium concept art pipelines. Maintain balance between technically segmented "
        "prompt blocks for Midjourney and natural descriptive readability for Flux."
    ),
    "DALL-E 3": (
        "Structure prompts as highly descriptive cinematic production briefs written in natural language, "
        "emphasizing literal scene construction, real-world materials, physical lighting behavior, lens "
        "characteristics, and microtexture realism. Explicitly enforce photorealistic rendering by specifying "
        "'photograph', 'cinematic still', 'architectural visualization', 'commercial product photography', or "
        "'editorial fashion photography' as applicable, and prohibit stylization drift by excluding "
        "cartoon/anime/illustrative language unless requested. Anchor outputs to premium aesthetic domains such "
        "as luxury editorial campaigns, architectural digest visualization, Vogue-style photography, and high-end "
        "commercial rendering for maximum realism and compositional discipline."
    ),
    "Gemini (Imagen 3)": (
        "Structure prompts for Gemini/Imagen 3 as a spatially explicit natural-language visual specification "
        "optimized for photorealism, typography fidelity, and layout adherence. Always describe the scene in "
        "ordered layers: primary subject → environment/background → composition/layout → lighting/materials → "
        "stylistic/aesthetic cues. When text must appear in the image, write the exact text in quotation marks "
        "and explicitly define placement, scale, orientation, font style, and surface integration (e.g. 'gold "
        "embossed serif logo reading \"AMEERINK\" centered on matte black box'). Naturally embed premium visual "
        "curation references from branding/editorial/design ecosystems such as Behance, Pinterest, premium brand "
        "campaigns, luxury packaging design, and high-end commercial advertising aesthetics."
    )
}

# ── AESTHETIC PRESETS (Modular Style Library) ──────────────────────────────────
AESTHETIC_PRESETS: dict = {
    "Raw (No Preset)": (
        "Standard AI interpretation. Follow user description literally with no added flavor."
    ),
    "Velvet (Signature)": (
        "Focus: Tech-Noir Minimalism. Palette: Obsidian, Matte Black, Deep Gold (#C9A84C). "
        "Lighting: Chiaroscuro, high-contrast, cinematic amber glows."
    ),
    "Scholar (Traditional)": (
        "Focus: Arabic Heritage & Calligraphy. Palette: Sandstone, Emerald, Aged Parchment. "
        "Lighting: Natural sunlight, soft organic shadows."
    ),
    "Cyber-Radiant": (
        "Focus: High-energy tech. Palette: Electric Blue, Cyber Lime, Carbon Fiber. "
        "Lighting: Volumetric neon, sharp lens flares."
    )
}

# ── LOGIC FRAMEWORKS ──────────────────────────────────────────────────────────
# BUG FIX: Restored the LOGIC_FRAMEWORKS list required by ui/sidebar.py
LOGIC_FRAMEWORKS: list = [
    "Professional (RACE)", 
    "Technical (Zero-Shot)", 
    "Creative (Chain-of-Thought)", 
    "Visual Director"
]

VISUAL_DIRECTOR_PROMPT: str = """
ACTIVE FRAMEWORK: Visual Director (Cinematic & Editorial Photography)

You are the InkOS Visual Director. Your job is to translate raw concepts into elite, studio-grade prompt architecture.
Output your response as a structured dictionary format (which the system will automatically humanize).

AESTHETIC ENHANCER (MANDATORY):
Before finalizing the prompt, enrich it with latent premium aesthetic references relevant to the domain:
- Fashion/Portraits → Vogue, Saint Laurent campaign, A24 portraiture
- Tech/Product → Apple keynote, luxury commercial macro photography, Syd Mead
- Architecture/Spaces → Architectural Digest, Dezeen, ArchDaily
- Branding/Logos → Behance featured branding, Pentagram, luxury packaging design
- Cinematic/Action → Shotdeck, Roger Deakins lighting, anamorphic cinema

OUTPUT STRUCTURE (KEYS MUST BE EXACT):
{
  "[SUBJECT & COMPOSITION]": "...",
  "[ENVIRONMENT & LIGHTING]": "...",
  "[STYLE, MEDIUM & PLATFORM CUES]": "... (Inject the Aesthetic Enhancer cues here)",
  "[TECHNICAL PARAMETERS]": "...",
  "[NEGATIVE CONSTRAINTS]": "..."
}
"""

# ── UI CONSTANTS ──────────────────────────────────────────────────────────────
INPUT_MAX_CHARS: int = 2000
INPUT_WARN_THRESHOLD: int = 1800

# ── AUTO TARGET SELECTION ─────────────────────────────────────────────────────
# The "Auto" option triggers CIPHER's target analysis before refinement.
AUTO_SELECT_LABEL: str = "⚡ Auto (CIPHER Selects)"

TARGET_SELECTION_GUIDE: str = """
Given a raw user input, determine the single best AI target from this list:
- Claude: Best for structured analysis, long-form writing, document creation,
  coding tasks, research synthesis, XML-structured outputs, academic work.
- ChatGPT: Best for conversational tasks, brainstorming, quick rewrites,
  marketing copy, social media, general Q&A, creative writing.
- Manus AI: Best for multi-step agentic tasks, web research pipelines,
  file operations, automation sequences, tasks requiring tool use.
- Midjourney/Flux: Best for cinematic art, stylized concepts, high-end tech-noir, and complex lighting/materials.
- DALL-E 3: Best for photorealistic scenes, product shots, narrative descriptions, and highly literal physical constraints.
- Gemini (Imagen 3): Best for precise text rendering, readable typography, brand/logo text, signage, packaging labels, UI mockups, infographics, and strict spatial/positional composition requirements.

Selection signals to look for:
  Code / technical / analysis → Claude
  Creative / social / copy    → ChatGPT
  Research / automation / web → Manus AI
  Cinematic art / concepts    → Midjourney/Flux
  Photorealism / products     → DALL-E 3
  Typography / logos / text   → Gemini (Imagen 3)
  Arabic scholarly / Sharia   → Claude
"""