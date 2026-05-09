"""
InkOS | app.py — Entry Point
==============================
v2026.4.6: Master Sync — Horizontal Navigation Refactor.
           - REFACTORED: Global navigation moved to top-level tabs.
           - INTEGRATED: "ABOUT" tab persistent across all identity states.
           - ENFORCED: Soft-Gate Workspace logic (Splash renders inside tab).
           - PURGED: Standard OS Emojis and sidebar navigation radio.
"""

import sys
import os
import textwrap
from datetime import datetime, timezone

# Ensure local imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

# 1. Page Config must be first — Emoji purged
st.set_page_config(
    page_title="InkOS", 
    page_icon="❖", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

from config import API_KEY_MISSING
from state import init_session_state, K
from ui.styles import STYLES
from ui.sidebar import render_sidebar
from ui.tabs.about import render_about      # 🟢 New Import
from ui.tabs.workspace import render_workspace
from ui.tabs.archive import render_archive
from ui.tabs.security_log import render_security_log
from ui.tabs.cognitive_map import render_cognitive_map
from ui.tabs.vault import render_vault
from ui.tabs.forge import render_forge
from ui.tabs.guide import render_guide
from i18n.translations import t, is_rtl

if API_KEY_MISSING:
    st.error("[!] SYSTEM ERROR: GROQ_API_KEY not found in environment.")
    st.stop()

# ── URL REHYDRATION (SID ONLY) ──────────────────────────────────────────────
if "sid" in st.query_params:
    st.session_state[K.USER_HASH] = st.query_params["sid"]

# ── INITIALIZE STATE ────────────────────────────────────────────────────────
init_session_state()

# ── 🟢 BOOTSTRAP VALIDATION MATRIX ─────────────────────────────────
from config import validate_config
config_errors = validate_config()
if config_errors:
    for err in config_errors:
        st.error(f'[!] CONFIG ERROR: {err}')
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
    
    /* ── Tab Layout Override ── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
        border-bottom: 1px solid rgba(255,255,255,0.05);
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent !important;
        border: none !important;
        font-family: var(--font-m) !important;
        font-size: 0.7rem !important;
        letter-spacing: 2px !important;
        color: var(--text-dim) !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--gold) !important;
        border-bottom: 2px solid var(--gold) !important;
    }

    @keyframes pulse-gold {
        0% { box-shadow: 0 0 0 0 rgba(201, 168, 76, 0.7); }
        70% { box-shadow: 0 0 0 6px rgba(201, 168, 76, 0); }
        100% { box-shadow: 0 0 0 0 rgba(201, 168, 76, 0); }
    }
    
    /* ── TACTICAL TOGGLE SWITCHES ── */
    div[data-testid="stToggle"] label p {
        font-family: var(--font-m) !important;
        font-size: 0.65rem !important;
        letter-spacing: 1px !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(STYLES, unsafe_allow_html=True)

# ── REHYDRATION PROTOCOL ─────────────────────────────────────────────
current_sid = st.session_state.get(K.USER_HASH)
is_guest = not current_sid or "GUEST_" in str(current_sid).upper()

if not is_guest:
    if not st.session_state.get("boot_rehydrated"):
        with st.spinner("Re-establishing Neural Uplink..."):
            from vault.vault_engine import rehydrate_session
            recovered = rehydrate_session(current_sid)
            if recovered:
                st.session_state[K.PERSONA_LIST] = recovered.get("personas", [])
                dna = recovered.get("dna", {})
                if dna.get("ink"): st.session_state[K.INK_DNA] = dna["ink"]
                if dna.get("intel"): st.session_state[K.INTEL_DNA] = dna["intel"]
                if dna.get("hikmah"): st.session_state[K.HIKMAH_DNA] = dna["hikmah"]
                st.toast(f"> IDENTITY REHYDRATED: {current_sid[:8]}")
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
                    [ ⨂ ] TERMINAL LOCKED
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
    if is_guest:
        st.toast("> SYSTEM INITIALIZED [ GHOST MODE ]")
    else:
        if "boot_rehydrated" not in st.session_state:
            st.toast(f"[◈] IDENTITY LATCH: {current_sid[:8]}")
    st.session_state["boot_complete"] = True

# ── RTL CLASS INJECTION ─────────────────────────────────────────────────────
rtl_js = "<script>const app = window.parent.document.querySelector('.stApp'); if (app) app.classList.add('rtl-mode');</script>"
ltr_js = "<script>const app = window.parent.document.querySelector('.stApp'); if (app) app.classList.remove('rtl-mode');</script>"
st.markdown(rtl_js if is_rtl() else ltr_js, unsafe_allow_html=True)

# ── COMMAND DECK (Sidebar) ──────────────────────────────────────────────────
with st.sidebar:
    if is_guest:
        st.markdown("<div style='text-align:center; color:var(--danger); font-family:var(--font-m); font-size:0.7rem; letter-spacing:2px; margin-bottom:15px;'>[ ⨂ ] ACCESS RESTRICTED</div>", unsafe_allow_html=True)
    st.markdown("---")
    cfg = render_sidebar()

# Store config globally
st.session_state["app_config"] = cfg

# ── NAVIGATION MATRIX: Horizontal Tabular Refactor ──────────────────────────
# 🟢 Architecture: Documentation is global. Functional assets are identity-locked.

tab_labels = [t("tab_workspace"), t("tab_vault"), "ABOUT"]
tab_workspace, tab_vault, tab_about = st.tabs(tab_labels)

with tab_workspace:
    if is_guest:
        # Show the Gateway UI if not latched
        render_splash_screen()
    else:
        # Show the full logic workspace if latched
        render_workspace(cfg)

with tab_vault:
    if is_guest:
        st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; font-family:var(--font-m); color:var(--text-dim); letter-spacing:1px;'>[ ⨂ ] NEURAL VAULT LOCKED: IDENTITY LATCH REQUIRED.</div>", unsafe_allow_html=True)
    else:
        render_vault()

with tab_about:
    # Globally accessible architecture manifesto
    render_about()
