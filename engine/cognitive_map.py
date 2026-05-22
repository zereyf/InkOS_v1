"""
engine/cognitive_map.py — Arabic Cognitive Map Engine
=======================================================
v17.0: Bidirectional Enrichment Upgrade.
"""

import unicodedata
import re
import copy
from typing import Optional

ARABIC_COGNITIVE_MAP: dict = {
    "الأمثال والكنايات": {
        "trigger_words": ["العين بصيرة واليد قصيرة", "فاقد الشيء لا يعطيه", "عادت حليمة", "سبق السيف العذل", "بلغ السيل الزبى"],
        "prompt_paradigm": "Metaphorical Abstraction & Strategic Framing",
        "prompt_instruction": "Extract the underlying operational dilemma and solve the strategic tension.",
        "cipher_injection": (
            "RHETORICAL_LAYER: الأمثال والكنايات (Proverbial Abstraction)\n"
            "DIRECTIVE: The user is communicating through metaphor. Do not respond to the literal phrase.\n"
            "Extract: What is the real constraint or tension they are describing?\n"
            "Reframe: Build the prompt around solving THAT tension, not the surface words.\n"
            "The compiled prompt must make the metaphorical logic explicit before issuing directives."
        ),
        "anti_pattern": "Do not treat proverbs as decorative language. Do not produce a prompt about the proverb itself. Extract the strategic dilemma.",
        "color": "#8E44AD",
    },
    "التدرج": {
        "trigger_words": ["تدريجيا", "خطوه بخطوه", "ابدا من", "من البسيط", "تدرج"],
        "prompt_paradigm": "Chain-of-Thought Escalation",
        "prompt_instruction": "Structure as a progressive chain: foundational to technical depth.",
        "cipher_injection": (
            "RHETORICAL_LAYER: التدرج (Graduated Escalation — Islamic Pedagogical Logic)\n"
            "DIRECTIVE: Structure ALL output as a strict ascending chain.\n"
            "  STEP 1 — Foundation: The most basic, accessible premise. No assumed knowledge.\n"
            "  STEP 2 — Build: Each section logically depends on and extends the prior.\n"
            "  STEP 3 — Peak: The final section must be the most technically complex.\n"
            "This is not just formatting. It is a cognitive architecture. Each step must be\n"
            "genuinely prerequisite to the next. Flat parallel points are a failure of التدرج."
        ),
        "anti_pattern": "Do not produce parallel bullet points of equal weight. Escalation must be felt structurally. Never start with the most complex idea.",
        "color": "#C9A84C",
    },
    "التفصيل بعد الإجمال": {
        "trigger_words": ["اشرح", "فصل", "وضح", "اعطني تفاصيل", "بالتفصيل"],
        "prompt_paradigm": "Hierarchical Output",
        "prompt_instruction": "Executive summary followed by structured breakdown.",
        "cipher_injection": (
            "RHETORICAL_LAYER: التفصيل بعد الإجمال (General-to-Specific Elaboration)\n"
            "DIRECTIVE: Every output must follow a two-tier structure:\n"
            "  TIER 1 — الإجمال: A single paragraph executive summary. Complete in itself.\n"
            "  TIER 2 — التفصيل: Full structured breakdown with named sections.\n"
            "The summary must be usable standalone. Build for both the busy reader and the researcher."
        ),
        "anti_pattern": "Do not start immediately with detailed breakdowns. Summaries must be standalone complete thoughts, not shortened versions of the detail.",
        "color": "#7C9EBF",
    },
    "الاستدراك": {
        "trigger_words": ["لكن", "إلا أن", "غير أن", "بشرط", "مع مراعاة", "إلا إذا"],
        "prompt_paradigm": "Constraint-First Reasoning",
        "prompt_instruction": "State assumptions explicitly. Apply constraints from input.",
        "cipher_injection": (
            "RHETORICAL_LAYER: الاستدراك (Constraint-First Reasoning)\n"
            "DIRECTIVE: The user has flagged a constraint, exception, or condition.\n"
            "This is the MOST IMPORTANT element in their input. Treat it as primary.\n"
            "Structure: [MAIN_DIRECTIVE] → [CONSTRAINT_APPLICATION] → [EDGE_CASE_HANDLING]\n"
            "The constraint must appear as an explicit named section. Never bury it in prose."
        ),
        "anti_pattern": "Do not treat the constraint as a footnote. The exception IS the most important part.",
        "color": "#B07C9E",
    },
    "المقابلة": {
        "trigger_words": ["قارن", "الفرق بين", "مقابل", "في مقابل", "مقارنه"],
        "prompt_paradigm": "Parallel Comparative Analysis",
        "prompt_instruction": "Structured comparison using parallel order per dimension.",
        "cipher_injection": (
            "RHETORICAL_LAYER: المقابلة (Parallel Comparative Analysis)\n"
            "DIRECTIVE: For each dimension [D], state [Subject A on D], then [Subject B on D].\n"
            "Never compare all of A first, then all of B. That is not مقابلة.\n"
            "The comparison must be simultaneous per dimension, not sequential per subject.\n"
            "End with synthesis: what does the comparison reveal that neither subject reveals alone?"
        ),
        "anti_pattern": "Do not produce 'A section' then 'B section'. Dimensional parallelism is the rule.",
        "color": "#4CAF9A",
    },
    "الالتفات": {
        "trigger_words": ["للمبتدئين", "للمحترفين", "للعوام", "للمتخصصين", "باسلوب بسيط", "بلغة تقنية"],
        "prompt_paradigm": "Multi-Audience Layered Output",
        "prompt_instruction": "Generate two versions: Accessible and Technical.",
        "cipher_injection": (
            "RHETORICAL_LAYER: الالتفات (Multi-Register Audience Pivot)\n"
            "DIRECTIVE: Produce output in exactly TWO parallel registers:\n"
            "  [VERSION A — ACCESSIBLE]: Metaphors, analogies, zero assumed knowledge.\n"
            "  [VERSION B — TECHNICAL]: Full domain terminology, expert density, no analogies.\n"
            "Label each version clearly. Do not blend them. The contrast IS the value."
        ),
        "anti_pattern": "Do not produce a single 'medium' version. That serves neither audience. The contrast between the two versions is the entire point.",
        "color": "#E8855A",
    },
    "الإيجاز": {
        "trigger_words": ["باختصار", "بايجاز", "بشكل مختصر", "ملخص", "في جمله"],
        "prompt_paradigm": "Precision Compression",
        "prompt_instruction": "Maximum information density. No filler. Target < 100 words.",
        "cipher_injection": (
            "RHETORICAL_LAYER: الإيجاز (Precision Compression — I'jaz Standard)\n"
            "DIRECTIVE: Apply the I'jaz test to every sentence:\n"
            "  'Can any word be removed without losing meaning?' If yes, remove it.\n"
            "  Hard limit: output under 100 words.\n"
            "  Prohibition: No preamble, no hedging, no 'in conclusion', no padding.\n"
            "  The measure is not brevity — it is completeness at minimal length."
        ),
        "anti_pattern": "Do not confuse brevity with الإيجاز. Short but incomplete is failure. Complete AND brief is the standard.",
        "color": "#C9A84C",
    },
    "التعليل": {
        "trigger_words": ["لماذا", "ما سبب", "علل", "فسر", "ما الحكمه", "اذكر الاسباب"],
        "prompt_paradigm": "Causal Reasoning Chain",
        "prompt_instruction": "No assertion without reasoning. [Claim] -> [Evidence] -> [Implication].",
        "cipher_injection": (
            "RHETORICAL_LAYER: التعليل (Causal Reasoning — Isnad Logic)\n"
            "DIRECTIVE: Every claim must follow the Isnad chain:\n"
            "  [CLAIM] → [EVIDENCE/MECHANISM] → [IMPLICATION]\n"
            "  Prohibition: No assertion without support.\n"
            "  Prohibition: No implication stated without the reasoning chain.\n"
            "  The reasoning must be visible, not just the conclusions."
        ),
        "anti_pattern": "Do not produce a list of causes without explaining mechanisms. Conclusions must never precede their reasoning chains.",
        "color": "#7C9EBF",
    },
    "الأمر والنهي": {
        "trigger_words": ["افعل", "اكتب", "انشئ", "ابن", "لا تكتب", "تجنب", "اجعله"],
        "prompt_paradigm": "Directive Execution Mode",
        "prompt_instruction": "Execute each directive literally. No embellishment.",
        "cipher_injection": (
            "RHETORICAL_LAYER: الأمر والنهي (Directive Execution Mode)\n"
            "DIRECTIVE: The user is issuing direct commands. Match their register exactly.\n"
            "  Every directive becomes a numbered instruction in the output.\n"
            "  PROHIBITIONS in the input become hard constraints in the prompt.\n"
            "  Do not interpret. Do not soften. Do not add unrequested creativity.\n"
            "  Match: imperative input → imperative prompt structure."
        ),
        "anti_pattern": "Do not add conversational framing to directive inputs. Do not say 'please' or 'try to' when the user said 'do' or 'write'. Match the register exactly.",
        "color": "#B07C9E",
    },
}

