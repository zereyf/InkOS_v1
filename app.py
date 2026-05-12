"""
InkOS | app.py — Entry Point
==============================
v24.0: The iOS Design System Sync.
       - Integrated Global Token Styles (Light/Dark).
       - Fixed Bottom Navigation (Mobile-first iOS architecture).
       - Theme toggle sync between Workspace and Root.
       - Safely preserves all Session, DNA, and Auth logics.
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

# ── Apply Theme (Synced with Workspace Toggle) ──
# We sync the legacy "dark_mode" with the new "desk_theme" toggle
if "desk_theme" in st.session_state:
    dark_mode = st.session_state["desk_theme"] == "dark"
else:
    dark_mode = st.session_state.get("dark_mode", False) # Default to iOS Light Mode

is_rtl = st.session_state.get("is_rtl", False)

if global_mem.get("maintenance_mode") and not is_admin:
    st.markdown(get_styles(dark_mode), unsafe_allow_html=True)
    st.markdown('<div class="maintenance-lock">[ ⨂ ] SYSTEM LOCKDOWN</div>',
                unsafe_allow_html=True)
    st.stop()

# Inject Global Styles
st.markdown(get_styles(dark_mode), unsafe_allow_html=True)

# Inject RTL/LTR direction
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

# ── Sidebar (Kept intact for desktop/settings) ──
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
        if st.button(f"{icon}  {tab}", key=f"nav_side_{tab}",
                     use_container_width=True):
            st.session_state["active_tab"] = tab
            st.session_state["in_studio"] = False # Reset studio state on navigation
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


# ── IOS FIXED BOTTOM NAVIGATION ──
# We use the :has(.bottom-nav-marker) CSS injected via styles.py to float these columns.
st.markdown("<div class='bottom-nav-marker'></div>", unsafe_allow_html=True)

# We must use unique keys since the sidebar also has buttons for these tabs
nav1, nav2, nav3, nav4, nav5 = st.columns(5)

with nav1:
    if st.button("Desk", key="bnav_desk"):
        st.session_state["active_tab"] = "WORKSPACE"
        st.session_state["in_studio"] = False
        st.rerun()
with nav2:
    if st.button("Vault", key="bnav_vault") and not is_guest:
        st.session_state["active_tab"] = "VAULT"
        st.rerun()
with nav3:
    # The Floating Action Button (+) 
    if st.button("+", key="bnav_forge") and not is_guest:
        st.session_state["active_tab"] = "FORGE"
        st.rerun()
with nav4:
    if st.button("Archive", key="bnav_archive"):
        st.session_state["active_tab"] = "ARCHIVE"
        st.rerun()
with nav5:
    if st.button("Map", key="bnav_map") and not is_guest:
        st.session_state["active_tab"] = "COGNITIVE MAP"
        st.rerun()

# ── INJECT BOTTOM NAV CSS FIX ──
# Ties the Streamlit columns to the iOS fixed bar design
st.markdown("""
<style>
/* Targets the specific Streamlit block holding our nav buttons */
div[data-testid="stHorizontalBlock"]:has(.bottom-nav-marker) {
    position: fixed !important;
    bottom: 0 !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: 100% !important;
    max-width: 430px !important;
    background: rgba(255, 255, 255, 0.95) !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    border-top: 1px solid rgba(0,0,0,0.05) !important;
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    padding: 10px 20px 25px 20px !important; /* iOS Home Bar space */
    z-index: 999 !important;
}

div[data-testid="stHorizontalBlock"]:has(.bottom-nav-marker) > div[data-testid="column"] {
    width: 20% !important;
    flex: 1 1 0px !important;
}

div[data-testid="stHorizontalBlock"]:has(.bottom-nav-marker) button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    height: auto !important;
    padding: 5px 0 !important;
    color: var(--text-2) !important;
    border-radius: 0 !important;
    width: 100% !important;
}

div[data-testid="stHorizontalBlock"]:has(.bottom-nav-marker) button p {
    font-size: 10px !important;
    font-weight: 500 !important;
    margin-top: 4px !important;
    font-family: var(--font-sans) !important;
    color: inherit !important;
}

/* Icon Injections via pseudo-elements */
div[data-testid="stHorizontalBlock"]:has(.bottom-nav-marker) > div:nth-child(1) button::before { content: "⌂"; font-size: 22px; line-height: 1; }
div[data-testid="stHorizontalBlock"]:has(.bottom-nav-marker) > div:nth-child(2) button::before { content: "❖"; font-size: 20px; line-height: 1; }
div[data-testid="stHorizontalBlock"]:has(.bottom-nav-marker) > div:nth-child(4) button::before { content: "📁"; font-size: 18px; line-height: 1; margin-top: 2px;}
div[data-testid="stHorizontalBlock"]:has(.bottom-nav-marker) > div:nth-child(5) button::before { content: "🧠"; font-size: 18px; line-height: 1; margin-top: 2px;}

/* ── Center FAB (+) Override ── */
div[data-testid="stHorizontalBlock"]:has(.bottom-nav-marker) > div:nth-child(3) button {
    background: var(--accent) !important;
    color: #ffffff !important;
    width: 52px !important;
    height: 52px !important;
    border-radius: 50% !important;
    margin: -30px auto 0 auto !important; /* Pull up above bar */
    box-shadow: var(--shadow-lg) !important;
    transition: transform 0.2s ease !important;
}
div[data-testid="stHorizontalBlock"]:has(.bottom-nav-marker) > div:nth-child(3) button::before {
    display: none !important;
}
div[data-testid="stHorizontalBlock"]:has(.bottom-nav-marker) > div:nth-child(3) button p {
    font-size: 28px !important;
    font-weight: 300 !important;
    line-height: 0 !important;
    margin-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)
