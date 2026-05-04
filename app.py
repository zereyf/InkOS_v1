"""
InkOS | app.py — Entry Point
==============================
v1: Professional CSS loading refactor.
Standardized for Senior Engineer Audit compliance.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
st.set_page_config(page_title="InkOS", page_icon="⚡", layout="wide")

# ── INITIAL CSS INJECTION ─────────────────────────────────────────────────────
# We keep these few lines here for structural stability (header and padding),
# while the bulk of the design is loaded via load_css().
st.markdown("""
    <style>
        header[data-testid="stHeader"] {
            position: fixed !important; top: 0 !important; z-index: 9999 !important;
        }
        .block-container { padding-top: 4rem !important; }
        
        div[data-testid="stSelectbox"] > div[data-baseweb="select"] {
            border-color: rgba(201,168,76,0.3) !important;
            background-color: var(--bg-raised) !important;
        }
    </style>
""", unsafe_allow_html=True)

from config import API_KEY_MISSING
from state import init_session_state, K
from ui.styles import load_css  # UPDATED: Import function instead of string
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

# ── PROFESSIONAL CSS LOAD ─────────────────────────────────────────────────────
load_css()  # UPDATED: Executing the file-based loader

# ── RTL MODE ──────────────────────────────────────────────────────────────────
if is_rtl():
    st.markdown("""
    <script>
        const app = window.parent.document.querySelector('.stApp');
        if (app) app.classList.add('rtl-mode');
    </script>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <script>
        const app = window.parent.document.querySelector('.stApp');
        if (app) app.classList.remove('rtl-mode');
    </script>
    """, unsafe_allow_html=True)

cfg = render_sidebar()

# ── MOBILE-OPTIMIZED NAVIGATION ───────────────────────────────────────────────
nav_options = {
    t("tab_workspace"):     lambda: render_workspace(cfg),
    t("tab_archive"):       render_archive,
    t("tab_security"):      render_security_log,
    t("tab_cognitive_map"): render_cognitive_map,
    t("tab_vault"):         render_vault,
    t("tab_forge"):         render_forge,
    t("tab_guide"):         render_guide,
}

selected_nav = st.selectbox(
    "Navigation", 
    list(nav_options.keys()), 
    label_visibility="collapsed"
)

st.markdown("<hr style='border: none; border-bottom: 1px solid rgba(201,168,76,0.15); margin-top: 0; margin-bottom: 15px;'>", unsafe_allow_html=True)

# Execute the selected page
nav_options[selected_nav]()