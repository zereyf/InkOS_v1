"""
InkOS | app.py — Entry Point
==============================
v4: ARCHITECTURE ALIGNMENT
- Completely removed inline CSS. All styling delegated to ui/styles.py.
- Lifted 'cfg' into session state for global tab access.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
st.set_page_config(page_title="InkOS", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

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

# Inject centralized styling ONLY once
st.markdown(STYLES, unsafe_allow_html=True)

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

# ── PERSISTENT SIDEBAR NAVIGATION ─────────────────────────────────────────────
nav_options = {
    t("tab_workspace"):     render_workspace,
    t("tab_archive"):       render_archive,
    t("tab_security"):      render_security_log,
    t("tab_cognitive_map"): render_cognitive_map,
    t("tab_vault"):         render_vault,
    t("tab_forge"):         render_forge,
    t("tab_guide"):         render_guide,
}

# Render sidebar and capture config
cfg = render_sidebar()

# ── GLOBAL STATE REGISTRATION ─────────────────────────────────────────────────
st.session_state[K.APP_CONFIG] = cfg

# ── MAIN CONTENT EXECUTION ────────────────────────────────────────────────────
if cfg:
    selected_nav = st.session_state.get(K.APP_CONFIG, {}).get("target_model", "") # Fallback safety
    # We retrieve the actual selected nav from the radio button in the sidebar (which is now in styles)
    # Wait, the radio button needs to exist. We moved it to sidebar.py in previous patches. 

# Re-implementing the missing radio button securely inside app.py's sidebar context
with st.sidebar:
    selected_nav = st.radio(
        "Navigation", 
        list(nav_options.keys()), 
        label_visibility="collapsed"
    )

if selected_nav == t("tab_workspace"):
    nav_options[selected_nav](cfg)
else:
    nav_options[selected_nav]()
