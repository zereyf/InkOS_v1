"""
state.py — Session State Contract
===================================
v20.7.2: Forensic Recovery Patch.
       - RESTORED: LAST_RESULT, LAST_AUDIT, and PERSONA_LIST defaults.
       - UPDATED: reset_session now preserves ACTIVE_PERSONA for identity continuity.
       - RETAINED: Hikmah & Aesthetic DNA rehydration keys.
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
    LAST_RESULT     = "last_result"    # 🟢 RESTORED
    LAST_AUDIT      = "last_audit"     # 🟢 RESTORED
    LAST_SAVED      = "last_saved"      
    
    # ── FORGE & VAULT ────────────────────────────────────────────────────────
    ACTIVE_PERSONA  = "active_persona"
    PERSONA_LIST    = "persona_list"   # 🟢 RESTORED
    
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
    K.IS_ADMIN:         False,
    K.TIMESTAMPS:      [],
    
    K.LAST_RESULT:     None,           # 🟢 INITIALIZED
    K.LAST_AUDIT:      {},             # 🟢 INITIALIZED
    K.LAST_SAVED:      "Never",
    
    K.ACTIVE_PERSONA:  None,
    K.PERSONA_LIST:    [],             # 🟢 INITIALIZED

    K.HIKMAH_STYLE:     "None",      
    K.AESTHETIC_CHOICE: "Default",   
    
    # 🧪 DNA INITIALIZATION (AmeerInk Defaults)
    K.INK_DNA: "ROLE: Creative Director. AESTHETIC: Obsidian and Gold tech-noir.",
    K.INTEL_DNA: "ROLE: Tech Observer. FOCUS: AI and Cybersecurity trends.",
    K.HIKMAH_DNA: "ROLE: Academic Scholar. FOCUS: Arabic Linguistics & Ethics.",
}

def init_session_state() -> None:
    """Idempotent initialization of the Neural Core."""
    for key, default in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = deepcopy(default)

def reset_session() -> None:
    """
    Refined Reset: Flushes transient data while anchoring Identity.
    Preserves DNA, Admin status, and the currently engaged Persona.
    """
    # Define what MUST survive the flush
    anchors = [
        K.USER_HASH, K.IS_ADMIN, K.ACTIVE_PERSONA, 
        K.HIKMAH_STYLE, K.AESTHETIC_CHOICE,
        K.INK_DNA, K.INTEL_DNA, K.HIKMAH_DNA,
        K.PERSONA_LIST
    ]
    
    preserved = {k: st.session_state.get(k) for k in anchors}
    
    st.session_state.clear()
    init_session_state()
    
    # Re-inject preserved values
    for k, v in preserved.items():
        if v is not None:
            st.session_state[k] = v
