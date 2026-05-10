"""
state.py — Hardened Session Contract
====================================
v21.6: Initialization Integrity Patch.
       - RESTORED: get_global_memory() for app.py maintenance checks.
       - FIXED: KeyError protection on all global accessors.
"""

import streamlit as st
from copy import deepcopy
from datetime import datetime, timedelta, timezone

class K:
    # Logic & History
    HISTORY         = "prompt_history"
    SECURITY_LOG    = "security_log"
    
    # Identity & DNA
    USER_HASH       = "user_hash"
    IS_ADMIN        = "is_admin"
    INK_DNA         = "ink_dna"
    INTEL_DNA       = "intel_dna"
    HIKMAH_DNA      = "hikmah_dna"
    PERSONA_LIST    = "persona_list"
    ACTIVE_PERSONA  = "active_persona"

    # UI & HUD
    LAST_RESULT     = "last_result"
    LAST_AUDIT      = "last_audit"
    LAST_SAVED      = "last_saved"
    AUTO_TARGET     = "auto_target"
    AUTO_REASON     = "auto_reason"
    UI_LANG         = "ui_lang"
    TIMESTAMPS      = "call_timestamps"
    AESTHETIC_CHOICE = "sb_aesthetic"
    HIKMAH_STYLE     = "sb_hikmah_style"

_DEFAULTS = {
    K.HISTORY: [], K.SECURITY_LOG: [], K.USER_HASH: None, K.IS_ADMIN: False,
    K.INK_DNA: "Default", K.INTEL_DNA: "Default", K.HIKMAH_DNA: "Default",
    K.PERSONA_LIST: [], K.ACTIVE_PERSONA: None, K.LAST_RESULT: None,
    K.LAST_AUDIT: {}, K.LAST_SAVED: "Never", K.UI_LANG: "en",
    K.AUTO_TARGET: "ChatGPT", K.AUTO_REASON: "Awaiting Uplink...",
    K.TIMESTAMPS: [], K.AESTHETIC_CHOICE: "Default", K.HIKMAH_STYLE: "None"
}

# ── 🟢 RESTORED: GLOBAL MEMORY ──
@st.cache_resource
def get_global_memory() -> dict:
    """Maintains system-wide state across all user sessions (e.g., Maintenance Mode)."""
    return {
        "broadcast": None,
        "maintenance_mode": False
    }

def init_session_state():
    """Hardened initialization to prevent 'KeyError' during hot-reloading."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(default)

def reset_session():
    """Surgical reset: Wipes transient history but preserves the Latch Identity."""
    preserved = {
        K.USER_HASH: st.session_state.get(K.USER_HASH),
        K.IS_ADMIN: st.session_state.get(K.IS_ADMIN),
        K.INK_DNA: st.session_state.get(K.INK_DNA),
        K.INTEL_DNA: st.session_state.get(K.INTEL_DNA),
        K.HIKMAH_DNA: st.session_state.get(K.HIKMAH_DNA),
        K.PERSONA_LIST: st.session_state.get(K.PERSONA_LIST),
        K.ACTIVE_PERSONA: st.session_state.get(K.ACTIVE_PERSONA)
    }
    st.session_state.clear()
    init_session_state()
    for k, v in preserved.items():
        if v is not None: st.session_state[k] = v

def get_remaining_calls(window: int = 60, max_calls: int = 10) -> int:
    try:
        now = datetime.now(timezone.utc)
        st.session_state[K.TIMESTAMPS] = [t for t in st.session_state.get(K.TIMESTAMPS, []) if t > now - timedelta(seconds=window)]
        return max(0, max_calls - len(st.session_state[K.TIMESTAMPS]))
    except Exception: return 0
