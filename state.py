"""
state.py — Session State Contract
===================================
v15.0: Advanced DNA & Identity Preservation.
       Integrated Muse Trigger, VelvetCodex, and Team Rei tactical data.
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
    USER_PIN       = "user_pin"
    FAILED_ATTEMPTS = "failed_attempts"
    LOCKOUT_UNTIL  = "lockout_until"
    VAULT_SEARCH   = "vault_search"
    VAULT_STATS    = "vault_stats"
    ACTIVE_PERSONA = "active_persona"
    PERSONA_LIST   = "persona_list"
    UI_LANG        = "ui_lang"          
    AUTO_TARGET    = "auto_target"      
    AUTO_REASON    = "auto_reason"      
    APP_CONFIG     = "app_config"
    
    # 🧪 ADVANCED DNA KEYS
    MUSE_DNA       = "muse_dna"         # AmeerInk Visual DNA
    VELVET_DNA     = "velvet_dna"       # Technical Auditing DNA
    REI_DNA        = "rei_dna"          # Team Rei Tactical DNA


_DEFAULTS: dict = {
    K.HISTORY:         [],
    K.TIMESTAMPS:      [],
    K.SECURITY_LOG:    [],
    K.LAST_RESULT:     None,
    K.LAST_AUDIT:      None,
    K.LAST_INPUT:      "",
    K.LAST_PATTERN:    None,
    K.USER_HASH:       None,
    K.USER_PIN:        None,
    K.FAILED_ATTEMPTS: 0,
    K.LOCKOUT_UNTIL:   None,
    K.VAULT_SEARCH:    "",
    K.VAULT_STATS:     {},
    K.ACTIVE_PERSONA:  None,
    K.PERSONA_LIST:    [],
    K.UI_LANG:         "en",
    K.AUTO_TARGET:     None,
    K.AUTO_REASON:     None,
    K.APP_CONFIG:      None,

    # 🧪 INITIALIZING ADVANCED DNA (Forensic Pre-load)
    K.MUSE_DNA: (
        "AESTHETIC: Chiaroscuro lighting, tech-noir cyberpunk vibes, minimalist framing. "
        "COLOR: Obsidian and Gold. STYLE: High-contrast digital photography, 8k resolution, cinematic atmosphere."
    ),
    K.VELVET_DNA: (
        "PROTOCOL: VelvetCodex. FOCUS: Forensic code auditing, security vulnerability detection, "
        "and logical leak analysis. TONE: Authoritative and challenging."
    ),
    K.REI_DNA: (
        "TEAM: Rei. ROSTER: Ascendant (Captain), Emrys (Roam), Dethrine (Gold), Phantom (Exp), Aizen (Mage). "
        "FOCUS: MLBB Meta-strategy and competitive tactical anthems."
    ),
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
    """Nuclear reset: flushes state but preserves Identity and Advanced DNA."""
    # 🛡️ Preserve security and Advanced DNA status during reset
    preserved = {
        K.USER_HASH:       st.session_state.get(K.USER_HASH),
        K.USER_PIN:        st.session_state.get(K.USER_PIN),
        K.UI_LANG:         st.session_state.get(K.UI_LANG, "en"),
        K.FAILED_ATTEMPTS: st.session_state.get(K.FAILED_ATTEMPTS, 0),
        K.LOCKOUT_UNTIL:   st.session_state.get(K.LOCKOUT_UNTIL),
        
        # 🧪 Preserve your personal branding/logic
        K.MUSE_DNA:        st.session_state.get(K.MUSE_DNA),
        K.VELVET_DNA:      st.session_state.get(K.VELVET_DNA),
        K.REI_DNA:         st.session_state.get(K.REI_DNA),
    }
    
    st.session_state.clear()
    
    init_session_state()
    
    # 🛡️ Restore preserved keys
    for key, value in preserved.items():
        if value is not None:
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
