"""
app.py — Entry Point
=====================
v2.0: Visual Director tab registered in nav matrix.

Changes:
  - "◈ VISUAL" added to NAV_ITEMS between WORKSPACE and VAULT
  - GUEST_HIDDEN updated — Visual Director is accessible to guests
    (it produces prompts, not vault operations — no auth needed)
  - Tab routing handles "VISUAL DIRECTOR" → render_visual_director()
  - All Phase 1–4 fixes preserved
"""

import sys
import os
import traceback

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from state import init_session_state, K, get_global_memory, read_global_memory
from config import API_KEY_MISSING

icon_path = "icon.svg"
st.set_page_config(
    page_title            = "InkOS",
    page_icon             = icon_path if os.path.exists(icon_path) else "❖",
    layout                = "wide",
    initial_sidebar_state = "expanded",
)

init_session_state()

# ── URL Rehydration ───────────────────────────────────────────────────────────
if "sid" in st.query_params and st.session_state.get(K.USER_HASH) is None:
    sid = st.query_params["sid"]
    st.session_state[K.USER_HASH] = sid
    from vault.vault_engine import rehydrate_session
    user_data = rehydrate_session(sid)
    dna       = user_data.get("dna", {})
    st.session_state[K.INK_DNA]      = dna.get("ink")    or st.session_state[K.INK_DNA]
    st.session_state[K.INTEL_DNA]    = dna.get("intel")  or st.session_state[K.INTEL_DNA]
    st.session_state[K.HIKMAH_DNA]   = dna.get("hikmah") or st.session_state[K.HIKMAH_DNA]
    st.session_state[K.PERSONA_LIST] = user_data.get("personas", [])
    st.session_state[K.IS_ADMIN]     = user_data.get("is_admin", False)

# ── Imports ───────────────────────────────────────────────────────────────────
from ui.styles import get_styles
from ui.splash import render_splash_screen
from ui.sidebar import render_sidebar, render_sidebar_brand
from ui.tabs.workspace import render_workspace
from ui.tabs.visual_director import render_visual_director
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

# ── Maintenance gate ──────────────────────────────────────────────────────────
is_admin       = st.session_state.get(K.IS_ADMIN, False)
maintenance_on = read_global_memory("maintenance_mode", False)

dark_mode = st.session_state.get("dark_mode", True)
is_rtl    = st.session_state.get("is_rtl", False)

if maintenance_on and not is_admin:
    st.markdown(get_styles(dark_mode), unsafe_allow_html=True)
    st.markdown(
        '<div class="maintenance-lock">[ ⨂ ] SYSTEM LOCKDOWN</div>',
        unsafe_allow_html=True,
    )
    st.stop()

st.markdown(get_styles(dark_mode), unsafe_allow_html=True)

direction = "rtl" if is_rtl else "ltr"
st.markdown(f"""
<style>
  .main {{ direction: {direction}; }}
  [data-testid="stSidebar"] {{ direction: {direction}; }}
</style>
""", unsafe_allow_html=True)

# ── Broadcast banner ──────────────────────────────────────────────────────────
broadcast_msg = read_global_memory("broadcast", None)
if broadcast_msg:
    st.info(f"📡 {broadcast_msg}", icon=None)

# ── Nav matrix ────────────────────────────────────────────────────────────────
current_sid = st.session_state.get(K.USER_HASH)
is_guest    = not current_sid or "GUEST_" in str(current_sid).upper()

NAV_ITEMS = [
    ("🖊",  "WORKSPACE"),
    ("◈",   "VISUAL DIRECTOR"),   # ← new
    ("🔒",  "VAULT"),
    ("⚙️",  "FORGE"),
    ("🧠",  "COGNITIVE MAP"),
    ("📁",  "ARCHIVE"),
    ("🛡️",  "SECURITY LOG"),
    ("📖",  "GUIDE"),
    ("◈",   "ABOUT"),
]

# Visual Director is accessible to guests — it generates prompts, no DB needed
GUEST_HIDDEN = {"VAULT", "FORGE", "COGNITIVE MAP"}

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "WORKSPACE"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    render_sidebar_brand()
    st.markdown("<div class='nav-section'>", unsafe_allow_html=True)

    for icon, tab in NAV_ITEMS:
        if is_guest and tab in GUEST_HIDDEN:
            st.markdown(
                f"<div class='nav-item nav-locked'>"
                f"<span style='font-family:IBM Plex Mono,monospace;font-size:10px;"
                f"padding:6px 8px;display:block;'>{icon}  {tab}</span>"
                f"</div>"
                f"<div class='nav-locked-label'>Login required</div>",
                unsafe_allow_html=True,
            )
            continue

        is_active = st.session_state["active_tab"] == tab
        if is_active:
            st.markdown("<div class='nav-active'>", unsafe_allow_html=True)
        st.markdown("<div class='nav-item'>", unsafe_allow_html=True)
        if st.button(f"{icon}  {tab}", key=f"nav_{tab.replace(' ', '_')}",
                     use_container_width=True):
            st.session_state["active_tab"] = tab
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        if is_active:
            st.markdown("</div>", unsafe_allow_html=True)

    # Admin nav
    if is_admin:
        tab       = "◈ OVERWATCH"
        is_active = st.session_state["active_tab"] == tab
        if is_active:
            st.markdown("<div class='nav-active'>", unsafe_allow_html=True)
        st.markdown("<div class='nav-item'>", unsafe_allow_html=True)
        if st.button("◈  OVERWATCH", key="nav_overwatch", use_container_width=True):
            st.session_state["active_tab"] = tab
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        if is_active:
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    cfg = render_sidebar()


# ── Tab routing ───────────────────────────────────────────────────────────────

def _safe(tab_name: str, render_fn, *args, **kwargs) -> None:
    """Error boundary — logs to stderr, shows clean card, app continues."""
    try:
        render_fn(*args, **kwargs)
    except Exception as exc:
        tb = traceback.format_exc()
        print(
            f"[InkOS ERROR] Tab '{tab_name}' raised:\n{tb}",
            file=sys.stderr,
        )
        st.error(
            f"**{tab_name} encountered an error.**\n\n"
            f"`{type(exc).__name__}: {exc}`\n\n"
            "Logged. Continue using other tabs.\n"
            "If this persists, try Reset in the sidebar."
        )


active_tab = st.session_state["active_tab"]

if active_tab == "WORKSPACE":
    if is_guest:
        render_splash_screen()
    else:
        _safe("WORKSPACE", render_workspace, cfg)

elif active_tab == "VISUAL DIRECTOR":
    # Accessible to both guests and logged-in users
    _safe("VISUAL DIRECTOR", render_visual_director)

elif active_tab == "VAULT":
    _safe("VAULT", render_vault)

elif active_tab == "FORGE":
    _safe("FORGE", render_forge)

elif active_tab == "ARCHIVE":
    _safe("ARCHIVE", render_archive)

elif active_tab == "SECURITY LOG":
    _safe("SECURITY LOG", render_security_log)

elif active_tab == "COGNITIVE MAP":
    _safe("COGNITIVE MAP", render_cognitive_map)

elif active_tab == "GUIDE":
    _safe("GUIDE", render_guide)

elif active_tab == "ABOUT":
    _safe("ABOUT", render_about)

elif active_tab == "◈ OVERWATCH" and is_admin:
    from ui.tabs.admin import render_admin_board
    _safe("OVERWATCH", render_admin_board)
