"""
tests/test_state.py
====================
Tests for state.py — the application memory core.

Architecture note: CIPHER pattern functions (store_cipher_pattern,
store_cipher_failure, store_meta_insight, get_best_pattern_for_target)
write to the module-level _API_STATE dict, not to st.session_state.
Tests for those functions use a direct reset fixture, not a Streamlit mock.

init_session_state() writes to st.session_state, so that test patches
Streamlit as before.
"""

import pytest
from unittest.mock import patch

import state
from state import (
    K,
    init_session_state,
    reset_session,
    get_global_memory,
    update_global_memory,
    store_cipher_pattern,
    store_cipher_failure,
    store_meta_insight,
    get_best_pattern_for_target,
)


# ── FIXTURES ──────────────────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def reset_api_state():
    """
    Reset the in-process _API_STATE and _GLOBAL_MEM before every test.
    Prevents state leaking between test runs.
    """
    state._API_STATE[K.CIPHER_PATTERNS] = []
    state._API_STATE[K.CIPHER_FAILURES] = []
    state._API_STATE[K.META_INSIGHTS]   = []
    state._API_STATE[K.LAST_META]       = {}
    state._GLOBAL_MEM.clear()
    yield
    # Teardown: same cleanup
    state._API_STATE[K.CIPHER_PATTERNS] = []
    state._API_STATE[K.CIPHER_FAILURES] = []
    state._API_STATE[K.META_INSIGHTS]   = []
    state._API_STATE[K.LAST_META]       = {}
    state._GLOBAL_MEM.clear()


@pytest.fixture
def mock_st_state():
    """Patches Streamlit's session_state for testing init_session_state()."""
    mock_state = {}
    with patch("state.st") as mock_st:
        mock_st.session_state = mock_state
        yield mock_state


# ── K CLASS ───────────────────────────────────────────────────────────────────

def test_k_has_all_required_constants():
    """Every constant referenced across the codebase must exist in K."""
    required = [
        "USER_HASH", "IS_ADMIN", "SHOW_PROFILE", "BOOT_TIME",
        "UI_LANG", "DARK_MODE",
        "LAST_RESULT", "LAST_AUDIT", "LAST_INPUT", "PROMPT_COUNT", "HISTORY",
        "AUTO_TARGET", "AUTO_REASON",
        "ACTIVE_PERSONA", "PERSONA_LIST", "AESTHETIC_CHOICE", "HIKMAH_STYLE",
        "INK_DNA", "INTEL_DNA", "HIKMAH_DNA",
        "SECURITY_LOG", "QUARANTINE_LOG",
        "CIPHER_PATTERNS", "CIPHER_FAILURES", "META_INSIGHTS", "LAST_META",
    ]
    for name in required:
        assert hasattr(K, name), f"K.{name} is missing"


def test_k_values_are_strings():
    """All K values must be plain strings (used as dict keys)."""
    for attr in [a for a in dir(K) if not a.startswith("_")]:
        val = getattr(K, attr)
        assert isinstance(val, str), f"K.{attr} is {type(val)}, expected str"


def test_k_values_are_unique():
    """No two constants should share the same string value."""
    attrs = [a for a in dir(K) if not a.startswith("_")]
    values = [getattr(K, a) for a in attrs]
    assert len(values) == len(set(values)), "Duplicate values found in K"


# ── INIT SESSION STATE ────────────────────────────────────────────────────────

def test_init_session_state_sets_all_keys(mock_st_state):
    """init_session_state() must populate every K constant as a key."""
    init_session_state()

    k_values = {getattr(K, a) for a in dir(K) if not a.startswith("_")}
    for key in k_values:
        assert key in mock_st_state, f"Key '{key}' missing after init_session_state()"


def test_init_session_state_is_idempotent(mock_st_state):
    """Calling init_session_state() twice must not overwrite existing values."""
    init_session_state()
    mock_st_state[K.USER_HASH] = "existing_user"
    mock_st_state[K.PROMPT_COUNT] = 99

    init_session_state()

    assert mock_st_state[K.USER_HASH] == "existing_user"
    assert mock_st_state[K.PROMPT_COUNT] == 99


def test_init_session_state_defaults(mock_st_state):
    """Verify specific default values are correct."""
    init_session_state()

    assert mock_st_state[K.IS_ADMIN]     is False
    assert mock_st_state[K.SHOW_PROFILE] is False
    assert mock_st_state[K.HISTORY]      == []
    assert mock_st_state[K.PROMPT_COUNT] == 0
    assert mock_st_state[K.AUTO_TARGET]  == "ChatGPT"
    assert mock_st_state[K.UI_LANG]      == "en"
    assert mock_st_state[K.DARK_MODE]    is True


