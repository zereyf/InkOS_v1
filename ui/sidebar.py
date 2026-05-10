"""
ui/sidebar.py — Sidebar Command Deck
====================================
v21.1: Zenith Autonomous Edition — Alignment Patch.
       - FIXED: Indentation Error in LATCH_IDENTITY block.
       - FIXED: Rehydration logic integrated into the Login flow.
       - STABLE: Proactive Intelligence HUD (Auto-Switch feedback).
       - RETAINED: Tactical Wordmarks and InkOS Branding.
"""

import streamlit as st
import textwrap
from typing import TypedDict, Optional

from state import K, get_remaining_calls
from config import TARGET_GUIDES, AESTHETIC_PRESETS, AUTO_SELECT_LABEL, LOGIC_FRAMEWORKS
from config.personas import STARTER_PERSONAS
from vault.supabase_client import SUPABASE_MISSING
from vault.vault_engine import authenticate_terminal, check_id_availability, rehydrate_session
from i18n.translations import t

# ── 🟢 ENGINE INTEGRATIONS ──
from forge.rhetoric_engine import HIKMAH_PROFILES

class SidebarConfig(TypedDict):
    target_model:     str
    framework:        str
    source_lang:      str
    hikmah_style:     str
    aesthetic_choice: str
    active_persona:   Optional[dict]
    expert_mode:      bool

# ── HELPER COMPONENTS ────────────────────────────────────────────────────────

def render_proactive_hud():
    """Displays the current Autonomous Routing decision and reasoning."""
    if st.session_state.get("sb_target") != AUTO_SELECT_LABEL:
        return

    target = st.session_state.get(K.AUTO_TARGET, "INITIALIZING")
    reason = st.session_state.get(K.AUTO_REASON, "Scanning mission parameters...")

    st.markdown(f"""
        <div style="background:rgba(201,168,76,0.05); border-left:3px solid var(--gold); padding:12px; margin-bottom:20px; border-radius:0 4px 4px 0;">
            <div style="font-family:var(--font-m); font-size:0.5rem; color:var(--gold); letter-spacing:1.5px; margin-bottom:4px;">PROACTIVE_INTELLIGENCE_LAYER</div>
            <div style="font-family:var(--font-m); font-size:0.75rem; color:var(--text); font-weight:bold;">{target.upper()}</div>
            <div style="font-family:var(--font-m); font-size:0.5rem; color:var(--text-dim); line-height:1.3; margin-top:4px;">{reason}</div>
        </div>
    """, unsafe_allow_html=True)

def _load_user_personas(user_hash: str) -> list:
    if SUPABASE_MISSING: return []
    try:
        from forge.persona_store import list_personas
        personas, _ = list_personas(user_hash, target_filter="All")
        return personas or []
    except Exception: return []

def _enforce_admin_clearance() -> None:
    uid = st.session_state.get(K.USER_HASH)
    if not uid or "GUEST_" in str(uid).upper():
        st.session_state[K.IS_ADMIN] = False
        return
    try:
        master_secret = st.secrets.get("MASTER_IDS", "")
        master_list = [x.strip().upper() for x in master_secret.split(",") if x.strip()]
        st.session_state[K.IS_ADMIN] = (str(uid).upper() in master_list)
    except Exception: st.session_state[K.IS_ADMIN] = False

# ── 1. TOP MATRIX: BRAND & UPLINK ────────────────────────────────────────────

