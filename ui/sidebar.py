import streamlit as st
from typing import TypedDict, Optional
from state import K, get_remaining_calls
from config import TARGET_GUIDES, AESTHETIC_PRESETS, AUTO_SELECT_LABEL, LOGIC_FRAMEWORKS
from config.personas import STARTER_PERSONAS
from forge.rhetoric_engine import HIKMAH_PROFILES
from vault.supabase_client import SUPABASE_MISSING

class SidebarConfig(TypedDict):
    target_model: str
    framework: str
    source_lang: str
    hikmah_style: str
    aesthetic_choice: str
    active_persona: Optional[dict]
    expert_mode: bool

def render_sidebar_brand() -> None:
    is_active = not SUPABASE_MISSING and bool(st.session_state.get(K.USER_HASH))
    label = "ACTIVE" if is_active else ("DB_FAULT" if SUPABASE_MISSING else "OFFLINE")
    st.markdown(f"<div class='uplink-bar'><span>NEURAL_UPLINK</span><span class='dot {'active' if is_active else 'inactive'}'>● {label}</span></div><div class='brand-ar'>حبر وفكرة</div><div class='brand-divider'></div><div class='brand-en'>INKOS  //  MUTI_AUTONOMOUS v1.0</div>", unsafe_allow_html=True)

def render_sidebar() -> SidebarConfig:
    if st.session_state.get(K.USER_HASH):
        st.markdown("<div class='identity-card'><div class='avatar'>A</div><div class='name'>Ameer</div><div class='logout'>↩</div></div>", unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn"):
            st.session_state[K.USER_HASH] = None
            st.rerun()
    target_model = st.selectbox("Target Model", [AUTO_SELECT_LABEL] + list(TARGET_GUIDES.keys()), key="sb_target")
    framework = st.selectbox("Framework", LOGIC_FRAMEWORKS, key="sb_framework")
    source_lang = st.selectbox("Input Language", ["English", "Arabic (العربية)"], key="sb_lang")
    user_personas = st.session_state.get(K.PERSONA_LIST, [])
    options_map = {'None': None}
    for name, p in STARTER_PERSONAS.items():
        if name != 'None': options_map[f'{name} [S]'] = p
    for p in user_personas: options_map[f"{p['name']} [C]"] = p
    selected_key = st.selectbox('Persona Select', options=list(options_map.keys()), key='sb_persona_global_widget', label_visibility='collapsed')
    active_p = options_map.get(selected_key)
    st.session_state[K.ACTIVE_PERSONA] = active_p
    aesthetic_choice = st.selectbox("Aesthetic", list(AESTHETIC_PRESETS.keys()), key=K.AESTHETIC_CHOICE, disabled=active_p is not None)
    st.selectbox("Hikmah Style", list(HIKMAH_PROFILES.keys()), key=K.HIKMAH_STYLE, disabled=active_p is not None)
    expert_mode = st.checkbox("Expert Diagnostics", key="sb_expert")
    st.caption(f"Calls remaining: {get_remaining_calls()}")
    return SidebarConfig(target_model=target_model, framework=framework, source_lang=source_lang, hikmah_style=st.session_state.get(K.HIKMAH_STYLE, "None"), aesthetic_choice=aesthetic_choice, active_persona=active_p, expert_mode=expert_mode)
