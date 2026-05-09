"""
ui/sidebar.py — Sidebar Command Deck
====================================
v13.4: Master Latch Production Build.
       - Fixed NameError by restoring helper functions.
       - Unified Widget Key: 'sb_persona_global_widget'.
       - URL-Param Priority Latch for absolute refresh stability.
"""

import streamlit as st
import json
import textwrap
from datetime import datetime, timezone
from typing import TypedDict, Optional

from state import K, get_remaining_calls
from config import TARGET_GUIDES, AESTHETIC_PRESETS, AUTO_SELECT_LABEL, LOGIC_FRAMEWORKS
from config.personas import STARTER_PERSONAS
from forge.persona_engine import get_persona_display_name
from vault.supabase_client import SUPABASE_MISSING
from vault.vault_engine import (
    authenticate_terminal, 
    check_id_availability
)
from i18n.translations import t, set_lang, get_lang, LANGUAGES


class SidebarConfig(TypedDict):
    target_model:     str
    framework:        str
    source_lang:      str
    islamic_mode:     bool
    aesthetic_choice: str
    active_persona:   Optional[dict]
    expert_mode:      bool

# ── HELPER FUNCTIONS ─────────────────────────────────────────────────────────

def _load_user_personas(user_hash: str) -> list:
    """Loads custom personas from the database."""
    if SUPABASE_MISSING:
        return []
    try:
        from forge.persona_store import list_personas
        personas, _ = list_personas(user_hash, target_filter="All")
        return personas or []
    except Exception:
        return []

def render_language_switcher() -> None:
    """Renders flags for language selection."""
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

# ── MAIN RENDERER ─────────────────────────────────────────────────────────────

