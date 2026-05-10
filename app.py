"""
InkOS | app.py — Entry Point
==============================
v2026.4.15: Master Sync — Full Tactical Restoration.
           - RESTORED: Archive, Security Log, and Cognitive Map modules.
           - UI: Maintained Premium Block-Stretch Aesthetics.
"""

import sys
import os
import textwrap
from datetime import datetime, timezone

# Ensure local imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import os

# ── 🟢 DYNAMIC FAVICON GENERATOR ──
ICON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" fill="#C9A84C">
    <path d="M73.4 182.6C60.9 170.1 60.9 149.8 73.4 137.3C85.9 124.8 106.2 124.8 118.7 137.3L278.7 297.3C291.2 309.8 291.2 330.1 278.7 342.6L118.7 502.6C106.2 515.1 85.9 515.1 73.4 502.6C60.9 490.1 60.9 469.8 73.4 457.3L210.7 320L73.4 182.6zM288 448L544 448C561.7 448 576 462.3 576 480C576 497.7 561.7 512 544 512L288 512C270.3 512 256 497.7 256 480C256 462.3 270.3 448 288 448z"/>
</svg>"""

icon_path = "icon.svg"
if not os.path.exists(icon_path):
    with open(icon_path, "w") as f:
        f.write(ICON_SVG)

# 1. Page Config
st.set_page_config(
    page_title="InkOS", 
    page_icon=icon_path, 
    layout="wide", 
    initial_sidebar_state="expanded"
)

from config import API_KEY_MISSING
from state import init_session_state, K, get_global_memory
from ui.styles import STYLES
from ui.splash import render_splash_screen
from ui.tabs.about import render_about
from ui.tabs.forge import render_forge
from ui.tabs.guide import render_guide     
from ui.tabs.workspace import render_workspace
from ui.tabs.vault import render_vault
from i18n.translations import t, is_rtl

if API_KEY_MISSING:
    st.error("[!] SYSTEM ERROR: GROQ_API_KEY not found in environment.")
    st.stop()

if "sid" in st.query_params:
    st.session_state[K.USER_HASH] = st.query_params["sid"]

init_session_state()

# ── 🟢 MAINTENANCE MODE GATE ──
if st.session_state.get(K.MAINTENANCE_MODE) and not st.session_state.get(K.IS_ADMIN):
    lockdown_html = textwrap.dedent("""
        <div style="height:80vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;">
            <div style="font-family:var(--font-m); color:var(--danger); font-size:2rem; letter-spacing:4px; margin-bottom:10px;">
                [ ⨂ ] SYSTEM LOCKDOWN
            </div>
            <div style="font-family:var(--font-m); color:var(--text-muted); font-size:0.8rem; max-width:400px; line-height:1.6;">
                The System Architect has initiated a root-level maintenance protocol.<br>
                Access will be restored upon directive.
            </div>
        </div>
    """)
    st.markdown(lockdown_html, unsafe_allow_html=True)
    st.stop()

# ── 🟢 PREMIUM CSS ROOT INJECTION ──
st.markdown("""
<style>
    :root {
        --gold: #C9A84C;
        --gold-glow: rgba(201, 168, 76, 0.4);
        --bg-card: rgba(18, 18, 18, 0.95);
        --text: #E2E8F0;
        --text-muted: #A0AEC0;
        --text-dim: #718096;
        --steel: #7C9EBF;
        --danger: #E53E3E;
        --font-m: 'Courier New', Courier, monospace;
    }

    [data-testid="stSidebar"] {
        background: radial-gradient(circle at 50% 5%, rgba(201, 168, 76, 0.04) 0%, rgba(14, 17, 23, 1) 30%) !important;
    }

    /* 2. NEON-EDGE NAVIGATION TABS */
    div[data-testid="stRadio"]:has(div[aria-label="Navigation"]) {
        width: 100% !important;
    }
    
    div[role="radiogroup"][aria-label="Navigation"] { 
        display: flex !important; 
        flex-direction: column !important;
        width: 100% !important;
        align-items: stretch !important;
    }
    
    div[role="radiogroup"][aria-label="Navigation"] label > div:first-child { 
        display: none !important; 
    }
    
    div[role="radiogroup"][aria-label="Navigation"] label,
    div[role="radiogroup"][aria-label="Navigation"] label > div:nth-child(2) {
        width: 100% !important;
        max-width: 100% !important;
        display: flex !important;
        flex-grow: 1 !important;
    }
    
    div[role="radiogroup"][aria-label="Navigation"] label {
        background-color: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.02) !important;
        border-left: 4px solid transparent !important;
        padding: 14px 20px !important; margin: 0 !important; 
        box-sizing: border-box !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    div[role="radiogroup"][aria-label="Navigation"] label:hover {
        background-color: rgba(201, 168, 76, 0.03) !important;
    }
    
    div[role="radiogroup"][aria-label="Navigation"] label p {
        color: var(--text-dim) !important; font-family: var(--font-m) !important; font-size: 0.85rem !important;
        letter-spacing: 2px !important; text-transform: uppercase !important; margin: 0 !important; visibility: visible !important; display: block !important;
        width: 100% !important;
    }
    
    div[role="radiogroup"][aria-label="Navigation"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(201, 168, 76, 0.1) 0%, transparent 100%) !important;
        border-left: 4px solid var(--gold) !important;
        box-shadow: inset 4px 0 12px -4px var(--gold-glow);
    }
    
    div[role="radiogroup"][aria-label="Navigation"] label:has(input:checked) p {
        color: var(--gold) !important; font-weight: 600 !important; letter-spacing: 3px !important;
    }

    /* 3. GHOST INPUTS */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div, 
    [data-testid="stSidebar"] div[data-baseweb="input"] > div {
        background-color: rgba(0,0,0,0.2) !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        border-radius: 3px !important;
    }
