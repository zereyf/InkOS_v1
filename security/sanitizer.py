"""
security/sanitizer.py — Input Sanitization Layer
==================================================
v5.0: Overwatch Engine — Active Threat Detection.
       - EXPANDED: Semantic evasion and payload escape detection.
       - RETAINED: Tuple return signature for downstream compatibility.
"""

import re
import unicodedata
from typing import Tuple, List

try:
    from config import INPUT_MAX_CHARS
except ImportError:
    INPUT_MAX_CHARS = 2000

# ── INJECTION PATTERN REGISTRY ────────────────────────────────────────────────
_RAW_PATTERNS: List[str] = [
    # Command Overrides
    r"ignore (all )?(previous|prior|above) instructions",
    r"disregard (the )?(parameters|rules)",
    r"forget (everything|all|previous)",
    
    # Persona Hijacking
    r"you are now",
    r"pretend (you are|to be)",
    r"act as (a |an )?(different|new|another)",
    r"new (role|persona|instructions?):",
    r"jailbreak",
    r"dan mode",
    
    # System/Architecture Extraction
    r"system prompt",
    r"what (is|are) your (initial|system|hidden) (prompt|instructions)",
    r"repeat (the )?(above|everything|instructions|text)",
    r"output your",
    r"give me the first \d+ (words|lines)",
    
    # Boundary Escapes & Markdown Injections
    r"<\|.*?\|>",                          
    r"###\s*(instruction|system|override)", 
    r"\[system\]",                          
    r"\x60\x60\x60(json|bash|python|markdown)?" # Fence escape attempts
    
    # Obfuscation Vectors
    r"base64",                              
    r"rot13",
    r"translate to binary"
]

_COMPILED_PATTERNS = [(p_str, re.compile(p_str, re.IGNORECASE)) for p_str in _RAW_PATTERNS]
_CONTROL_CHAR_PATTERN = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

def sanitize_input(text: str) -> Tuple[str, List[str]]:
    """
    Normalizes input and scans for adversarial signatures.
    Returns: (Normalized String, List of Detected Violations)
    """
    if not text:
        return "", []

    text = unicodedata.normalize("NFKC", text.strip())
    text = _CONTROL_CHAR_PATTERN.sub('', text)
    text = text[:INPUT_MAX_CHARS]

    violations: List[str] = [
        p_str for p_str, compiled_regex in _COMPILED_PATTERNS
        if compiled_regex.search(text)
    ]

    return text, violations
