"""
InkOS | app.py — Entry Point
==============================
v2026.4.4: Master Sync — Bootloader Hardened.
           - Destroyed duplicate Persona Rehydration trap.
           - Injected Task 10 Startup Validation matrix.
           - V3 Brute-Force Tactical Toggle Override Active.
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
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

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

# ── URL REHYDRATION (SID ONLY) ──────────────────────────────────────────────
if "sid" in st.query_params:
    st.session_state[K.USER_HASH] = st.query_params["sid"]

# ── INITIALIZE STATE ────────────────────────────────────────────────────────
init_session_state()

# ── 🟢 TASK 10: BOOTSTRAP VALIDATION MATRIX ─────────────────────────────────
from config import validate_config
config_errors = validate_config()
if config_errors:
    for err in config_errors:
        st.error(f'CONFIG ERROR: {err}')
    st.stop()

# ── CSS ROOT INJECTION: The "AmeerInk" Grit Variables ──────────────────────
st.markdown("""
<style>
    :root {
        --gold: #C9A84C;
        --gold-border: rgba(201, 168, 76, 0.3);
        --gold-dim: rgba(201, 168, 76, 0.6);
        --bg-card: rgba(18, 18, 18, 0.95);
        --text: #E2E8F0;
        --text-muted: #A0AEC0;
        --text-dim: #718096;
        --steel: #7C9EBF;
        --danger: #E53E3E;
        --font-m: 'Courier New', Courier, monospace;
        --font-d: 'Impact', sans-serif;
        --font-a: 'Amiri', serif;
    }
    @keyframes pulse-gold {
        0% { box-shadow: 0 0 0 0 rgba(201, 168, 76, 0.7); }
        70% { box-shadow: 0 0 0 6px rgba(201, 168, 76, 0); }
        100% { box-shadow: 0 0 0 0 rgba(201, 168, 76, 0); }
    }
    
    /* ── TACTICAL TOGGLE SWITCHES (V3 BRUTE-FORCE OVERRIDE) ── */
    
    /* 1. Terminal Font for the Label */
    div[data-testid="stToggle"] label p,
    div[data-testid="stToggle"] label span {
        font-family: var(--font-m) !important;
        font-size: 0.65rem !important;
        letter-spacing: 1px !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
    }

    /* 2. Square the Track (Inactive) */
    div[data-testid="stToggle"] label > div:first-of-type {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 2px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* 3. Square the Thumb (Inactive) */
    div[data-testid="stToggle"] label > div:first-of-type > div {
        background-color: var(--text-dim) !important;
        border-radius: 1px !important;
        box-shadow: none !important;
    }

    /* 4. ACTIVE STATE: The Amber Forensic Track */
    div[data-testid="stToggle"] input:checked + div {
        background-color: rgba(201, 168, 76, 0.15) !important;
        border-color: var(--gold) !important;
        box-shadow: inset 0 0 8px rgba(201, 168, 76, 0.1) !important;
    }

    /* 5. ACTIVE STATE: The Glowing Amber Thumb */
    div[data-testid="stToggle"] input:checked + div > div {
        background-color: var(--gold) !important;
        box-shadow: 0 0 8px rgba(201, 168, 76, 0.6) !important;
    }

</style>
""", unsafe_allow_html=True)

st.markdown(STYLES, unsafe_allow_html=True)

# ── REHYDRATION PROTOCOL (Zero-Cost Persistence) ─────────────────────────────
current_sid = st.session_state.get(K.USER_HASH)

if current_sid and not str(current_sid).upper().startswith("GUEST_"):
    if not st.session_state.get("boot_rehydrated"):
        with st.spinner("Re-establishing Neural Uplink..."):
            from vault.vault_engine import rehydrate_session
            recovered = rehydrate_session(current_sid)
            
            if recovered:
                st.session_state[K.PERSONA_LIST] = recovered.get("personas", [])
                
                # Recover DNA Strings (Only overwrite if data exists in DB)
                dna = recovered.get("dna", {})
                if dna.get("ink"): st.session_state[K.INK_DNA] = dna["ink"]
                if dna.get("intel"): st.session_state[K.INTEL_DNA] = dna["intel"]
                if dna.get("hikmah"): st.session_state[K.HIKMAH_DNA] = dna["hikmah"]
                
                st.toast(f"Terminal Identity Rehydrated: {current_sid[:8]}", icon="⚡")
        st.session_state["boot_rehydrated"] = True

# ── SECURITY GATE: LOCKOUT CHECK ────────────────────────────────────────────
lockout_ts = st.session_state.get(K.LOCKOUT_UNTIL)
if lockout_ts:
    now = datetime.now(timezone.utc)
    if now < lockout_ts:
        remaining = int((lockout_ts - now).total_seconds() / 60)
        lockout_html = textwrap.dedent(f"""
            <div style="height:80vh; display:flex; flex-direction:column; align-items:center; justify-content:center; text-align:center;">
                <div style="font-family:var(--font-m); color:var(--danger); font-size:2rem; letter-spacing:4px; margin-bottom:10px;">
                    TERMINAL LOCKED
                </div>
                <div style="font-family:var(--font-m); color:var(--text-muted); font-size:0.8rem; max-width:400px; line-height:1.6;">
                    Multiple failed authentication attempts detected.<br>
                    System self-destruct protocol active.<br><br>
                    <span style="color:var(--gold);">Access restored in: {remaining + 1} minutes.</span>
                </div>
            </div>
        """)
        st.markdown(lockout_html, unsafe_allow_html=True)
        st.stop()
    else:
        st.session_state[K.LOCKOUT_UNTIL] = None
        st.session_state[K.FAILED_ATTEMPTS] = 0

# 🔗 IDENTITY LATCHING: Persist SID in URL
if current_sid:
    st.query_params["sid"] = current_sid

# ── BOOT SEQUENCE ───────────────────────────────────────────────────────────
if "boot_complete" not in st.session_state:
    if not current_sid or "GUEST_" in str(current_sid).upper():
        st.toast("InkOS System Initialized. Running in Ghost Mode.", icon="📡")
    else:
        if "boot_rehydrated" not in st.session_state:
            st.toast(f"Terminal Identity Latch: {current_sid[:8]}", icon="🔐")
    st.session_state["boot_complete"] = True

# ── RTL CLASS INJECTION ─────────────────────────────────────────────────────
rtl_js = "<script>const app = window.parent.document.querySelector('.stApp'); if (app) app.classList.add('rtl-mode');</script>"
ltr_js = "<script>const app = window.parent.document.querySelector('.stApp'); if (app) app.classList.remove('rtl-mode');</script>"
st.markdown(rtl_js if is_rtl() else ltr_js, unsafe_allow_html=True)

# ── NAVIGATION MATRIX ───────────────────────────────────────────────────────
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
    selected_nav = st.radio("Nav", list(nav_options.keys()), label_visibility="collapsed")
    st.markdown("---")
    cfg = render_sidebar()

# Store config globally for the execution loop
st.session_state["app_config"] = cfg

# ── EXECUTE SELECTED TAB ────────────────────────────────────────────────────
if selected_nav == t("tab_workspace"):
    nav_options[selected_nav](cfg)
else:
    nav_options[selected_nav]()