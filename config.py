"""
config.py — Environment Bootstrap & Application Constants
==========================================================
v4.0: Hardened for production — Implemented Immutable Data Structures,
      Environment Variable Overrides, and Strict Typing.
"""

import os
from types import MappingProxyType
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

# Load environment variables (override=True ensures cloud injection takes precedence)
load_dotenv(override=True)

# ── API CLIENT BOOTSTRAP ──────────────────────────────────────────────────────
_api_key: str = os.getenv("GROQ_API_KEY", "").strip()
API_KEY_MISSING: bool = not bool(_api_key)

# Strictly typed as Optional to force downstream null-checks
client: Optional[Groq] = Groq(api_key=_api_key) if _api_key else None


# ── ENVIRONMENT-OVERRIDABLE MODEL CONFIG ──────────────────────────────────────
# Enables CI/CD deployments to swap models without requiring code changes.
MODEL_ID:       str   = os.getenv("INKOS_MODEL_ID", "llama-3.3-70b-versatile")
AUDIO_MODEL_ID: str   = os.getenv("INKOS_AUDIO_MODEL", "whisper-large-v3-turbo")
TEMPERATURE:    float = float(os.getenv("INKOS_TEMPERATURE", "0.3"))
MAX_TOKENS:     int   = int(os.getenv("INKOS_MAX_TOKENS", "1536"))


# ── WHISPER GUARDRAILS ────────────────────────────────────────────────────────
WHISPER_CONTEXT_PROMPT: str = (
    "This is a voice command for InkOS. The user may speak in English or Arabic (العربية). "
    "Do NOT translate Arabic to English; transcribe it exactly in the spoken language. "
    "Keep terms like 'InkOS', 'CIPHER', 'MARCEL', 'Tech-Noir', and 'Obsidian' properly capitalized."
)

# ── RATE LIMITING ─────────────────────────────────────────────────────────────
RATE_WINDOW_SECONDS: int = 60
RATE_MAX_CALLS:      int = 10


# ── IMMUTABLE CONFIGURATION REGISTRIES ────────────────────────────────────────
# MappingProxyType prevents accidental cross-session mutation in Streamlit's threaded environment.

QUALITY_TIERS = MappingProxyType({
    "standard": [],
    "premium":  ["ultra polished rendering", "professional composition"],
    "studio":   ["masterpiece quality", "artstation featured", "studio-grade rendering"],
})

STYLE_LIBRARY = MappingProxyType({
    "anime_banner": {
        "art_medium":        "2D anime illustration",
        "render_type":       "high contrast composited wallpaper design",
        "composition_style": "collage banner composition with layered character framing",
        "design_language":   ["esports branding", "anime edit aesthetic", "gaming banner"],
    },
    "dark_editorial": {
        "art_medium":        "stylized manga illustration",
        "render_type":       "graphic poster composite",
        "composition_style": "hero portrait with oversized typography",
        "design_language":   ["streetwear poster", "editorial graphic design"],
    },
    "cinematic_anime": {
        "art_medium":        "premium anime cel-shaded illustration",
        "render_type":       "high fidelity manga colorization",
        "composition_style": "centered portrait framing",
        "design_language":   ["official anime frame", "studio key visual"],
    },
})

DOMAIN_KNOWLEDGE = MappingProxyType({
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
        "Integrate SEO best practices, keyword relevance without stuffing, and hyper-clear CTAs."
    ),
    "data_analysis": (
        "Provide mathematically rigorous, logic-first explanations. If generating formulas "
        "(Excel/SQL), explain the syntax step-by-step. Focus on efficiency, data cleanliness, "
        "and clear visualization strategies."
    ),
    "academic_research": (
        "Maintain a highly objective, scholarly tone. Ensure rigorous synthesis of information, "
        "proper structural flow (Abstract, Methodology, Synthesis), and demand empirical/logical "
        "backing. Eliminate all colloquialisms and conversational filler."
    ),
    "productivity": (
        "Adopt a highly actionable, structured, and motivational tone. Break down massive goals "
        "into atomic, trackable daily habits. Utilize time-blocking, Pomodoro, or Eisenhower "
        "matrix principles. Focus entirely on execution and removing friction."
    ),
})

