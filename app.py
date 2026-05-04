"""
InkOS | app.py — Entry Point
v1: Collision-resistant Layout.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
st.set_page_config(page_title="InkOS", page_icon="⚡", layout="wide")

from config import API_KEY_MISSING
from state import init_session_state, K
from ui.styles import load_css
from ui.sidebar import render_sidebar
from ui.tabs.workspace import render_workspace
from ui.tabs.archive import render_archive
from ui.tabs.security_log import render_security_log
from ui.tabs.cognitive_map import render_cognitive_map
from ui.tabs.vault import render_vault
from ui.tabs.forge import render_forge
from ui.tabs.guide import render_guide
from i18n.translations import t, is_rtl

if API_KEY_MISSING:
    st.error("SYSTEM ERROR: GROQ_API_KEY not found in environment.")
    st.stop()

init_session_state()

# ── LOAD EXTERNAL DESIGN ──────────────────────────────────────────────────────
load_css()

# ── RTL & HEADER PROTECTION ──────────────────────────────────────────────────
# This pushes the content down to make room for the sticky logo
st.markdown("""
    <style>
        header[data-testid="stHeader"] { z-index: 1000 !important; }
        .block-container { padding-top: 6.5rem !important; }
    </style>
""", unsafe_allow_html=True)

if is_rtl():
    st.markdown("<script>const app = window.parent.document.querySelector('.stApp'); if (app) app.classList.add('rtl-mode');</script>", unsafe_allow_html=True)
else:
    st.markdown("<script>const app = window.parent.document.querySelector('.stApp'); if (app) app.classList.remove('rtl-mode');</script>", unsafe_allow_html=True)

cfg = render_sidebar()

# ── NAVIGATION ────────────────────────────────────────────────────────────────
nav_options = {
    t("tab_workspace"):     lambda: render_workspace(cfg),
    t("tab_archive"):       render_archive,
    t("tab_security"):      render_security_log,
    t("tab_cognitive_map"): render_cognitive_map,
    t("tab_vault"):         render_vault,
    t("tab_forge"):         render_forge,
    t("tab_guide"):         render_guide,
}

# Navigation Safe Zone
st.markdown('<div class="nav-safe-zone">', unsafe_allow_html=True)
selected_nav = st.selectbox(
    "Navigation", 
    list(nav_options.keys()), 
    label_visibility="collapsed"
)
st.markdown('</div>', unsafe_allow_html=True)

# Divider
st.markdown("<hr style='border: none; border-bottom: 1px solid rgba(201,168,76,0.15); margin: 0 0 20px 0;'>", unsafe_allow_html=True)

# Run Page
nav_options[selected_nav]()