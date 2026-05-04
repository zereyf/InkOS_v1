"""
config.py — Environment Bootstrap & Application Constants
==========================================================
Updated v1.2: Added Aesthetic Presets, Visual Dialects, and Ultimate Visual Director Framework.
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
        "Visual technical syntax: [Subject], [Environment], [Lens/Camera], [Style]. "
        "Include mandatory parameters: --ar 16:9 --v 6.0."
    ),
    "DALL-E 3": (
        "Descriptive narrative syntax. Focus on literal scene description, "
        "cinematic lighting, and hyper-detailed textures."
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
VISUAL_DIRECTOR_PROMPT: str = """
You are an Elite Visual Synthesis Engine. Your objective is to transform raw concepts into professional, studio-grade image generation prompts.

Execute this agentic workflow before outputting the final prompt:
1. Visual Medium Analyzer: Categorize the raw input into a domain (Cinematic Realism, Anime, Manga, 3D Rendering, Tech-Noir, Architecture, or Editorial Photography).
2. Premium Platform Synthesis (Latent Scraping): Analyze and synthesize aesthetic standards from top-tier curation platforms relevant to the domain. Pull cinematic framing from Shotdeck/FilmGrab, 3D/Digital mastery from ArtStation/CGSociety, editorial grading from Vogue Italia, architectural precision from ArchDaily, and trending curation cues from Behance and Pinterest. 
3. Vocabulary Injection: Inject domain-specific technical terminology (e.g., 'Arri Alexa 65, 35mm f/1.4' or 'Kodak Portra 400' for Realism; 'Unreal Engine 5, Raytracing, Octane Render' for 3D).
4. Output Synthesis: Output the final prompt strictly using these exact headers. DO NOT include conversational filler.

[SUBJECT & COMPOSITION]: (Hyper-detailed description of character, action, and framing)
[ENVIRONMENT & LIGHTING]: (Setting details, lighting ratios, weather, color grading)
[STYLE, MEDIUM & PLATFORM CUES]: (Artistic domain, mood, and specific platform curation keywords like 'trending on ArtStation' or 'Shotdeck cinematic still')
[TECHNICAL PARAMETERS]: (Camera specs, rendering engines, aspect ratio)
[NEGATIVE CONSTRAINTS]: (What the AI must strictly avoid, e.g., text, deformed, watermarks, low resolution)
"""

# ── UI CONSTANTS ──────────────────────────────────────────────────────────────
INPUT_MAX_CHARS: int = 2000
INPUT_WARN_THRESHOLD: int = 1800

# ── AUTO TARGET SELECTION ─────────────────────────────────────────────────────
# The "Auto" option triggers CIPHER's target analysis before refinement.
# CIPHER reads the input and selects the best target based on intent signals.
AUTO_SELECT_LABEL: str = "⚡ Auto (CIPHER Selects)"

# Decision rules CIPHER uses to select the best target
TARGET_SELECTION_GUIDE: str = """
Given a raw user input, determine the single best AI target from this list:
- Claude: Best for structured analysis, long-form writing, document creation,
  coding tasks, research synthesis, XML-structured outputs, academic work.
- ChatGPT: Best for conversational tasks, brainstorming, quick rewrites,
  marketing copy, social media, general Q&A, creative writing.
- Manus AI: Best for multi-step agentic tasks, web research pipelines,
  file operations, automation sequences, tasks requiring tool use.
- Midjourney/Flux: Best for image generation, visual art direction,
  photography prompts, design briefs, aesthetic direction.
- DALL-E 3: Best for realistic image generation, scene illustration,
  product mockups, visual storytelling.

Selection signals to look for:
  Code / technical / analysis → Claude
  Creative / social / copy    → ChatGPT
  Research / automation / web → Manus AI
  Art / image / visual        → Midjourney/Flux or DALL-E 3
  Arabic scholarly / Sharia   → Claude (XML structure handles Arabic constraints best)
"""
