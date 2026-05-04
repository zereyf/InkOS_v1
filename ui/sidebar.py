"""
ui/sidebar.py — Sidebar Configuration
=======================================
v1: Robust Path Imports & Branding Restoration.
"""

import streamlit as st
import sys
import os

# ── ROBUST IMPORT LOGIC ──────────────────────────────────────────────────────
# This ensures that even as a sub-module, sidebar.py can see the root config.py
try:
    from config import LOGIC_FRAMEWORKS, TARGET_GUIDES, AESTHETIC_PRESETS, AUTO_SELECT_LABEL
except ImportError:
    # Manual path injection fallback for specific cloud environments
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from config import LOGIC_FRAMEWORKS, TARGET_GUIDES, AESTHETIC_PRESETS, AUTO_SELECT_LABEL

from i18n.translations import t

def render_sidebar() -> dict:
    """Renders the left sidebar with branding, flags, and logic config."""
    
    with st.sidebar:
        # ── RESTORED BRANDING (SIDEBAR TOP) ──────────────────────────────────
        # Negative margin-top helps it sit perfectly at the top of the sidebar
        st.markdown(f"""
            <div style="margin-bottom: 25px; margin-top: -15px; text-align: left;">
                <div class="vc-wordmark" style="font-size: 1.4rem;">⚡ INKOS</div>
                <div class="vc-wordmark-sub" style="font-size: 0.55rem;">ARABIC COGNITIVE PROMPT ENGINE</div>
            </div>
        """, unsafe_allow_html=True)

        # ── LANGUAGE SWITCHER ────────────────────────────────────────────────
        st.markdown(f'<div class="vc-header" style="margin-bottom:10px;">{t("lang_select")}</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("🇬🇧 EN", key="btn_en", use_container_width=True):
                st.session_state["lang"] = "English"
        with col2:
            if st.button("🇸🇦 AR", key="btn_ar", use_container_width=True):
                st.session_state["lang"] = "Arabic"
        with col3:
            if st.button("🇫🇷 FR", key="btn_fr", use_container_width=True):
                st.session_state["lang"] = "French"

        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

        # ── LOGIC CONFIGURATION ──────────────────────────────────────────────
        st.markdown(f'<div class="vc-header"><span class="status-dot"></span>{t("logic_config")}</div>', unsafe_allow_html=True)

        target_model = st.selectbox(
            t("target_dialect"),
            options=[AUTO_SELECT_LABEL] + list(TARGET_GUIDES.keys()),
            help=t("target_help"),
            key="sb_target"
        )

        framework = st.selectbox(
            t("logic_framework"),
            options=LOGIC_FRAMEWORKS,
            help=t("framework_help"),
            key="sb_frame"
        )

        source_lang = st.radio(
            t("linguistic_source"),
            options=["English", "Arabic (العربية)"],
            help=t("source_help"),
            key="sb_lang"
        )

        islamic_mode = st.toggle(
            "🌙 " + t("islamic_mode"),
            value=False,
            help=t("islamic_help"),
            key="sb_islamic"
        )

        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)

        # ── PERSONA & AESTHETICS ─────────────────────────────────────────────
        st.markdown(f'<div class="vc-header">🎭 {t("active_persona")}</div>', unsafe_allow_html=True)
        active_persona = st.selectbox(
            "Persona", 
            options=["None", "Analyst", "Poet", "Architect"], 
            label_visibility="collapsed",
            key="sb_pers"
        )

        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        
        st.markdown(f'<div class="vc-header">🎨 {t("aesthetic_direction")}</div>', unsafe_allow_html=True)
        aesthetic_choice = st.selectbox(
            t("aesthetic_preset"),
            options=list(AESTHETIC_PRESETS.keys()),
            help=t("aesthetic_help"),
            key="sb_aest"
        )

        return {
            "target_model": target_model,
            "framework": framework,
            "source_lang": source_lang,
            "islamic_mode": islamic_mode,
            "aesthetic_choice": aesthetic_choice,
            "active_persona": active_persona if active_persona != "None" else None
        }