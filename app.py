"""
InkOS | app.py — Entry Point
==============================
v21.1: Zenith Neural Edition (Persistence Patch).
       - FIXED: URL-based Neural Rehydration condition.
       - REFACTORED: Dynamic nav_options (Ghost Lockdown).
       - HARDENED: Unified State Initialization.
"""

import sys
import os
import streamlit as st

# Ensure local imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from state import init_session_state, K, get_global_memory
from config import API_KEY_MISSING

# 1. Page Config (Must be first)
icon_path = "icon.svg"
st.set_page_config(
    page_title="InkOS", 
    page_icon=icon_path if os.path.exists(icon_path) else "❖", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ── 🟢 NEURAL CORE INITIALIZATION ──
init_session_state()

# ── 🟢 URL REHYDRATION HOOK (PATCHED) ──
# Only triggers if USER_HASH is None (Fresh load), preventing refresh logouts.
if "sid" in st.query_params and st.session_state.get(K.USER_HASH) is None:
    sid = st.query_params["sid"]
    st.session_state[K.USER_HASH] = sid
    
    from vault.vault_engine import rehydrate_session
    user_data = rehydrate_session(sid)
    
    # Instate DNA (Fallback to defaults if DB returns empty)
    dna = user_data.get("dna", {})
    st.session_state[K.INK_DNA] = dna.get("ink") or st.session_state[K.INK_DNA]
    st.session_state[K.INTEL_DNA] = dna.get("intel") or st.session_state[K.INTEL_DNA]
    st.session_state[K.HIKMAH_DNA] = dna.get("hikmah") or st.session_state[K.HIKMAH_DNA]
    
    # Instate Personas
    st.session_state[K.PERSONA_LIST] = user_data.get("personas", [])

# ── 🟢 MODULE IMPORTS ──
from ui.styles import STYLES
from ui.splash import render_splash_screen
from ui.sidebar import render_sidebar, render_sidebar_brand 
from ui.tabs.workspace import render_workspace
from i18n.translations import t

# (Other imports)
from ui.tabs.vault import render_vault
from ui.tabs.forge import render_forge
from ui.tabs.archive import render_archive
from ui.tabs.security_log import render_security_log
from ui.tabs.cognitive_map import render_cognitive_map
from ui.tabs.guide import render_guide
from ui.tabs.about import render_about

if API_KEY_MISSING:
    st.error("[!] SYSTEM ERROR: GROQ_API_KEY not found.")
    st.stop()

# ── 🟢 MAINTENANCE & SECURITY GATES ──
global_mem = get_global_memory()
is_admin = st.session_state.get(K.IS_ADMIN, False)

if global_mem.get("maintenance_mode") and not is_admin:
    st.markdown('<div class="maintenance-lock">[ ⨂ ] SYSTEM LOCKDOWN</div>', unsafe_allow_html=True)
    st.stop()

st.markdown(STYLES, unsafe_allow_html=True)

# ── 🟢 NAVIGATION MATRIX ──
current_sid = st.session_state.get(K.USER_HASH)
is_guest = not current_sid or "GUEST_" in str(current_sid).upper()

nav_options = ["WORKSPACE"]
if not is_guest:
    nav_options.extend(["VAULT", "FORGE", "COGNITIVE MAP"])
nav_options.extend(["ARCHIVE", "SECURITY LOG", "GUIDE", "ABOUT"])

if is_admin:
    nav_options.append("◈ OVERWATCH")

# ── 🟢 SIDEBAR RENDER ──
with st.sidebar:
    render_sidebar_brand()
    nav_map = {"⚡ WORKSPACE":"WORKSPACE","🔒 VAULT":"VAULT","⚙️ FORGE":"FORGE","🧠 COGNITIVE MAP":"COGNITIVE MAP","📁 ARCHIVE":"ARCHIVE","🛡️ SECURITY LOG":"SECURITY LOG","📖 GUIDE":"GUIDE","◈  ABOUT":"ABOUT"}
    if is_admin: nav_map["◈ OVERWATCH"] = "◈ OVERWATCH"
    allowed = [k for k,v in nav_map.items() if v in nav_options]
    if "active_tab" not in st.session_state: st.session_state["active_tab"] = "WORKSPACE"
    for label in allowed:
        active = nav_map[label] == st.session_state["active_tab"]
        if st.button(label, key=f"nav_{label}", use_container_width=True, type="secondary"):
            st.session_state["active_tab"] = nav_map[label]
    active_tab = st.session_state["active_tab"]
    cfg = render_sidebar()

# ── 🟢 ROUTING ──
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
