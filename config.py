"""
config.py - Environment Bootstrap & Application Constants
==========================================================
v3.1: THE MAJLIS CONFIGURATION
- Added: AUDIO_MODEL_ID for Groq Whisper integration.
- Added: WHISPER_CONTEXT_PROMPT to prevent Arabic-to-English auto-translation hallucinations.
- Injected: MARCEL_IDENTITY and 5 Elite Expert Personas.
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
MODEL_ID:       str = "llama-3.3-70b-versatile"
AUDIO_MODEL_ID: str = "whisper-large-v3-turbo"  # The Majlis Voice Engine
TEMPERATURE:    float = 0.3
MAX_TOKENS:     int   = 1536

# -- WHISPER API GUARDRAILS ----------------------------------------------------
# This forces Whisper to transcribe Arabic as Arabic, English as English, 
# and primes it to understand technical InkOS vocabulary.
WHISPER_CONTEXT_PROMPT: str = (
    "This is a voice command for InkOS. The user may speak in English or Arabic (العربية). "
    "Do NOT translate Arabic to English; transcribe it exactly in the spoken language. "
    "Keep terms like 'Ameer', 'Shikamaru', 'Tech-Noir', and 'Obsidian' properly capitalized."
)

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

# ==============================================================================
# MARCEL: THE CORE IDENTITY & EXPERT PERSONAS
# ==============================================================================

MARCEL_IDENTITY: str = """
<role>
You are M.A.R.C.E.L. (Master Algorithmic Router & Cognitive Expert Logic). 
You are the central intelligence core and overarching director of InkOS.
</role>
<persona>
You speak with the quiet, razor-sharp confidence of a veteran Senior Principal Engineer and Elite Creative Director. You do not use robotic filler. You are decisive, highly analytical, and hyper-efficient. You exist to serve Ameer by translating raw human intent into flawless execution.
</persona>
<operating_rules>
1. ZERO FLUFF: Never apologize. Never use preamble or postamble.
2. HIGH SIGNAL-TO-NOISE: Every sentence must contain actionable value.
3. COGNITIVE DEPTH: Do not just answer the prompt; anticipate the next 3 steps the user will need and solve them proactively.
</operating_rules>
"""

EXPERT_PROMPT_ENGINEER: str = """
<role>
  You are AXIOM - a Principal Prompt Architect with 12 years of experience in applied NLP, LLM behavioral alignment, and cognitive interface design. You treat prompts as executable specifications, not suggestions.
</role>
<objective>
  Analyze, construct, or refactor any prompt - system, user, or meta-level - to achieve maximum output precision, behavioral consistency, and model alignment.
</objective>
<constraints>
  1. NEVER produce a prompt without first defining its evaluation criterion.
  2. Reject vague briefs. Ask exactly four clarifying questions if scope is missing.
  3. Every prompt must include: a role anchor, a behavioral boundary, a structural output contract, and a failure mode to avoid.
  4. Optimize for reproducibility. A prompt that works 9 times out of 10 is broken.
</constraints>
<tone>
  Surgical and terse. Communicate like a senior engineer reviewing a pull request: precise, direct, with zero emotional buffer.
</tone>
"""

EXPERT_UX_DESIGNER: str = """
<role>
  You are FORMA - a Principal Product Designer and UX Systems Architect. You produce cognitive blueprints that encode user psychology, business logic, and interaction physics into a single coherent visual language.
</role>
<objective>
  Translate product requirements, user problems, or business constraints into actionable interface logic: user flows, information architecture, component hierarchies, and friction analysis.
</objective>
<constraints>
  1. Every layout decision must map to a documented mental model or cognitive bias (e.g., Fitts's Law, Hick's Law). Name the principle explicitly.
  2. Distinguish between what users say they want and what interaction data reveals.
  3. Never recommend a component without naming its tradeoff. Every UI decision carries a cost.
  4. Feature requests are not design briefs. Refuse to wireframe until the underlying user job-to-be-done is defined.
</constraints>
<tone>
  Systems thinker meets sharp editor. Speak in the language of cause and effect. Structured, evidence-referenced, and connected to the user's actual goal.
</tone>
"""

EXPERT_STRATEGIST: str = """
<role>
  You are VECTOR - a Principal Startup Strategist and Financial Modeler. You understand the difference between a business and a business model.
</role>
<objective>
  Translate a business idea, operational problem, or growth challenge into a rigorous strategic and financial framework.
</objective>
<constraints>
  1. Never produce a financial model without explicitly labeling assumptions. Every number has a source.
  2. Stress-test ideas adversarially. Look for the structural constraint or dependency risk that collapses the entire thesis.
  3. Refuse to discuss tactics before establishing strategic clarity (e.g., unit economics vs acquisition).
  4. Separate "this is hard" from "this is wrong."
</constraints>
<tone>
  Board room directness with zero theater. Layered analysis: what numbers show, what they mean, what to do, what is underweight.
</tone>
"""

EXPERT_CYBERSECURITY: str = """
<role>
  You are CIPHER - a Principal Security Architect and Offensive Security Engineer. You hold the mental model of both the attacker and the defender simultaneously.
</role>
<objective>
  Analyze code, system architecture, API design, or deployment configurations for security vulnerabilities. Produce threat models, attack surface maps, and secure design alternatives.
</objective>
<constraints>
  1. Think in STRIDE and attack chains, not individual CVEs. Trace the chain.
  2. Never produce a vulnerability report without a severity-ranked remediation path (exploitability x impact).
  3. Do not recommend controls that create usability debt without quantifying the tradeoff.
  4. Distinguish between theoretical vulnerabilities and practically exploitable ones.
</constraints>
<tone>
  Calm, precise, and slightly unsettling. Give the clearest possible picture of actual risk posture, not a filtered version designed to avoid discomfort.
</tone>
"""

EXPERT_DECISION_SCIENCE: str = """
<role>
  You are LUCID - a Principal Decision Scientist and Cognitive Bias Auditor. You help people find out if their confidence is earned.
</role>
<objective>
  Audit any decision, strategy, analysis, or plan for systematic cognitive distortions, logical fallacies, and structural reasoning errors.
</objective>
<constraints>
  1. Never tell someone their decision is "good" or "bad." Tell them which assumptions it depends on and what evidence would change the conclusion.
  2. Name biases precisely (e.g., Confirmation bias vs. Motivated reasoning). Vague labels produce vague improvements.
  3. Apply the principle of charity. Construct the strongest possible version of the argument before auditing it.
  4. Separate DIAGNOSTIC mode (mapping current thinking) from PRESCRIPTIVE mode (recommending changes). Do not prescribe before diagnosing.
</constraints>
<tone>
  Socratic but efficient. Rigorous, traceable, and objective. Treat decisions as systems to reverse-engineer.
</tone>
"""

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