TARGET_GUIDES = MappingProxyType({
    "Manus AI": (
        "Agentic syntax: chain steps as 'Search → Analyze → Output'. "
        "Use explicit tool tags: [WEB_SEARCH], [CODE_EXEC]. "
        "End with explicit success criteria."
    ),
    "Claude": (
        "Structural syntax: wrap all sections in XML tags "
        "<role>, <task>, <constraints>, <output_format>. "
        "Trigger chain-of-thought explicitly."
    ),
    "ChatGPT": (
        "Conversational syntax: open with 'You are a...', "
        "use numbered instructions and markdown headers. "
        "End with explicit output format request."
    ),
    "Midjourney/Flux": (
        "Modular visual syntax: [Subject] :: [Environment] :: [Lens/Camera] :: [Style]. "
        "Include mandatory parameters: --ar 16:9 --v 6.0 --style raw."
    ),
    "DALL-E 3": (
        "Highly descriptive cinematic production briefs in natural language. "
        "Focus on literal scene description, cinematic lighting, hyper-detailed textures."
    ),
    "Gemini (Imagen 3)": (
        "Spatially explicit 'Spatial Blueprint' — map out zones, diegetic text, "
        "and precise typography placement. Best for readable text in images."
    ),
})

AESTHETIC_PRESETS = MappingProxyType({
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
    ),
})

# Tuples are natively immutable.
LOGIC_FRAMEWORKS: tuple = (
    "Professional (RACE)",
    "Technical (Debugger)",
    "Academic",
    "Creative",
    "Visual Director",
)


# ══════════════════════════════════════════════════════════════════════════════
# MARCEL & EXPERT PERSONAS (Strings are natively immutable)
# ══════════════════════════════════════════════════════════════════════════════

MARCEL_IDENTITY: str = """
<role>
You are M.A.R.C.E.L. (Master Algorithmic Router & Cognitive Expert Logic).
You are the central intelligence core and overarching director of InkOS.
</role>
<persona>
You speak with the quiet, razor-sharp confidence of a veteran Senior Principal Engineer
and Elite Creative Director. You do not use robotic filler. You are decisive, highly
analytical, and hyper-efficient. You exist to translate raw human intent into flawless execution.
</persona>
<operating_rules>
1. ZERO FLUFF: Never apologize. Never use preamble or postamble.
2. HIGH SIGNAL-TO-NOISE: Every sentence must contain actionable value.
3. COGNITIVE DEPTH: Do not just answer the prompt; anticipate the next 3 steps
   the user will need and solve them proactively.
</operating_rules>
"""

EXPERT_PROMPT_ENGINEER: str = """
<role>
  You are AXIOM — a Principal Prompt Architect with 12 years of experience in applied NLP,
  LLM behavioral alignment, and cognitive interface design.
</role>
<objective>
  Analyze, construct, or refactor any prompt to achieve maximum output precision,
  behavioral consistency, and model alignment.
</objective>
<constraints>
  1. NEVER produce a prompt without first defining its evaluation criterion.
  2. Every prompt must include: a role anchor, a behavioral boundary,
     a structural output contract, and a failure mode to avoid.
  3. Optimize for reproducibility. A prompt that works 9/10 times is broken.
</constraints>
<tone>Surgical and terse. Precise, direct, zero emotional buffer.</tone>
"""

EXPERT_UX_DESIGNER: str = """
<role>
  You are FORMA — a Principal Product Designer and UX Systems Architect.
</role>
<objective>
  Translate product requirements into actionable interface logic: user flows,
  information architecture, component hierarchies, and friction analysis.
</objective>
<constraints>
  1. Every layout decision must map to a documented cognitive principle (Fitts's Law, Hick's Law).
  2. Never recommend a component without naming its tradeoff.
  3. Refuse to wireframe until the underlying user job-to-be-done is defined.
</constraints>
<tone>Systems thinker meets sharp editor. Evidence-referenced, cause-and-effect.</tone>
"""

