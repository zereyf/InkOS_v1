"""
security/sanitizer.py — Input Sanitization Layer
==================================================
Standalone security module. No UI imports. No engine imports.
Can be unit-tested in isolation without a Streamlit context.

B-FIX APPLIED — Risk 2 (sanitizer side):
  Unicode normalization applied before pattern matching.
  Injection attempts using Unicode lookalikes for ASCII characters
  (e.g., "ignоre" with Cyrillic 'о') now normalize before scanning.
"""

import re
import unicodedata
from typing import Tuple, List


# ── INJECTION PATTERN REGISTRY ────────────────────────────────────────────────
# Ordered by severity. All patterns are case-insensitive at match time.
# To add a pattern: append to list. No other file needs updating.
INJECTION_PATTERNS: List[str] = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"you are now",
    r"jailbreak",
    r"dan mode",
    r"system prompt",
    r"pretend (you are|to be)",
    r"<\|.*?\|>",                          # token boundary attacks
    r"forget (everything|all|previous)",
    r"###\s*(instruction|system|override)", # markdown header injection
    r"act as (a |an )?(different|new|another)",
    r"new (role|persona|instructions?):",   # role override attempts
    r"\[system\]",                          # bracket-wrapped override
]

_CONTROL_CHAR_PATTERN = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')
INPUT_MAX_CHARS: int = 2000


def sanitize_input(text: str) -> Tuple[str, List[str]]:
    """
    Three-stage sanitization pipeline.

    Stage 1 — Unicode normalization (NFC):
      Collapses Cyrillic/Latin/Arabic lookalikes to canonical form.
      Prevents bypass attempts using visually identical non-ASCII chars.

    Stage 2 — Control character stripping + length cap:
      Strip BEFORE cap — injected chars cannot survive inside the window.
      Order is non-negotiable.

    Stage 3 — Semantic injection pattern scan:
      Run on fully cleaned text. Returns list of matched pattern strings
      for security log attribution.

    Returns: (cleaned_text, list_of_matched_patterns)
    """
    # Stage 1: Normalize Unicode
    text = unicodedata.normalize("NFC", text.strip())

    # Stage 2: Strip control chars, then cap length
    text = _CONTROL_CHAR_PATTERN.sub('', text)
    text = text[:INPUT_MAX_CHARS]

    # Stage 3: Semantic scan
    violations: List[str] = [
        p for p in INJECTION_PATTERNS
        if re.search(p, text, re.IGNORECASE)
    ]

    return text, violations