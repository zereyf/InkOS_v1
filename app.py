"""
InkOS | app.py — Entry Point
==============================
v2026.4.6: Full Audit Fix Pass.
           - CSS vars unified via ui.theme — single source of truth.
           - --font-d corrected to Georgia (Impact is wrong for Arabic).
           - Lockout HTML moved to components.html() — no more Markdown leak.
           - render_sidebar() gated behind auth check — guests see login only.
           - boot_complete toast debounced — guests no longer see it on refresh.
           - is_guest hardened against falsy SID edge cases.
"""

import sys
import os
import streamlit.components.v1 as components
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

# 1. Page config must be first
st.set_page_config(
    page_title="InkOS",
    page_icon="❖",
    layout="wide",
    initial_sidebar_state="expanded"
)

from config import API_KEY_MISSING
from state import init_session_state, K
from ui.styles import STYLES
from ui.theme import THEME_STYLES, VARS          # ← single source of truth
from ui.sidebar import render_sidebar
from ui.splash import render_splash_screen
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

# ── URL REHYDRATION (SID ONLY) ───────────────────────────────────────────────
if "sid" in st.query_params:
    st.session_state[K.USER_HASH] = st.query_params["sid"]

# ── INITIALIZE STATE ─────────────────────────────────────────────────────────
init_session_state()

# ── TASK 10: BOOTSTRAP VALIDATION MATRIX ────────────────────────────────────
from config import validate_config
config_errors = validate_config()
if config_errors:
    for err in config_errors:
        st.error(f'[!] CONFIG ERROR: {err}')
    st.stop()

# ── THEME INJECTION (vars + keyframes — sourced from ui/theme.py) ────────────
st.markdown(THEME_STYLES, unsafe_allow_html=True)

