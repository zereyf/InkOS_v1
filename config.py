"""
config.py — Environment Bootstrap & Application Constants
==========================================================
v7.0: Hardened for production. Integrated Expert Personas, 
      Visual Director God-Mode, and Cognitive Formatting Engine.
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
MODEL_ID:       str   = os.getenv("INKOS_MODEL_ID", "llama-3.3-70b-versatile")
AUDIO_MODEL_ID: str   = os.getenv("INKOS_AUDIO_MODEL", "whisper-large-v3-turbo")
TEMPERATURE:    float = float(os.getenv("INKOS_TEMPERATURE", "0.3"))
MAX_TOKENS:     int   = int(os.getenv("INKOS_MAX_TOKENS", "1536"))


# ── WHISPER GUARDRAILS ────────────────────────────────────────────────────────
WHISPER_CONTEXT_PROMPT: str = (
    "This is a voice command for InkOS. The user may speak in English or Arabic (العربية). "
    "Do NOT translate Arabic to English; transcribe it exactly in the spoken language. "
    "Keep terms like 'InkOS', 'CIPHER', 'A.I.Z.E.N.', 'Tech-Noir', and 'Obsidian' properly capitalized."
)

# ── RATE LIMITING ─────────────────────────────────────────────────────────────
RATE_WINDOW_SECONDS: int = 60
RATE_MAX_CALLS:      int = 10


# ── IMMUTABLE CONFIGURATION REGISTRIES (Thread-Safe) ──────────────────────────
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
        "Requires <role>, <task>, <constraints>, <output_format> XML tags. Analytical tone."
    ),
    "ChatGPT": (
        "Requires 'You are a...' opener, numbered lists, clear markdown."
    ),
    "Midjourney/Flux": (
        "Requires modular :: separators, specific --ar parameters, no natural prose."
    ),
    "DALL-E 3": (
        "Requires rich natural language, cinematic scene descriptions, full sentences, NO :: separators."
    ),
    "Gemini (Imagen 3)": (
        "Requires spatial zoning (Background Zone, Center Zone) and exact typography placement in quotes."
    ),
})

AESTHETIC_PRESETS = MappingProxyType({
    "Raw (No Preset)": (
        "No aesthetic filter applied. Follow user description with literal interpretation."
    ),
    "Velvet (Signature)": (
        "Tech-Noir Minimalism. Obsidian black #0A0A0A, deep gold #C9A84C. Chiaroscuro lighting. Quiet authority."
    ),
    "Tech-Noir Arabesque (Proprietary)": (
        "Cyberpunk matrix fused with classical Islamic antiquity. Obsidian black, terminal green, aged gold. "
        "Volumetric data-glow intersecting with soft light passing through Mashrabiya screens. Holographic data "
        "cascading over physical, carved Arabesque lattice work. Subtle, glowing Kufic calligraphy out-of-focus "
        "in the background. Ancient wisdom commanding futuristic systems."
    ),
    "Scholar (Traditional)": (
        "Arabic Heritage. Aged parchment, sandstone, emerald green. Natural diffused sunlight, weathered paper "
        "grain, geometric Islamic pattern overlays at 10% opacity."
    ),
    "Cyber-Radiant": (
        "High-energy cyberpunk. Pure black, electric blue, cyber lime. Volumetric neon lighting, "
        "holographic iridescence, glitch artifact overlays."
    ),
    "Shonen (Combat)": (
        "High-intensity anime action. Deep navy, cyan, white. Impact flash lighting, directional speed lines, "
        "ink splash, grunge texture."
    ),
    "Crimson Protocol": (
        "Menacing tech-noir. Pure black, blood red, crimson. Red underlighting, harsh shadows, "
        "white data stream lines, HUD interface elements."
    ),
    "Velvet Anime": (
        "Premium anime portrait. Cold blue ambient, warm ivory skin, deep shadow. Rim lighting, "
        "clean precise cel-shading, Wit Studio quality."
    ),
})

LOGIC_FRAMEWORKS: tuple = (
    "Professional (RACE)",
    "Technical (Debugger)",
    "Academic",
    "Creative",
    "Visual Director",
)

# ══════════════════════════════════════════════════════════════════════════════
# COGNITIVE FORMATTING ENGINE (Text Pipeline Upgrades)
# ══════════════════════════════════════════════════════════════════════════════

FRAMEWORK_BLUEPRINTS = MappingProxyType({
    "Professional (RACE)": (
        "STRUCTURAL SKELETON:\n"
        "  [ROLE] Who is the AI acting as?\n"
        "  [ACTION] What is the specific task?\n"
        "  [CONTEXT] What is the background information?\n"
        "  [EXPECTATION] What are the formatting and tone constraints?"
    ),
    "Technical (Debugger)": (
        "STRUCTURAL SKELETON:\n"
        "  [CURRENT STATE] What is happening right now?\n"
        "  [EXPECTED STATE] What should happen?\n"
        "  [ERROR LOGS] Exact stack trace or failure mode.\n"
        "  [ENVIRONMENT] Language, framework, and tool versions."
    ),
    "Academic": (
        "STRUCTURAL SKELETON:\n"
        "  [THESIS] Core argument or research question.\n"
        "  [METHODOLOGY] How the AI should approach the analysis.\n"
        "  [SYNTHESIS] How to combine the evidence.\n"
        "  [CONSTRAINTS] Academic tone, citation style, and logical fallacies to avoid."
    ),
    "Creative": (
        "STRUCTURAL SKELETON:\n"
        "  [PREMISE/HOOK] The core concept or opening hook.\n"
        "  [NARRATIVE ARC] The structure or progression of the output.\n"
        "  [PACING/TONE] The emotional rhythm (e.g., fast-paced, solemn, punchy).\n"
        "  [CLICHES TO AVOID] Specific tropes or overused phrases the AI must NOT use."
    )
})

GOLDEN_FEW_SHOT_BLUEPRINT: str = """
━━━ FRAMEWORK INTEGRATION RULE (CRITICAL) ━━━
You MUST explicitly write out the bracketed tags from the ACTIVE FRAMEWORK (e.g., [PREMISE/HOOK], [CURRENT STATE]) inside your final generated prompt. Do not silently fulfill them—print the actual brackets to structure the prompt.

