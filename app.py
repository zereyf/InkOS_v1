"""
InkOS | app.py — Entry Point
==============================
v2026.4.10: Master Sync — Tactical Sidebar Evolution.
           - RESTORED: Vertical Sidebar Navigation Matrix.
           - UI: Custom Cyber-Noir CSS injected for radio-menu.
           - INTEGRATED: Global Broadcast Receiver.
"""

import sys
import os
import textwrap
from datetime import datetime, timezone

# Ensure local imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

# 1. Page Config must be first
st.set_page_config(
    page_title="InkOS", 
    page_icon="❖", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

from config import API_KEY_MISSING
from state import init_session_state, K, get_global_memory
from ui.styles import STYLES
from ui.sidebar import render_sidebar
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

# ── URL REHYDRATION (SID ONLY) ──────────────────────────────────────────────
if "sid" in st.query_params:
    st.session_state[K.USER_HASH] = st.query_params["sid"]

# ── INITIALIZE STATE ────────────────────────────────────────────────────────
init_session_state()

# ── 🟢 MAINTENANCE MODE GATE ──────────────────────────────────────
if st.session_state.get(K.MAINTENANCE_MODE) and not st.session_state.get(K.IS_ADMIN):
    lockdown_html = textwrap.dedent("""
        <div style="height:80vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;">
            <div style="font-family:var(--font-m); color:var(--danger); font-size:2rem; letter-spacing:4px; margin-bottom:10px;">
                [ ⨂ ] SYSTEM LOCKDOWN
            </div>
            <div style="font-family:var(--font-m); color:var(--text-muted); font-size:0.8rem; max-width:400px; line-height:1.6;">
                The System Architect has initiated a root-level maintenance protocol.<br>
                All neural uplinks have been temporarily severed.<br><br>
                <span style="color:var(--gold);">Access will be restored upon directive.</span>
            </div>
        </div>
    """)
    st.markdown(lockdown_html, unsafe_allow_html=True)
    st.stop()

# ── 🟢 BOOTSTRAP VALIDATION MATRIX ─────────────────────────────────
from config import validate_config
config_errors = validate_config()
if config_errors:
    for err in config_errors:
        st.error(f'[!] CONFIG ERROR: {err}')
    st.stop()

# ── CSS ROOT INJECTION ──────────────────────────────────────────────────────
st.markdown("""
<style>
    :root {
        --gold: #C9A84C;
        --gold-border: rgba(201, 168, 76, 0.3);
        --bg-card: rgba(18, 18, 18, 0.95);
        --text: #E2E8F0;
        --text-muted: #A0AEC0;
        --text-dim: #718096;
        --steel: #7C9EBF;
        --danger: #E53E3E;
        --font-m: 'Courier New', Courier, monospace;
        --font-d: 'Impact', sans-serif;
    }
</style>
""", unsafe_allow_html=True)
st.markdown(STYLES, unsafe_allow_html=True)

# ── REHYDRATION PROTOCOL ─────────────────────────────────────────────
current_sid = st.session_state.get(K.USER_HASH)
is_guest = not current_sid or "GUEST_" in str(current_sid).upper()

if not is_guest and not st.session_state.get("boot_rehydrated"):
    from vault.vault_engine import rehydrate_session
    recovered = rehydrate_session(current_sid)
    if recovered:
        st.session_state[K.PERSONA_LIST] = recovered.get("personas", [])
        dna = recovered.get("dna", {})
        for key in ["ink", "intel", "hikmah"]:
            if dna.get(key): st.session_state[getattr(K, f"{key.upper()}_DNA")] = dna[key]
    st.session_state["boot_rehydrated"] = True

if "boot_complete" not in st.session_state:
    st.toast("> SYSTEM INITIALIZED" if is_guest else f"[◈] IDENTITY LATCH: {current_sid[:8]}")
    st.session_state["boot_complete"] = True

rtl_js = f"<script>const app = window.parent.document.querySelector('.stApp'); if (app) app.classList.{'add' if is_rtl() else 'remove'}('rtl-mode');</script>"
st.markdown(rtl_js, unsafe_allow_html=True)

# ── 📡 GLOBAL BROADCAST RECEIVER ────────────────────────────────────────────
global_mem = get_global_memory()
active_broadcast = global_mem.get("broadcast")

if active_broadcast:
    st.markdown(f"""
    <div style="background: rgba(201, 168, 76, 0.05); border-left: 3px solid var(--gold); padding: 12px 18px; margin-bottom: 20px; font-family: var(--font-m); font-size: 0.8rem; color: var(--gold); letter-spacing: 1px; border-radius: 2px;">
        <strong style="color:#E2E8F0;">📡 INK_OS DIRECTIVE //</strong> {active_broadcast}
    </div>
    """, unsafe_allow_html=True)

# ── 🟢 TACTICAL MENU CSS HACK ───────────────────────────────────────────────
st.markdown("""
<style>
    /* 1. Target ONLY the Navigation Radio Group (Protects Input Language) */
    div[role="radiogroup"][aria-label="Navigation"] {
        gap: 0 !important;
    }
    
    /* 2. Hide specifically the radio circle, not the text */
    div[role="radiogroup"][aria-label="Navigation"] label > div:first-child {
        display: none !important;
    }
    
    /* 3. Style the Navigation blocks */
    div[role="radiogroup"][aria-label="Navigation"] label {
        background-color: transparent !important;
        border: 1px solid rgba(255,255,255,0.01) !important;
        border-bottom: 1px solid rgba(255,255,255,0.05) !important;
        border-left: 4px solid transparent !important;
        padding: 12px 20px !important;
        margin: 0 !important;
        width: 100% !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    
    /* 4. Hover effect */
    div[role="radiogroup"][aria-label="Navigation"] label:hover {
        background-color: rgba(255,255,255,0.02) !important;
    }
    
    /* 5. Base Text Styling */
    div[role="radiogroup"][aria-label="Navigation"] label p {
        color: var(--text-dim) !important;
        font-family: var(--font-m) !important;
        font-size: 0.85rem !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        margin: 0 !important;
        visibility: visible !important;
        display: block !important;
    }
    
    /* 6. 🟢 ACTIVE STATE STYLING */
    div[role="radiogroup"][aria-label="Navigation"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(201, 168, 76, 0.08) 0%, transparent 100%) !important;
        border-left: 4px solid var(--gold) !important;
        border-top: 1px solid rgba(201, 168, 76, 0.05) !important;
        border-bottom: 1px solid rgba(201, 168, 76, 0.05) !important;
    }
    
    /* Active Text Color */
    div[role="radiogroup"][aria-label="Navigation"] label:has(input:checked) p {
        color: var(--gold) !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)



# ── COMMAND DECK (Sidebar) ──────────────────────────────────────────────────
is_admin = st.session_state.get(K.IS_ADMIN, False)

with st.sidebar:
    if is_guest:
        st.markdown("<div style='text-align:center; color:var(--danger); font-family:var(--font-m); font-size:0.7rem; letter-spacing:2px; margin-bottom:15px;'>[ ⨂ ] ACCESS RESTRICTED</div>", unsafe_allow_html=True)
    
    # NAVIGATION MATRIX
    nav_options = ["WORKSPACE", "🔒 VAULT", "🎭 FORGE", "GUIDE", "ABOUT"]
    if is_admin:
        nav_options.append("◈ OVERWATCH")
        
    active_tab = st.radio("Navigation", nav_options, label_visibility="collapsed")
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    
    # The rest of the sidebar logic loads underneath
    cfg = render_sidebar()

st.session_state["app_config"] = cfg

# ── CONTENT ROUTING MATRIX ──────────────────────────────────────────────────

if active_tab == "WORKSPACE":
    if is_guest:
        render_splash_screen()
    else:
        render_workspace(cfg)

elif active_tab == "🔒 VAULT":
    if is_guest:
        st.markdown("<div style='text-align:center; font-family:var(--font-m); color:var(--text-dim); padding-top:100px;'>[ ⨂ ] NEURAL VAULT LOCKED.</div>", unsafe_allow_html=True)
    else:
        render_vault()

elif active_tab == "🎭 FORGE":
    if is_guest:
        st.markdown("<div style='text-align:center; font-family:var(--font-m); color:var(--text-dim); padding-top:100px;'>[ ⨂ ] FORGE RESTRICTED.</div>", unsafe_allow_html=True)
    else:
        render_forge()

elif active_tab == "GUIDE":
    render_guide()

elif active_tab == "ABOUT":
    render_about()

elif active_tab == "◈ OVERWATCH" and is_admin:
    from ui.tabs.admin import render_admin_board
    render_admin_board()
