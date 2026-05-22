import pytest
from engine.cognitive_map import (
    _normalize,
    detect_arabic_pattern,
    get_cipher_injection,
    get_anti_pattern,
    get_full_cipher_block
)

def test_normalize_removes_diacritics():
    """Ensure Tashkeel (harakat) are stripped completely."""
    raw = "بِالتَّفْصِيلِ"
    assert _normalize(raw) == "بالتفصيل"

def test_normalize_standardizes_letters():
    """Ensure Alefs, Taa Marbutas, and Alif Maqsuras are normalized for matching."""
    raw = "أإآةى"
    assert _normalize(raw) == "اااهي"

def test_detect_pattern_positive_match():
    """Ensure a standard trigger word correctly identifies the rhetorical paradigm."""
    result = detect_arabic_pattern("أريد الشرح بالتفصيل من فضلك")
    
    assert result is not None
    assert result["pattern"] == "التفصيل بعد الإجمال"
    assert result["is_negated"] is False
    assert "التفصيل بعد الإجمال" in result["cipher_injection"]

def test_detect_pattern_negated_match():
    """Ensure a negation word within 15 characters before the trigger flags the constraint."""
    # "بدون" is a negation anchor, "تفاصيل" (normalized from بالتفصيل/تفاصيل triggers) 
    # Let's use a direct match for the trigger "بالتفصيل"
    result = detect_arabic_pattern("أريد ذلك لكن ليس بالتفصيل")
    
    assert result is not None
    assert result["pattern"] == "التفصيل بعد الإجمال"
    assert result["is_negated"] is True
    assert "CRITICAL NEGATIVE CONSTRAINT" in result["prompt_instruction"]
    assert "NEGATION ACTIVE" in result["cipher_injection"]

def test_detect_pattern_no_match():
    """Ensure irrelevant text returns None safely."""
    result = detect_arabic_pattern("مرحبا، كيف حالك اليوم؟")
    assert result is None

def test_multiple_triggers_tiebreaker():
    """Ensure the engine picks the pattern with the most hits if multiple are present."""
    # "بالتفصيل" (التفصيل بعد الإجمال) x1
    # "خطوه بخطوه" (التدرج) x2
    text = "اشرح بالتفصيل لكن أريد ذلك خطوه بخطوه، نعم خطوه بخطوه"
    result = detect_arabic_pattern(text)
    
    assert result is not None
    assert result["pattern"] == "التدرج"

def test_get_cipher_injection_and_anti_pattern():
    """Ensure helper functions return the correct strings from the map."""
    injection = get_cipher_injection("الإيجاز")
    anti = get_anti_pattern("الإيجاز")
    
    assert "الإيجاز" in injection
    assert "brevity" in anti

def test_get_full_cipher_block_active():
    """Ensure the final block is formatted correctly for an active injection."""
    detected = detect_arabic_pattern("اشرح بالتفصيل")
    block = get_full_cipher_block(detected)
    
    assert "[ COGNITIVE_MAP_INJECTION" in block
    assert "STATUS: ACTIVE" in block
    assert "ANTI_PATTERN_GUARD" in block

def test_get_full_cipher_block_negated():
    """Ensure the final block is formatted correctly for a negated injection."""
    detected = detect_arabic_pattern("ليس بالتفصيل")
    block = get_full_cipher_block(detected)
    
    assert "STATUS: NEGATED — ACTIVE AVOIDANCE" in block
