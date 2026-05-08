"""
ui/sidebar.py — Sidebar Command Deck
====================================
v12.1: Master Sync — Indentation Repair.
       Fixed SyntaxError on return SidebarConfig.
       Synchronized with v20.4 State Ledger and v2026.4 Master Sync.
"""

import streamlit as st
import json
import textwrap
from datetime import datetime, timedelta, timezone
from typing import TypedDict, Optional

from state import K, get_remaining_calls
from config import TARGET_GUIDES, AESTHETIC_PRESETS, AUTO_SELECT_LABEL, LOGIC_FRAMEWORKS
from forge.persona_engine import STARTER_PERSONAS, get_persona_display_name
from vault.supabase_client import SUPABASE_MISSING
from vault.vault_engine import (
    authenticate_terminal, 
    check_id_availability
)
from i18n.translations import t, set_lang, get_lang, LANGUAGES, is_rtl


class SidebarConfig(TypedDict):
    target_model:     str
    framework:        str
    source_lang:      str
    islamic_mode:     bool
    aesthetic_choice: str
    active_persona:   Optional[dict]
    expert_mode:      bool


def _load_user_personas(user_hash: str) -> list:
    if SUPABASE_MISSING:
        return []
    try:
        from forge.persona_store import list_personas
        personas, _ = list_personas(user_hash, target_filter="All")
        return personas or []
    except Exception:
        return []


def render_language_switcher() -> None:
    current = get_lang()
    cols = st.columns(len(LANGUAGES))
    for i, lang in enumerate(LANGUAGES):
        with cols[i]:
            is_active = lang["code"] == current
            if st.button(
                f"{lang['flag']}",
                key=f"lang_btn_{lang['code']}",
                use_container_width=True,
                help=lang['label'],
                type="primary" if is_active else "secondary"
            ):
                if not is_active:
                    set_lang(lang["code"])
                    st.rerun()


