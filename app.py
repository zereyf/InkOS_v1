"""
InkOS | app.py — Entry Point
v1: Sidebar Branding Restored.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
st.set_page_config(page_title="InkOS", page_icon="⚡", layout="wide")

from state import init_session_state
from ui.styles import load_css
from ui.sidebar import render_sidebar
from ui.tabs.workspace import render_workspace
# ... (rest of your imports)

init_session_state()
load_css()

# ── RTL & SIDEBAR BRANDING FIX ───────────────────────────────────────────────
st.markdown("""
    <style>
        header[data-testid="stHeader"] { z-index: 1000 !important; }
        .block-container { padding-top: 2rem !important; }
        
        /* Make sure the sidebar wordmark looks elite */
        [data-testid="stSidebar"] .vc-wordmark {
            text-shadow: 0 0 10px rgba(201,168,76,0.3);
            margin-top: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# (Insert your RTL/LTR Javascript here)

cfg = render_sidebar()

# ── NAVIGATION ────────────────────────────────────────────────────────────────
# (Insert your nav_options and selectbox logic here)
# ...