"""
engine/cognitive_map.py — Arabic Cognitive Map Engine
=======================================================
v16.0: Linguistic Performance Edition.
       Pre-normalized trigger registry and orthographic variance shielding.
"""

import unicodedata
from typing import Optional
from engine.islamic_layer import ISLAMIC_CONTEXT_LAYER  # noqa: F401

# ── ARABIC COGNITIVE MAP ──────────────────────────────────────────────────────
# (Contents identical to your v15.0 registry)
ARABIC_COGNITIVE_MAP: dict = {
    "الأمثال والكنايات": {
        "trigger_words": ["العين بصيرة واليد قصيرة", "فاقد الشيء لا يعطيه", "عادت حليمة", "سبق السيف العذل", "بلغ السيل الزبى"],
        "prompt_paradigm": "Metaphorical Abstraction & Strategic Framing",
        "prompt_instruction": "Extract the underlying operational dilemma and solve the strategic tension.",
        "color": "#8E44AD",
    },
    "التدرج": {
        "trigger_words": ["تدريجياً", "خطوة بخطوة", "ابدأ من", "من البسيط", "تدرج"],
        "prompt_paradigm": "Chain-of-Thought Escalation",
        "prompt_instruction": "Structure as a progressive chain: foundational to technical depth.",
        "color": "#C9A84C",
    },
    "التفصيل بعد الإجمال": {
        "trigger_words": ["اشرح", "فصّل", "وضّح", "اعطني تفاصيل", "بالتفصيل"],
        "prompt_paradigm": "Hierarchical Output",
        "prompt_instruction": "Executive summary followed by structured breakdown.",
        "color": "#7C9EBF",
    },
    "الاستدراك": {
        "trigger_words": ["لكن", "إلا أن", "غير أن", "بشرط", "مع مراعاة", "إلا إذا"],
        "prompt_paradigm": "Constraint-First Reasoning",
        "prompt_instruction": "State assumptions explicitly. Apply constraints from input.",
        "color": "#B07C9E",
    },
    "المقابلة": {
        "trigger_words": ["قارن", "الفرق بين", "مقابل", "في مقابل", "مقارنة"],
        "prompt_paradigm": "Parallel Comparative Analysis",
        "prompt_instruction": "Structured comparison using parallel order per dimension.",
        "color": "#4CAF9A",
    },
    "الالتفات": {
        "trigger_words": ["للمبتدئين", "للمحترفين", "للعوام", "للمتخصصين", "بأسلوب بسيط", "بلغة تقنية"],
        "prompt_paradigm": "Multi-Audience Layered Output",
        "prompt_instruction": "Generate two versions: Accessible and Technical.",
        "color": "#E8855A",
    },
    "الإيجاز": {
        "trigger_words": ["باختصار", "بإيجاز", "بشكل مختصر", "ملخص", "في جملة"],
        "prompt_paradigm": "Precision Compression",
        "prompt_instruction": "Maximum information density. No filler. Target < 100 words.",
        "color": "#C9A84C",
    },
    "التعليل": {
        "trigger_words": ["لماذا", "ما سبب", "علل", "فسّر", "ما الحكمة", "اذكر الأسباب"],
        "prompt_paradigm": "Causal Reasoning Chain",
        "prompt_instruction": "No assertion without reasoning. [Claim] -> [Evidence] -> [Implication].",
        "color": "#7C9EBF",
    },
    "الأمر والنهي": {
        "trigger_words": ["افعل", "اكتب", "أنشئ", "ابنِ", "لا تكتب", "تجنب", "اجعله"],
        "prompt_paradigm": "Directive Execution Mode",
        "prompt_instruction": "Execute each directive literally. No embellishment.",
        "color": "#B07C9E",
    },
}

# ── LINGUISTIC NORMALIZATION ──────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """
    Apply Unicode NFC and Orthographic normalization.
    Collapses variations of Alef, Ya, and Ta-Marbuta for better matching.
    """
    if not text: return ""
    # NFC Normalization
    text = unicodedata.normalize("NFC", text)
    # Orthographic Normalization
    replacements = {
        "أ": "ا", "إ": "ا", "آ": "ا", # Normalize Alef
        "ة": "ه",                     # Normalize Ta-Marbuta
        "ى": "ي"                      # Normalize Ya
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text

# 🧪 PRE-NORMALIZED REGISTRY: Loaded once at startup to optimize performance
PRE_NORMALIZED_MAP = {
    name: [_normalize(trigger) for trigger in data["trigger_words"]]
    for name, data in ARABIC_COGNITIVE_MAP.items()
}

# ── CORE DETECTION LOGIC ──────────────────────────────────────────────────────

def detect_arabic_pattern(text: str) -> Optional[dict]:
    """
    Scans normalized input against the pre-normalized trigger registry.
    Returns the most contextually relevant pattern based on hit density.
    """
    norm_text = _normalize(text)
    scores: dict = {}

    for name, triggers in PRE_NORMALIZED_MAP.items():
        hits = sum(1 for trigger in triggers if trigger in norm_text)
        if hits > 0:
            scores[name] = hits

    if not scores:
        return None

    # Sort by hits descending, then by trigger density as a tiebreaker
    best = max(
        scores,
        key=lambda k: (scores[k], len(ARABIC_COGNITIVE_MAP[k]["trigger_words"]))
    )
    
    return {"pattern": best, **ARABIC_COGNITIVE_MAP[best]}