def render_sidebar() -> SidebarConfig:
    """
    🟢 MASTER RENDERER: Indentation-Locked
    """
    with st.sidebar:
        # ── NEURAL LINK STATUS ────────────────────────────────────────────────
        uplink_color = "#A93226" if SUPABASE_MISSING else "#4CAF9A"
        uplink_label = "OFFLINE" if SUPABASE_MISSING else "ACTIVE"
        
        link_html = textwrap.dedent(f"""
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; padding:0 5px;">
                <div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-dim); letter-spacing:1px;">NEURAL_UPLINK</div>
                <div style="display:flex; align-items:center; gap:6px;">
                    <span style="height:6px; width:6px; background:{uplink_color}; border-radius:50%; box-shadow: 0 0 5px {uplink_color};"></span>
                    <span style="font-family:var(--font-m); font-size:0.55rem; color:{uplink_color}; font-weight:bold;">{uplink_label}</span>
                </div>
            </div>
        """)
        st.markdown(link_html, unsafe_allow_html=True)

        # ── WORDMARK ──────────────────────────────────────────────────────────
        wordmark_html = textwrap.dedent(f"""
            <div style="padding:0 0 14px 0; border-bottom:1px solid rgba(255,255,255,0.05); margin-bottom:15px;">
                <div class="vc-wordmark" style="font-size:1.4rem;">⚡ {t('app_name')}</div>
                <div class="vc-wordmark-sub" style="letter-spacing:2px; font-size:0.5rem; color:var(--gold);">حبر وفكرة // INKOS v2026.4</div>
            </div>
        """)
        st.markdown(wordmark_html, unsafe_allow_html=True)

                # ── TERMINAL IDENTITY HUD ─────────────────────────────────────────────
        current_sid = st.session_state.get(K.USER_HASH)
        
        # 🟢 FIXED: Explicitly handle None so the login screen actually appears
        is_guest = not current_sid or "GUEST_" in str(current_sid).upper()
        sess_ref = str(current_sid)[:8] if current_sid else "GHOST_ID"

        st.markdown(f'<div class="vc-header" style="font-size:0.55rem; color:var(--text-muted); margin-top:20px;">SESS_REF: {sess_ref}</div>', unsafe_allow_html=True)

        
         if is_guest:
            new_sid = st.text_input("ID", placeholder="Identity Name", key="sid_input_sidebar", label_visibility="collapsed")
            new_pin = st.text_input("PIN", placeholder="PIN", type="password", key="pin_input_sidebar", label_visibility="collapsed")
            is_new_user = st.toggle("Register New?", value=False, key="is_new_user_toggle")
            
            # 🟢 RESTORED: Real-time ID Scanner
            id_is_valid = True
            if is_new_user and new_sid.strip():
                available, status_msg = check_id_availability(new_sid.strip())
                color = "#4CAF9A" if available else "#E53E3E"
                st.markdown(f"<div style='color:{color}; font-size:0.55rem; font-family:var(--font-m); margin-bottom:8px;'>{status_msg}</div>", unsafe_allow_html=True)
                id_is_valid = available
            
            if st.button("LATCH IDENTITY", use_container_width=True, key="btn_latch_sid"):
                if is_new_user and not id_is_valid:
                    st.error("Cannot latch: ID is unavailable or reserved.")
                elif new_sid.strip() and new_pin.strip():
                    with st.spinner("Uplinking..."):

                        success, error_msg = authenticate_terminal(new_sid.strip(), new_pin.strip(), is_new=is_new_user)
                    
                    if success:
                        st.session_state[K.USER_HASH] = new_sid.strip()
                        st.query_params["sid"] = new_sid.strip()
                        st.rerun()
                    else:
                        st.error(error_msg)
        else:
            st.markdown('<div style="background:rgba(201,168,76,0.05); border:1px solid rgba(201,168,76,0.2); padding:10px; border-radius:3px; margin-bottom:10px; font-size:0.55rem; color:var(--gold); display:flex; align-items:center; gap:8px;">IDENTITY SECURED</div>', unsafe_allow_html=True)
            if st.button("Terminate Latch", use_container_width=True):
                st.session_state[K.USER_HASH] = None 
                st.query_params.clear()
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── LOGIC CONFIGURATION ───────────────────────────────────────────────
        st.subheader(t("logic_config"))
        target_options = [AUTO_SELECT_LABEL] + list(TARGET_GUIDES.keys())
        target_model = st.selectbox("Target Model", options=target_options, key="sb_target")

        framework = st.selectbox(t("logic_framework"), LOGIC_FRAMEWORKS, key="sb_framework")
        source_lang = st.radio("Input Language", ["English", "Arabic (العربية)"], key="sb_lang")

        st.markdown("<hr>", unsafe_allow_html=True)

                # ── PERSONA SELECTOR ──────────────────────────────────────────────────
        st.subheader(t("active_persona", fallback="Active Persona"))
        user_personas = _load_user_personas(st.session_state.get(K.USER_HASH, ""))
        all_names = list(STARTER_PERSONAS.keys()) + [p["name"] for p in user_personas]

        # 🟢 ARMORED: Removed the on_change callback trap. Evaluated synchronously.
        sel_persona = st.selectbox(
            "Persona Select", 
            options=["None"] + all_names, 
            key="sb_persona", 
            label_visibility="collapsed"
        )
        
        # Determine which persona object to lock in
        if sel_persona == "None":
            active_p = None
        elif sel_persona in STARTER_PERSONAS:
            active_p = STARTER_PERSONAS[sel_persona]
        else:
            active_p = next((p for p in user_personas if p["name"] == sel_persona), None)

        # Lock to state
        st.session_state[K.ACTIVE_PERSONA] = active_p

        if active_p:
            st.markdown(f"""
                <div style="background:rgba(201,168,76,0.07); border:1px solid rgba(201,168,76,0.25); padding:8px; border-radius:3px; font-size:0.6rem; color:var(--gold);">
                    <strong>{active_p.get('name','')}</strong><br>
                    <span style="color:var(--text-muted); font-style:italic;">{active_p.get('role','')[:60]}...</span>
                </div>
            """, unsafe_allow_html=True)

        # ── OPTIONS ───────────────────────────────────────────────────────────
        aesthetic_choice = st.selectbox(t("aesthetic_preset"), options=list(AESTHETIC_PRESETS.keys()), key="sb_aesthetic")
        islamic_mode = st.toggle(t("islamic_mode"), value=False, key="sb_islamic")
        expert_mode = st.toggle("Expert Diagnostics", value=False, key="sb_expert")

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── METRICS ───────────────────────────────────────────────────────────
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(t("session_runs", fallback="Runs"), len(st.session_state.get(K.HISTORY, [])))
        with m2:
            st.metric(t("session_remaining", fallback="Calls"), get_remaining_calls())
        with m3:
            st.metric(t("last_saved", fallback="Saved"), st.session_state.get(K.LAST_SAVED, "Never"))

        st.markdown("<hr>", unsafe_allow_html=True)

        if st.button(t("reset_session"), use_container_width=True):
            from state import reset_session
            reset_session()
            st.rerun()

    # 🟢 THE RETURN: Indented by 4 spaces (INSIDE render_sidebar)
    return SidebarConfig(
        target_model     = target_model,
        framework        = framework,
        source_lang      = source_lang,
        islamic_mode     = islamic_mode,
        aesthetic_choice = aesthetic_choice,
        active_persona   = active_p,
        expert_mode      = expert_mode,
    )
