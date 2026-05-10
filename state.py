"""
state.py — Session State Contract
===================================
v20.7.3: The "Memory Restoration" Patch.
       - RESTORED: get_global_memory for server-wide directives.
       - STABLE: Zenith Neural Keys (DNA, Hikmah, Aesthetic).
       - STABLE: Forensic HUD and Identity anchors.
"""

import streamlit as st
from copy import deepcopy
from datetime import datetime, timedelta, timezone

class K:
    # ── ENGINE & HISTORY ─────────────────────────────────────────────────────
    HISTORY         = "prompt_history"
    
    # ── IDENTITY & SECURITY ──────────────────────────────────────────────────
    USER_HASH       = "user_hash"
    IS_ADMIN        = "is_admin"
    TIMESTAMPS      = "call_timestamps"

    # ── HUD METRICS ─────────────────────────────────────────────────
    LAST_RESULT     = "last_result"    
    LAST_AUDIT      = "last_audit"     
    LAST_INPUT      = "last_input"
    LAST_SAVED      = "last_saved"      
    AUTO_TARGET     = "auto_target"    
    AUTO_REASON     = "auto_reason"    
    
    # ── FORGE & VAULT ────────────────────────────────────────────────────────
    ACTIVE_PERSONA  = "active_persona"
    PERSONA_LIST    = "persona_list"   
    
    # ── BEHAVIORAL KEYS (Hikmah Refinement) ─────────────────────────────
    HIKMAH_STYLE     = "sb_hikmah_style"   
    AESTHETIC_CHOICE = "sb_aesthetic"      
    
    # ── ADVANCED DNA KEYS (The AmeerInk Trifecta) ───────────────────────────
    INK_DNA         = "ink_dna"          
    INTEL_DNA       = "intel_dna"        
    HIKMAH_DNA      = "hikmah_dna"       

_DEFAULTS: dict = {
    K.HISTORY:         [],
    K.USER_HASH:       None,
    K.IS_ADMIN:        False,
    K.TIMESTAMPS:      [],
    
    K.LAST_RESULT:     None,           
    K.LAST_AUDIT:      {},             
    K.LAST_INPUT:      "",
    K.LAST_SAVED:      "Never",
    K.AUTO_TARGET:     "ChatGPT",        
    K.AUTO_REASON:     "Awaiting Uplink...", 
    
    K.ACTIVE_PERSONA:  None,
    K.PERSONA_LIST:    [],             

    K.HIKMAH_STYLE:     "None",      
    K.AESTHETIC_CHOICE: "Default",   
    
    # 🧪 DNA INITIALIZATION (AmeerInk Defaults)
    K.INK_DNA: "ROLE: Creative Director. AESTHETIC: Obsidian and Gold tech-noir.",
    K.INTEL_DNA: "ROLE: Tech Observer. FOCUS: AI and Cybersecurity trends.",
    K.HIKMAH_DNA: "ROLE: Academic Scholar. FOCUS: Arabic Linguistics & Ethics.",
}

# ── 🟢 SHARED SERVER MEMORY (The Missing Link) ──

@st.cache_resource
def get_global_memory() -> dict:
    """Creates a shared memory space across ALL active users on the server."""
    return {
        "broadcast": None,
        "maintenance_mode": False
    }

# ── 🟢 SESSION MANAGEMENT ──

def init_session_state() -> None:
    """Idempotent initialization of the Neural Core."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(default)

def reset_session() -> None:
    """Refined Reset: Preserves Identity anchors but clears history."""
    anchors = [
        K.USER_HASH, K.IS_ADMIN, K.ACTIVE_PERSONA, 
        K.HIKMAH_STYLE, K.AESTHETIC_CHOICE,
        K.INK_DNA, K.INTEL_DNA, K.HIKMAH_DNA,
        K.PERSONA_LIST
    ]
    preserved = {k: st.session_state.get(k) for k in anchors}
    
    st.session_state.clear()
    init_session_state()
    
    for k, v in preserved.items():
        if v is not None:
            st.session_state[k] = v

def get_remaining_calls(window_seconds: int = 60, max_calls: int = 10) -> int:
    """Forensic rate limiting."""
    now = datetime.now(timezone.utc)
    timestamps = st.session_state.get(K.TIMESTAMPS) or []
    valid_timestamps = [t for t in timestamps if t > now - timedelta(seconds=window_seconds)]
    st.session_state[K.TIMESTAMPS] = valid_timestamps
    return max(0, max_calls - len(valid_timestamps))

def record_api_call() -> None:
    """Log secure uplink action."""
    if K.TIMESTAMPS not in st.session_state:
        st.session_state[K.TIMESTAMPS] = []
    st.session_state[K.TIMESTAMPS].append(datetime.now(timezone.utc))