def render_sidebar() -> SidebarConfig:
    """
    🟢 MASTER RENDERER: Identity-Locked Uplink
    """
    with st.sidebar:
        # ── 1. EVALUATE IDENTITY ──────────────────────────────────────────────
        current_sid = st.session_state.get(K.USER_HASH)
        is_guest = not current_sid or "GUEST_" in str(current_sid).upper()
        sess_ref = str(current_sid)[:8] if current_sid else "GHOST_ID"

        # ── 2. NEURAL LINK STATUS ──────────────────────────────────────────────
        if SUPABASE_MISSING:
            uplink_color, uplink_label = "#E53E3E", "DB_FAULT"
        elif is_guest:
            uplink_color, uplink_label = "var(--text-dim)", "OFFLINE" 
        else:
            uplink_color, uplink_label = "#4CAF9A", "ACTIVE" 

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

        # ── 3. WORDMARK ────────────────────────────────────────────────────────
        wordmark_html = textwrap.dedent(f"""
            <div style="padding:0 0 14px 0; border-bottom:1px solid rgba(255,255,255,0.05); margin-bottom:15px;">
                <div class="vc-wordmark" style="font-size:1.4rem;">⚡ {t('app_name')}</div>
                <div class="vc-wordmark-sub" style="letter-spacing:2px; font-size:0.5rem; color:var(--gold);">حبر وفكرة // INKOS v2026.4</div>
            </div>
        """)
        st.markdown(wordmark_html, unsafe_allow_html=True)

        # ── 4. TERMINAL IDENTITY HUD ───────────────────────────────────────────
        st.markdown(f'<div class="vc-header" style="font-size:0.55rem; color:var(--text-muted); margin-top:20px;">SESS_REF: {sess_ref}</div>', unsafe_allow_html=True)

        if is_guest:
            new_sid = st.text_input("ID", placeholder="Identity Name", key="sid_input_sidebar", label_visibility="collapsed")
            new_pin = st.text_input("PIN", placeholder="PIN", type="password", key="pin_input_sidebar", label_visibility="collapsed")
            is_new_user = st.toggle("Register New?", value=False, key="is_new_user_toggle")
            
            if is_new_user and new_sid.strip():
                available, status_msg = check_id_availability(new_sid.strip())
                color = "#4CAF9A" if available else "#E53E3E"
                st.markdown(f"<div style='color:{color}; font-size:0.55rem; font-family:var(--font-m); margin-bottom:8px;'>{status_msg}</div>", unsafe_allow_html=True)
            
            if st.button("LATCH IDENTITY", use_container_width=True, key="btn_latch_sid"):
                if new_sid.strip() and new_pin.strip():
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

        # ── 5. LOGIC CONFIGURATION ────────────────────────────────────────────
        st.markdown(f'<div class="vc-header" style="margin-top:20px; font-size:0.65rem;">[ {t("logic_config", fallback="LOGIC_CONFIGURATION").upper()} ]</div>', unsafe_allow_html=True)
        target_options = [AUTO_SELECT_LABEL] + list(TARGET_GUIDES.keys())
        target_model = st.selectbox("Target Model", options=target_options, key="sb_target")

        framework = st.selectbox(t("logic_framework", fallback="Framework"), LOGIC_FRAMEWORKS, key="sb_framework")
        source_lang = st.radio("Input Language", ["English", "Arabic (العربية)"], key="sb_lang")

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── 6. PERSONA SELECTOR (v2026.4 MASTER LATCH) ────────────────────
        st.markdown(f'<div class="vc-header" style="margin-top:20px; font-size:0.65rem;">[ {t("active_persona", fallback="ACTIVE_PERSONA").upper()} ]</div>', unsafe_allow_html=True)
        
        user_personas = _load_user_personas(st.session_state.get(K.USER_HASH, ''))

        # A. Build Option Map (Label -> Data)
        options_map: dict = {'None': None}
        for name, p_data in STARTER_PERSONAS.items():
            if name != 'None':
                options_map[f'{name} [S]'] = p_data
        for p_data in user_personas:
            options_map[f"{p_data['name']} [C]"] = p_data
        
        options_list = list(options_map.keys())

        # B. Resolve Index (The Persistence Latch)
        url_p_name = st.query_params.get("p")
        current_active = st.session_state.get(K.ACTIVE_PERSONA)
        
        # Priority: URL > Session State
        target_id = url_p_name if url_p_name else (current_active.get('name') if current_active else None)
        
        p_index = 0
        if target_id:
            for i, label in enumerate(options_list):
                data = options_map[label]
                if data and data.get('name') == target_id:
                    p_index = i
                    break

        # C. The Master Widget
        selected_key = st.selectbox(
            'Persona Select', 
            options=options_list,
            index=p_index, 
            key='sb_persona_global_widget', 
            label_visibility='collapsed',
        )
        
        # D. Sync State & URL
        active_p = options_map[selected_key]
        st.session_state[K.ACTIVE_PERSONA] = active_p

        if active_p:
            st.query_params['p'] = active_p.get('name', '')
            st.markdown(f"""
                <div style="background:rgba(201,168,76,0.07); border:1px solid rgba(201,168,76,0.25); padding:8px; border-radius:3px; font-size:0.6rem; color:var(--gold);">
                    <strong>{active_p.get('name','')}</strong><br>
                    <span style="color:var(--text-muted); font-style:italic;">{active_p.get('role','')[:60]}...</span>
                </div>
            """, unsafe_allow_html=True)
        else:
            if 'p' in st.query_params:
                del st.query_params['p']

        # ── 7. SYSTEM TOGGLES ─────────────────────────────────────────────────
        st.markdown("<hr style='margin-top:5px;'>", unsafe_allow_html=True)
        aesthetic_choice = st.selectbox(t("aesthetic_preset", fallback="Aesthetic"), options=list(AESTHETIC_PRESETS.keys()), key="sb_aesthetic")
        
        islamic_mode = st.checkbox("Islamic Mode", value=False, key="sb_islamic")
        expert_mode = st.checkbox("Expert Diagnostics", value=False, key="sb_expert")

        # ── 8. METRICS ────────────────────────────────────────────────────────
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(t("session_runs", fallback="Runs"), len(st.session_state.get(K.HISTORY, [])))
        with m2:
            st.metric(t("session_remaining", fallback="Calls"), get_remaining_calls())
        with m3:
            st.metric(t("last_saved", fallback="Saved"), st.session_state.get(K.LAST_SAVED, "Never"))

        st.markdown("<hr>", unsafe_allow_html=True)

        if st.button(t("reset_session", fallback="Reset Session"), use_container_width=True):
            from state import reset_session
            reset_session()
            st.rerun()

    return SidebarConfig(
        target_model     = target_model,
        framework        = framework,
        source_lang      = source_lang,
        islamic_mode     = islamic_mode,
        aesthetic_choice = aesthetic_choice,
        active_persona   = active_p,
        expert_mode      = expert_mode,
    )
