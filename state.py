"""
state.py — Session State Contract
===================================
v10: Added APP_CONFIG key for global routing architecture.
"""

import uuid
import hashlib
import streamlit as st
from datetime import datetime, timedelta


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
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = list(default) if isinstance(default, list) else default
    if st.session_state[K.USER_HASH] is None:
        raw_id = str(uuid.uuid4())
        st.session_state[K.USER_HASH] = hashlib.sha256(raw_id.encode()).hexdigest()[:32]


def reset_session() -> None:
    preserved_hash = st.session_state.get(K.USER_HASH)
    preserved_lang = st.session_state.get(K.UI_LANG, "en")
    for key, default in _DEFAULTS.items():
        st.session_state[key] = list(default) if isinstance(default, list) else default
    st.session_state[K.USER_HASH] = preserved_hash
    st.session_state[K.UI_LANG]   = preserved_lang   # preserve language on reset


def get_remaining_calls(window_seconds: int = 60, max_calls: int = 10) -> int:
    now = datetime.now()
    active = [
        t for t in st.session_state.get(K.TIMESTAMPS, [])
        if t > now - timedelta(seconds=window_seconds)
    ]
    return max(0, max_calls - len(active))