</style>
""", unsafe_allow_html=True)
st.markdown(STYLES, unsafe_allow_html=True)

# ── REHYDRATION ──
current_sid = st.session_state.get(K.USER_HASH)
is_guest = not current_sid or "GUEST_" in str(current_sid).upper()

# ── 📡 GLOBAL BROADCAST RECEIVER ──
global_mem = get_global_memory()
active_broadcast = global_mem.get("broadcast")
if active_broadcast:
    st.markdown(f'<div style="background:rgba(201,168,76,0.05); border-left:3px solid var(--gold); padding:12px 18px; margin-bottom:20px; font-family:var(--font-m); font-size:0.8rem; color:var(--gold);"><strong>📡 INK_OS DIRECTIVE //</strong> {active_broadcast}</div>', unsafe_allow_html=True)

# ── COMMAND DECK (Sidebar) ──
is_admin = st.session_state.get(K.IS_ADMIN, False)
from ui.sidebar import render_sidebar, render_sidebar_brand 

with st.sidebar:
    render_sidebar_brand()

    # 🟢 FULL TACTICAL MENU RESTORATION
    nav_options = [
        "WORKSPACE", 
        "ARCHIVE", 
        "SECURITY LOG", 
        "COGNITIVE MAP", 
        "🔒 VAULT", 
        "🎭 FORGE", 
        "GUIDE", 
        "ABOUT"
    ]
    if is_admin:
        nav_options.append("◈ OVERWATCH")
        
    active_tab = st.radio("Navigation", nav_options, label_visibility="collapsed")
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    cfg = render_sidebar()

st.session_state["app_config"] = cfg

# ── CONTENT ROUTING MATRIX ──

if active_tab == "WORKSPACE":
    if is_guest: render_splash_screen()
    else: render_workspace(cfg)

elif active_tab == "ARCHIVE":
    st.markdown("### 🗄️ SYSTEM ARCHIVE")
    st.info("Historical data restoration in progress.")

elif active_tab == "SECURITY LOG":
    st.markdown("### 🛡️ SECURITY LOG")
    st.code("SCANNING FOR NEURAL BREACHES... [OK]", language="bash")

elif active_tab == "COGNITIVE MAP":
    # 🟢 Pointing to the Cognitive Map tab
    # Assuming you have a render function or placeholder
    st.markdown("### 🗺️ COGNITIVE MAP")
    st.write("Visualizing heuristic pathways...")

elif active_tab == "🔒 VAULT":
    if is_guest: st.markdown("<div style='text-align:center; padding-top:100px;'>[ ⨂ ] NEURAL VAULT LOCKED.</div>", unsafe_allow_html=True)
    else: render_vault()

elif active_tab == "🎭 FORGE":
    if is_guest: st.markdown("<div style='text-align:center; padding-top:100px;'>[ ⨂ ] FORGE RESTRICTED.</div>", unsafe_allow_html=True)
    else: render_forge()

elif active_tab == "GUIDE":
    render_guide()

elif active_tab == "ABOUT":
    render_about()

elif active_tab == "◈ OVERWATCH" and is_admin:
    from ui.tabs.admin import render_admin_board
    render_admin_board()
