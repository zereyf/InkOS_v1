"""
ui/tabs/cognitive_map.py — Cognitive Map Reference Tab
========================================================
Tab 4: Full Arabic rhetorical device reference.
Each pattern rendered as an interactive card with staggered animation.
Functions as both a reference tool and a brand asset.
"""

import streamlit as st
from engine.cognitive_map import ARABIC_COGNITIVE_MAP
from engine.islamic_layer import ISLAMIC_CONTEXT_LAYER


def render_cognitive_map() -> None:
    st.markdown(
        '<div class="vc-header"><span class="status-dot"></span>Arabic Cognitive Map</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-family:var(--font-m);font-size:0.72rem;color:var(--text-muted);'
        'line-height:1.8;margin-bottom:22px;">'
        'Eight classical Arabic rhetorical devices from '
        '<strong style="color:var(--gold);">علم البيان</strong> and '
        '<strong style="color:var(--gold);">علم المعاني</strong> — '
        'each mapped to its AI prompting equivalent. '
        'This is the engine no other tool has.</p>',
        unsafe_allow_html=True,
    )

    for i, (name, data) in enumerate(ARABIC_COGNITIVE_MAP.items()):
        color = data.get("color", "#C9A84C")
        # Staggered animation — each card appears 50ms after the previous
        delay = i * 0.05
        triggers_html = " ".join(
            f'<span class="trigger-chip">{w}</span>'
            for w in data["trigger_words"]
        )
        st.markdown(f"""
        <div class="map-entry" style="animation-delay:{delay}s;">
            <div style="display:flex;justify-content:space-between;
                        align-items:flex-start;flex-wrap:wrap;gap:10px;">
                <div>
                    <div class="map-arabic" style="color:{color};">{name}</div>
                    <div class="map-paradigm" style="color:{color};">→ {data['prompt_paradigm']}</div>
                </div>
                <div style="text-align:right;direction:rtl;">{triggers_html}</div>
            </div>
            <div class="map-instruction">{data['prompt_instruction']}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<div class="vc-header" style="font-size:0.62rem;margin-top:6px;">'
        'Islamic Professional Context Layer</div>',
        unsafe_allow_html=True,
    )
    st.code(ISLAMIC_CONTEXT_LAYER.strip(), language="text")