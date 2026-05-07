"""
state.py — Session State Contract
===================================
v1.0: Security Vault Integration (PIN, Failed Attempts, and Lockout Logic).
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
    USER_PIN       = "user_pin"         # 🛡️ NEW: Verified Security PIN
    FAILED_ATTEMPTS = "failed_attempts" # 🛡️ NEW: Counter for Self-Destruct logic
    LOCKOUT_UNTIL  = "lockout_until"    # 🛡️ NEW: Timestamp for system lockout
    VAULT_SEARCH   = "vault_search"
    VAULT_STATS    = "vault_stats"
    ACTIVE_PERSONA = "active_persona"
    PERSONA_LIST   = "persona_list"
    UI_LANG        = "ui_lang"          # "en" | "ar" | "fr"
    AUTO_TARGET    = "auto_target"      # target selected by CIPHER
    AUTO_REASON    = "auto_reason"      # reason for CIPHER's selection
    APP_CONFIG     = "app_config"       # global sidebar configuration


_DEFAULTS: dict = {
    K.HISTORY:         [],
    K.TIMESTAMPS:      [],
    K.SECURITY_LOG:    [],
    K.LAST_RESULT:     None,
    K.LAST_AUDIT:      None,
    K.LAST_INPUT:      "",
    K.LAST_PATTERN:    None,
    K.USER_HASH:       None,
    K.USER_PIN:        None,            # 🛡️ Initialized
    K.FAILED_ATTEMPTS: 0,               # 🛡️ Initialized
    K.LOCKOUT_UNTIL:   None,            # 🛡️ Initialized
    K.VAULT_SEARCH:    "",
    K.VAULT_STATS:     {},
    K.ACTIVE_PERSONA:  None,
    K.PERSONA_LIST:    [],
    K.UI_LANG:         "en",
    K.AUTO_TARGET:     None,
    K.AUTO_REASON:     None,
    K.APP_CONFIG:      None,
}


def init_session_state() -> None:
    """Idempotent initialization with URL-based Identity Latching."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(default)
            
    # 🔗 IDENTITY LATCHING LOGIC
    if st.session_state.get(K.USER_HASH) is None:
        url_sid = st.query_params.get("sid")

        if url_sid:
            st.session_state[K.USER_HASH] = url_sid
        else:
            raw_id = str(uuid.uuid4())
            guest_suffix = hashlib.sha256(raw_id.encode()).hexdigest()[:8].upper()
            st.session_state[K.USER_HASH] = f"GUEST_{guest_suffix}"


def reset_session() -> None:
    """Nuclear reset: flushes state but preserves security context."""
    # 🛡️ Preserve identity and security status during reset
    preserved = {
        K.USER_HASH:       st.session_state.get(K.USER_HASH),
        K.USER_PIN:        st.session_state.get(K.USER_PIN),
        K.UI_LANG:         st.session_state.get(K.UI_LANG, "en"),
        K.FAILED_ATTEMPTS: st.session_state.get(K.FAILED_ATTEMPTS, 0),
        K.LOCKOUT_UNTIL:   st.session_state.get(K.LOCKOUT_UNTIL),
    }
    
    st.session_state.clear()
    
    init_session_state()
    
    # 🛡️ Restore preserved security keys
    for key, value in preserved.items():
        st.session_state[key] = value

    # 🐛 UI Clean-up
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
