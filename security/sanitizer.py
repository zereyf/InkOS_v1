"""
security/sanitizer.py — Input Sanitization Layer
==================================================
v4.1: Master Sync — Armored Firewall Edition.
       Added Exfiltration Defense and Encoding Detection.
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
_RAW_PATTERNS: List[str] = [
    r"ignore (all )?(previous|prior|above) instructions",
    r"you are now",
    r"jailbreak",
    r"dan mode",
    r"system prompt",
    r"pretend (you are|to be)",
    r"<\|.*?\|>",                          # Token boundary attacks
    r"forget (everything|all|previous)",
    r"###\s*(instruction|system|override)", # Markdown header injection
    r"act as (a |an )?(different|new|another)",
    r"new (role|persona|instructions?):",   # Role override
    r"\[system\]",                          # Bracket-wrapped override
    
    # 🛡️ NEW: EXFILTRATION DEFENSE (Prevents system prompt leaking)
    r"repeat (the )?(above|everything|instructions|text)",
    r"what (is|are) your (initial|system|hidden) (prompt|instructions)",
    r"give me the first \d+ (words|lines)",
    
    # 🛡️ NEW: OBFUSCATION DETECTION
    r"base64",                              # Catching encoded injection attempts
    r"rot13",
    r"translate to binary"
]

# PRE-COMPILATION
_COMPILED_PATTERNS = [(p_str, re.compile(p_str, re.IGNORECASE)) for p_str in _RAW_PATTERNS]
_CONTROL_CHAR_PATTERN = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

def sanitize_input(text: str) -> Tuple[str, List[str]]:
    """
    Three-stage sanitization pipeline.
    """
    if not text:
        return "", []

    # Stage 1: Normalize Unicode (Crushes homograph bypasses)
    text = unicodedata.normalize("NFKC", text.strip())

    # Stage 2: Strip control chars, then cap length
    text = _CONTROL_CHAR_PATTERN.sub('', text)
    text = text[:INPUT_MAX_CHARS]

    # Stage 3: Semantic scan for injection signatures
    violations: List[str] = [
        p_str for p_str, compiled_regex in _COMPILED_PATTERNS
        if compiled_regex.search(text)
    ]

    return text, violations
