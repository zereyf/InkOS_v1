"""
config.py — Environment Bootstrap & Application Constantsd
==========================================================
v1.8: STABLE RESTORATION.
- Restores all original UI constants and Groq client.
- Preserves the Style DNA Library for elite visual deconstruction.
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
    "premium": ["ultra polished rendering", "professional composition"],
    "studio": ["masterpiece quality", "artstation featured", "studio-grade rendering"]
}

# ── STYLE DNA LIBRARY ─────────────────────────────────────────────────────────
STYLE_LIBRARY: dict = {
    "anime_banner": {
        "art_medium": "2D anime illustration",
        "render_type": "high contrast composited wallpaper design",
        "composition_style": "collage banner composition with layered character framing",
        "design_language": ["esports branding", "anime edit aesthetic", "gaming banner"]
    },
    "dark_editorial": {
        "art_medium": "stylized manga illustration",
        "render_type": "graphic poster composite",
        "composition_style": "hero portrait with oversized typography",
        "design_language": ["streetwear poster", "editorial graphic design"]
    }
}

# ── TARGET AI DIALECT GUIDES ──────────────────────────────────────────────────
TARGET_GUIDES: dict = {
    "Manus AI": "Agentic syntax: chain steps as 'Search → Analyze → Output'.",
    "Claude": "Structural syntax: wrap all sections in XML tags.",
    "ChatGPT": "Conversational syntax: open with 'You are a...'",
    "Midjourney/Flux": "Modular visual syntax: [Subject] :: [Environment] :: [Parameters]",
    "DALL-E 3": "Highly descriptive cinematic production briefs in natural language.",
    "Gemini (Imagen 3)": "Spatially explicit 'Spatial Blueprint' mapping out zones and diegetic text."
}

# ── AESTHETIC PRESETS ─────────────────────────────────────────────────────────
AESTHETIC_PRESETS: dict = {
    "Raw (No Preset)": "Standard AI interpretation.",
    "Velvet (Signature)": "Focus: Tech-Noir Minimalism. Palette: Obsidian, Matte Black, Gold.",
    "Scholar (Traditional)": "Focus: Arabic Heritage. Palette: Sandstone, Emerald.",
    "Cyber-Radiant": "Focus: High-energy tech. Palette: Electric Blue, Cyber Lime."
}

# ── LOGIC FRAMEWORKS ──────────────────────────────────────────────────────────
LOGIC_FRAMEWORKS: list = ["Professional (RACE)", "Technical (Zero-Shot)", "Creative (Chain-of-Thought)", "Visual Director"]

VISUAL_DIRECTOR_PROMPT: str = """
ACTIVE FRAMEWORK: Visual Director (Cognitive Prompt Compiler)
Task: Deconstruct user intent into a high-end visual blueprint. 
Output strictly JSON matching the required pipeline schemas.
"""

# ── UI CONSTANTS ──────────────────────────────────────────────────────────────
INPUT_MAX_CHARS: int = 2000
INPUT_WARN_THRESHOLD: int = 1800
AUTO_SELECT_LABEL: str = "⚡ Auto (CIPHER Selects)"

TARGET_SELECTION_GUIDE: str = """
Select the best target:
- Claude: Code/Technical.
- ChatGPT: Conversational.
- Midjourney/Flux: Cinematic art.
- DALL-E 3: Products.
- Gemini (Imagen 3): Typography/Banners.
"""