"""
security/sanitizer.py — Input Sanitization Layer
==================================================
v4.0: Hardened with NFKC normalization, pre-compiled regex, and synced config.
Standalone security module. No UI imports. No engine imports.
Can be unit-tested in isolation without a Streamlit context.
"""

import re
import unicodedata
from typing import Tuple, List

# Synchronize with global state to prevent truncation drift
try:
    from config import INPUT_MAX_CHARS
except ImportError:
    INPUT_MAX_CHARS = 2000

# ── INJECTION PATTERN REGISTRY ────────────────────────────────────────────────
# Ordered by severity. All patterns are case-insensitive at match time.
# To add a pattern: append to list. No other file needs updating.
_RAW_PATTERNS: List[str] = [
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

# PRE-COMPILATION: Compile once at module load for O(1) execution speed
_COMPILED_PATTERNS = [(p_str, re.compile(p_str, re.IGNORECASE)) for p_str in _RAW_PATTERNS]

_CONTROL_CHAR_PATTERN = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')


def sanitize_input(text: str) -> Tuple[str, List[str]]:
    """
    Three-stage sanitization pipeline.

    Stage 1 — Unicode normalization (NFKC):
      Collapses Cyrillic/Latin/Arabic lookalikes and compatibility font variants 
      (e.g., full-width, mathematical bold) to their canonical ASCII forms.
      Prevents bypass attempts using visually identical non-ASCII chars.

    Stage 2 — Control character stripping + length cap:
      Strip BEFORE cap — injected chars cannot survive inside the window.
      Order is non-negotiable.

    Stage 3 — Semantic injection pattern scan:
      Run on fully cleaned text using pre-compiled regex engine. Returns 
      list of matched pattern strings for security log attribution.

    Returns: (cleaned_text, list_of_matched_patterns)
    """
    if not text:
        return "", []

    # Stage 1: Normalize Unicode (NFKC crushes font-variant injection bypasses)
    text = unicodedata.normalize("NFKC", text.strip())

    # Stage 2: Strip control chars, then cap length
    text = _CONTROL_CHAR_PATTERN.sub('', text)
    text = text[:INPUT_MAX_CHARS]

    # Stage 3: Semantic scan
    violations: List[str] = [
        p_str for p_str, compiled_regex in _COMPILED_PATTERNS
        if compiled_regex.search(text)
    ]

    return text, violations
