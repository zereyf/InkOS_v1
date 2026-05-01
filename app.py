"""
VelvetCodex v7 | app.py — Entry Point
=======================================
Topology at a glance:
  config.py          — env, Groq client, constants
  state.py           — session key registry + init/reset
  engine/
    cognitive_map.py — Arabic rhetorical pattern detection
    islamic_layer.py — Islamic professional context layer
    refiner.py       — single-call refinement + audit engine
  security/
    sanitizer.py     — input sanitization + injection detection
    rate_limiter.py  — sliding window rate limiter
  ui/
    styles.py        — full CSS design system
    sidebar.py       — sidebar widget rendering
    tabs/
      workspace.py   — Tab 1: input, execution, results
      archive.py     — Tab 2: history and export
      security_log.py— Tab 3: blocked request ledger
      cognitive_map.py— Tab 4: rhetorical device reference

Rule: app.py renders layout only.
      All logic lives in engine/ and security/.
      All state keys live in state.py.
"""

import sys
import os

# ── PATH FIX ──────────────────────────────────────────────────────────────────
# Streamlit Cloud launches from the repo root, not from inside the project
# subfolder. This inserts the directory containing app.py into sys.path so all
# sibling modules (config, state, engine/, security/, ui/) resolve correctly
# regardless of where Streamlit is invoked from.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

# ── PAGE CONFIG — must be the absolute first st.* call ────────────────────────
st.set_page_config(page_title="InkOS", page_icon="⚡", layout="wide")
st.markdown("""
    <style>
        /* Force the Streamlit header (and hamburger menu) to stay fixed on mobile */
        header[data-testid="stHeader"] {
            position: fixed !important;
            top: 0 !important;
            z-index: 9999 !important;
        }
        
        /* Ensure the main content doesn't get hidden under the fixed header */
        .block-container {
            padding-top: 4rem !important; 
        }
    </style>
""", unsafe_allow_html=True)
# ── IMPORTS (safe after page config) ─────────────────────────────────────────
from config import API_KEY_MISSING
from state import init_session_state
from ui.styles import STYLES
from ui.sidebar import render_sidebar
from ui.tabs.workspace import render_workspace
from ui.tabs.archive import render_archive
from ui.tabs.security_log import render_security_log
from ui.tabs.cognitive_map import render_cognitive_map

# ── BOOT SEQUENCE ─────────────────────────────────────────────────────────────
if API_KEY_MISSING:
    st.error("SYSTEM ERROR: GROQ_API_KEY not found in environment.")
    st.stop()

init_session_state()

# ── DESIGN SYSTEM ─────────────────────────────────────────────────────────────
st.markdown(STYLES, unsafe_allow_html=True)

# ── LAYOUT ────────────────────────────────────────────────────────────────────
cfg = render_sidebar()

tab1, tab2, tab3, tab4 = st.tabs([
    "WORKSPACE", "ARCHIVE", "SECURITY", "COGNITIVE MAP"
])

with tab1: render_workspace(cfg)
with tab2: render_archive()
with tab3: render_security_log()
with tab4: render_cognitive_map()