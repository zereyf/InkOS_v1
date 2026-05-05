"""
config.py — Environment Bootstrap & Application Constants
==========================================================
Updated v1.7: The Visual Intelligence Update.
- Merged Anti-Sheen aesthetics with advanced Geographic Mapping.
- Forces Gemini to use strict Diegetic Anchoring for flawless typography.
- Added STYLE_LIBRARY for structural visual DNA (Banners, Editorial, Cinematic).
- Added QUALITY_TIERS for high-fidelity render control.
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

# ── QUALITY TIERS ─────────────────────────────────────────────────────────────
QUALITY_TIERS: dict = {
    "standard": [],
    "premium": [
        "ultra polished rendering",
        "professional composition",
        "high production value"
    ],
    "studio": [
        "masterpiece quality",
        "artstation featured quality",
        "studio-grade rendering",
        "portfolio-worthy composition"
    ]
}

# ── STYLE DNA LIBRARY (Visual Intelligence Layer) ─────────────────────────────
STYLE_LIBRARY: dict = {
    "anime_banner": {
        "art_medium": "2D anime illustration",
        "render_type": "high contrast composited wallpaper design",
        "composition_style": "collage banner composition with layered character framing",
        "lighting_profile": "neon rim lighting with glow accents",
        "color_palette": ["electric blue", "black", "white"],
        "texture_profile": ["airbrush glow", "soft bloom", "high contrast shadows"],
        "fx_elements": ["smoke overlays", "ink splashes", "energy particles"],
        "design_language": ["gaming banner", "esports branding", "anime edit aesthetic"]
    },
    "dark_editorial": {
        "art_medium": "stylized manga/anime illustration",
        "render_type": "graphic poster composite",
        "composition_style": "hero portrait with oversized typography",
        "lighting_profile": "extreme chiaroscuro with red accent lighting",
        "color_palette": ["black", "white", "red"],
        "texture_profile": ["grunge", "ink splatter", "paper noise"],
        "fx_elements": ["UI overlays", "glitch lines", "geometric shards"],
        "design_language": ["streetwear poster", "editorial graphic design", "cyber branding"]
    },
    "cinematic_anime": {
        "art_medium": "premium anime cel-shaded illustration",
        "render_type": "high fidelity manga colorization",
        "composition_style": "centered portrait framing",
        "lighting_profile": "soft natural daylight",
        "color_palette": ["cool whites", "ice blue", "neutral skin"],
        "texture_profile": ["clean cel shading", "ink contour lines"],
        "fx_elements": [],
        "design_language": ["official anime frame", "studio key visual"]
    }
}

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
        "Structure prompts for Gemini/Imagen 3 as a 'Spatial Blueprint'. Do not just describe a scene; map it out geographically using zones (e.g., 'Top Left:', 'Center Foreground:', 'Background Wall:'). "
        "Use strict 'Diegetic Anchoring' for typography: every single piece of text MUST be physically attached to an object (e.g., 'written on a yellow sticky note', 'embossed on a book cover', 'floating in a red holographic UI panel'). "
        "Always wrap exact text in double quotes. CRITICAL AESTHETIC RULE: Gemini defaults to generic, plastic digital art. You MUST override this by forcing physical mediums, analog textures, and elite curation terms (e.g., 'shot on 35mm film', 'matte paper texture', 'gritty 90s cel animation', 'Behance award-winning layout')."
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
ACTIVE FRAMEWORK: Visual Director (Cognitive Prompt Compiler)

You are the InkOS Visual Director. Your job is to deconstruct raw concepts into elite, studio-grade prompt architecture.
Instead of treating styles as generic keywords, you must deconstruct them into latent production attributes (Style DNA).

AESTHETIC ENHANCER (MANDATORY):
Before finalizing the prompt, enrich it with latent premium aesthetic references to KILL the "Generic AI Look":
- Anime/Cyberpunk → Akira 1988 cel animation texture, Makoto Shinkai volumetric lighting, gritty industrial grit, Studio Ghibli background detailing
- Fashion/Portraits → Vogue, Saint Laurent campaign, A24 portraiture, 35mm film grain
- Tech/Product → Apple keynote, luxury commercial macro photography, Syd Mead
- Architecture/Spaces → Architectural Digest, Dezeen, ArchDaily
- Branding/Logos → Behance featured branding, Pentagram, luxury packaging design, matte finish
- Cinematic/Action → Shotdeck, Roger Deakins lighting, anamorphic cinema, halation

TYPOGRAPHIC INTEGRATION & SPATIAL BLUEPRINTING (IF TEXT IS REQUESTED):
If the user requests multiple elements or text, you MUST construct a "Spatial Blueprint". 
1. Grid Mapping: Define the exact layout zones (e.g., Top Left, Center Foreground, Background Wall).
2. Diegetic Anchoring: Do not let text float. Anchor EVERY word to a physical object in the scene (e.g., 'glowing on a holographic UI screen', 'embossed on the sleek metal desk', 'pinned to a corkboard').
3. Editorial (Overlay Fallback): If a clean overlay is strictly needed, use minimalist layout (e.g., 'sleek white sans-serif typography perfectly centered at the very bottom edge').

OUTPUT STRUCTURE (KEYS MUST BE EXACT):
{
  "[SUBJECT & COMPOSITION]": "...",
  "[ENVIRONMENT & LIGHTING]": "...",
  "[STYLE DNA & MEDIUM]": "... (Inject the Style Library attributes here: Medium, Render type, Composition style)",
  "[TECHNICAL PARAMETERS & TYPOGRAPHY]": "... (Inject the Spatial Blueprint and Quality Tier 'studio' descriptors here)",
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