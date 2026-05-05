"""
ui/tabs/cognitive_map.py — Cognitive Map Reference Tab
========================================================
Tab 4: Full Arabic rhetorical device reference.
v14.5: THE INTERACTIVE UPGRADE
- Converted static cards into interactive "Remote Control" buttons.
- Added FRAMEWORK_ROUTER to safely translate Arabic patterns to system frameworks.
- Added a direct toggle for Islamic Professional Mode.
"""

import streamlit as st
import time
from engine.cognitive_map import ARABIC_COGNITIVE_MAP
from engine.islamic_layer import ISLAMIC_CONTEXT_LAYER

# Maps the Arabic rhetorical device to the backend system framework
FRAMEWORK_ROUTER = {
    "التدرج": "Creative",            # Gradualism -> Chain-of-Thought
    "الإيجاز": "Professional (RACE)", # Conciseness -> RACE Framework
    "التفصيل": "Academic",            # Elaboration -> Academic Rigor
    "التصوير": "Visual Director",     # Imagery -> Visual DNA Compiler
    "default": "Technical (Debugger)" # Fallback
}

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
        'Click a framework to instantly apply its logic to your next prompt.</p>',
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
        
        # Render the informational card
        st.markdown(f"""
        <div class="map-entry" style="animation-delay:{delay}s; margin-bottom: 8px;">
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
        
        # The Interactive Remote Control
        target_framework = FRAMEWORK_ROUTER.get(name, FRAMEWORK_ROUTER["default"])
        
        # Align the action button to the right side under the card
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button(f"⚡ Apply {name}", key=f"btn_apply_{name}", use_container_width=True):
                # Update the sidebar's session state key
                st.session_state["sb_framework"] = target_framework
                st.toast(f"✅ {name} Logic Applied! (Routing to {target_framework})")
                time.sleep(0.3) # Brief pause so the user sees the toast before UI refreshes
                st.rerun()
                
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # ── ISLAMIC CONTEXT LAYER ────────────────────────────────────────────────
    st.markdown(
        '<div class="vc-header" style="font-size:0.62rem;margin-top:6px;">'
        'Islamic Professional Context Layer</div>',
        unsafe_allow_html=True,
    )
    
    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.code(ISLAMIC_CONTEXT_LAYER.strip(), language="text")
    with col_b:
        # Check current state from the sidebar toggle
        is_active = st.session_state.get("sb_islamic", False)
        btn_label = "🟢 Mode Active" if is_active else "⚡ Activate Mode"
        
        if st.button(btn_label, key="btn_activate_islamic", use_container_width=True):
            st.session_state["sb_islamic"] = not is_active
            status_msg = "Activated" if not is_active else "Deactivated"
            st.toast(f"✅ Islamic Context Layer {status_msg}!")
            time.sleep(0.3)
            st.rerun()
