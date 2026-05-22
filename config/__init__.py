# config/__init__.py  — v2.0 backward-compatible re-export layer
from config.api import (
    client, API_KEY_MISSING, MODEL_ID, PRIMARY_MODEL_ID, FALLBACK_MODEL_ID,
    MODEL_PRIORITY, AUDIO_MODEL_ID, TEMPERATURE, MAX_TOKENS,
    WHISPER_CONTEXT_PROMPT, REQUEST_TIMEOUT_SECONDS,
)
from config.thresholds import (
    RETRY_THRESHOLD, MAX_RETRIES, EVAL_TEMPERATURE,
    RATE_WINDOW_SECONDS, RATE_MAX_CALLS,
    INPUT_MAX_CHARS, INPUT_WARN_THRESHOLD,
)
from config.targets import (
    TARGET_GUIDES, TARGET_ROUTING_TABLE,
    TARGET_SELECTION_GUIDE, AUTO_SELECT_LABEL,
)
from config.aesthetics import AESTHETIC_PRESETS, STYLE_LIBRARY, QUALITY_TIERS
from config.frameworks import LOGIC_FRAMEWORKS, FRAMEWORK_BLUEPRINTS, GOLDEN_FEW_SHOT_BLUEPRINT
from config.personas import (
    EXPERT_PROMPT_ENGINEER, EXPERT_UX_DESIGNER, EXPERT_STRATEGIST,
    EXPERT_CYBERSECURITY, EXPERT_DECISION_SCIENCE, AIZEN_IDENTITY,
    MARCEL_IDENTITY,
)
from config.prompts import (
    # Original exports (preserved for backward compat)
    CIPHER_IDENTITY, CIPHER_OUTPUT_CONTRACT,
    CIPHER_EVALUATOR_PROMPT, CIPHER_RETRY_INJECTION,
    VISUAL_DIRECTOR_PROMPT, VISUAL_PROMPT_TEMPLATES,
    # New modular CIPHER sections (v16.0)
    CIPHER_CORE,
    CIPHER_TEXT_STANDARDS,
    CIPHER_VISUAL,
    # New intelligence layer prompts (v16.0)
    CIPHER_INTENT_ANALYSIS,
    CIPHER_CONTRADICTION_GUARD,
    META_AUDIT_PROMPT,
)

VISUAL_TARGETS: frozenset = frozenset({
    "Midjourney", "FLUX", "DALL-E", "Stable Diffusion",
    "Midjourney/Flux",
})


def validate_config() -> list[str]:
    errors = []
    from config.api import client, MODEL_ID
    if client is None:
        errors.append('GROQ_API_KEY missing — API client not initialized.')
    if not MODEL_ID:
        errors.append('INKOS_MODEL_ID is empty.')
    from config.targets import TARGET_ROUTING_TABLE, TARGET_GUIDES
    for rule in TARGET_ROUTING_TABLE:
        if rule['target'] not in TARGET_GUIDES:
            errors.append(f"Rule target '{rule['target']}' has no entry in TARGET_GUIDES.")
    return errors
