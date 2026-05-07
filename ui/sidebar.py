"""
ui/sidebar.py — Sidebar Rendering
====================================
v11: Fixed confusing UX labels and added clarification tooltips per audit.
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

        # ── LOGIC CONFIGURATION ───────────────────────────────────────────────
        st.subheader(t("logic_config", fallback="Logic Configuration"))
        target_options = [AUTO_SELECT_LABEL] + list(TARGET_GUIDES.keys())
        
        # AUDIT FIX: Renamed from "Target Dialect" to "Target AI Model"
        target_model = st.selectbox(
            "Target AI Model", 
            options=target_options,
            key="sb_target",
            help="Select the AI you are prompting. CIPHER will adapt the syntax perfectly for this model.",
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
            else:
                st.markdown("""
                <div style="
                    font-family:var(--font-m);font-size:0.62rem;
                    color:var(--text-muted);padding:6px 0;
                ">
                    CIPHER will analyse your intent and pick the best AI target.
                </div>
                """, unsafe_allow_html=True)
                
        framework = st.selectbox(
            t("logic_framework", fallback="Logic Framework"),
            LOGIC_FRAMEWORKS,
            key="sb_framework",
            help="Defines the structural boundaries of the generated prompt.",
        )
        
        # AUDIT FIX: Renamed from "Linguistic Source" to "Input Language"
        source_lang = st.radio(
            "Input Language",
            ["English", "Arabic (العربية)"],
            key="sb_lang",
            help="The language of your raw intent. Arabic inputs engage the cognitive mapping layer.",
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── PERSONA SELECTOR ──────────────────────────────────────────────────
        st.subheader(t("active_persona", fallback="Active Persona"))

        user_hash     = st.session_state.get(K.USER_HASH, "")
        user_personas = _load_user_personas(user_hash)

        starter_names = list(STARTER_PERSONAS.keys())
        user_names    = [p["name"] for p in user_personas]
        all_names     = starter_names + user_names

        current_persona = get_persona_display_name(st.session_state.get(K.ACTIVE_PERSONA))
        if current_persona not in all_names:
            current_persona = "None"

        selected_name = st.selectbox(
            "Persona Select",
            options=all_names,
            index=all_names.index(current_persona),
            key="sb_persona",
            label_visibility="collapsed",
            help="A.I.Z.E.N. handles default routing. Select an Expert Persona for strict, domain-specific logic.",
        )

        if selected_name == "None":
            active_persona = None
        elif selected_name in STARTER_PERSONAS:
            active_persona = STARTER_PERSONAS[selected_name]
        else:
            active_persona = next(
                (p for p in user_personas if p["name"] == selected_name), None
            )

        st.session_state[K.ACTIVE_PERSONA] = active_persona

        if active_persona:
            st.markdown(f"""
            <div style="
                background:rgba(201,168,76,0.07);
                border:1px solid rgba(201,168,76,0.25);
                border-radius:3px;padding:8px 12px;
                font-family:var(--font-m);font-size:0.62rem;
                color:var(--gold);line-height:1.6;margin-top:6px;
            ">
                <span class="status-dot"></span>
                {active_persona.get('name','')}<br>
                <span style="color:var(--text-muted);">
                    {active_persona.get('role','')[:80]}...
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        # ── AESTHETIC ─────────────────────────────────────────────────────────
        st.subheader(t("aesthetic_dir", fallback="Aesthetic Direction"))
        aesthetic_choice = st.selectbox(
            t("aesthetic_preset", fallback="Preset"),
            options=list(AESTHETIC_PRESETS.keys()),
            key="sb_aesthetic",
            help="Only affects prompts generated for Midjourney/Flux and DALL-E 3.",
        )

        islamic_mode = st.toggle(t("islamic_mode", fallback="Islamic Professional Mode"), value=False, key="sb_islamic")
        if islamic_mode:
            st.markdown(f"""
            <div class="islamic-badge">
                <span class="status-dot green"></span>{t('islamic_active', fallback='Active')}<br>
                {t('islamic_sharia', fallback='Sharia Compliant')}<br>
                {t('islamic_citation', fallback='Requires strict citations')}
            </div>
            """, unsafe_allow_html=True)

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
                data=json.dumps(
                    st.session_state[K.HISTORY],
                    ensure_ascii=False,
                    indent=2,
                ),
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
        active_persona   = active_persona,
    )
