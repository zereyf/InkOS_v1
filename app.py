"""
InkOS | app.py — Entry Point
==============================
v2026.4.17: Secure Navigation Patch.
           - REFACTORED: Dynamic nav_options construction (Ghost Lockdown).
           - REFACTORED: Content Routing Matrix for authenticated gates.
"""

import sys
import os
import textwrap
import streamlit as st
from datetime import datetime, timezone

# Ensure local imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 1. Page Config
icon_path = "icon.svg" # Assuming this exists from previous runs
st.set_page_config(
    page_title="InkOS", 
    page_icon=icon_path if os.path.exists(icon_path) else "❖", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

from config import API_KEY_MISSING
from state import init_session_state, K, get_global_memory
from ui.styles import STYLES
from ui.splash import render_splash_screen

# ── 🟢 TACTICAL MODULE IMPORTS ──
from ui.tabs.workspace import render_workspace
from ui.tabs.archive import render_archive
from ui.tabs.security_log import render_security_log
from ui.tabs.cognitive_map import render_cognitive_map
from ui.tabs.vault import render_vault
from ui.tabs.forge import render_forge
from ui.tabs.guide import render_guide
from ui.tabs.about import render_about

from i18n.translations import t

if API_KEY_MISSING:
    st.error("[!] SYSTEM ERROR: GROQ_API_KEY not found.")
    st.stop()

if "sid" in st.query_params:
    st.session_state[K.USER_HASH] = st.query_params["sid"]

init_session_state()

# ── 🟢 MAINTENANCE MODE GATE ──
global_mem = get_global_memory()
is_admin = st.session_state.get(K.IS_ADMIN, False)

if global_mem.get("maintenance_mode") and not is_admin:
    st.markdown("""
        <div style="height:80vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;">
            <div style="font-family:var(--font-m); color:var(--danger); font-size:2rem; letter-spacing:4px;">[ ⨂ ] SYSTEM LOCKDOWN</div>
            <div style="font-family:var(--font-m); color:var(--text-muted); font-size:0.8rem; margin-top:10px;">Maintenance protocol active. Access restricted.</div>
        </div>
    """, unsafe_allow_html=True)
    st.stop()

# ── 🟢 CSS ROOT INJECTION ──
st.markdown(STYLES, unsafe_allow_html=True)

# ── 🟢 DYNAMIC NAVIGATION MATRIX ──
current_sid = st.session_state.get(K.USER_HASH)
is_guest = not current_sid or "GUEST_" in str(current_sid).upper()
is_admin = st.session_state.get(K.IS_ADMIN, False)

# 1. Build the list based on clearance levels
nav_options = ["WORKSPACE"]

# Identity-Gated Tabs (Vanish for Guests)
if not is_guest:
    nav_options.extend(["VAULT", "FORGE", "COGNITIVE MAP"])

# Utility Tabs (Always visible)
nav_options.extend(["ARCHIVE", "SECURITY LOG", "GUIDE", "ABOUT"])

# Root-Gated Tabs (Vanish for non-admins)
if is_admin:
    nav_options.append("◈ OVERWATCH")

# ── 🟢 COMMAND DECK (Sidebar) ──
from ui.sidebar import render_sidebar, render_sidebar_brand 
with st.sidebar:
    render_sidebar_brand()
    
    # Render the Radio with the filtered list
    active_tab = st.radio("Navigation", nav_options, label_visibility="collapsed")
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    cfg = render_sidebar()

# ── 🟢 CONTENT ROUTING MATRIX ──
if active_tab == "WORKSPACE":
    if is_guest: render_splash_screen()
    else: render_workspace(cfg)

elif active_tab == "VAULT":
    render_vault()

elif active_tab == "FORGE":
    render_forge()

elif active_tab == "ARCHIVE":
    render_archive()

elif active_tab == "SECURITY LOG":
    render_security_log()

elif active_tab == "COGNITIVE MAP":
    render_cognitive_map()

elif active_tab == "GUIDE":
    render_guide()

elif active_tab == "ABOUT":
    render_about()

elif active_tab == "◈ OVERWATCH" and is_admin:
    from ui.tabs.admin import render_admin_board
    render_admin_board()