def render_sidebar_brand() -> None:
    current_sid = st.session_state.get(K.USER_HASH)
    is_guest = not current_sid or "GUEST_" in str(current_sid).upper()

    if SUPABASE_MISSING: uplink_color, uplink_label = "#E53E3E", "DB_FAULT"
    elif is_guest: uplink_color, uplink_label = "var(--text-dim)", "OFFLINE" 
    else: uplink_color, uplink_label = "#4CAF9A", "ACTIVE" 

    st.markdown(textwrap.dedent(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px; padding:0 5px;">
            <div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-dim); letter-spacing:1px;">NEURAL_UPLINK</div>
            <div style="display:flex; align-items:center; gap:6px;">
                <span style="height:6px; width:6px; background:{uplink_color}; border-radius:50%; box-shadow: 0 0 5px {uplink_color};"></span>
                <span style="font-family:var(--font-m); font-size:0.55rem; color:{uplink_color}; font-weight:bold;">{uplink_label}</span>
            </div>
        </div>
        <div style="padding:0 0 14px 0; border-bottom:1px solid rgba(255,255,255,0.05); margin-bottom:5px; text-align:center;">
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" style="width: 34px; height: 34px; fill: var(--gold);">
                    <path d="M73.4 182.6C60.9 170.1 60.9 149.8 73.4 137.3C85.9 124.8 106.2 124.8 118.7 137.3L278.7 297.3C291.2 309.8 291.2 330.1 278.7 342.6L118.7 502.6C106.2 515.1 85.9 515.1 73.4 502.6C60.9 490.1 60.9 469.8 73.4 457.3L210.7 320L73.4 182.6zM288 448L544 448C561.7 448 576 462.3 576 480C576 497.7 561.7 512 544 512L288 512C270.3 512 256 497.7 256 480C256 462.3 270.3 448 288 448z"/>
                </svg>
                <span style="font-family: var(--font-m); font-size: 1.5rem; color: var(--text); letter-spacing: 4px; margin-left: 12px; font-weight: bold;">
                    INK<span style="color: var(--gold);">OS</span>
                </span>
            </div>
            <div style="letter-spacing:2px; font-size:0.5rem; color:var(--gold);">حبر وفكرة // ZENITH_AUTONOMOUS v21.1</div>
        </div>
    """), unsafe_allow_html=True)

# ── 2. BOTTOM MATRIX: IDENTITY & CONTROLS ─────────────────────────────────────

def render_sidebar() -> SidebarConfig:
    _enforce_admin_clearance()

    current_sid = st.session_state.get(K.USER_HASH)
    is_guest = not current_sid or "GUEST_" in str(current_sid).upper()
    sess_ref = str(current_sid)[:8] if current_sid else "GHOST_ID"

    st.markdown(f'<div class="vc-header" style="font-size:0.55rem; color:var(--text-muted); margin-top:10px;">SESS_REF: {sess_ref}</div>', unsafe_allow_html=True)

   if is_guest:
        new_sid = st.text_input("ID", placeholder="Identity Name", key="sid_input_sidebar", label_visibility="collapsed")
        new_pin = st.text_input("PIN", placeholder="PIN", type="password", key="pin_input_sidebar", label_visibility="collapsed")
        
        # 🟢 RESTORED: Registration Toggle (Required for the Engine)
        is_new_user = st.toggle("Register New Identity?", value=False, key="is_new_user_toggle")
        
        if st.button("LATCH IDENTITY", use_container_width=True, key="btn_latch_sid"):
            if new_sid.strip() and new_pin.strip():
                with st.spinner("Uplinking..."):
                    # 🟢 FIXED: Passed is_new_user to match the engine signature
                    success, error_msg = authenticate_terminal(
                        new_sid.strip(), 
                        new_pin.strip(), 
                        is_new=is_new_user
                    )
                
                if success:
                    st.session_state[K.USER_HASH] = new_sid.strip()
                    
                    # 🧩 NEURAL REHYDRATION
                    user_data = rehydrate_session(new_sid.strip())
                    dna = user_data.get("dna", {})
                    st.session_state[K.INK_DNA] = dna.get("ink", st.session_state[K.INK_DNA])
                    st.session_state[K.INTEL_DNA] = dna.get("intel", st.session_state[K.INTEL_DNA])
                    st.session_state[K.HIKMAH_DNA] = dna.get("hikmah", st.session_state[K.HIKMAH_DNA])
                    st.session_state[K.PERSONA_LIST] = user_data.get("personas", [])
                    
                    st.query_params["sid"] = new_sid.strip()
                    st.rerun()
                else:
                    st.error(f"[!] {error_msg}")
    else:
        st.markdown('<div style="background:rgba(201,168,76,0.05); border:1px solid rgba(201,168,76,0.2); padding:10px; border-radius:3px; margin-bottom:10px; font-size:0.55rem; color:var(--gold); display:flex; align-items:center; gap:8px;">[◈] IDENTITY SECURED</div>', unsafe_allow_html=True)
        if st.button("Terminate Latch", use_container_width=True):
            st.session_state[K.USER_HASH] = None 
            st.query_params.clear()
            st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── 🟢 PROACTIVE HUD ──
    render_proactive_hud()

    # ── LOGIC CONFIGURATION ──
    st.markdown(f'<div class="vc-header" style="font-size:0.65rem;">[ {t("logic_config", fallback="LOGIC_CONFIGURATION").upper()} ]</div>', unsafe_allow_html=True)
    
    target_options = [AUTO_SELECT_LABEL] + list(TARGET_GUIDES.keys())
    target_model = st.selectbox("Target Model", options=target_options, key="sb_target")
    framework = st.selectbox(t("logic_framework", fallback="Framework"), options=LOGIC_FRAMEWORKS, key="sb_framework")
    source_lang = st.radio("Input Language", ["English", "Arabic (العربية)"], key="sb_lang")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── PERSONA SELECTOR ──
    st.markdown(f'<div class="vc-header" style="font-size:0.65rem;">[ {t("active_persona", fallback="ACTIVE_PERSONA").upper()} ]</div>', unsafe_allow_html=True)
    user_personas = st.session_state.get(K.PERSONA_LIST, [])
    options_map = {'None': None}
    for name, p in STARTER_PERSONAS.items(): 
        if name != 'None': options_map[f'{name} [S]'] = p
    for p in user_personas: options_map[f"{p['name']} [C]"] = p
    
    options_list = list(options_map.keys())
    selected_key = st.selectbox('Persona Select', options=options_list, key='sb_persona_global_widget', label_visibility='collapsed')
    active_p = options_map[selected_key]
    st.session_state[K.ACTIVE_PERSONA] = active_p

    # ── SYSTEM TOGGLES ──
    st.markdown("<hr style='margin-top:5px;'>", unsafe_allow_html=True)
    is_locked = active_p is not None

    aesthetic_choice = st.selectbox(
        t("aesthetic_preset", fallback="Aesthetic"), 
        options=list(AESTHETIC_PRESETS.keys()), 
        key=K.AESTHETIC_CHOICE,
        disabled=is_locked 
    )
    
    hikmah_choice = st.selectbox(
        t("hikmah_style", fallback="Hikmah Style"), 
        options=list(HIKMAH_PROFILES.keys()), 
        key=K.HIKMAH_STYLE,
        disabled=is_locked,
        help="Behavior is locked when a Specialist is engaged."
    )
    
    expert_mode = st.checkbox("Expert Diagnostics", key="sb_expert")

    # ── METRICS ──
    m1, m2, m3 = st.columns(3)
    with m1: st.metric("RUNS", len(st.session_state.get(K.HISTORY, [])))
    with m2: st.metric("CALLS", get_remaining_calls())
    with m3: st.metric("SAVED", st.session_state.get(K.LAST_SAVED, "Never"))

    if st.button("RESET SESSION", use_container_width=True):
        from state import reset_session
        reset_session()
        st.rerun()

    return SidebarConfig(
        target_model     = target_model,
        framework        = framework,
        source_lang      = source_lang,
        hikmah_style     = st.session_state.get(K.HIKMAH_STYLE, "None"),
        aesthetic_choice = st.session_state.get(K.AESTHETIC_CHOICE, "Default"),
        active_persona   = active_p,
        expert_mode      = expert_mode,
    )
