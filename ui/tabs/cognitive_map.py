"""
ui/tabs/cognitive_map.py — Cognitive Map Reference Tab
========================================================
Tab 4: Full Arabic rhetorical device reference.
v15.0: Upgraded for InkOS. Advanced Tech-Noir UI, Matrix Routing styling, 
       and Streamlit Callback persistence.
"""

import streamlit as st
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

# ── STREAMLIT CALLBACKS ───────────────────────────────────────────────────────
# Callbacks execute BEFORE the main script runs, bypassing the render lock.

def apply_framework_callback(target_framework: str, name: str):
    st.session_state["sb_framework"] = target_framework
    st.toast(f"LATCHED: {name} → {logic}", icon="⚡") 

def toggle_islamic_callback():
    current_state = st.session_state.get("sb_islamic", False)
    st.session_state["sb_islamic"] = not current_state
    status_msg = "Activated" if not current_state else "Deactivated"
    st.toast(f"☪ Protocol {status_msg}")

# ──────────────────────────────────────────────────────────────────────────────

def render_cognitive_map() -> None:
    st.markdown(
        '<div class="vc-header"><span class="status-dot" style="background:#90CDF4;box-shadow:0 0 8px #90CDF4;"></span>Linguistic Routing Matrix</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-family:var(--font-m);font-size:0.72rem;color:var(--text-muted);'
        'line-height:1.8;margin-bottom:24px;">'
        'Neural translation logic mapping Classical Arabic rhetorical structures '
        '(<strong style="color:var(--gold);">علم البيان</strong> & <strong style="color:var(--gold);">علم المعاني</strong>) '
        'to algorithmic AI prompt frameworks. Latch a node below to override current session logic.</p>',
        unsafe_allow_html=True,
    )

    for i, (name, data) in enumerate(ARABIC_COGNITIVE_MAP.items()):
        color = data.get("color", "#90CDF4")
        
        triggers_html = " ".join(
            f'<span style="display:inline-block;background:rgba(124,158,191,0.1);border:1px solid rgba(124,158,191,0.25);border-radius:2px;padding:2px 8px;margin:2px;font-size:0.75rem;font-family:var(--font-a);color:#E2E8F0;">{w}</span>'
            for w in data["trigger_words"]
        )
        
        target_framework = FRAMEWORK_ROUTER.get(name, FRAMEWORK_ROUTER["default"])
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"""
            <div style="
                background:rgba(255,255,255,0.015);
                border:1px solid rgba(255,255,255,0.05);
                border-left:3px solid {color};
                border-radius:0 4px 4px 0;
                padding:16px; margin-bottom:12px;
            ">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px;margin-bottom:14px;">
                    <div>
                        <div style="font-family:var(--font-a);font-size:1.4rem;color:{color};line-height:1.2;">{name}</div>
                        <div style="font-family:var(--font-m);font-size:0.6rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.1em;margin-top:6px;">
                            ENGINE MAPPING: <span style="color:var(--gold);">{data['prompt_paradigm']}</span>
                        </div>
                    </div>
                    <div style="text-align:right;direction:rtl;max-width:60%;">
                        <div style="font-size:0.55rem;color:var(--steel);letter-spacing:0.1em;margin-bottom:6px;font-family:var(--font-m);">DETECTION TRIGGERS</div>
                        {triggers_html}
                    </div>
                </div>
                <div style="font-family:var(--font-m);font-size:0.75rem;color:#E2E8F0;line-height:1.6;background:rgba(0,0,0,0.3);padding:12px;border-radius:4px;border:1px solid rgba(255,255,255,0.03);">
                    <span style="color:{color};font-weight:bold;margin-right:8px;font-size:0.65rem;letter-spacing:0.05em;">SYSTEM DIRECTIVE:</span><br>
                    {data['prompt_instruction']}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown("<div style='height:35px'></div>", unsafe_allow_html=True) # Vertical alignment trick
            st.button(
                f"LATCH {target_framework.upper()}", 
                key=f"btn_apply_{name}", 
                on_click=apply_framework_callback,
                args=(target_framework, name),
                use_container_width=True,
                help=f"Locks the {target_framework} framework to your sidebar."
            )

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # ── ISLAMIC CONTEXT LAYER ────────────────────────────────────────────────
    is_active = st.session_state.get("sb_islamic", False)
    status_color = "#4CAF9A" if is_active else "var(--text-dim)"
    status_text = "ONLINE" if is_active else "STANDBY"
    
    st.markdown(f"""
    <div style="
        display:flex;justify-content:space-between;align-items:center;
        border-bottom:1px dashed rgba(255,255,255,0.1);
        padding-bottom:12px;margin-bottom:16px;
    ">
        <div style="font-family:var(--font-m);font-size:0.8rem;color:#6EE7B7;letter-spacing:0.1em;text-transform:uppercase;">
            ✦ Islamic Compliance Protocol
        </div>
        <div style="font-family:var(--font-m);font-size:0.65rem;color:{status_color};letter-spacing:0.1em;">
            STATUS: {status_text}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col_a, col_b = st.columns([4, 1])
    with col_a:
        st.markdown('<div style="font-size:0.6rem;color:var(--text-muted);font-family:var(--font-m);margin-bottom:6px;text-transform:uppercase;">Injected Payload</div>', unsafe_allow_html=True)
        st.code(ISLAMIC_CONTEXT_LAYER.strip(), language="text")
    with col_b:
        btn_label = "Deactivate" if is_active else "Initialize"
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        st.button(
            btn_label, 
            key="btn_activate_islamic", 
            on_click=toggle_islamic_callback,
            use_container_width=True,
            type="primary" if not is_active else "secondary"
        )