# ── CIPHER PATTERN MEMORY ─────────────────────────────────────────────────────

def test_store_cipher_pattern_sorting_and_limit():
    """Patterns must be sorted highest-score first and capped at 20."""
    for i in range(25):
        store_cipher_pattern("Midjourney", "Visual Director", i, f"instruction {i}")

    patterns = state._API_STATE[K.CIPHER_PATTERNS]

    assert len(patterns) == 20
    assert patterns[0]["score"] == 24
    assert patterns[0]["key_instruction"] == "instruction 24"
    assert patterns[-1]["score"] == 5


def test_store_cipher_pattern_timestamp_present():
    """Each stored pattern must have a timestamp."""
    store_cipher_pattern("Claude", "RACE", 80, "good instruction")

    patterns = state._API_STATE[K.CIPHER_PATTERNS]
    assert len(patterns) == 1
    assert "timestamp" in patterns[0]


def test_store_cipher_pattern_truncates_long_instruction():
    """key_instruction must be capped at 500 characters."""
    long = "A" * 600
    store_cipher_pattern("FLUX", "Creative", 75, long)

    patterns = state._API_STATE[K.CIPHER_PATTERNS]
    assert len(patterns[0]["key_instruction"]) == 500


# ── CIPHER FAILURE MEMORY ─────────────────────────────────────────────────────

def test_store_cipher_failure_limit():
    """Failures must be capped at 10 (keeps the most recent)."""
    for i in range(15):
        store_cipher_failure("FLUX", f"critique {i}", 40)

    failures = state._API_STATE[K.CIPHER_FAILURES]
    assert len(failures) == 10


def test_store_cipher_failure_truncates_critique():
    """Critique strings longer than 300 chars must be truncated."""
    long_critique = "A" * 500
    store_cipher_failure("FLUX", long_critique, 40)

    failures = state._API_STATE[K.CIPHER_FAILURES]
    assert len(failures[0]["critique"]) == 300


# ── META INSIGHTS ─────────────────────────────────────────────────────────────

def test_store_meta_insight_appends_and_updates_last():
    """Insight must appear in META_INSIGHTS and update LAST_META."""
    insight = {
        "pattern_tag": "FORMAT_MISMATCH",
        "weakness":    "Ignored prose paragraphs",
        "score":       85,
    }

    store_meta_insight(insight)

    assert state._API_STATE[K.LAST_META] == insight

    insights = state._API_STATE[K.META_INSIGHTS]
    assert len(insights) == 1
    assert insights[0]["pattern_tag"] == "FORMAT_MISMATCH"
    assert "timestamp" in insights[0]


def test_store_meta_insight_limit():
    """META_INSIGHTS must be capped at 20."""
    for i in range(25):
        store_meta_insight({"pattern_tag": f"TAG_{i}", "score": i})

    assert len(state._API_STATE[K.META_INSIGHTS]) == 20


# ── GET BEST PATTERN ──────────────────────────────────────────────────────────

def test_get_best_pattern_returns_highest_score_for_target():
    """Must return highest-score entry for the requested target only."""
    store_cipher_pattern("ChatGPT", "RACE", 80, "good")
    store_cipher_pattern("ChatGPT", "RACE", 95, "best")
    store_cipher_pattern("Claude",  "RACE", 99, "irrelevant")

    best = get_best_pattern_for_target("ChatGPT")

    assert best is not None
    assert best["score"] == 95
    assert best["key_instruction"] == "best"


def test_get_best_pattern_ignores_other_targets():
    """Must not return patterns from a different target."""
    store_cipher_pattern("Claude", "RACE", 99, "claude best")

    best = get_best_pattern_for_target("ChatGPT")
    assert best is None


def test_get_best_pattern_empty_state():
    """Must return None safely when no patterns exist."""
    result = get_best_pattern_for_target("DALL-E")
    assert result is None


# ── GLOBAL MEMORY ─────────────────────────────────────────────────────────────

def test_update_and_get_global_memory():
    """Basic write/read round-trip."""
    update_global_memory("broadcast", "test message")
    mem = get_global_memory()
    assert mem["broadcast"] == "test message"


def test_update_global_memory_delete_on_none():
    """Passing None as value must remove the key."""
    update_global_memory("broadcast", "something")
    update_global_memory("broadcast", None)
    mem = get_global_memory()
    assert "broadcast" not in mem


def test_get_global_memory_returns_copy():
    """Mutations to the returned dict must not affect internal state."""
    update_global_memory("key", "value")
    mem = get_global_memory()
    mem["key"] = "mutated"

    fresh = get_global_memory()
    assert fresh["key"] == "value"