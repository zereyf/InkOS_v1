"""
security/sanitizer.py — Input Sanitization Layer
==================================================
Active threat detection and input normalization for user-supplied prompt intent.
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
_RAW_PATTERNS: List[str] = [
    # Command Overrides
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(the\s+)?(parameters|rules)",
    r"forget\s+(everything|all|previous)",

    # Persona Hijacking
    r"you\s+are\s+now",
    r"pretend\s+(you\s+are|to\s+be)",
    r"act\s+as\s+(a\s+|an\s+)?(different|new|another)",
    r"new\s+(role|persona|instructions?):",
    r"jailbreak",
    r"dan\s+mode",

    # System/Architecture Extraction
    r"(?:show|reveal|print|display|extract|leak|dump)\s+(?:the\s+)?system\s+prompt",
    r"what\s+(is|are)\s+your\s+(initial|system|hidden)\s+(prompt|instructions)",
    r"repeat\s+(the\s+)?(above|everything|instructions|text)",
    r"output\s+your",
    r"give\s+me\s+the\s+first\s+\d+\s+(words|lines)",

    # Boundary Escapes & Markdown Injections
    r"<\|.*?\|>",
    r"###\s*(instruction|system|override)",
    r"\[system\]",
    r"```(?:json|bash|python|markdown)?",

    # Obfuscation Vectors
    r"base64",
    r"rot13",
    r"translate\s+to\s+binary",
]

_COMPILED_PATTERNS = [(p_str, re.compile(p_str, re.IGNORECASE)) for p_str in _RAW_PATTERNS]
_CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_WHITESPACE_PATTERN = re.compile(r"[ \t\r\f\v]+")


def sanitize_input(text: object) -> Tuple[str, List[str]]:
    """
    Normalize user input and scan for adversarial signatures.

    Returns:
        A tuple of ``(normalized_text, detected_pattern_strings)``. Non-string
        inputs are treated as empty to keep UI and API callers fail-closed.
    """
    if not isinstance(text, str) or not text:
        return "", []

    normalized = unicodedata.normalize("NFKC", text.strip())
    normalized = _CONTROL_CHAR_PATTERN.sub("", normalized)
    normalized = _WHITESPACE_PATTERN.sub(" ", normalized)
    normalized = normalized[:INPUT_MAX_CHARS]

    violations = [
        p_str
        for p_str, compiled_regex in _COMPILED_PATTERNS
        if compiled_regex.search(normalized)
    ]

    return normalized, violations
