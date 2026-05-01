"""
ui/sidebar.py — Sidebar Rendering
"""

import streamlit as st
import json
from datetime import datetime
from typing import TypedDict
from state import K, get_remaining_calls
from config import TARGET_GUIDES, AESTHETIC_PRESETS

class SidebarConfig(TypedDict):
    target_model:  str
    framework:     str
    source_lang:   str
    islamic_mode:  bool
    aesthetic_choice: str

def render_sidebar() -> SidebarConfig:
    with st.sidebar:
        st.markdown("""
        <div style="padding:10px 0 18px 0;">
            <div class="vc-wordmark">⚡ InkOs V1.0</div>
            <div class="vc-wordmark-sub">Arabic Cognitive Prompt Engine</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        st.subheader("⚙️ Logic Configuration")
        target_model = st.selectbox(
            "Target Dialect",
            options=list(TARGET_GUIDES.keys()),
            key="sb_target",
        )
        framework = st.selectbox(
            "Logic Framework",
            ["Professional (RACE)", "Technical (Debugger)", "Academic", "Creative"],
            key="sb_framework",
        )
        source_lang = st.radio(
            "Linguistic Source",
            ["English", "Arabic (العربية)"],
            key="sb_lang",
        )

        st.markdown("<hr>", unsafe_allow_html=True)

        st.subheader("🎨 Aesthetic Direction")
        aesthetic_choice = st.selectbox(
            "Aesthetic Preset",
            options=list(AESTHETIC_PRESETS.keys()),
            key="sb_aesthetic",
            help="Select 'Raw' for literal interpretation or a preset for branded styling."
        )

        islamic_mode = st.toggle("☪️ Islamic Professional Mode", value=False, key="sb_islamic")
        if islamic_mode:
            st.markdown("""
            <div class="islamic-badge">
                <span class="status-dot green"></span>ACTIVE<br>
                Sharia-aware framing enabled<br>
                Arabic scholarly citation style
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        total_runs = len(st.session_state.get(K.HISTORY, []))
        remaining = get_remaining_calls()

        m1, m2 = st.columns(2)
        with m1:
            st.metric("Runs", total_runs)
        with m2:
            st.metric("Remaining", remaining)

        st.markdown("<hr>", unsafe_allow_html=True)

        if st.button("Reset Session", use_container_width=True, key="btn_reset"):
            from state import reset_session
            reset_session()
            st.rerun()

        if st.session_state.get(K.HISTORY):
            st.download_button(
                "Export Archive",
                data=json.dumps(
                    st.session_state[K.HISTORY],
                    ensure_ascii=False,
                    indent=2,
                ),
                file_name=f"velvetcodex_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True,
                key="btn_export_sidebar",
            )

    return SidebarConfig(
        target_model=target_model,
        framework=framework,
        source_lang=source_lang,
        islamic_mode=islamic_mode,
        aesthetic_choice=aesthetic_choice
    )