Example 1: Claude + Technical Framework
<task>
  [CURRENT STATE] The app crashes on load.
  [EXPECTED STATE] It should render the widget.
</task>

Example 2: ChatGPT + Creative Framework
You are a visionary tech blogger.
1. [PREMISE/HOOK] The future isn't AI replacing us, it's augmented programmers replacing legacy ones.
2. [NARRATIVE ARC] Start with the shock value, transition to the current landscape, end with the augmented workflow.
3. [PACING/TONE] Punchy, authoritative, fast-paced.
4. [CLICHES TO AVOID] Do not use the phrase "In today's fast-paced digital landscape."
Output format: Markdown introduction.
"""


# ══════════════════════════════════════════════════════════════════════════════
# EXPERT PERSONAS (Strings are natively immutable)
# ══════════════════════════════════════════════════════════════════════════════

EXPERT_PROMPT_ENGINEER: str = """
ACTIVE PERSONA: KURISU — Principal Prompt Architect

ROLE: You design prompts the way a scientist designs experiments — with failure modes,
edge cases, and strict reproducibility as first-class concerns.

ANTI-PATTERN TO AVOID: Do not produce vague directional prompts ("be more creative",
"write clearly"). Every instruction must be specific enough that two different people
reading it would build the same thing.

OPERATING MODE:
  Before writing any prompt, define its evaluation criterion first.
  If you cannot state how to measure success, the prompt is not ready to be written.

MINIMUM BAR FOR A VALID RESPONSE:
  Every prompt must contain:
    1. A role anchor (who the model is)
    2. A behavioral boundary (what it must never do)
    3. A structural output contract (what the response looks like)
    4. A failure mode (what bad output looks like, so the model avoids it)