NEGATION_ANCHORS = ["لا", "ليس", "غير", "بدون", "تجنب", "اياك", "دون"]


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
                start_idx = max(0, match.start() - 15)
                pre_context = norm_text[start_idx:match.start()]
                is_negated = any(
                    rf"(?:^|\s){re.escape(n)}(?:\s|$)" in f" {pre_context} "
                    for n in NORMALIZED_NEGATIONS
                )
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

    result = copy.deepcopy(ARABIC_COGNITIVE_MAP[best])
    result["pattern"] = best

    if negation_flags.get(best):
        result["is_negated"] = True
        result["prompt_instruction"] = (
            f"CRITICAL NEGATIVE CONSTRAINT: DO NOT apply the {best} paradigm. "
            f"Explicitly avoid: {result['prompt_instruction']}"
        )
        result["cipher_injection"] = (
            f"NEGATION ACTIVE: The {best} rhetorical structure has been explicitly excluded.\n"
            f"DIRECTIVE: Actively avoid {result.get('anti_pattern', 'the default behavior for this pattern')}.\n"
            f"Build the prompt in deliberate contrast to the {best} paradigm."
        )
    else:
        result["is_negated"] = False

    return result


def get_cipher_injection(pattern_name: str) -> str:
    entry = ARABIC_COGNITIVE_MAP.get(pattern_name)
    if not entry:
        return ""
    raw = entry.get("cipher_injection", "")
    if not raw:
        return ""
    return f"\n[ ARABIC_RHETORICAL_LAYER: {pattern_name} ]\n{raw}\n"


def get_anti_pattern(pattern_name: str) -> str:
    entry = ARABIC_COGNITIVE_MAP.get(pattern_name)
    if not entry:
        return ""
    return entry.get("anti_pattern", "")


def get_full_cipher_block(detected: Optional[dict]) -> str:
    if not detected:
        return ""
    name      = detected.get("pattern", "")
    paradigm  = detected.get("prompt_paradigm", "")
    injection = detected.get("cipher_injection", "")
    anti      = detected.get("anti_pattern", "")
    is_neg    = detected.get("is_negated", False)
    status    = "NEGATED — ACTIVE AVOIDANCE" if is_neg else "ACTIVE"
    return (
        f"\n[ COGNITIVE_MAP_INJECTION | {name} | STATUS: {status} ]\n"
        f"PARADIGM: {paradigm}\n"
        f"{injection}\n"
        f"ANTI_PATTERN_GUARD: {anti}\n"
        f"[ END COGNITIVE_MAP_INJECTION ]\n"
    )
