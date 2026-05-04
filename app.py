"""
InkOS | app.py — Entry Point
==============================
v1: Language switcher — EN/AR/FR with RTL support.
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
        
        /* Tab Fix 1: VelvetCodex Gold Underline */
        .stTabs [data-baseweb="tab-highlight"] {
            background-color: #C9A84C !important;
        }

        /* Tab Fix 2: Horizontal Swipe on Mobile (Prevents wrapping bug) */
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: nowrap !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
            padding-bottom: 5px;
            scrollbar-width: none; /* Hide scrollbar Firefox */
        }
        
        /* Hide scrollbar Chrome/Safari */
        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none; 
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
# This flips all text direction and font without touching any component code.
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

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    t("tab_workspace"),
    t("tab_archive"),
    t("tab_security"),
    t("tab_cognitive_map"),
    t("tab_vault"),
    t("tab_forge"),
    t("tab_guide"),
])

with tab1: render_workspace(cfg)
with tab2: render_archive()
with tab3: render_security_log()
with tab4: render_cognitive_map()
with tab5: render_vault()
with tab6: render_forge()
with tab7: render_guide()
