"""
ui/sidebar.py — Sidebar Command Deck
====================================
v15.0: Zenith Edition — The Hikmah Refinement.
       - REFACTORED: Replaced 'Islamic Mode' checkbox with 'Hikmah Style' profiles.
       - UPDATED: SidebarConfig TypedDict to support string-based rhetoric.
       - RETAINED: Idempotent IAM and state hardening.
"""

import streamlit as st
import textwrap
from typing import TypedDict, Optional

from state import K, get_remaining_calls
from config import TARGET_GUIDES, AESTHETIC_PRESETS, AUTO_SELECT_LABEL, LOGIC_FRAMEWORKS
from config.personas import STARTER_PERSONAS
from vault.supabase_client import SUPABASE_MISSING
from vault.vault_engine import authenticate_terminal, check_id_availability
from i18n.translations import t, set_lang, get_lang, LANGUAGES

# 🟢 NEW: Import the Rhetoric Profiles from the engine
from forge.rhetoric_engine import HIKMAH_PROFILES

class SidebarConfig(TypedDict):
    target_model:     str
    framework:        str
    source_lang:      str
    hikmah_style:     str # CHANGED: Now a specific style key
    aesthetic_choice: str
    active_persona:   Optional[dict]
    expert_mode:      bool

# ... (Helper functions _load_user_personas, _enforce_admin_clearance remain unchanged)

def render_sidebar() -> SidebarConfig:
    _enforce_admin_clearance()

    current_sid = st.session_state.get(K.USER_HASH)
    is_guest = not current_sid or "GUEST_" in str(current_sid).upper()
    sess_ref = str(current_sid)[:8] if current_sid else "GHOST_ID"

    st.markdown(f'<div class="vc-header" style="font-size:0.55rem; color:var(--text-muted); margin-top:10px;">SESS_REF: {sess_ref}</div>', unsafe_allow_html=True)

    if is_guest:
        # ... (Latch identity logic remains unchanged)
        pass 
    else:
        st.markdown('<div style="background:rgba(201,168,76,0.05); border:1px solid rgba(201,168,76,0.2); padding:10px; border-radius:3px; margin-bottom:10px; font-size:0.55rem; color:var(--gold); display:flex; align-items:center; gap:8px;">[◈] IDENTITY SECURED</div>', unsafe_allow_html=True)
        if st.button("Terminate Latch", use_container_width=True):
            st.session_state[K.USER_HASH] = None 
            st.session_state[K.IS_ADMIN] = False
            st.query_params.clear()
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── LOGIC CONFIGURATION ──
    st.markdown(f'<div class="vc-header" style="margin-top:20px; font-size:0.65rem;">[ {t("logic_config", fallback="LOGIC_CONFIGURATION").upper()} ]</div>', unsafe_allow_html=True)
    
    target_options = [AUTO_SELECT_LABEL] + list(TARGET_GUIDES.keys())
    if "sb_target" not in st.session_state: st.session_state["sb_target"] = AUTO_SELECT_LABEL
    target_model = st.selectbox("Target Model", options=target_options, key="sb_target")

    if "sb_framework" not in st.session_state: st.session_state["sb_framework"] = LOGIC_FRAMEWORKS[0]
    framework = st.selectbox(t("logic_framework", fallback="Framework"), options=LOGIC_FRAMEWORKS, key="sb_framework")

    source_lang = st.radio("Input Language", ["English", "Arabic (العربية)"], key="sb_lang")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── PERSONA SELECTOR ──
    # ... (Persona selector logic remains unchanged)
    # Ensure active_p is defined here for the final return

    # ── SYSTEM TOGGLES ──
    st.markdown("<hr style='margin-top:5px;'>", unsafe_allow_html=True)
    
    aest_options = list(AESTHETIC_PRESETS.keys())
    if "sb_aesthetic" not in st.session_state: st.session_state["sb_aesthetic"] = aest_options[0]
    aesthetic_choice = st.selectbox(t("aesthetic_preset", fallback="Aesthetic"), options=aest_options, key="sb_aesthetic")
    
    # 🟢 REFACTORED: HIKMAH STYLE SELECTOR
    hikmah_options = list(HIKMAH_PROFILES.keys())
    if "sb_hikmah_style" not in st.session_state: st.session_state["sb_hikmah_style"] = "None"
    hikmah_choice = st.selectbox(
        t("hikmah_style", fallback="Hikmah Style"), 
        options=hikmah_options, 
        key="sb_hikmah_style",
        help="Select a rhetorical profile to influence Arabic output quality."
    )
    
    expert_mode = st.checkbox("Expert Diagnostics", value=False, key="sb_expert")

    # ── METRICS ──
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("RUNS", len(st.session_state.get(K.HISTORY, [])))
    with m2:
        st.metric("CALLS", get_remaining_calls())
    with m3:
        st.metric("SAVED", st.session_state.get(K.LAST_SAVED, "Never"))

    st.markdown("<hr>", unsafe_allow_html=True)

    if st.button("RESET SESSION", use_container_width=True):
        from state import reset_session
        reset_session()
        st.rerun()

    return SidebarConfig(
        target_model     = target_model,
        framework        = framework,
        source_lang      = source_lang,
        hikmah_style     = hikmah_choice, # UPDATED
        aesthetic_choice = aesthetic_choice,
        active_persona   = st.session_state.get(K.ACTIVE_PERSONA),
        expert_mode      = expert_mode,
    )