# ── TACTICAL TOGGLE SWITCHES (V3 BRUTE-FORCE OVERRIDE) ──────────────────────
st.markdown("""
<style>
    div[data-testid="stToggle"] label p,
    div[data-testid="stToggle"] label span {
        font-family: var(--font-m) !important;
        font-size: 0.65rem !important;
        letter-spacing: 1px !important;
        color: var(--text-muted) !important;
        text-transform: uppercase !important;
    }
    div[data-testid="stToggle"] label > div:first-of-type {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-radius: 2px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    div[data-testid="stToggle"] label > div:first-of-type > div {
        background-color: var(--text-dim) !important;
        border-radius: 1px !important;
        box-shadow: none !important;
    }
    div[data-testid="stToggle"] input:checked + div {
        background-color: rgba(201, 168, 76, 0.15) !important;
        border-color: var(--gold) !important;
        box-shadow: inset 0 0 8px rgba(201, 168, 76, 0.1) !important;
    }
    div[data-testid="stToggle"] input:checked + div > div {
        background-color: var(--gold) !important;
        box-shadow: 0 0 8px rgba(201, 168, 76, 0.6) !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(STYLES, unsafe_allow_html=True)

# ── IS_GUEST: Hardened against falsy SID edge cases ─────────────────────────
def _resolve_guest_status(sid) -> bool:
    """
    Returns True (guest) if:
      - sid is None, empty string, False, 0, or any falsy non-string
      - sid string contains 'GUEST_' (case-insensitive)
    Returns False (authenticated) only for a non-empty, non-guest string.
    """
    if not sid:
        return True
    if not isinstance(sid, str):
        return True
    return "GUEST_" in sid.upper()

current_sid = st.session_state.get(K.USER_HASH)
is_guest = _resolve_guest_status(current_sid)

# ── REHYDRATION PROTOCOL (Authenticated users only) ──────────────────────────
if not is_guest:
    if not st.session_state.get("boot_rehydrated"):
        with st.spinner("Re-establishing Neural Uplink..."):
            from vault.vault_engine import rehydrate_session
            recovered = rehydrate_session(current_sid)

            if recovered:
                st.session_state[K.PERSONA_LIST] = recovered.get("personas", [])
                dna = recovered.get("dna", {})
                if dna.get("ink"):    st.session_state[K.INK_DNA]    = dna["ink"]
                if dna.get("intel"):  st.session_state[K.INTEL_DNA]  = dna["intel"]
                if dna.get("hikmah"): st.session_state[K.HIKMAH_DNA] = dna["hikmah"]

                st.toast(f"> IDENTITY REHYDRATED: {current_sid[:8]}")
        st.session_state["boot_rehydrated"] = True

# ── SECURITY GATE: LOCKOUT CHECK ─────────────────────────────────────────────
lockout_ts = st.session_state.get(K.LOCKOUT_UNTIL)
if lockout_ts:
    now = datetime.now(timezone.utc)
    if now < lockout_ts:
        remaining = int((lockout_ts - now).total_seconds() / 60) + 1
        v = VARS
        lockout_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    height: 80vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    background: transparent;
    font-family: {v['font_m']};
  }}
  .lock-title {{
    color: {v['danger']};
    font-size: 2rem;
    letter-spacing: 4px;
    margin-bottom: 10px;
  }}
  .lock-body {{
    color: {v['text_muted']};
    font-size: 0.8rem;
    max-width: 400px;
    line-height: 1.6;
  }}
  .lock-timer {{ color: {v['gold']}; }}
</style>
</head><body>
  <div class="lock-title">[ &#x2298; ] TERMINAL LOCKED</div>
  <div class="lock-body">
    Multiple failed authentication attempts detected.<br>
    System self-destruct protocol active.<br><br>
    <span class="lock-timer">Access restored in: {remaining} minutes.</span>
  </div>
</body></html>"""
        components.html(lockout_html, height=400, scrolling=False)
        st.stop()
    else:
        st.session_state[K.LOCKOUT_UNTIL] = None
        st.session_state[K.FAILED_ATTEMPTS] = 0

# ── IDENTITY LATCHING: Persist SID in URL ────────────────────────────────────
if current_sid:
    st.query_params["sid"] = current_sid

# ── BOOT SEQUENCE (authenticated users only — guests skip toast) ─────────────
if "boot_complete" not in st.session_state:
    if not is_guest:
        if "boot_rehydrated" not in st.session_state:
            st.toast(f"[◈] IDENTITY LATCH: {current_sid[:8]}")
    st.session_state["boot_complete"] = True

# ── RTL CLASS INJECTION ──────────────────────────────────────────────────────
rtl_js = "<script>const app = window.parent.document.querySelector('.stApp'); if (app) app.classList.add('rtl-mode');</script>"
ltr_js = "<script>const app = window.parent.document.querySelector('.stApp'); if (app) app.classList.remove('rtl-mode');</script>"
st.markdown(rtl_js if is_rtl() else ltr_js, unsafe_allow_html=True)

# ── NAVIGATION MATRIX ────────────────────────────────────────────────────────
nav_options = {
    t("tab_workspace"):     render_workspace,
    t("tab_archive"):       render_archive,
    t("tab_security"):      render_security_log,
    t("tab_cognitive_map"): render_cognitive_map,
    t("tab_vault"):         render_vault,
    t("tab_forge"):         render_forge,
    t("tab_guide"):         render_guide,
}

# ── SIDEBAR: Gated by auth status ────────────────────────────────────────────
with st.sidebar:
    if is_guest:
        # Guests see only the locked indicator + login input (inside render_sidebar)
        st.markdown(
            "<div style='text-align:center; color:#E53E3E; font-family:\"Courier New\",monospace; "
            "font-size:0.7rem; letter-spacing:2px; margin-bottom:15px;'>"
            "[ &#x2298; ] ACCESS DENIED</div>",
            unsafe_allow_html=True
        )
        selected_nav = None
        render_sidebar()          # renders login input only — no nav controls exposed
    else:
        selected_nav = st.radio("Nav", list(nav_options.keys()), label_visibility="collapsed")
        st.markdown("---")
        render_sidebar()

# Store config globally for the execution loop
cfg = st.session_state.get("app_config", {})

# ── GATEWAY LOCK & EXECUTION ──────────────────────────────────────────────────
if is_guest:
    render_splash_screen()
else:
    if selected_nav == t("tab_workspace"):
        nav_options[selected_nav](cfg)
    elif selected_nav:
        nav_options[selected_nav]()
