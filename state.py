import streamlit as st
from copy import deepcopy
from datetime import datetime, timedelta, timezone

class K:
    HISTORY         = "prompt_history"
    USER_HASH       = "user_hash"
    IS_ADMIN        = "is_admin"
    ACTIVE_PERSONA  = "active_persona"
    HIKMAH_STYLE    = "sb_hikmah_style"
    AESTHETIC_CHOICE= "sb_aesthetic"
    INK_DNA         = "ink_dna"
    INTEL_DNA       = "intel_dna"
    HIKMAH_DNA      = "hikmah_dna"
    TIMESTAMPS      = "call_timestamps"
    LAST_SAVED      = "last_saved"

_DEFAULTS = {
    K.HISTORY: [], K.USER_HASH: None, K.IS_ADMIN: False,
    K.ACTIVE_PERSONA: None, K.HIKMAH_STYLE: "None", K.AESTHETIC_CHOICE: "Default",
    K.INK_DNA: "AmeerInk: Obsidian/Gold, Tech-Noir.",
    K.INTEL_DNA: "Tech Observer: AI/Cybersecurity focus.",
    K.HIKMAH_DNA: "Scholar: Arabic Linguistics/Ethics.",
    K.TIMESTAMPS: [], K.LAST_SAVED: "Never"
}

def init_session_state():
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(default)

def reset_session():
    # Preserve Identity and Behavioral DNA
    preserved = {k: st.session_state.get(k) for k in [K.USER_HASH, K.IS_ADMIN, K.HIKMAH_STYLE, K.AESTHETIC_CHOICE, K.INK_DNA, K.INTEL_DNA, K.HIKMAH_DNA]}
    st.session_state.clear()
    init_session_state()
    for k, v in preserved.items():
        if v is not None: st.session_state[k] = v
