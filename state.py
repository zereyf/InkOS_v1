"""
state.py — Session State Contract
===================================
v12: Integrated URL-based Identity Latching and Volatile State Detection.
"""

import uuid
import hashlib
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import streamlit as st


class K:
    HISTORY        = "prompt_history"
    TIMESTAMPS     = "call_timestamps"
    SECURITY_LOG   = "security_log"
    LAST_RESULT    = "last_result"
    LAST_AUDIT     = "last_audit"
    LAST_INPUT     = "last_input"
    LAST_PATTERN   = "last_pattern"
    USER_HASH      = "user_hash"
    VAULT_SEARCH   = "vault_search"
    VAULT_STATS    = "vault_stats"
    ACTIVE_PERSONA = "active_persona"
    PERSONA_LIST   = "persona_list"
    UI_LANG        = "ui_lang"          # "en" | "ar" | "fr"
    AUTO_TARGET    = "auto_target"      # target selected by CIPHER
    AUTO_REASON    = "auto_reason"      # reason for CIPHER's selection
    APP_CONFIG     = "app_config"       # global sidebar configuration


_DEFAULTS: dict = {
    K.HISTORY:        [],
    K.TIMESTAMPS:     [],
    K.SECURITY_LOG:   [],
    K.LAST_RESULT:    None,
    K.LAST_AUDIT:     None,
    K.LAST_INPUT:     "",
    K.LAST_PATTERN:   None,
    K.USER_HASH:      None,
    K.VAULT_SEARCH:   "",
    K.VAULT_STATS:    {},
    K.ACTIVE_PERSONA: None,
    K.PERSONA_LIST:   [],
    K.UI_LANG:        "en",
    K.AUTO_TARGET:    None,
    K.AUTO_REASON:    None,
    K.APP_CONFIG:     None,
}


def init_session_state() -> None:
    """Idempotent initialization with URL-based Identity Latching."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(default)
            
    # 🔗 IDENTITY LATCHING LOGIC
    if st.session_state.get(K.USER_HASH) is None:
        # Check URL for existing Session ID (sid)
        url_sid = st.query_params.get("sid")

        if url_sid:
            # Latch onto the ID found in the URL
            st.session_state[K.USER_HASH] = url_sid
        else:
            # Generate a temporary Volatile Guest ID
            raw_id = str(uuid.uuid4())
            guest_suffix = hashlib.sha256(raw_id.encode()).hexdigest()[:8].upper()
            st.session_state[K.USER_HASH] = f"GUEST_{guest_suffix}"


def reset_session() -> None:
    """Nuclear reset: flushes state but preserves the Identity context."""
    preserved_hash = st.session_state.get(K.USER_HASH)
    preserved_lang = st.session_state.get(K.UI_LANG, "en")
    
    st.session_state.clear()
    
    init_session_state()
    st.session_state[K.USER_HASH] = preserved_hash
    st.session_state[K.UI_LANG]   = preserved_lang

    # 🐛 LEVEL 1 FIX: Kill frontend browser ghosting
    st.session_state["ta_input"]            = ""
    st.session_state["refined_output_area"] = ""
    st.session_state["vault_title_input"]   = ""
    st.session_state["vault_tags_input"]    = ""


def get_remaining_calls(window_seconds: int = 60, max_calls: int = 10) -> int:
    """Calculates remaining quota and executes garbage collection on expired timestamps."""
    now = datetime.now(timezone.utc)
    
    valid_timestamps = [
        t for t in st.session_state.get(K.TIMESTAMPS, [])
        if t > now - timedelta(seconds=window_seconds)
    ]
    
    st.session_state[K.TIMESTAMPS] = valid_timestamps
    return max(0, max_calls - len(valid_timestamps))


def record_api_call() -> None:
    """Standardized utility to record a rate-limited action."""
    if K.TIMESTAMPS not in st.session_state:
        st.session_state[K.TIMESTAMPS] = []
    st.session_state[K.TIMESTAMPS].append(datetime.now(timezone.utc))
