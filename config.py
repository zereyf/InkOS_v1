"""
config.py - Environment Bootstrap & Application Constants
==========================================================
v2.1: The Omni-Expert + UI Restoration Update.
- Restored AESTHETIC_PRESETS, AUTO_SELECT_LABEL, and VISUAL_DIRECTOR_PROMPT.
- Maintains the expansive DOMAIN_KNOWLEDGE dictionary for expert routing.
"""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

# -- API CLIENT ----------------------------------------------------------------
_api_key: str = os.getenv("GROQ_API_KEY", "")
client: Groq = Groq(api_key=_api_key) if _api_key else None  # type: ignore
API_KEY_MISSING: bool = not bool(_api_key)

# -- MODEL CONFIG --------------------------------------------------------------
MODEL_ID:    str = "llama-3.3-70b-versatile"
TEMPERATURE: float = 0.3
MAX_TOKENS:  int   = 1536

# -- RATE LIMITING -------------------------------------------------------------
RATE_WINDOW_SECONDS: int = 60
RATE_MAX_CALLS:      int = 10

# -- QUALITY TIERS -------------------------------------------------------------
QUALITY_TIERS: dict = {
    "standard": [],
    "premium": ["ultra polished rendering", "professional composition"],
    "studio": ["masterpiece quality", "artstation featured", "studio-grade rendering"]
}

# -- STYLE DNA LIBRARY ---------------------------------------------------------
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
    },
    "cinematic_anime": {
        "art_medium": "premium anime cel-shaded illustration",
        "render_type": "high fidelity manga colorization",
        "composition_style": "centered portrait framing",
        "design_language": ["official anime frame", "studio key visual"]
    }
}

# -- DOMAIN KNOWLEDGE (The Omni-Expert Memory) --------------------------------
DOMAIN_KNOWLEDGE: dict = {
    "code_analysis": (
        "Strictly adhere to SOLID principles and DRY code. Provide comprehensive Big-O complexity "
        "analysis for time and space. Enforce robust error handling, edge-case mitigation, and "
        "include production-grade docstrings/type-hints."
    ),
    "text_copy": (
        "Optimize for readability, tone alignment, and persuasive structure. Use strong semantic "
        "HTML/Markdown headers (H1/H2). Eliminate fluff, jargon, and passive voice."
    ),
    "agentic_automation": (
        "Execute as a precise agent workflow. Validate prerequisites before execution. "
        "Explicitly tag tool usage. Provide clear fail-states and validation metrics."
    ),
    "marketing": (
        "Optimize for virality, high-conversion hooks, and psychological triggers (FOMO, curiosity). "
        "Integrate SEO best practices, keyword relevance without stuffing, and hyper-clear Call-to-Actions (CTAs)."
    ),
    "data_analysis": (
        "Provide mathematically rigorous, logic-first explanations. If generating formulas (Excel/SQL), "
        "explain the syntax step-by-step. Focus on efficiency, data cleanliness, and clear visualization strategies."
    ),
    "academic_research": (
        "Maintain a highly objective, scholarly tone. Ensure rigorous synthesis of information, "
        "proper structural flow (Abstract, Methodology, Synthesis), and demand empirical/logical backing. "
        "Eliminate all colloquialisms and conversational filler."
    ),
    "productivity": (
        "Adopt a highly actionable, structured, and motivational tone. Break down massive goals into "
        "atomic, trackable daily habits. Utilize time-blocking, Pomodoro, or Eisenhower matrix principles. "
        "Focus entirely on execution and removing friction."
    )
}

# -- TARGET AI DIALECT GUIDES --------------------------------------------------
TARGET_GUIDES: dict = {
    "Manus AI": "Agentic syntax: chain steps as 'Search -> Analyze -> Output'.",
    "Claude": "Structural syntax: wrap all sections in XML tags.",
    "ChatGPT": "Conversational syntax: open with 'You are a...'",
    "Midjourney/Flux": "Modular visual syntax: [Subject] :: [Environment] :: [Parameters]",
    "DALL-E 3": "Highly descriptive cinematic production briefs in natural language.",
    "Gemini (Imagen 3)": "Spatially explicit 'Spatial Blueprint' mapping out zones and diegetic text."
}

# -- AESTHETIC PRESETS (RESTORED FOR UI) ---------------------------------------
AESTHETIC_PRESETS: dict = {
    "Raw (No Preset)": "Standard AI interpretation. Follow user description literally with no added flavor.",
    "Velvet (Signature)": "Focus: Tech-Noir Minimalism. Palette: Obsidian, Matte Black, Deep Gold (#C9A84C). Lighting: Chiaroscuro, high-contrast, cinematic amber glows.",
    "Scholar (Traditional)": "Focus: Arabic Heritage & Calligraphy. Palette: Sandstone, Emerald, Aged Parchment. Lighting: Natural sunlight, soft organic shadows.",
    "Cyber-Radiant": "Focus: High-energy tech. Palette: Electric Blue, Cyber Lime, Carbon Fiber. Lighting: Volumetric neon, sharp lens flares."
}

# -- LOGIC FRAMEWORKS ----------------------------------------------------------
LOGIC_FRAMEWORKS: list = [
    "Professional (RACE)", 
    "Technical (Zero-Shot)", 
    "Creative (Chain-of-Thought)", 
    "Visual Director"
]

VISUAL_DIRECTOR_PROMPT: str = """
ACTIVE FRAMEWORK: Visual Director (Cognitive Prompt Compiler)
Task: Deconstruct raw concepts into elite, studio-grade prompt architecture.
Instead of treating styles as generic keywords, you must deconstruct them into latent production attributes (Style DNA).
"""

# -- UI CONSTANTS --------------------------------------------------------------
INPUT_MAX_CHARS: int = 2000
INPUT_WARN_THRESHOLD: int = 1800
AUTO_SELECT_LABEL: str = "⚡ Auto (CIPHER Selects)"

TARGET_SELECTION_GUIDE: str = """
Given a raw user input, determine the single best AI target from this list:
- Claude: Best for structured analysis, long-form writing, document creation, coding tasks, research synthesis.
- ChatGPT: Best for conversational tasks, brainstorming, quick rewrites, marketing copy, social media.
- Manus AI: Best for multi-step agentic tasks, web research pipelines, file operations, automation sequences.
- Midjourney/Flux: Best for cinematic art, stylized concepts, high-end tech-noir.
- DALL-E 3: Best for photorealistic scenes, product shots, narrative descriptions.
- Gemini (Imagen 3): Best for precise text rendering, readable typography, brand/logo text, signage.
"""