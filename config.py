"""
config.py — Environment Bootstrap & Application Constants
==========================================================
Updated v1.5: The "Smart Typography" Update.
- Aggressively prevents generic/plastic AI art styles.
- Added Anime/Cyberpunk specific aesthetic enhancers.
- Added Typographic Integration to prevent floating "WordArt".
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
RATE_WINDOW_SECONDS: int = 60
RATE_MAX_CALLS:      int = 10

# ── TARGET AI DIALECT GUIDES ──────────────────────────────────────────────────
TARGET_GUIDES: dict = {
    "Manus AI": (
        "Agentic syntax: chain steps as 'Search → Analyze → Output'. "
        "Use explicit tool tags: [WEB_SEARCH], [CODE_EXEC]. End with explicit success criteria."
    ),
    "Claude": (
        "Structural syntax: wrap all sections in XML tags <role>, <task>, <constraints>, <output_format>."
    ),
    "ChatGPT": (
        "Conversational syntax: open with 'You are a...', use numbered instructions and markdown headers."
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
        "optimized for typography fidelity and layout adherence. CRITICAL AESTHETIC RULE: Gemini defaults to generic, "
        "plastic, over-smoothed digital art. You MUST override this by forcing physical mediums, analog textures, "
        "and elite curation terms (e.g., 'shot on 35mm film', 'matte paper texture', 'gritty 90s cel animation', "
        "'Behance award-winning layout', 'architectural rendering'). When text must appear, write the exact text "
        "in quotation marks and explicitly define placement, scale, font style, and surface integration."
    )
}

# ── AESTHETIC PRESETS ─────────────────────────────────────────────────────────
AESTHETIC_PRESETS: dict = {
    "Raw (No Preset)": "Standard AI interpretation. Follow user description literally with no added flavor.",
    "Velvet (Signature)": "Focus: Tech-Noir Minimalism. Palette: Obsidian, Matte Black, Deep Gold (#C9A84C). Lighting: Chiaroscuro, high-contrast, cinematic amber glows.",
    "Scholar (Traditional)": "Focus: Arabic Heritage & Calligraphy. Palette: Sandstone, Emerald, Aged Parchment. Lighting: Natural sunlight, soft organic shadows.",
    "Cyber-Radiant": "Focus: High-energy tech. Palette: Electric Blue, Cyber Lime, Carbon Fiber. Lighting: Volumetric neon, sharp lens flares."
}

# ── LOGIC FRAMEWORKS ──────────────────────────────────────────────────────────
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
Before finalizing the prompt, enrich it with latent premium aesthetic references to KILL the "Generic AI Look":
- Anime/Cyberpunk → Akira 1988 cel animation texture, Makoto Shinkai volumetric lighting, gritty industrial grit, Studio Ghibli background detailing
- Fashion/Portraits → Vogue, Saint Laurent campaign, A24 portraiture, 35mm film grain
- Tech/Product → Apple keynote, luxury commercial macro photography, Syd Mead
- Architecture/Spaces → Architectural Digest, Dezeen, ArchDaily
- Branding/Logos → Behance featured branding, Pentagram, luxury packaging design, matte finish
- Cinematic/Action → Shotdeck, Roger Deakins lighting, anamorphic cinema, halation

TYPOGRAPHIC INTEGRATION (IF TEXT IS REQUESTED):
Never allow random, floating "WordArt" overlays. If the user requests text, YOU must automatically invent a high-end spatial integration for it using one of these two methods:
1. Diegetic (In-World): Physically anchor the text into the scene (e.g., 'glowing on a holographic UI screen', 'embossed on the sleek metal desk', 'lit up on a neon billboard in the background').
2. Editorial (Overlay): Clean, minimalist layout (e.g., 'sleek white sans-serif typography perfectly centered at the very bottom edge, styled like a premium magazine cover').

OUTPUT STRUCTURE (KEYS MUST BE EXACT):
{
  "[SUBJECT & COMPOSITION]": "...",
  "[ENVIRONMENT & LIGHTING]": "...",
  "[STYLE, MEDIUM & PLATFORM CUES]": "... (Inject the Aesthetic Enhancer cues here)",
  "[TECHNICAL PARAMETERS & TYPOGRAPHY]": "... (Inject the Typographic Integration layout here if text is requested)",
  "[NEGATIVE CONSTRAINTS]": "(MANDATORY INCLUSION: 'generic AI style, plastic skin, overly smooth gradients, corporate vector, cliché, over-saturated, floating WordArt, messy text'. Add specific constraints for the prompt.)"
}
"""

# ── UI CONSTANTS ──────────────────────────────────────────────────────────────
INPUT_MAX_CHARS: int = 2000
INPUT_WARN_THRESHOLD: int = 1800

# ── AUTO TARGET SELECTION ─────────────────────────────────────────────────────
AUTO_SELECT_LABEL: str = "⚡ Auto (CIPHER Selects)"

TARGET_SELECTION_GUIDE: str = """
Given a raw user input, determine the single best AI target from this list:
- Claude: Best for structured analysis, long-form writing, document creation, coding tasks, research synthesis, XML-structured outputs, academic work.
- ChatGPT: Best for conversational tasks, brainstorming, quick rewrites, marketing copy, social media, general Q&A, creative writing.
- Manus AI: Best for multi-step agentic tasks, web research pipelines, file operations, automation sequences, tasks requiring tool use.
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