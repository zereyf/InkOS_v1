"""
state.py — Session State Contract
===================================
v20.5: Master Sync — Neural Core Edition.
       RESTORED: K.HISTORY to prevent Sidebar AttributeError.
"""

import uuid
import hashlib
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import streamlit as st


class K:
    # ── ENGINE & HISTORY (RESTORED) ──────────────────────────────────────────
    HISTORY         = "prompt_history"  # 🟢 RESTORED
    
    # ── IDENTITY & SECURITY ──────────────────────────────────────────────────
    USER_HASH       = "user_hash"
    USER_PIN        = "user_pin"
    FAILED_ATTEMPTS = "failed_attempts"
    LOCKOUT_UNTIL   = "lockout_until"
    SECURITY_LOG    = "security_log"
    TIMESTAMPS      = "call_timestamps"
    
    # ── HUD METRICS ─────────────────────────────────────────────────
    LAST_RESULT     = "last_result"
    LAST_AUDIT      = "last_audit"
    LAST_INPUT      = "last_input"
    LAST_PATTERN    = "last_pattern"
    LAST_SAVED      = "last_saved"      
    AUTO_TARGET     = "auto_target"      
    AUTO_REASON     = "auto_reason"      
    ATHAR_TRACE     = "athar_trace"     
    
    # ── FORGE & VAULT ────────────────────────────────────────────────────────
    ACTIVE_PERSONA  = "active_persona"
    PERSONA_LIST    = "persona_list"
    VAULT_SEARCH    = "vault_search"
    VAULT_STATS     = "vault_stats"
    
    # ── ADVANCED DNA KEYS (The AmeerInk Trifecta) ───────────────────────────
    INK_DNA         = "ink_dna"          
    INTEL_DNA       = "intel_dna"        
    HIKMAH_DNA      = "hikmah_dna"       

    # ── APP CONFIG ───────────────────────────────────────────────────────────
    UI_LANG         = "ui_lang"          
    APP_CONFIG      = "app_config"
    BOOT_COMPLETE   = "boot_complete"


_DEFAULTS: dict = {
    K.HISTORY:         [],              # 🟢 RESTORED
    K.USER_HASH:       None,
    K.USER_PIN:        None,
    K.FAILED_ATTEMPTS: 0,
    K.LOCKOUT_UNTIL:   None,
    K.SECURITY_LOG:    [],
    K.TIMESTAMPS:      [],
    
    K.LAST_RESULT:     None,
    K.LAST_AUDIT:      {},              
    K.LAST_INPUT:      "",
    K.LAST_PATTERN:    {},              
    K.LAST_SAVED:      "Never",
    K.AUTO_TARGET:     "ChatGPT",        
    K.AUTO_REASON:     "Awaiting Uplink...", 
    K.ATHAR_TRACE:     False,           
    
    K.ACTIVE_PERSONA:  None,
    K.PERSONA_LIST:    [],
    K.VAULT_SEARCH:    "",
    K.VAULT_STATS:     {},
    
    K.UI_LANG:         "en",
    K.APP_CONFIG:      None,
    K.BOOT_COMPLETE:   False,


# for profile 
    PROMPT_COUNT = "prompt_count",
    OPERATOR_NAME = "operator_name",
    SHOW_PROFILE = "show_profile",
    BOOT_TIME = "boot_time",
    CYCLES = "cycles",

    # 🧪 DNA INITIALIZATION (AmeerInk Defaults)
    K.INK_DNA: (
        "ROLE: Creative Director. AESTHETIC: Chiaroscuro lighting, tech-noir minimalist vibes. "
        "COLOR: Obsidian and Gold. STYLE: High-contrast digital photography, 8k resolution. "
        "IDENTITY: AmeerInk Brand (حبر وفكرة)."
    ),
    K.INTEL_DNA: (
        "ROLE: Tech Observer. FOCUS: AI trends, Cybersecurity, and Tech News. "
        "METHOD: Forensic analysis of tech shifts and authoritative insights. "
        "TONE: Critical, sharp, and highly analytical."
    ),
    K.HIKMAH_DNA: (
        "ROLE: Academic Scholar. FOCUS: Arabic Linguistics (Balagha, Nahw) & Islamic Ethics. "
        "METHOD: High-fidelity pedagogical clarity with evidence-based logic. "
        "TONE: Reverent, objective, and deeply scholarly."
    ),
}


def init_session_state() -> None:
    """Idempotent initialization of the Neural Core."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(default)


def reset_session() -> None:
    """Nuclear reset: flushes processing state but preserves DNA and Identity."""
    preserved = {
        K.USER_HASH:       st.session_state.get(K.USER_HASH),
        K.USER_PIN:        st.session_state.get(K.USER_PIN),
        K.INK_DNA:         st.session_state.get(K.INK_DNA),
        K.INTEL_DNA:       st.session_state.get(K.INTEL_DNA),
        K.HIKMAH_DNA:      st.session_state.get(K.HIKMAH_DNA),
        K.PERSONA_LIST:    st.session_state.get(K.PERSONA_LIST, []),
        K.UI_LANG:         st.session_state.get(K.UI_LANG, "en"),
        K.LAST_SAVED:      st.session_state.get(K.LAST_SAVED, "Never"),
    }
    
    st.session_state.clear()
    init_session_state()
    
    for key, value in preserved.items():
        if value is not None:
            st.session_state[key] = value


def get_remaining_calls(window_seconds: int = 60, max_calls: int = 10) -> int:
    """Forensic rate limiting calculator."""
    now = datetime.now(timezone.utc)
    timestamps = st.session_state.get(K.TIMESTAMPS) or []
    valid_timestamps = [
        t for t in timestamps
        if t > now - timedelta(seconds=window_seconds)
    ]
    st.session_state[K.TIMESTAMPS] = valid_timestamps
    return max(0, max_calls - len(valid_timestamps))


def record_api_call() -> None:
    """Log secure uplink action."""
    if K.TIMESTAMPS not in st.session_state:
        st.session_state[K.TIMESTAMPS] = []
    st.session_state[K.TIMESTAMPS].append(datetime.now(timezone.utc))
