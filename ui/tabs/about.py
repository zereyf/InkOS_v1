"""
ui/tabs/about.py — System Manifesto & HUD
==========================================
v1.5: Final Integration.
      - Integrated dynamic datetime telemetry.
      - Refined HUD diagnostic metrics.
      - Hardened typographic constraints (Emoji-Free).
      - Applied textwrap.dedent for Markdown/HTML safety.
"""

import streamlit as st
import textwrap
from datetime import datetime

def render_about():
    # ── 0. TELEMETRY INITIALIZATION ──
    # Captures current execution time for the boot log
    now = datetime.now().strftime("%H:%M:%S")

    # ── 1. HEADER & SYSTEM IDENTITY ──
    header_html = textwrap.dedent("""
    <div style="border-left: 3px solid var(--gold); padding-left: 20px; margin-bottom: 40px; margin-top: 10px;">
        <h1 style="font-family: var(--font-d); color: var(--gold); margin: 0; font-size: 2.8rem; letter-spacing: 3px;">حبر وفكرة</h1>
        <span style="font-family: var(--font-m); font-size: 0.75rem; color: var(--text-dim); letter-spacing: 5px;">INKOS V2026.4 // VELVETCODEX CORE</span>
    </div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    # ── 2. SYSTEM DIAGNOSTICS (THE HUD) ──
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(textwrap.dedent("""
            <div style="border: 1px solid rgba(201,168,76,0.2); padding: 15px; border-radius: 4px; background: rgba(0,0,0,0.2);">
                <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--gold); letter-spacing: 2px;">❖ FUSHA_PRECISION</div>
                <div style="font-family: var(--font-d); font-size: 1.8rem; color: var(--text);">99.8<span style="font-size: 0.8rem; color: var(--gold);">%</span></div>
                <div style="font-family: var(--font-m); font-size: 0.45rem; color: #4CAF9A;">STATUS: NOMINAL</div>
            </div>
        """), unsafe_allow_html=True)

    with col2:
        st.markdown(textwrap.dedent("""
            <div style="border: 1px solid rgba(124,158,191,0.2); padding: 15px; border-radius: 4px; background: rgba(0,0,0,0.2);">
                <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--steel); letter-spacing: 2px;">❖ NEURAL_LOAD</div>
                <div style="font-family: var(--font-d); font-size: 1.8rem; color: var(--text);">14.2<span style="font-size: 0.8rem; color: var(--steel);">ms</span></div>
                <div style="font-family: var(--font-m); font-size: 0.45rem; color: var(--gold);">LATENCY: OPTIMIZED</div>
            </div>
        """), unsafe_allow_html=True)

    with col3:
        st.markdown(textwrap.dedent("""
            <div style="border: 1px solid rgba(229,62,62,0.2); padding: 15px; border-radius: 4px; background: rgba(0,0,0,0.2);">
                <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--danger); letter-spacing: 2px;">❖ MAQASID_GUARD</div>
                <div style="font-family: var(--font-d); font-size: 1.8rem; color: var(--text);">ACTIVE</div>
                <div style="font-family: var(--font-m); font-size: 0.45rem; color: var(--danger);">ENFORCING ETHICS</div>
            </div>
        """), unsafe_allow_html=True)

    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)

    # ── 3. THE ARCHITECTURE MANIFESTO ──
    manifesto_html = textwrap.dedent("""
    <div style="background: rgba(255,255,255,0.02); padding: 25px; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px;">
        <h4 style="color: var(--gold); font-family: var(--font-m); font-size: 0.9rem; letter-spacing: 2px; margin-bottom: 20px;">[ LOGIC_GATES & MODULES ]</h4>
        
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
            <div>
                <p style="color: var(--steel); font-family: var(--font-m); font-size: 0.75rem; margin-bottom: 5px;">> REFLEX ENGINE</p>
                <p style="color: var(--text-muted); font-size: 0.8rem; line-height: 1.5;">8B Intelligence optimized for surgical prompt refraction and logic auditing.</p>
            </div>
            <div>
                <p style="color: var(--steel); font-family: var(--font-m); font-size: 0.75rem; margin-bottom: 5px;">> LISĀN AL-'ARAB</p>
                <p style="color: var(--text-muted); font-size: 0.8rem; line-height: 1.5;">Morphological layer ensuring linguistic purity and dialectal bleed negation.</p>
            </div>
            <div>
                <p style="color: var(--steel); font-family: var(--font-m); font-size: 0.75rem; margin-bottom: 5px;">> MAQASID FRAMEWORK</p>
                <p style="color: var(--text-muted); font-size: 0.8rem; line-height: 1.5;">Inherent ethical alignment protocol guarding against adversarial outputs.</p>
            </div>
            <div>
                <p style="color: var(--steel); font-family: var(--font-m); font-size: 0.75rem; margin-bottom: 5px;">> VELVETCODEX</p>
                <p style="color: var(--text-muted); font-size: 0.8rem; line-height: 1.5;">The underlying security initiative governing neural persistence and vault encryption.</p>
            </div>
        </div>
    </div>
    """)
    st.markdown(manifesto_html, unsafe_allow_html=True)

    st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)

    # ── 4. DYNAMIC TERMINAL BOOT LOG ──
    # Uses f-string to inject real-time clock data
    log_html = textwrap.dedent(f"""
    <div style="background: #000; padding: 15px; border: 1px solid rgba(255,255,255,0.1); border-radius: 2px; font-family: var(--font-m); font-size: 0.65rem; color: #4CAF9A; opacity: 0.8;">
        <div style="margin-bottom: 4px;">[ {now} ] BOOT: InkOS Kernel v2026.4.6 loaded.</div>
        <div style="margin-bottom: 4px;">[ {now} ] AUTH: Identity check bypass... [GHOST_MODE_ACTIVE]</div>
        <div style="margin-bottom: 4px;">[ {now} ] SYNC: Connecting to Maqasid Ethical Layer... DONE</div>
        <div style="margin-bottom: 4px;">[ {now} ] LANG: Injecting Fusha linguistic constraints... DONE</div>
        <div style="margin-bottom: 4px; color: var(--gold);">[ {now} ] ALERT: Awaiting Operator Latch...</div>
    </div>
    """)
    st.markdown(log_html, unsafe_allow_html=True)

    # ── 5. CTAs ──
    current_uid = st.session_state.get("USER_HASH")
    is_guest = not current_uid or "GUEST_" in str(current_uid).upper()
    
    if is_guest:
        st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
        if st.button("[ INITIATE TERMINAL LATCH ]", use_container_width=True):
            st.toast("> ALIGN IDENTITY IN SIDEBAR TO PROCEED.")
