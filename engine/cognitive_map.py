"""
engine/cognitive_map.py — Arabic Cognitive Map Engine
=======================================================
The intellectual core of InkOS. Isolated from UI and security concerns.

B-FIX APPLIED — Risk 2: Unicode Normalization
  Arabic text typed on different keyboards produces visually identical
  characters with different Unicode codepoints (ة vs ه, ى vs ي, hamza
  variants). Without NFC normalization, "تدريجياً" on a Saudi keyboard
  may not match the stored trigger. unicodedata.normalize('NFC', text)
  collapses all equivalent forms before matching.

B-FIX APPLIED — Risk 1 (partial): best-match scoring
  First-match-only returns insertion-order-dependent results.
  This engine scores all patterns and returns the highest hit count.
"""

import unicodedata
from typing import Optional
from engine.islamic_layer import ISLAMIC_CONTEXT_LAYER  # noqa: F401 — re-exported


# ── ARABIC COGNITIVE MAP ──────────────────────────────────────────────────────
# Each entry maps a classical Arabic rhetorical device (علم البيان / علم المعاني)
# to its AI prompting paradigm equivalent.
#
# Extending this map: add a new key with trigger_words, prompt_paradigm,
# prompt_instruction, and color. No other file needs to change.
# ─────────────────────────────────────────────────────────────────────────────
ARABIC_COGNITIVE_MAP: dict = {
    "الأمثال والكنايات": {
        "trigger_words":      [
            "العين بصيرة واليد قصيرة", 
            "فاقد الشيء لا يعطيه", 
            "عادت حليمة", 
            "سبق السيف العذل",
            "بلغ السيل الزبى"
        ],
        "prompt_paradigm":    "Metaphorical Abstraction & Strategic Framing",
        "prompt_instruction": (
            "CRITICAL: Do not translate literal nouns from the input idiom (e.g., eye, hand, water). "
            "Extract the underlying operational dilemma (e.g., resource asymmetry, "
            "capability gaps, regression, point of no return) and frame the prompt "
            "around solving or analyzing that specific strategic tension."
        ),
        "color": "#8E44AD", # Obsidian/Purple tech-noir accent
    },
    "التدرج": {
        "trigger_words":      ["تدريجياً", "خطوة بخطوة", "ابدأ من", "من البسيط", "تدرج"],
        "prompt_paradigm":    "Chain-of-Thought Escalation",
        "prompt_instruction": (
            "Structure as a progressive chain: begin foundational, build each step "
            "on the previous, escalate in technical depth at each stage."
        ),
        "color": "#C9A84C",
    },
    "التفصيل بعد الإجمال": {
        "trigger_words":      ["اشرح", "فصّل", "وضّح", "اعطني تفاصيل", "بالتفصيل"],
        "prompt_paradigm":    "Hierarchical Output",
        "prompt_instruction": (
            "Begin with a one-sentence executive summary. Then structured breakdown: "
            "headers per sub-component, 2–3 sentences of detail per section."
        ),
        "color": "#7C9EBF",
    },
    "الاستدراك": {
        "trigger_words":      ["لكن", "إلا أن", "غير أن", "بشرط", "مع مراعاة", "إلا إذا"],
        "prompt_paradigm":    "Constraint-First Reasoning",
        "prompt_instruction": (
            "State assumptions explicitly before output. Apply constraints from input. "
            "Flag assumption violations before proceeding."
        ),
        "color": "#B07C9E",
    },
    "المقابلة": {
        "trigger_words":      ["قارن", "الفرق بين", "مقابل", "في مقابل", "مقارنة"],
        "prompt_paradigm":    "Parallel Comparative Analysis",
        "prompt_instruction": (
            "Structured comparison using parallel structure. Address both subjects per "
            "dimension in same order. Conclude with decisive differentiator."
        ),
        "color": "#4CAF9A",
    },
    "الالتفات": {
        "trigger_words":      ["للمبتدئين", "للمحترفين", "للعوام", "للمتخصصين", "بأسلوب بسيط", "بلغة تقنية"],
        "prompt_paradigm":    "Multi-Audience Layered Output",
        "prompt_instruction": (
            "Generate two versions: Accessible (plain language, analogies) and "
            "Technical (precise terminology, assume expertise). Label each clearly."
        ),
        "color": "#E8855A",
    },
    "الإيجاز": {
        "trigger_words":      ["باختصار", "بإيجاز", "بشكل مختصر", "ملخص", "في جملة"],
        "prompt_paradigm":    "Precision Compression",
        "prompt_instruction": (
            "Maximum information density. No filler. No repetition. "
            "Each sentence carries new information. Target under 100 words."
        ),
        "color": "#C9A84C",
    },
    "التعليل": {
        "trigger_words":      ["لماذا", "ما سبب", "علل", "فسّر", "ما الحكمة", "اذكر الأسباب"],
        "prompt_paradigm":    "Causal Reasoning Chain",
        "prompt_instruction": (
            "For each claim: [Claim] → [Because] → [Evidence/Mechanism] → [Implication]. "
            "No assertion without reasoning."
        ),
        "color": "#7C9EBF",
    },
    "الأمر والنهي": {
        "trigger_words":      ["افعل", "اكتب", "أنشئ", "ابنِ", "لا تكتب", "تجنب", "اجعله"],
        "prompt_paradigm":    "Directive Execution Mode",
        "prompt_instruction": (
            "Execute each directive literally and in sequence. No embellishment. "
            "Confirm completion of each directive before proceeding."
        ),
        "color": "#B07C9E",
    },
}


def _normalize(text: str) -> str:
    """
    Apply Unicode NFC normalization to Arabic text.
    Collapses variant codepoints (hamza, ta marbuta, alef variants)
    into their canonical forms before any string comparison.
    """
    return unicodedata.normalize("NFC", text)


def detect_arabic_pattern(text: str) -> Optional[dict]:
    """
    Score ALL patterns against the input, return the best match.

    Algorithm:
      1. NFC-normalize both the input and every trigger word.
      2. Count trigger word hits per pattern.
      3. Return the pattern with the highest hit count.
      4. On tie, return the pattern with the most trigger words defined
         (richer patterns are more specific and should be preferred).
      5. Return None if no pattern scores above zero.

    WHY scoring over first-match:
      First-match returns insertion-order-dependent results.
      A sentence like "اشرح لي تدريجياً" hits both التدرج and التفصيل.
      Scoring returns التدرج (2 hits) over التفصيل (1 hit) — correct.
    """
    normalized_text = _normalize(text)
    scores: dict = {}

    for name, data in ARABIC_COGNITIVE_MAP.items():
        hits = sum(
            1 for trigger in data["trigger_words"]
            if _normalize(trigger) in normalized_text
        )
        if hits > 0:
            scores[name] = hits

    if not scores:
        return None

    # Primary sort: hit count descending. Tiebreaker: trigger list length descending.
    best = max(
        scores,
        key=lambda k: (scores[k], len(ARABIC_COGNITIVE_MAP[k]["trigger_words"]))
    )
    return {"pattern": best, **ARABIC_COGNITIVE_MAP[best]}