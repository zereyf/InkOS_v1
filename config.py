"""
config.py — Environment Bootstrap & Application Constants
==========================================================
Updated V7.2: Added Aesthetic Presets, Visual Dialects, and Restored Rate Limits.
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

# ── UI CONSTANTS ──────────────────────────────────────────────────────────────
INPUT_MAX_CHARS: int = 2000
INPUT_WARN_THRESHOLD: int = 1800