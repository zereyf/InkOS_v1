"""
engine/cognitive_map.py — Arabic Cognitive Map Engine
=======================================================
v16.3: Constraint-Inversion Patch.
       - Integrated Tashkeel stripping.
       - Regex-based word boundary protection.
       - Negation-aware instruction rewriting.
"""

import unicodedata
import re
import copy
from typing import Optional

# ── ARABIC COGNITIVE MAP ──────────────────────────────────────────────────────
ARABIC_COGNITIVE_MAP: dict = {
    "الأمثال والكنايات": {
        "trigger_words": ["العين بصيرة واليد قصيرة", "فاقد الشيء لا يعطيه", "عادت حليمة", "سبق السيف العذل", "بلغ السيل الزبى"],
        "prompt_paradigm": "Metaphorical Abstraction & Strategic Framing",
        "prompt_instruction": "Extract the underlying operational dilemma and solve the strategic tension.",
        "color": "#8E44AD",
    },
    "التدرج": {
        "trigger_words": ["تدريجيا", "خطوه بخطوه", "ابدا من", "من البسيط", "تدرج"],
        "prompt_paradigm": "Chain-of-Thought Escalation",
        "prompt_instruction": "Structure as a progressive chain: foundational to technical depth.",
        "color": "#C9A84C",
    },
    "التفصيل بعد الإجمال": {
        "trigger_words": ["اشرح", "فصل", "وضح", "اعطني تفاصيل", "بالتفصيل"],
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
        "trigger_words": ["قارن", "الفرق بين", "مقابل", "في مقابل", "مقارنه"],
        "prompt_paradigm": "Parallel Comparative Analysis",
        "prompt_instruction": "Structured comparison using parallel order per dimension.",
        "color": "#4CAF9A",
    },
    "الالتفات": {
        "trigger_words": ["للمبتدئين", "للمحترفين", "للعوام", "للمتخصصين", "باسلوب بسيط", "بلغة تقنية"],
        "prompt_paradigm": "Multi-Audience Layered Output",
        "prompt_instruction": "Generate two versions: Accessible and Technical.",
        "color": "#E8855A",
    },
    "الإيجاز": {
        "trigger_words": ["باختصار", "بايجاز", "بشكل مختصر", "ملخص", "في جمله"],
        "prompt_paradigm": "Precision Compression",
        "prompt_instruction": "Maximum information density. No filler. Target < 100 words.",
        "color": "#C9A84C",
    },
    "التعليل": {
        "trigger_words": ["لماذا", "ما سبب", "علل", "فسر", "ما الحكمه", "اذكر الاسباب"],
        "prompt_paradigm": "Causal Reasoning Chain",
        "prompt_instruction": "No assertion without reasoning. [Claim] -> [Evidence] -> [Implication].",
        "color": "#7C9EBF",
    },
    "الأمر والنهي": {
        "trigger_words": ["افعل", "اكتب", "انشئ", "ابن", "لا تكتب", "تجنب", "اجعله"],
        "prompt_paradigm": "Directive Execution Mode",
        "prompt_instruction": "Execute each directive literally. No embellishment.",
        "color": "#B07C9E",
    },
}

# ── NEGATION REGISTRY ─────────────────────────────────────────────────────────
NEGATION_ANCHORS = ["لا", "ليس", "غير", "بدون", "تجنب", "اياك", "دون"]

# ── LINGUISTIC NORMALIZATION ──────────────────────────────────────────────────

def _normalize(text: str) -> str:
    if not text: return ""
    text = unicodedata.normalize("NFC", text)
    text = re.sub(r"[\u064B-\u0652]", "", text) 
    replacements = {"أ": "ا", "إ": "ا", "آ": "ا", "ة": "ه", "ى": "ي"}
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.lower().strip()

PRE_NORMALIZED_MAP = {
    name: [_normalize(trigger) for trigger in data["trigger_words"]]
    for name, data in ARABIC_COGNITIVE_MAP.items()
}

NORMALIZED_NEGATIONS = [_normalize(n) for n in NEGATION_ANCHORS]

# ── CORE DETECTION LOGIC ──────────────────────────────────────────────────────

def detect_arabic_pattern(text: str) -> Optional[dict]:
    norm_text = _normalize(text)
    scores: dict = {}
    negation_flags: dict = {}

    for name, triggers in PRE_NORMALIZED_MAP.items():
        count = 0
        for trigger in triggers:
            pattern = rf"(?:^|\s|و|ب|ل){re.escape(trigger)}(?:\s|$)"
            match = re.search(pattern, norm_text)
            
            if match:
                # Check for negation in the 15-char look-back buffer
                start_idx = max(0, match.start() - 15)
                pre_context = norm_text[start_idx:match.start()]
                
                is_negated = any(rf"(?:^|\s){re.escape(n)}(?:\s|$)" in f" {pre_context} " 
                                for n in NORMALIZED_NEGATIONS)
                
                count += 1
                if is_negated:
                    negation_flags[name] = True
        
        if count > 0:
            scores[name] = count

    if not scores:
        return None

    best = max(
        scores,
        key=lambda k: (scores[k], -len(ARABIC_COGNITIVE_MAP[k]["trigger_words"]))
    )
    
    # Clone the data to avoid mutating the global map
    result = copy.deepcopy(ARABIC_COGNITIVE_MAP[best])
    result["pattern"] = best
    
    # 🟢 NEW: Inversion Logic
    if negation_flags.get(best):
        result["is_negated"] = True
        # Dynamically rewrite the instruction as a Negative Constraint
        result["prompt_instruction"] = (
            f"CRITICAL NEGATIVE CONSTRAINT: DO NOT apply the {best} paradigm. "
            f"Explicitly avoid the following behavior: {result['prompt_instruction']}"
        )
    else:
        result["is_negated"] = False
    
    return result
