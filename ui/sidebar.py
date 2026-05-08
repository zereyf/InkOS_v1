"""
ui/sidebar.py — Sidebar Rendering
====================================
v28.0: The Synchronized Build.
       Integrated LAST_SAVED metrics and dedent protocol for UI stability.
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
                f"{lang['flag']} {lang['label']}",
                key=f"lang_btn_{lang['code']}",
                use_container_width=True,
                type="primary" if is_active else "secondary"
            ):
                if not is_active:
                    set_lang(lang["code"])
                    st.rerun()


def render_sidebar() -> SidebarConfig:
    with st.sidebar:
        # ── WORDMARK ──────────────────────────────────────────────────────────
        wordmark_html = textwrap.dedent(f"""
            <div style="padding:10px 0 14px 0;">
                <div class="vc-wordmark">⚡ {t('app_name')}</div>
                <div class="vc-wordmark-sub">{t('app_subtitle')}</div>
            </div>
        """)
        st.markdown(wordmark_html, unsafe_allow_html=True)

        # ── LANGUAGE SWITCHER ─────────────────────────────────────────────────
        render_language_switcher()

        # ── TERMINAL IDENTITY HUD ─────────────────────────────────────────────
        st.markdown('<div class="vc-header" style="font-size:0.55rem; color:var(--text-muted); margin-top:14px;">TERMINAL IDENTITY</div>', unsafe_allow_html=True)
        
        current_sid = st.session_state.get(K.USER_HASH, "UNKNOWN")
        is_guest = "GUEST_" in str(current_sid).upper()
        
        st.code(current_sid, language=None)
        
        if is_guest:
            new_sid = st.text_input("Access Key", placeholder="Identity Name", key="sid_input_sidebar", label_visibility="collapsed")
            new_pin = st.text_input("Security PIN", placeholder="4-6 Digit PIN", type="password", key="pin_input_sidebar", label_visibility="collapsed")
            is_new_user = st.toggle("Registering new identity?", value=False, key="is_new_user_toggle")
            
            id_is_valid = True
            if is_new_user and new_sid.strip():
                available, status_msg = check_id_availability(new_sid.strip())
                color = "#4CAF9A" if available else "#A93226"
                if "Reserved Prefix" in status_msg:
                    color = "#C9A84C"
                
                status_html = textwrap.dedent(f"""
                    <div style="color:{color}; font-size:0.6rem; margin-bottom:10px; font-family:var(--font-m);">
                        {status_msg}
                    </div>
                """)
                st.markdown(status_html, unsafe_allow_html=True)
                id_is_valid = available

            if st.button("LATCH IDENTITY", use_container_width=True, key="btn_latch_sid"):
                if not id_is_valid and is_new_user:
                    st.error("Cannot latch: ID is unavailable.")
                elif new_sid.strip() and new_pin.strip():
                    with st.spinner("Authenticating..."):
                        success, error_msg = authenticate_terminal(new_sid.strip(), new_pin.strip(), is_new=is_new_user)
                    
                    if success:
                        st.session_state[K.USER_HASH] = new_sid.strip()
                        st.session_state[K.USER_PIN]  = new_pin.strip()
                        st.session_state[K.FAILED_ATTEMPTS] = 0
                        st.query_params["sid"] = new_sid.strip()
                        st.rerun()
                    else:
                        st.session_state[K.FAILED_ATTEMPTS] += 1
                        if st.session_state[K.FAILED_ATTEMPTS] >= 5:
                            st.session_state[K.LOCKOUT_UNTIL] = datetime.now(timezone.utc) + timedelta(minutes=10)
                            st.rerun()
                        st.error(error_msg)
        else:
            secure_html = textwrap.dedent("""
                <div style="font-size:0.62rem; color:var(--gold); margin-bottom:10px; display:flex; align-items:center; gap:8px;">
                    <span class="status-dot"></span>
                    IDENTITY SECURED
                </div>
            """)
            st.markdown(secure_html, unsafe_allow_html=True)
            
            if st.button("Logout / Clear Latch", use_container_width=True):
                st.session_state[K.USER_HASH] = None 
                st.session_state[K.USER_PIN]  = None
                st.session_state[K.FAILED_ATTEMPTS] = 0
                st.query_params.clear()
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── LOGIC CONFIGURATION ───────────────────────────────────────────────
        st.subheader(t("logic_config"))
        target_options = [AUTO_SELECT_LABEL] + list(TARGET_GUIDES.keys())
        target_model = st.selectbox("Target AI Model", options=target_options, key="sb_target")

        if target_model == AUTO_SELECT_LABEL:
            auto_target = st.session_state.get(K.AUTO_TARGET)
            auto_reason = st.session_state.get(K.AUTO_REASON)
            if auto_target:
                auto_html = textwrap.dedent(f"""
                    <div style="background:rgba(201,168,76,0.07); border:1px solid rgba(201,168,76,0.25); border-radius:3px; padding:8px 12px; font-family:var(--font-m); font-size:0.62rem; color:var(--gold); line-height:1.6; margin-top:4px;">
                        <span class="status-dot"></span>
                        CIPHER: <strong>{auto_target}</strong><br>
                        <span style="color:var(--text-muted);">{auto_reason}</span>
                    </div>
                """)
                st.markdown(auto_html, unsafe_allow_html=True)
                
        framework = st.selectbox(t("logic_framework"), LOGIC_FRAMEWORKS, key="sb_framework")
        source_lang = st.radio("Input Language", ["English", "Arabic (العربية)"], key="sb_lang")

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── PERSONA SELECTOR ──────────────────────────────────────────────────
        st.subheader(t("active_persona"))
        user_personas = _load_user_personas(st.session_state.get(K.USER_HASH, ""))
        all_names = list(STARTER_PERSONAS.keys()) + [p["name"] for p in user_personas]

        def _sb_persona_changed():
            sel = st.session_state.sb_persona
            if sel == "None":
                st.session_state[K.ACTIVE_PERSONA] = None
            elif sel in STARTER_PERSONAS:
                st.session_state[K.ACTIVE_PERSONA] = STARTER_PERSONAS[sel]
            else:
                st.session_state[K.ACTIVE_PERSONA] = next((p for p in user_personas if p["name"] == sel), None)

        st.selectbox("Persona Select", options=["None"] + all_names, key="sb_persona", on_change=_sb_persona_changed, label_visibility="collapsed")

        active_p = st.session_state.get(K.ACTIVE_PERSONA)
        if active_p:
            persona_html = textwrap.dedent(f"""
                <div style="background:rgba(201,168,76,0.07); border:1px solid rgba(201,168,76,0.25); border-radius:3px; padding:8px 12px; font-family:var(--font-m); font-size:0.62rem; color:var(--gold); line-height:1.6; margin-top:6px;">
                    <span class="status-dot"></span>
                    {active_p.get('name','')}<br>
                    <span style="color:var(--text-muted);">{active_p.get('role','')[:80]}...</span>
                </div>
            """)
            st.markdown(persona_html, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── AESTHETIC & EXPERT MODE ───────────────────────────────────────────
        aesthetic_choice = st.selectbox(t("aesthetic_preset"), options=list(AESTHETIC_PRESETS.keys()), key="sb_aesthetic")
        islamic_mode = st.toggle(t("islamic_mode"), value=False, key="sb_islamic")
        expert_mode = st.toggle("Enable Expert Diagnostics", value=False, key="sb_expert")

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── METRICS (3-Column Layout) ─────────────────────────────────────────
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(t("session_runs"), len(st.session_state.get(K.HISTORY, [])))
        with m2:
            st.metric(t("session_remaining"), get_remaining_calls())
        with m3:
            # 🟢 SYNCED: Displays Last Saved timestamp from Workspace actions
            st.metric(t("last_saved", fallback="Saved"), st.session_state.get(K.LAST_SAVED, "Never"))

        st.markdown("<hr>", unsafe_allow_html=True)

        if st.button(t("reset_session"), use_container_width=True):
            from state import reset_session
            reset_session()
            st.rerun()

        if st.session_state.get(K.HISTORY):
            st.download_button(
                t("export_archive"),
                data=json.dumps(st.session_state[K.HISTORY], ensure_ascii=False, indent=2),
                file_name=f"inkos_archive_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True
            )

    return SidebarConfig(
        target_model     = target_model,
        framework        = framework,
        source_lang      = source_lang,
        islamic_mode     = islamic_mode,
        aesthetic_choice = aesthetic_choice,
        active_persona   = active_p,
        expert_mode      = expert_mode,
    )
