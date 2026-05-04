"""
InkOS | app.py — Entry Point
==============================
v9: Language switcher — EN/AR/FR with RTL support.
Mobile-Optimized Selectbox Navigation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
st.set_page_config(page_title="InkOS", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
        /* Sticky Header */
        header[data-testid="stHeader"] {
            position: fixed !important; top: 0 !important; z-index: 9999 !important;
        }
        .block-container { padding-top: 4rem !important; }
        
        /* Make the navigation selectbox look more premium */
        div[data-testid="stSelectbox"] > div[data-baseweb="select"] {
            border-color: rgba(201,168,76,0.3) !important;
            background-color: var(--bg-raised) !important;
        }
    </style>
""", unsafe_allow_html=True)

from config import API_KEY_MISSING
from state import init_session_state, K
from ui.styles import STYLES
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
st.markdown(STYLES, unsafe_allow_html=True)

# ── RTL MODE ──────────────────────────────────────────────────────────────────
# When Arabic UI is active, inject a JS snippet that adds the
# "rtl-mode" CSS class to the stApp element.
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

# The Dropdown Navigation Bar
selected_nav = st.selectbox(
    "Navigation", 
    list(nav_options.keys()), 
    label_visibility="collapsed"
)

# A subtle divider to separate navigation from the content
st.markdown("<hr style='border: none; border-bottom: 1px solid rgba(201,168,76,0.15); margin-top: 0; margin-bottom: 15px;'>", unsafe_allow_html=True)

# Execute the selected page
nav_options[selected_nav]()
