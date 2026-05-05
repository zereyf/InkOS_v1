"""
InkOS | app.py — Entry Point
==============================
v2.1: THE UX OVERHAUL + COMMAND PILL SUPPORT
- Added 'field-sizing' for auto-expanding text area.
- Added column alignment for circular action buttons.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
# FIX: Forced sidebar to remain expanded so users never lose the navigation menu
st.set_page_config(page_title="InkOS", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
        /* Sticky Header */
        header[data-testid="stHeader"] {
            position: fixed !important; top: 0 !important; z-index: 9999 !important;
        }
        .block-container { padding-top: 4rem !important; }
        
        /* Clean up the sidebar radio buttons to look like a premium SaaS menu */
        div[data-testid="stSidebarNav"] {display: none;} /* Hide default multipage nav */
        div[role="radiogroup"] > label {
            padding: 8px 12px;
            border-radius: 6px;
            transition: all 0.2s ease-in-out;
            cursor: pointer;
        }
        div[role="radiogroup"] > label:hover {
            background-color: rgba(201,168,76,0.1);
        }

        /* ── COMMAND PILL STRUCTURAL UPDATES ── */
        div[data-testid="stTextArea"] textarea {
            field-sizing: content !important; /* The Magic: Auto-grows as you type */
            min-height: 56px !important;
            max-height: 350px !important;
        }

        /* Align circular Mic/Execute buttons to the bottom of the pill as it grows */
        [data-testid="column"] {
            display: flex;
            align-items: flex-end;
        }

        /* Stylize action buttons into hardware circles */
        .stButton > button, 
        [data-testid="stAudioInput"] button {
            border-radius: 50% !important;
            width: 52px !important;
            height: 52px !important;
            min-width: 52px !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
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

with st.sidebar:
    st.markdown("### ⚡ InkOS")
    selected_nav = st.radio(
        "Navigation", 
        list(nav_options.keys()), 
        label_visibility="collapsed"
    )
    st.markdown("---") # Visual divider before the configuration controls

# Render the rest of the sidebar configuration controls
cfg = render_sidebar()

# ── MAIN CONTENT EXECUTION ────────────────────────────────────────────────────
# The main UI is now completely clean of navigation clutter.
if selected_nav == t("tab_workspace"):
    nav_options[selected_nav](cfg)
else:
    nav_options[selected_nav]()
