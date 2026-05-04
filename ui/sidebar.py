"""
ui/sidebar.py — Sidebar Configuration
=======================================
Restored v1: Includes the beautiful InkOS Branding & Wordmark.
"""

import streamlit as st
from i18n.translations import t
from config import LOGIC_FRAMEWORKS, TARGET_GUIDES, AESTHETIC_PRESETS, AUTO_SELECT_LABEL

def render_sidebar() -> dict:
    """Renders the left sidebar with branding, flags, and logic config."""
    
    with st.sidebar:
        # ── RESTORED BRANDING ────────────────────────────────────────────────
        st.markdown(f"""
            <div style="margin-bottom: 25px;">
                <div class="vc-wordmark">⚡ INKOS</div>
                <div class="vc-wordmark-sub">ARABIC COGNITIVE PROMPT ENGINE</div>
            </div>
        """, unsafe_allow_html=True)

        # ── LANGUAGE SWITCHER ────────────────────────────────────────────────
        st.markdown(f'<div class="vc-header" style="margin-bottom:10px;">{t("lang_select")}</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🇬🇧 EN", use_container_width=True):
                st.session_state["lang"] = "English"
        with col2:
            if st.button("🇸🇦 AR", use_container_width=True):
                st.session_state["lang"] = "Arabic"
        with col3:
            if st.button("🇫🇷 FR", use_container_width=True):
                st.session_state["lang"] = "French"

        st.markdown("<br>", unsafe_allow_html=True)

        # ── LOGIC CONFIGURATION ──────────────────────────────────────────────
        st.markdown(f'<div class="vc-header"><span class="status-dot"></span>{t("logic_config")}</div>', unsafe_allow_html=True)

        target_model = st.selectbox(
            t("target_dialect"),
            options=[AUTO_SELECT_LABEL] + list(TARGET_GUIDES.keys()),
            help=t("target_help")
        )

        framework = st.selectbox(
            t("logic_framework"),
            options=LOGIC_FRAMEWORKS,
            help=t("framework_help")
        )

        source_lang = st.radio(
            t("linguistic_source"),
            options=["English", "Arabic (العربية)"],
            help=t("source_help")
        )

        islamic_mode = st.toggle(
            "🌙 " + t("islamic_mode"),
            value=False,
            help=t("islamic_help")
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── PERSONA & AESTHETICS ─────────────────────────────────────────────
        st.markdown(f'<div class="vc-header">🎭 {t("active_persona")}</div>', unsafe_allow_html=True)
        # Assuming you have a persona engine loader here
        active_persona = st.selectbox("Persona", options=["None", "Analyst", "Poet", "Architect"], label_visibility="collapsed")

        st.markdown("<br>", unsafe_allow_html=True)
        
        st.markdown(f'<div class="vc-header">🎨 {t("aesthetic_direction")}</div>', unsafe_allow_html=True)
        aesthetic_choice = st.selectbox(
            t("aesthetic_preset"),
            options=list(AESTHETIC_PRESETS.keys()),
            help=t("aesthetic_help")
        )

        # Return the config for use in the workspace
        return {
            "target_model": target_model,
            "framework": framework,
            "source_lang": source_lang,
            "islamic_mode": islamic_mode,
            "aesthetic_choice": aesthetic_choice,
            "active_persona": active_persona if active_persona != "None" else None
        }