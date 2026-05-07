"""
ui/sidebar.py — Sidebar Rendering
====================================
v1.0: Integrated Terminal Identity HUD for Persistent Latching.
       Includes Level 4 Expert Diagnostics & Multi-Language Support.
"""

import streamlit as st
import json
from datetime import datetime
from typing import TypedDict, Optional
from state import K, get_remaining_calls
from config import TARGET_GUIDES, AESTHETIC_PRESETS, AUTO_SELECT_LABEL, LOGIC_FRAMEWORKS
from forge.persona_engine import STARTER_PERSONAS, get_persona_display_name
from vault.supabase_client import SUPABASE_MISSING
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
        st.markdown(f"""
        <div style="padding:10px 0 14px 0;">
            <div class="vc-wordmark">⚡ {t('app_name')}</div>
            <div class="vc-wordmark-sub">{t('app_subtitle')}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── LANGUAGE SWITCHER ─────────────────────────────────────────────────
        render_language_switcher()

            # ── TERMINAL IDENTITY HUD ─────────────────────────────────────────────
        st.markdown(f'<div class="vc-header" style="font-size:0.55rem; color:var(--text-muted); margin-top:14px;">TERMINAL IDENTITY</div>', unsafe_allow_html=True)
        
        current_sid = st.session_state.get(K.USER_HASH, "UNKNOWN")
        is_guest = "GUEST_" in current_sid
        
        # Display current ID in a clean block
        st.code(current_sid, language=None)
        
        # 🟢 If it's a GUEST, show the input box to encourage "Saving"
        if is_guest:
            new_sid = st.text_input(
                "Identity Latch", 
                placeholder="Enter an ID to save your data...", 
                key="sid_input_sidebar", 
                label_visibility="collapsed"
            )
            
            if st.button("SAVE IDENTITY", use_container_width=True, key="btn_latch_sid"):
                if new_sid.strip():
                    st.session_state[K.USER_HASH] = new_sid.strip()
                    st.query_params["sid"] = new_sid.strip()
                    st.toast(f"Identity Saved: {new_sid.strip()}", icon="🔐")
                    st.rerun()
        
        # 🔵 If it's a REAL ID (like Ameer), hide the box and show a "Switch" button
        else:
            st.markdown(f"""
                <div style="font-size:0.62rem; color:var(--gold); margin-bottom:10px;">
                    ✓ Identity Secured & Saved
                </div>
            """, unsafe_allow_html=True)
            
            if st.button("Switch Identity / Logout", use_container_width=True, key="btn_logout_sid"):
                # Clear the ID and the URL, then rerun
                st.session_state[K.USER_HASH] = None 
                st.query_params.clear()
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)


        # ── LOGIC CONFIGURATION ───────────────────────────────────────────────
        st.subheader(t("logic_config", fallback="Logic Configuration"))
        target_options = [AUTO_SELECT_LABEL] + list(TARGET_GUIDES.keys())
        
        target_model = st.selectbox(
            "Target AI Model", 
            options=target_options,
            key="sb_target",
            help="Select the target AI. CIPHER maps intent to specific syntax: strict XML for Claude, conversational structures for ChatGPT, and parameter-heavy tokens for Midjourney.",
        )

        if target_model == AUTO_SELECT_LABEL:
            auto_target = st.session_state.get(K.AUTO_TARGET)
            auto_reason = st.session_state.get(K.AUTO_REASON)
            if auto_target:
                st.markdown(f"""
                <div style="
                    background:rgba(201,168,76,0.07);
                    border:1px solid rgba(201,168,76,0.25);
                    border-radius:3px;padding:8px 12px;
                    font-family:var(--font-m);font-size:0.62rem;
                    color:var(--gold);line-height:1.6;margin-top:4px;
                ">
                    <span class="status-dot"></span>
                    CIPHER selected: <strong>{auto_target}</strong><br>
                    <span style="color:var(--text-muted);">{auto_reason}</span>
                </div>
                """, unsafe_allow_html=True)
                
        framework = st.selectbox(
            t("logic_framework", fallback="Logic Framework"),
            LOGIC_FRAMEWORKS,
            key="sb_framework",
            help="Forces the AI's cognitive boundary. 'RACE' enforces Role-Action-Context-Execution. 'Technical' forces a Chain-of-Thought <thinking> block before generating code.",
        )
        
        source_lang = st.radio(
            "Input Language",
            ["English", "Arabic (العربية)"],
            key="sb_lang",
            help="Language of raw intent. Arabic engages the Cognitive Mapping Layer to preserve rhetorical authority and structural rules.",
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── PERSONA SELECTOR ──────────────────────────────────────────────────
        st.subheader(t("active_persona", fallback="Active Persona"))

        user_hash     = st.session_state.get(K.USER_HASH, "")
        user_personas = _load_user_personas(user_hash)

        all_names = list(STARTER_PERSONAS.keys()) + [p["name"] for p in user_personas]

        current_persona = get_persona_display_name(st.session_state.get(K.ACTIVE_PERSONA))
        if current_persona not in all_names:
            current_persona = "None"

        if st.session_state.get("sb_persona") != current_persona:
            st.session_state["sb_persona"] = current_persona

        def _sb_persona_changed():
            sel = st.session_state.sb_persona
            if sel == "None":
                st.session_state[K.ACTIVE_PERSONA] = None
            elif sel in STARTER_PERSONAS:
                st.session_state[K.ACTIVE_PERSONA] = STARTER_PERSONAS[sel]
            else:
                st.session_state[K.ACTIVE_PERSONA] = next((p for p in user_personas if p["name"] == sel), None)

        st.selectbox(
            "Persona Select",
            options=all_names,
            key="sb_persona",
            on_change=_sb_persona_changed,
            label_visibility="collapsed",
            help="Injects 'Expert DNA'. Select a Persona for strict, domain-specific logic.",
        )

        active_persona_state = st.session_state.get(K.ACTIVE_PERSONA)
        if active_persona_state:
            st.markdown(f"""
            <div style="
                background:rgba(201,168,76,0.07);
                border:1px solid rgba(201,168,76,0.25);
                border-radius:3px;padding:8px 12px;
                font-family:var(--font-m);font-size:0.62rem;
                color:var(--gold);line-height:1.6;margin-top:6px;
            ">
                <span class="status-dot"></span>
                {active_persona_state.get('name','')}<br>
                <span style="color:var(--text-muted);">
                    {active_persona_state.get('role','')[:80]}...
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── AESTHETIC & EXPERT MODE ───────────────────────────────────────────
        st.subheader(t("aesthetic_dir", fallback="Aesthetic Direction"))
        aesthetic_choice = st.selectbox(
            t("aesthetic_preset", fallback="Preset"),
            options=list(AESTHETIC_PRESETS.keys()),
            key="sb_aesthetic",
        )

        islamic_mode = st.toggle(t("islamic_mode", fallback="Islamic Professional Mode"), value=False, key="sb_islamic")
        if islamic_mode:
            st.markdown(f"""
            <div class="islamic-badge">
                <span class="status-dot green"></span>{t('islamic_active', fallback='Active')}<br>
                {t('islamic_sharia', fallback='Sharia Compliant')}
            </div>
            """, unsafe_allow_html=True)
            
        expert_mode = st.toggle("Enable Expert Diagnostics", value=False, key="sb_expert")

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── METRICS ───────────────────────────────────────────────────────────
        total_runs = len(st.session_state.get(K.HISTORY, []))
        remaining  = get_remaining_calls()

        m1, m2 = st.columns(2)
        with m1:
            st.metric(t("session_runs", fallback="Runs"), total_runs)
        with m2:
            st.metric(t("session_remaining", fallback="Remaining"), remaining)

        st.markdown("<hr>", unsafe_allow_html=True)

        if st.button(t("reset_session", fallback="Reset Session"), use_container_width=True, key="btn_reset"):
            from state import reset_session
            reset_session()
            st.rerun()

        if st.session_state.get(K.HISTORY):
            st.download_button(
                t("export_archive", fallback="Export Archive"),
                data=json.dumps(st.session_state[K.HISTORY], ensure_ascii=False, indent=2),
                file_name=f"inkos_archive_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True,
                key="btn_export_sidebar",
            )

    return SidebarConfig(
        target_model     = target_model,
        framework        = framework,
        source_lang      = source_lang,
        islamic_mode     = islamic_mode,
        aesthetic_choice = aesthetic_choice,
        active_persona   = active_persona_state,
        expert_mode      = expert_mode,
    )
