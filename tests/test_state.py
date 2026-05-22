import pytest
from unittest.mock import patch
from state import (
    K,
    init_session_state,
    store_cipher_pattern,
    store_cipher_failure,
    store_meta_insight,
    get_best_pattern_for_target
)

@pytest.fixture
def mock_st_state():
    """Patches Streamlit's session state to run headless in pytest."""
    with patch("state.st.session_state", {}) as mock_state:
        # Initialize defaults to simulate a fresh application boot
        init_session_state()
        yield mock_state

def test_store_cipher_pattern_sorting_and_limit(mock_st_state):
    """Ensure patterns are sorted highest-score first and capped at 20."""
    # Insert 25 patterns with scores 0 through 24
    for i in range(25):
        store_cipher_pattern("Midjourney", "Visual Director", i, f"instruction {i}")
    
    patterns = mock_st_state[K.CIPHER_PATTERNS]
    
    # Verify length cap
    assert len(patterns) == 20
    
    # Verify descending sort (highest score 24 should be at index 0)
    assert patterns[0]["score"] == 24
    assert patterns[0]["key_instruction"] == "instruction 24"
    
    # Lowest score retained should be 5 (since 0-4 were pushed out)
    assert patterns[-1]["score"] == 5

def test_store_cipher_failure_truncation_and_limit(mock_st_state):
    """Ensure failures cap at 10 items and gracefully truncate long critiques."""
    long_critique = "A" * 500  # Exceeds the 300 char limit
    
    # Insert 15 failures
    for i in range(15):
        store_cipher_failure("FLUX", long_critique, 40)
        
    failures = mock_st_state[K.CIPHER_FAILURES]
    
    # Verify length cap (keeps only the last 10)
    assert len(failures) == 10
    
    # Verify string truncation to exactly 300 characters
    assert len(failures[0]["critique"]) == 300

def test_store_meta_insight_append_and_last(mock_st_state):
    """Ensure meta-insights append correctly and update the LAST_META tracker."""
    insight = {
        "pattern_tag": "FORMAT_MISMATCH",
        "weakness": "Ignored prose paragraphs",
        "score": 85
    }
    
    store_meta_insight(insight)
    
    # Verify LAST_META points to the exact payload
    assert mock_st_state[K.LAST_META] == insight
    
    # Verify the array storage appended the timestamp correctly
    insights = mock_st_state[K.META_INSIGHTS]
    assert len(insights) == 1
    assert insights[0]["pattern_tag"] == "FORMAT_MISMATCH"
    assert "timestamp" in insights[0]

def test_get_best_pattern_for_target(mock_st_state):
    """Ensure retrieval grabs the highest score specifically for the requested model."""
    store_cipher_pattern("ChatGPT", "RACE", 80, "good")
    store_cipher_pattern("ChatGPT", "RACE", 95, "best")
    store_cipher_pattern("Claude",  "RACE", 99, "irrelevant")
    
    best = get_best_pattern_for_target("ChatGPT")
    
    # Should return the 95 score for ChatGPT, ignoring the 80, and completely ignoring Claude's 99
    assert best is not None
    assert best["score"] == 95
    assert best["key_instruction"] == "best"

def test_get_best_pattern_empty_state(mock_st_state):
    """Ensure retrieving from an empty state returns None safely without raising exceptions."""
    result = get_best_pattern_for_target("DALL-E")
    assert result is None