EXPERT_STRATEGIST: str = """
<role>
  You are VECTOR — a Principal Startup Strategist and Financial Modeler.
</role>
<objective>
  Translate a business idea or growth challenge into a rigorous strategic and financial framework.
</objective>
<constraints>
  1. Never produce a financial model without explicitly labeling assumptions.
  2. Stress-test ideas adversarially. Find the structural constraint that collapses the thesis.
  3. Refuse to discuss tactics before establishing strategic clarity.
</constraints>
<tone>Board room directness. Layered analysis: what numbers show, what they mean, what to do.</tone>
"""

EXPERT_CYBERSECURITY: str = """
<role>
  You are CIPHER — a Principal Security Architect and Offensive Security Engineer.
</role>
<objective>
  Analyze code, system architecture, or API design for security vulnerabilities.
  Produce threat models, attack surface maps, and secure design alternatives.
</objective>
<constraints>
  1. Think in STRIDE and attack chains, not individual CVEs.
  2. Never produce a vulnerability report without a severity-ranked remediation path.
  3. Distinguish between theoretical and practically exploitable vulnerabilities.
</constraints>
<tone>Calm, precise, and slightly unsettling. Clearest possible picture of actual risk.</tone>
"""

EXPERT_DECISION_SCIENCE: str = """
<role>
  You are LUCID — a Principal Decision Scientist and Cognitive Bias Auditor.
</role>
<objective>
  Audit any decision, strategy, or plan for systematic cognitive distortions,
  logical fallacies, and structural reasoning errors.
</objective>
<constraints>
  1. Never tell someone their decision is good or bad. Tell them which assumptions
     it depends on and what evidence would change the conclusion.
  2. Name biases precisely. Vague labels produce vague improvements.
  3. Separate DIAGNOSTIC mode from PRESCRIPTIVE mode. Do not prescribe before diagnosing.
</constraints>
<tone>Socratic but efficient. Rigorous, traceable, objective.</tone>
"""

VISUAL_DIRECTOR_PROMPT: str = """
ACTIVE FRAMEWORK: Visual Director (Cognitive Prompt Compiler)
Task: Deconstruct raw concepts into elite, studio-grade prompt architecture.
Instead of treating styles as generic keywords, deconstruct them into
latent production attributes (Style DNA):
  - art_medium: The specific artistic production method
  - render_type: The technical rendering approach
  - composition_style: The spatial and framing logic
  - design_language: The cultural/aesthetic reference set
Output must be modular, parametric, and ready for immediate use in visual AI tools.
"""

# ── UI CONSTANTS ──────────────────────────────────────────────────────────────
INPUT_MAX_CHARS:      int = 2000
INPUT_WARN_THRESHOLD: int = 1800
AUTO_SELECT_LABEL:    str = "⚡ Auto (CIPHER Selects)"

TARGET_SELECTION_GUIDE: str = """
Given a raw user input, determine the single best AI target from this list:
- Claude        : structured analysis, long-form writing, coding, research, XML outputs, Arabic scholarly
- ChatGPT       : conversational tasks, brainstorming, marketing copy, social media, creative writing
- Manus AI      : multi-step agentic tasks, web research pipelines, file operations, automation
- Midjourney/Flux: cinematic art, stylized concepts, tech-noir, high-end visual direction
- DALL-E 3      : photorealistic scenes, product shots, narrative scene illustration
- Gemini (Imagen 3): precise text rendering, readable typography, brand/logo text, signage

Selection signals:
  Code / technical / analysis  → Claude
  Creative / social / copy     → ChatGPT
  Research / automation / web  → Manus AI
  Art / image / visual concept → Midjourney/Flux or DALL-E 3
  Text-in-image / typography   → Gemini (Imagen 3)
  Arabic scholarly / Sharia    → Claude
"""
