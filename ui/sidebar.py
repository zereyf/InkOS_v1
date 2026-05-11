"""
ui/sidebar.py — Premium Sidebar
=================================
v3.0: Dynamic username, stats card, clean section layout.
"""
import streamlit as st
from typing import TypedDict, Optional
from state import K, get_remaining_calls
from config import TARGET_GUIDES, AESTHETIC_PRESETS, AUTO_SELECT_LABEL, LOGIC_FRAMEWORKS
from config.personas import STARTER_PERSONAS
from forge.rhetoric_engine import HIKMAH_PROFILES
from vault.supabase_client import SUPABASE_MISSING


class SidebarConfig(TypedDict):
    target_model:    str
    framework:       str
    source_lang:     str
    hikmah_style:    str
    aesthetic_choice:str
    active_persona:  Optional[dict]
    expert_mode:     bool


def _get_display_name() -> str:
    """
    Returns the display name from USER_HASH.
    USER_HASH is the ID the user typed to log in (e.g. 'Ameer', 'Yuki').
    Falls back to 'User' if not set.
    """
    raw = st.session_state.get(K.USER_HASH) or ""
    raw = str(raw).strip()
    if not raw or raw.upper().startswith("GUEST_"):
        return "Guest"
    # Capitalize first letter, rest as-is
    return raw[0].upper() + raw[1:]


def _get_avatar_letter(name: str) -> str:
    return name[0].upper() if name else "?"


def render_sidebar_brand() -> None:
    is_active = not SUPABASE_MISSING and bool(st.session_state.get(K.USER_HASH))
    label     = "ACTIVE" if is_active else ("DB_FAULT" if SUPABASE_MISSING else "OFFLINE")
    dot_class = "active" if is_active else "inactive"

    st.markdown(f"""
    <div class='uplink-bar'>
      <span>NEURAL_UPLINK</span>
      <span class='dot {dot_class}'>● {label}</span>
    </div>
    <div class='brand-ar'>حبر وفكرة</div>
    <div class='brand-divider'></div>
    <div class='brand-en'>INKOS  //  MUTI_AUTONOMOUS v1.0</div>
    """, unsafe_allow_html=True)


def render_sidebar() -> SidebarConfig:

    # ── Identity Card ──
    name   = _get_display_name()
    letter = _get_avatar_letter(name)
    is_logged_in = (
        bool(st.session_state.get(K.USER_HASH))
        and not str(st.session_state.get(K.USER_HASH, "")).upper().startswith("GUEST_")
    )

    if is_logged_in:
        st.markdown(f"""
        <div class='identity-card'>
          <div class='avatar'>{letter}</div>
          <div class='name'>{name}</div>
          <div class='logout'>↩</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Logout", key="logout_btn", use_container_width=True):
            st.session_state[K.USER_HASH] = None
            st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Logic Configuration ──
    st.markdown("""
    <div class='sidebar-section-label'>LOGIC CONFIGURATION</div>
    """, unsafe_allow_html=True)

    target_model = st.selectbox(
        "Target Model",
        [AUTO_SELECT_LABEL] + list(TARGET_GUIDES.keys()),
        key="sb_target",
    )
    framework = st.selectbox(
        "Framework",
        LOGIC_FRAMEWORKS,
        key="sb_framework",
    )

    # Input Language as pill toggle
    lang_options = ["English", "Arabic (العربية)"]
    current_lang = st.session_state.get("sb_lang_idx", 0)
    lang_cols    = st.columns(2)
    for i, lang in enumerate(lang_options):
        with lang_cols[i]:
            is_sel = current_lang == i
            style  = (
                "background:#6366f1;color:#fff;border:1px solid #6366f1;"
                if is_sel else
                "background:transparent;color:#71717a;border:1px solid #ffffff0f;"
            )
            if st.button(
                lang,
                key=f"lang_{i}",
                use_container_width=True,
            ):
                st.session_state["sb_lang_idx"] = i
                st.rerun()
    source_lang = lang_options[st.session_state.get("sb_lang_idx", 0)]

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Active Persona ──
    st.markdown("""
    <div class='sidebar-section-label'>ACTIVE PERSONA</div>
    """, unsafe_allow_html=True)

    user_personas = st.session_state.get(K.PERSONA_LIST, [])
    options_map   = {"None": None}
    for pname, p in STARTER_PERSONAS.items():
        if pname != "None":
            options_map[f"{pname} [S]"] = p
    for p in user_personas:
        options_map[f"{p['name']} [C]"] = p

    selected_key = st.selectbox(
        "Persona",
        options=list(options_map.keys()),
        key="sb_persona_global_widget",
        label_visibility="collapsed",
    )
    active_p = options_map.get(selected_key)
    st.session_state[K.ACTIVE_PERSONA] = active_p

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Aesthetic ──
    st.markdown("""
    <div class='sidebar-section-label'>AESTHETIC</div>
    """, unsafe_allow_html=True)

    aesthetic_choice = st.selectbox(
        "Aesthetic",
        list(AESTHETIC_PRESETS.keys()),
        key=K.AESTHETIC_CHOICE,
        disabled=active_p is not None,
        label_visibility="collapsed",
    )
    st.selectbox(
        "Hikmah Style",
        list(HIKMAH_PROFILES.keys()),
        key=K.HIKMAH_STYLE,
        disabled=active_p is not None,
        label_visibility="collapsed",
    )
    expert_mode = st.checkbox("Expert Diagnostics", key="sb_expert")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Session Stats ──
    runs_val  = len(st.session_state.get(K.HISTORY, []))
    calls_val = 10 - get_remaining_calls()
    saved_val = len(st.session_state.get("local_vault_items", []))
    saved_str = str(saved_val) if saved_val > 0 else "—"

    st.markdown(f"""
    <div class='stats-card'>
      <div class='stat-item'>
        <div class='stat-value'>{runs_val}</div>
        <div class='stat-label'>RUNS</div>
      </div>
      <div class='stat-item'>
        <div class='stat-value'>{calls_val}</div>
        <div class='stat-label'>CALLS</div>
      </div>
      <div class='stat-item'>
        <div class='stat-value'>{saved_str}</div>
        <div class='stat-label'>SAVED</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Target Intelligence Card ──
    auto_target = st.session_state.get(K.AUTO_TARGET, "ChatGPT")
    auto_reason = st.session_state.get(K.AUTO_REASON, "Awaiting input...")
    st.markdown(f"""
    <div class='intel-card'>
      <div class='intel-title'>TARGET INTELLIGENCE</div>
      <div class='intel-row'>
        <span class='intel-key'>MODEL</span>
        <span class='intel-val'>{auto_target}</span>
      </div>
      <div class='intel-row'>
        <span class='intel-key'>ROUTING</span>
        <span class='intel-val'>{auto_reason[:40]}</span>
      </div>
      <div class='intel-row'>
        <span class='intel-key'>STATUS</span>
        <span class='intel-val' style='color:#22c55e;'>● Active</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    return SidebarConfig(
        target_model    = target_model,
        framework       = framework,
        source_lang     = source_lang,
        hikmah_style    = st.session_state.get(K.HIKMAH_STYLE, "None"),
        aesthetic_choice= aesthetic_choice,
        active_persona  = active_p,
        expert_mode     = expert_mode,
    )
