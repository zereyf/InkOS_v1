"""
state.py — Session State Contract
===================================
Single source of truth for all Streamlit session state keys.

WHY a typed K class:
  Raw string literals scattered across modules create silent bugs.
  If one module writes st.session_state["last_resut"] (typo) and another
  reads st.session_state["last_result"], the read silently returns None.
  With K.LAST_RESULT as the only reference point, IDEs catch typos at
  write-time, not at runtime in production.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Any


class K:
    """Typed session state key registry. Import K everywhere. Never use raw strings."""
    HISTORY      = "prompt_history"
    TIMESTAMPS   = "call_timestamps"
    SECURITY_LOG = "security_log"
    LAST_RESULT  = "last_result"
    LAST_AUDIT   = "last_audit"
    LAST_INPUT   = "last_input"    # always str, never None
    LAST_PATTERN = "last_pattern"


# Canonical default values — must match types used throughout the app.
_DEFAULTS: dict = {
    K.HISTORY:      [],
    K.TIMESTAMPS:   [],
    K.SECURITY_LOG: [],
    K.LAST_RESULT:  None,
    K.LAST_AUDIT:   None,
    K.LAST_INPUT:   "",    # str not None — prevents len() crash on display
    K.LAST_PATTERN: None,
}


def init_session_state() -> None:
    """
    Idempotent initialization guard.
    Safe to call on every script rerun — only sets keys not yet present.
    Must be called after st.set_page_config() and before any UI rendering.
    """
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            # Deep-copy lists to prevent shared reference bugs across reruns
            st.session_state[key] = list(default) if isinstance(default, list) else default


def reset_session() -> None:
    """
    Hard reset to canonical defaults.
    Preserves type contracts — last_input resets to "" not None.
    Caller is responsible for calling st.rerun() after this.
    """
    for key, default in _DEFAULTS.items():
        st.session_state[key] = list(default) if isinstance(default, list) else default


def get_remaining_calls(window_seconds: int = 60, max_calls: int = 10) -> int:
    """
    Returns remaining rate-limit slots in the current window.
    Used by sidebar metrics — read-only, does not consume slots.
    """
    now = datetime.now()
    active = [
        t for t in st.session_state.get(K.TIMESTAMPS, [])
        if t > now - timedelta(seconds=window_seconds)
    ]
    return max(0, max_calls - len(active))