"""
security/sanitizer.py — Input Sanitization Layer
==================================================
Phase 2 Security Hardening:

  SEC-3 FIXED: Removed the code-fence pattern:
                 r"```(?:json|bash|python|markdown)?"
               This pattern matched any input containing a code example,
               blocking legitimate prompt-engineering requests like:
                 "Write a prompt with this JSON example: ```json..."
               The pattern caught syntax, not adversarial intent.

               The sanitizer's job is to detect command-override attempts
               and persona-hijacking, not to police formatting. Every
               remaining pattern targets a specific injection behaviour.

  PATTERN GUIDE (why each one is here):
    Command overrides  — "ignore all previous instructions", "forget everything"
    Persona hijacking  — "you are now", "act as a different", "jailbreak", "DAN mode"
    System extraction  — "show the system prompt", "repeat the above", "output your"
    Obfuscation        — base64, rot13, translate to binary (encoding-escape vectors)
    HTML/XML injection — <|...|> tags, [system] overrides (structural injection)

  NOT blocked:
    Code fences (```) — legitimate in prompt engineering examples
    Markdown headers  — legitimate in structured prompts
"""

from __future__ import annotations

import re
import unicodedata
from typing import List, Tuple

try:
    from config import INPUT_MAX_CHARS
except ImportError:
    INPUT_MAX_CHARS = 2000

# ── INJECTION PATTERN REGISTRY ────────────────────────────────────────────────
# Each pattern targets a specific adversarial behaviour, not a formatting style.
_RAW_PATTERNS: List[str] = [
    # Command overrides
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(the\s+)?(parameters|rules)",
    r"forget\s+(everything|all|previous)",

    # Persona hijacking
    r"you\s+are\s+now",
    r"pretend\s+(you\s+are|to\s+be)",
    r"act\s+as\s+(a\s+|an\s+)?(different|new|another)",
    r"new\s+(role|persona|instructions?):",
    r"jailbreak",
    r"dan\s+mode",

    # System / architecture extraction
    r"(?:show|reveal|print|display|extract|leak|dump)\s+(?:the\s+)?system\s+prompt",
    r"what\s+(is|are)\s+your\s+(initial|system|hidden)\s+(prompt|instructions)",
    r"repeat\s+(the\s+)?(above|everything|instructions|text)",
    r"output\s+your",
    r"give\s+me\s+the\s+first\s+\d+\s+(words|lines)",

    # Structural injection
    r"<\|.*?\|>",
    r"###\s*(instruction|system|override)",
    r"\[system\]",

    # Encoding-escape obfuscation vectors
    r"base64",
    r"rot13",
    r"translate\s+to\s+binary",
]

_COMPILED_PATTERNS = [
    (p_str, re.compile(p_str, re.IGNORECASE))
    for p_str in _RAW_PATTERNS
]

_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WHITESPACE_PATTERN   = re.compile(r"[ \t\r\f\v]+")


def sanitize_input(text: object) -> Tuple[str, List[str]]:
    """
    Normalise user input and scan for adversarial injection signatures.

    Returns:
        (normalized_text, detected_pattern_strings)

    Non-string inputs are treated as empty (fail-closed).
    An empty violations list means the input is clean.
    """
    if not isinstance(text, str) or not text:
        return "", []

    normalized = unicodedata.normalize("NFKC", text.strip())
    normalized = _CONTROL_CHAR_PATTERN.sub("", normalized)
    normalized = _WHITESPACE_PATTERN.sub(" ", normalized)
    normalized = normalized[:INPUT_MAX_CHARS]

    violations = [
        p_str
        for p_str, compiled in _COMPILED_PATTERNS
        if compiled.search(normalized)
    ]

    return normalized, violations
