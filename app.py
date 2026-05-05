"""
InkOS | app.py — Entry Point
==============================
v2: THE UX OVERHAUL
- Killed the clunky dropdown navigation.
- Implemented persistent, clean sidebar routing.
- Added custom CSS to style the radio buttons like a premium SaaS menu.
- Preserved RTL support and mobile-optimized constraints.
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
        
        /* ── SAAS SIDEBAR NAVIGATION OVERHAUL ── */
        div[data-testid="stSidebarNav"] {display: none;}
        
        /* 1. Nuke the native radio circles */
        div[role="radiogroup"] > label > div:first-child {
            display: none !important;
        }
        
        /* 2. Style the menu item containers */
        div[role="radiogroup"] > label {
            width: 100% !important;
            padding: 12px 16px !important;
            margin-bottom: 4px !important;
            border-radius: 4px !important;
            background: transparent !important;
            border-left: 3px solid transparent !important;
            transition: all 0.2s ease !important;
            cursor: pointer !important;
        }
        
        /* 3. Typography for inactive items */
        div[role="radiogroup"] > label p {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.75rem !important;
            letter-spacing: 0.15em !important;
            color: #5D6D7E !important; /* text-muted */
            text-transform: uppercase !important;
            margin: 0 !important;
            transition: color 0.2s ease !important;
        }
        
        /* 4. Hover State */
        div[role="radiogroup"] > label:hover {
            background: rgba(201, 168, 76, 0.04) !important;
            border-left: 3px solid rgba(201, 168, 76, 0.4) !important;
        }
        div[role="radiogroup"] > label:hover p {
            color: #E2D5BC !important; /* text glow on hover */
        }
        
        /* 5. Active/Selected State Magic */
        div[role="radiogroup"] > label:has(input:checked) {
            background: linear-gradient(90deg, rgba(201,168,76,0.12) 0%, transparent 100%) !important;
            border-left: 3px solid #C9A84C !important;
        }
        
        div[role="radiogroup"] > label:has(input:checked) p {
            color: #C9A84C !important;
            font-weight: 600 !important;
            text-shadow: 0 0 10px rgba(201,168,76,0.2) !important;
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