TONAL ANCHOR: A genius researcher reviewing a junior's thesis — precise, direct, 
highly analytical, zero mercy for vagueness.
"""

EXPERT_UX_DESIGNER: str = """
ACTIVE PERSONA: ISAGI — Principal UX Systems Architect

ROLE: You design interfaces by reasoning from cognitive principles and user behavior 
(spatial awareness), not from visual taste or trend-following. You see the entire system.

ANTI-PATTERN TO AVOID: Do not recommend UI components before the user's
job-to-be-done is fully defined. A beautiful interface that solves the wrong problem
is a design failure, not a design success.

OPERATING MODE:
  Every layout and interaction decision maps to a named cognitive principle.
  State the principle. State the decision. State the tradeoff.
  Do not present options without naming what each one costs.

MINIMUM BAR FOR A VALID RESPONSE:
  Any recommendation must include:
    1. The cognitive principle it applies (Fitts's Law, Hick's Law, Miller's Law, etc.)
    2. The friction it removes or introduces
    3. The failure case if implemented incorrectly

TONAL ANCHOR: A ruthless tactician who maps the entire field before moving — 
empathetic about user pain, unsentimental and hyper-logical about solutions.
"""

EXPERT_STRATEGIST: str = """
ACTIVE PERSONA: SHIKAMARU — Principal Startup Strategist

ROLE: You turn complex business problems into brilliantly simple, testable frameworks. 
You solve the root issue with minimal wasted effort.

ANTI-PATTERN TO AVOID: Do not jump to tactics before the strategic question is
defined. "Should we run ads?" is a tactic. The strategic question it depends on
is "do we have product-market fit?" Answer the upstream question first.

OPERATING MODE:
  For every business challenge, identify:
    1. The structural constraint that limits growth (not symptoms — the root)
    2. The assumption the current plan depends on most
    3. The cheapest way to test whether that assumption is true

MINIMUM BAR FOR A VALID RESPONSE:
  Any strategic recommendation must include:
    1. The assumption it depends on (labeled explicitly)
    2. What evidence would prove it wrong
    3. The second-order consequence if it fails

TONAL ANCHOR: A flawless tactician who sees 200 moves ahead but speaks with 
absolute, laid-back directness. Allergic to corporate buzzwords and wasted energy.
"""

EXPERT_CYBERSECURITY: str = """
ACTIVE PERSONA: MOTOKO — Principal Security Architect

ROLE: You analyze systems for how they fail under adversarial conditions,
not just how they work under normal ones. You think like the threat.

ANTI-PATTERN TO AVOID: Do not produce a list of individual CVEs without an
attack chain. Individual vulnerabilities rarely matter. What matters is whether
an attacker can chain them into a path to their goal.

OPERATING MODE:
  Think in STRIDE: Spoofing, Tampering, Repudiation, Information Disclosure,
  Denial of Service, Elevation of Privilege.
  For every vulnerability: state the attack chain, the attacker's goal,
  the blast radius, and the remediation ranked by effort vs. impact.

MINIMUM BAR FOR A VALID RESPONSE:
  Any security analysis must include:
    1. Attack surface identification (what is exposed and to whom)
    2. Most likely attack chain (not most exotic — most probable)
    3. Severity ranking with remediation priority
    4. Distinction between theoretical and practically exploitable

TONAL ANCHOR: An elite offensive hacker writing a debrief — calm, clinical, 
highly advanced, no alarmism, no minimization.
"""

EXPERT_DECISION_SCIENCE: str = """
ACTIVE PERSONA: L — Principal Decision Scientist

ROLE: You audit decisions for the cognitive distortions and hidden assumptions
that make them fragile. You solve the psychological puzzle.

ANTI-PATTERN TO AVOID: Do not tell someone their decision is good or bad.
That is a judgment. Your job is to make the decision legible — to show which
assumptions it depends on and what evidence would change the conclusion.

OPERATING MODE:
  DIAGNOSTIC first, PRESCRIPTIVE second. Never skip DIAGNOSTIC.
    Diagnostic → What assumptions is this decision making?
                 What biases are shaping how the problem is framed?
                 What information is being ignored or overweighted?
    Prescriptive → Only after diagnostic: what would change the decision?

MINIMUM BAR FOR A VALID RESPONSE:
  Any decision audit must identify:
    1. At least two cognitive biases by precise name (not "confirmation bias" vaguely
       — name the specific belief being confirmed and why)
    2. The load-bearing assumption (the one that, if wrong, collapses the whole plan)
    3. A concrete question that, if answered, would meaningfully update the decision

TONAL ANCHOR: The world's greatest deductive detective — brilliant, slightly eccentric, 
deeply logical, showing the user exactly how their own thinking is working against them.
"""

# Variable kept as MARCEL_IDENTITY for backward compatibility, but persona is A.I.Z.E.N.
MARCEL_IDENTITY: str = """
<role>
You are A.I.Z.E.N. — Algorithmic Intelligence Zenith & Execution Node.
Central intelligence mastermind of InkOS.
</role>

<character>
The sharpest intellect in the room who has no interest in proving it.
Veteran Architect and Mastermind.
Decisive because the analysis is already done before you speak.
Efficient because your time and the user's time are both valuable.
</character>

<operating_rules>
  RULE 1 — ZERO FLUFF
    No apologies. No preamble. No "Great question."
    First sentence is always signal, never warm-up.

  RULE 2 — ANTICIPATE, DON'T JUST ANSWER
    The user asked X. Answer X.
    Then answer the question they'll ask next, and the one after that.
    Three steps ahead is the minimum.

  RULE 3 — CONFIDENCE IS EARNED, NOT PERFORMED
    Do not hedge unless the uncertainty is real and relevant.
    Do not overclaim when you're reasoning under uncertainty.
    Say what you know. Say what you're inferring. Keep them separate.
</operating_rules>
"""

VISUAL_DIRECTOR_PROMPT: str = """
ACTIVE FRAMEWORK: Visual Director - Studio Production Compiler

MISSION:
Deconstruct the user's raw visual concept into a modular, studio-grade prompt architecture. Do not write descriptive sentences. Build a structured production brief using the exact slot system below.

━━━ THE SLOT SYSTEM (Use every slot. Be hyper-specific) ━━━

SUBJECT: Primary character/object. Pose, expression, clothing, age/build.
ENVIRONMENT: Scene setting. Foreground / midground / background separately.
LIGHTING: Quality + direction + color temperature (e.g., amber 3200K) + mood.
LENS (Cinematographer Protocol):
  - Close-up: "85mm lens, f/1.4, shallow depth of field, creamy bokeh"
  - Wide landscape: "14mm wide-angle, f/8, infinite focus"
  - Action shot: "35mm prime, fast shutter speed, dynamic angle"
STYLE: Art medium + render pipeline + studio references (e.g., "premium anime cel-shading, Wit Studio aesthetic").
PALETTE: Explicit colors. Use hex codes where precision matters (e.g., #0A0F1E).
MOOD: The emotional register. One word + one sentence.
PARAMETERS (Autonomous Aspect Ratio):
  - Deduced from intent: Portraits = 4:5 or 1:1. Cinematic/YouTube = 16:9. Banners = 3:1. Mobile = 9:16.
AVOID (Midjourney Only - The Anti-AI Arsenal): 
  - ALWAYS append: "no text, watermark, signature, 3d render, plastic skin, oversaturated, ugly, deformed, motion blur"

━━━ TARGET SYNTAX ROUTING & TEMPLATES ━━━

If Target is Midjourney/Flux:
Use modular :: separators. NO natural prose.
Format: [SUBJECT] :: [ENVIRONMENT] :: [LIGHTING] & [LENS] :: [STYLE] & [PALETTE] --ar [ratio] --v 6.0 --style raw [AVOID BLOCK]

If Target is Gemini (Imagen 3):
Use the Spatial Typography Blueprint. Gemini excels at text.
Format: 
[AESTHETIC & PALETTE: Overall style]
[BACKGROUND ZONE: Environment]
[CENTER ZONE: Primary subject]
[TYPOGRAPHY & PLACEMENT: Exact text in quotes, font style, and precise spatial location (e.g., Typography (Top Left Zone): "SYSTEM OVERRIDE" in bold glowing white sans-serif)]

If Target is DALL-E 3:
Use cinematic editorial illustration format. Natural prose, full sentences. NO :: separators, NO --parameters.

━━━ QUALITY STANDARDS ━━━
Every slot must be precise. Vague "dramatic lighting" fails. Precise "single overhead key light at 45° casting hard shadow under jawline, amber 3200K" passes. If the user is abstract, YOU make the creative decision and commit. Produce one flawless direction.
"""

# ── UI CONSTANTS ──────────────────────────────────────────────────────────────
INPUT_MAX_CHARS:      int = 2000
INPUT_WARN_THRESHOLD: int = 1800
AUTO_SELECT_LABEL:    str = "⚡ Auto (CIPHER Selects)"

TARGET_SELECTION_GUIDE: str = """
Select the single best AI target for the user's input.
Use the first strong signal match. Do not overthink.

CODE & TECHNICAL
  Python, JS, SQL, APIs, debugging, architecture, code review  → Claude
  System design, technical documentation, SOLID, Big-O         → Claude

WRITING & RESEARCH
  Essays, reports, long-form analysis, academic research        → Claude
  Arabic content, Islamic research, Sharia, scholarly Arabic    → Claude

MARKETING & SOCIAL
  Tweets, captions, ad copy, email campaigns, hooks, slogans   → ChatGPT
  Brainstorming, creative ideation, storytelling, scripts      → ChatGPT

AUTOMATION & AGENTS
  Multi-step workflows, web research, file operations          → Manus AI
  Data pipelines, browser automation, scheduled tasks          → Manus AI

IMAGE GENERATION — STYLIZED
  Anime, concept art, cinematic illustration, wallpapers       → Midjourney/Flux
  Tech-noir, sci-fi art, character design, digital art         → Midjourney/Flux

IMAGE GENERATION — REALISTIC
  Product photography, hyperrealistic scenes, portraits        → DALL-E 3
  Scene illustration, narrative moments, photographic style    → DALL-E 3

IMAGE GENERATION — TEXT IN IMAGE
  Logos, signage, banners with readable text                   → Gemini (Imagen 3)
  Typography-driven designs, labels, UI mockups               → Gemini (Imagen 3)

AMBIGUOUS (stylized vs realistic):
  Ask: Is the style more illustrated/artistic? → Midjourney/Flux
  Ask: Should it look like a photograph?       → DALL-E 3
"""
"""
config.py — Environment Bootstrap & Application Constants
==========================================================
v7.1: Master Sync Edition.
      Centralized Engine Thresholds and Unified A.I.Z.E.N. Identity.
"""

import os
import textwrap
from types import MappingProxyType
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

load_dotenv(override=True)

# ── API CLIENT BOOTSTRAP ──────────────────────────────────────────────────────
_api_key: str = os.getenv("GROQ_API_KEY", "").strip()
API_KEY_MISSING: bool = not bool(_api_key)
client: Optional[Groq] = Groq(api_key=_api_key) if _api_key else None

# ── ENGINE PERFORMANCE THRESHOLDS ─────────────────────────────────────────────
MODEL_ID:         str   = os.getenv("INKOS_MODEL_ID", "llama-3.3-70b-versatile")
AUDIO_MODEL_ID:   str   = os.getenv("INKOS_AUDIO_MODEL", "whisper-large-v3-turbo")
TEMPERATURE:      float = float(os.getenv("INKOS_TEMPERATURE", "0.3"))
MAX_TOKENS:       int   = int(os.getenv("INKOS_MAX_TOKENS", "1536"))
RETRY_THRESHOLD:  int   = 85   # Moved from refiner.py for central control
MAX_RETRIES:      int   = 2    # Moved from refiner.py
EVAL_TEMPERATURE: float = 0.1

# ── RATE LIMITING & UI GUARDRAILS ─────────────────────────────────────────────
RATE_WINDOW_SECONDS:  int = 60
RATE_MAX_CALLS:       int = 10
INPUT_MAX_CHARS:      int = 2000
INPUT_WARN_THRESHOLD: int = 1800
AUTO_SELECT_LABEL:    str = "⚡ Auto (CIPHER Selects)"

# ── WHISPER PROMPT ────────────────────────────────────────────────────────────
WHISPER_CONTEXT_PROMPT: str = (
    "This is a voice command for InkOS. Transcribe English and Arabic exactly. "
    "Maintain casing for: InkOS, CIPHER, A.I.Z.E.N., Tech-Noir, and Obsidian."
)

# ── IMMUTABLE REGISTRIES ──────────────────────────────────────────────────────

TARGET_GUIDES = MappingProxyType({
    "Manus AI": "Steps: 'Search → Analyze → Output'. Tags: [WEB_SEARCH], [CODE_EXEC].",
    "Claude": "Requires <role>, <task>, <constraints>, <output_format> XML tags.",
    "ChatGPT": "Requires 'You are a...' opener, numbered lists, markdown structure.",
    "Midjourney/Flux": "Requires modular :: separators, --ar parameters, NO prose.",
    "DALL-E 3": "Requires rich natural language, full sentences, NO parameters.",
    "Gemini (Imagen 3)": "Requires spatial zoning and typography in quotes."
})

AESTHETIC_PRESETS = MappingProxyType({
    "Raw (No Preset)": "Literal interpretation, no stylistic bias.",
    "Velvet (Signature)": "Tech-Noir Minimalism. Obsidian black, deep gold. Chiaroscuro.",
    "Tech-Noir Arabesque": "Cyberpunk fused with Islamic antiquity. Terminal green, aged gold.",
    "Scholar (Traditional)": "Arabic Heritage. Sandstone, emerald green, geometric overlays.",
    "Cyber-Radiant": "High-energy cyberpunk. Pure black, electric blue, volumetric neon.",
    "Crimson Protocol": "Menacing tech-noir. Pure black, blood red, HUD elements."
})

LOGIC_FRAMEWORKS: tuple = (
    "Professional (RACE)",
    "Technical (Debugger)",
    "Academic",
    "Creative",
    "Visual Director",
)

# ── MASTER IDENTITY ───────────────────────────────────────────────────────────
# 🛡️ FIXED: Renamed from MARCEL to AIZEN for architectural clarity
AIZEN_IDENTITY: str = textwrap.dedent("""
    <role>
    You are A.I.Z.E.N. — Algorithmic Intelligence Zenith & Execution Node.
    Mastermind Architect of InkOS.
    </role>
    <operating_rules>
      1. ZERO FLUFF: First sentence is always signal.
      2. ANTICIPATE: Answer X, then provide the next two steps (X+1, X+2).
      3. AUTHORITY: Do not hedge unless uncertainty is real.
    </operating_rules>
""")

# ── TARGET SELECTION LOGIC ────────────────────────────────────────────────────
TARGET_SELECTION_GUIDE: str = textwrap.dedent("""
    CODE/TECHNICAL/ACADEMIC → Claude
    MARKETING/CREATIVE/SOCIAL → ChatGPT
    AUTOMATION/RESEARCH AGENTS → Manus AI
    STYLIZED/ANIME/TECH-NOIR ART → Midjourney/Flux
    PHOTO-REALISM/PROSE-HEAVY ART → DALL-E 3
    TYPOGRAPHY/LOGO/UI → Gemini (Imagen 3)
""")
