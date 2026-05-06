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
    /* 1. STICKY HEADER & SPACING */
    header[data-testid="stHeader"] { position: fixed !important; top: 0 !important; z-index: 9999 !important; }
    .block-container { padding-top: 4rem !important; }
    
    /* 2. LOGO WORDMARK */
    .sidebar-logo-box {
        background: linear-gradient(135deg, rgba(201,168,76,0.1) 0%, transparent 100%);
        border-left: 2px solid var(--gold);
        padding: 15px; border-radius: 0 8px 8px 0; margin-bottom: 25px;
        box-shadow: 10px 0 20px rgba(0,0,0,0.2);
    }
    .logo-text {
        font-family: 'Cinzel', serif !important; font-size: 1.4rem !important;
        font-weight: 700 !important; color: var(--gold) !important;
        letter-spacing: 3px !important; text-transform: uppercase;
        line-height: 1; display: flex; align-items: center; gap: 10px;
    }
    .logo-subtext {
        font-family: 'IBM Plex Mono', monospace !important; font-size: 0.55rem !important;
        color: var(--text-muted) !important; letter-spacing: 2px !important;
        margin-top: 5px; margin-left: 2px;
    }

            /* 3. SAAS SIDEBAR NAVIGATION & RADIO OVERHAUL (GHOST AESTHETIC) */
    div[data-testid="stSidebarNav"] { display: none; }
    
    /* SURGICAL NUKE: Hide ONLY the exact div that contains the radio input/circle */
    [data-testid="stSidebar"] [role="radiogroup"] [data-baseweb="radio"] > div:has(input[type="radio"]) {
        display: none !important;
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
    }

    /* ITEM CONTAINERS */
    [data-testid="stSidebar"] [role="radiogroup"] label {
        width: 100% !important; padding: 10px 14px !important; margin-bottom: 4px !important;
        border-radius: 4px !important; background: transparent !important;
        border-left: 3px solid transparent !important; transition: all 0.2s ease !important;
        cursor: pointer !important; display: block !important;
    }
    
    /* TEXT TYPOGRAPHY (Explicitly forcing display) */
    [data-testid="stSidebar"] [role="radiogroup"] label div,
    [data-testid="stSidebar"] [role="radiogroup"] label p,
    [data-testid="stSidebar"] [role="radiogroup"] label span {
        font-family: 'IBM Plex Mono', monospace !important; font-size: 0.75rem !important;
        letter-spacing: 0.15em !important; color: #85929E !important; 
        text-transform: uppercase !important; margin: 0 !important;
        transition: color 0.2s ease !important; 
        display: block !important; /* Forces visibility if inherited none */
    }
    
    /* HOVER STATE */
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(201, 168, 76, 0.04) !important;
        border-left: 3px solid rgba(201, 168, 76, 0.4) !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover div,
    [data-testid="stSidebar"] [role="radiogroup"] label:hover p,
    [data-testid="stSidebar"] [role="radiogroup"] label:hover span { 
        color: #E2D5BC !important; 
    }
    
    /* ACTIVE/SELECTED STATE */
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(201,168,76,0.12) 0%, transparent 100%) !important;
        border-left: 3px solid #C9A84C !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) div,
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p,
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) span {
        color: #C9A84C !important; font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(201,168,76,0.2) !important;
    }

    
    /* SURGICALLY KILL RADIO CIRCLES GLOBALLY */
    /* Targets the specific drawing div immediately following the hidden radio input */
    [data-testid="stSidebar"] [role="radiogroup"] input[type="radio"] + div {
        display: none !important;
    }

    /* ITEM CONTAINERS (Adapts to both Nav Menu and Linguistic Source) */
    [data-testid="stSidebar"] [role="radiogroup"] label {
        width: 100% !important; padding: 10px 14px !important; margin-bottom: 4px !important;
        border-radius: 4px !important; background: transparent !important;
        border-left: 3px solid transparent !important; transition: all 0.2s ease !important;
        cursor: pointer !important; display: block !important;
    }
    
    /* TEXT TYPOGRAPHY & ACCESSIBILITY FIX */
    [data-testid="stSidebar"] [role="radiogroup"] label div,
    [data-testid="stSidebar"] [role="radiogroup"] label p,
    [data-testid="stSidebar"] [role="radiogroup"] label span {
        font-family: 'IBM Plex Mono', monospace !important; font-size: 0.75rem !important;
        letter-spacing: 0.15em !important; 
        color: #85929E !important; /* Brightened from #5D6D7E for readable contrast */
        text-transform: uppercase !important; margin: 0 !important;
        transition: color 0.2s ease !important; display: inline-block !important;
    }
    
    /* HOVER STATE */
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(201, 168, 76, 0.04) !important;
        border-left: 3px solid rgba(201, 168, 76, 0.4) !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover div,
    [data-testid="stSidebar"] [role="radiogroup"] label:hover p,
    [data-testid="stSidebar"] [role="radiogroup"] label:hover span { 
        color: #E2D5BC !important; 
    }
    
    /* ACTIVE/SELECTED STATE */
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(201,168,76,0.12) 0%, transparent 100%) !important;
        border-left: 3px solid #C9A84C !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) div,
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p,
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) span {
        color: #C9A84C !important; font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(201,168,76,0.2) !important;
    }

    
    /* KILL RADIO CIRCLES: Targeted removal of the UI element only */
    [data-testid="stSidebar"] [role="radiogroup"] [data-baseweb="radio"] > div:nth-child(1) {
        display: none !important;
    }

    /* ITEM CONTAINERS */
    [data-testid="stSidebar"] [role="radiogroup"] label {
        width: 100% !important; padding: 10px 14px !important; margin-bottom: 4px !important;
        border-radius: 4px !important; background: transparent !important;
        border-left: 3px solid transparent !important; transition: all 0.2s ease !important;
        cursor: pointer !important; display: block !important;
    }
    
    /* TEXT TYPOGRAPHY (Forced visibility) */
    [data-testid="stSidebar"] [role="radiogroup"] label div,
    [data-testid="stSidebar"] [role="radiogroup"] label p,
    [data-testid="stSidebar"] [role="radiogroup"] label span {
        font-family: 'IBM Plex Mono', monospace !important; font-size: 0.75rem !important;
        letter-spacing: 0.15em !important; color: #5D6D7E !important; 
        text-transform: uppercase !important; margin: 0 !important;
        transition: color 0.2s ease !important; display: inline-block !important;
    }
    
    /* HOVER & ACTIVE STATES */
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(201, 168, 76, 0.04) !important;
        border-left: 3px solid rgba(201, 168, 76, 0.4) !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover * { color: #E2D5BC !important; }
    
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {
        background: linear-gradient(90deg, rgba(201,168,76,0.12) 0%, transparent 100%) !important;
        border-left: 3px solid #C9A84C !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) * {
        color: #C9A84C !important; font-weight: 600 !important;
        text-shadow: 0 0 10px rgba(201,168,76,0.2) !important;
    }

        /* 4. HORIZONTAL LANGUAGE SWITCHER (RIGID ALIGNMENT) */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:has(button) {
        display: flex !important; flex-direction: row !important;
        flex-wrap: nowrap !important; gap: 6px !important;
        align-items: center !important; margin-bottom: 10px !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"]:has(button) > div {
        min-width: 0 !important; flex: 1 1 0% !important;
    }

    /* Enforce identical geometry across all button states */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button {
        height: 36px !important; margin: 0 !important; padding: 0 !important;
        display: flex !important; align-items: center !important; justify-content: center !important;
        border: 1px solid var(--text-dim) !important; background: transparent !important;
        font-family: var(--font-m) !important; font-size: 0.7rem !important; color: var(--text-muted) !important;
        border-radius: 4px !important; transition: none !important; /* Disables click/hover vertical shift */
    }

    /* Target active state via Streamlit's 'primary' kind attribute */
    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button[kind="primary"] {
        border: 1px solid var(--gold) !important;
        background: var(--gold-glow) !important;
        color: var(--gold) !important;
    }

    [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] button[kind="secondary"]:hover {
        border: 1px solid var(--gold-border) !important;
        color: var(--text) !important;
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
