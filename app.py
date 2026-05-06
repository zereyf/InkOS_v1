"""
InkOS | app.py — Entry Point
==============================
v3: ARCHITECTURE ALIGNMENT
- Cleaned up duplicate CSS (Ghost menu safely moved to styles.py).
- Lifted 'cfg' into session state for global tab access.
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
        
        /* ── LOGO WORDMARK OVERHAUL ── */
        .sidebar-logo-box {
            background: linear-gradient(135deg, rgba(201,168,76,0.1) 0%, transparent 100%);
            border-left: 2px solid var(--gold);
            padding: 15px;
            border-radius: 0 8px 8px 0;
            margin-bottom: 25px;
            box-shadow: 10px 0 20px rgba(0,0,0,0.2);
        }
        .logo-text {
            font-family: 'Cinzel', serif !important;
            font-size: 1.4rem !important;
            font-weight: 700 !important;
            color: var(--gold) !important;
            letter-spacing: 3px !important;
            text-transform: uppercase;
            line-height: 1;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .logo-subtext {
            font-family: 'IBM Plex Mono', monospace !important;
            font-size: 0.55rem !important;
            color: var(--text-muted) !important;
            letter-spacing: 2px !important;
            margin-top: 5px;
            margin-left: 2px;
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
    # ⚡ BRANDED WORDMARK
    st.markdown("""
        <div class="sidebar-logo-box">
            <div class="logo-text">⚡ INK<span style="color:var(--text); opacity:0.8;">OS</span></div>
            <div class="logo-subtext">CORE NEURAL INTERFACE</div>
        </div>
    """, unsafe_allow_html=True)
    
    selected_nav = st.radio(
        "Navigation", 
        list(nav_options.keys()), 
        label_visibility="collapsed"
    )
    st.markdown("---") # Visual divider before the configuration controls

# Render the rest of the sidebar configuration controls
cfg = render_sidebar()

# ── GLOBAL STATE REGISTRATION ─────────────────────────────────────────────────
# Lift the sidebar config into the global session state.
# Now ANY tab can access st.session_state[K.APP_CONFIG] without prop-drilling.
st.session_state[K.APP_CONFIG] = cfg

# ── MAIN CONTENT EXECUTION ────────────────────────────────────────────────────
if selected_nav == t("tab_workspace"):
    nav_options[selected_nav](cfg)
else:
    nav_options[selected_nav]()
