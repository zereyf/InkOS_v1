"""
InkOS | app.py — Entry Point
==============================
v23.0: Official design system edition.
       - Dark/light mode toggle wired to styles
       - RTL/LTR direction support
       - Clean nav rows
"""
import sys, os
import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from state import init_session_state, K, get_global_memory
from config import API_KEY_MISSING

icon_path = "icon.svg"
st.set_page_config(
    page_title="InkOS",
    page_icon=icon_path if os.path.exists(icon_path) else "❖",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()

# ── URL Rehydration ──
if "sid" in st.query_params and st.session_state.get(K.USER_HASH) is None:
    sid = st.query_params["sid"]
    st.session_state[K.USER_HASH] = sid
    from vault.vault_engine import rehydrate_session
    user_data = rehydrate_session(sid)
    dna = user_data.get("dna", {})
    st.session_state[K.INK_DNA]      = dna.get("ink")    or st.session_state[K.INK_DNA]
    st.session_state[K.INTEL_DNA]    = dna.get("intel")  or st.session_state[K.INTEL_DNA]
    st.session_state[K.HIKMAH_DNA]   = dna.get("hikmah") or st.session_state[K.HIKMAH_DNA]
    st.session_state[K.PERSONA_LIST] = user_data.get("personas", [])

# ── Imports ──
from ui.styles import get_styles
from ui.splash import render_splash_screen
from ui.sidebar import render_sidebar, render_sidebar_brand
from ui.tabs.workspace import render_workspace
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

# ── Maintenance gate ──
global_mem = get_global_memory()
is_admin   = st.session_state.get(K.IS_ADMIN, False)

# ── Apply theme ──
dark_mode = st.session_state.get("dark_mode", True)
is_rtl    = st.session_state.get("is_rtl", False)

if global_mem.get("maintenance_mode") and not is_admin:
    st.markdown(get_styles(dark_mode), unsafe_allow_html=True)
    st.markdown('<div class="maintenance-lock">[ ⨂ ] SYSTEM LOCKDOWN</div>',
                unsafe_allow_html=True)
    st.stop()

st.markdown(get_styles(dark_mode), unsafe_allow_html=True)

# Inject RTL/LTR direction on the root element
direction = "rtl" if is_rtl else "ltr"
st.markdown(f"""
<style>
  .main {{ direction: {direction}; }}
  [data-testid="stSidebar"] {{ direction: {direction}; }}
</style>
""", unsafe_allow_html=True)

# ── Nav matrix ──
current_sid = st.session_state.get(K.USER_HASH)
is_guest    = not current_sid or "GUEST_" in str(current_sid).upper()

NAV_ITEMS = [
    ("🖊", "WORKSPACE"),
    ("🔒", "VAULT"),
    ("⚙️", "FORGE"),
    ("🧠", "COGNITIVE MAP"),
    ("📁", "ARCHIVE"),
    ("🛡️", "SECURITY LOG"),
    ("📖", "GUIDE"),
    ("◈",  "ABOUT"),
]
GUEST_HIDDEN = {"VAULT", "FORGE", "COGNITIVE MAP"}

if "active_tab" not in st.session_state:
    st.session_state["active_tab"] = "WORKSPACE"

# ── Sidebar ──
with st.sidebar:
    render_sidebar_brand()

    st.markdown("<div class='nav-section'>", unsafe_allow_html=True)
    for icon, tab in NAV_ITEMS:
        if is_guest and tab in GUEST_HIDDEN:
            continue
        is_active = st.session_state["active_tab"] == tab
        if is_active:
            st.markdown("<div class='nav-active'>", unsafe_allow_html=True)
        st.markdown("<div class='nav-item'>", unsafe_allow_html=True)
        if st.button(f"{icon}  {tab}", key=f"nav_{tab}",
                     use_container_width=True):
            st.session_state["active_tab"] = tab
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        if is_active:
            st.markdown("</div>", unsafe_allow_html=True)

    if is_admin:
        is_active = st.session_state["active_tab"] == "◈ OVERWATCH"
        if is_active:
            st.markdown("<div class='nav-active'>", unsafe_allow_html=True)
        st.markdown("<div class='nav-item'>", unsafe_allow_html=True)
        if st.button("◈  OVERWATCH", key="nav_overwatch",
                     use_container_width=True):
            st.session_state["active_tab"] = "◈ OVERWATCH"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        if is_active:
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    cfg = render_sidebar()

active_tab = st.session_state["active_tab"]

# ── Routing ──
if active_tab == "WORKSPACE":
    if is_guest: render_splash_screen()
    else:        render_workspace(cfg)
elif active_tab == "VAULT":         render_vault()
elif active_tab == "FORGE":         render_forge()
elif active_tab == "ARCHIVE":       render_archive()
elif active_tab == "SECURITY LOG":  render_security_log()
elif active_tab == "COGNITIVE MAP": render_cognitive_map()
elif active_tab == "GUIDE":         render_guide()
elif active_tab == "ABOUT":         render_about()
elif active_tab == "◈ OVERWATCH" and is_admin:
    from ui.tabs.admin import render_admin_board
    render_admin_board()
