"""
ui/splash.py — The Terminal Gateway
=====================================
v1.3: Full UI Fix Pass.
      - Hardcoded all CSS variables (self-contained, no parent dependency).
      - Moved @keyframes to st.markdown CSS injection to survive Streamlit's HTML sanitizer.
      - Added flex-wrap for mobile safety.
      - Escaped > as &gt; in HTML strings.
      - Added font fallback stacks.
      - Backslash after triple-quotes to prevent leading newline / code-block leak.
"""

import streamlit as st
import textwrap


def render_splash_screen():

    # ── Inject animation + base vars separately so Streamlit doesn't strip them ──
    st.markdown("""\
<style>
    :root {
        --gold:       #C9A84C;
        --steel:      #8BA7B8;
        --danger:     #E53E3E;
        --bg-card:    #0E1117;
        --text:       #D4D4D4;
        --text-dim:   #666677;
        --text-muted: #888899;
        --font-d:     'Georgia', 'Times New Roman', serif;
        --font-m:     'Courier New', 'Lucida Console', monospace;
    }
    @keyframes pulse {
        0%   { opacity: 0.6; }
        50%  { opacity: 1;   text-shadow: 0 0 8px var(--danger); }
        100% { opacity: 0.6; }
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0);   }
    }
</style>
""", unsafe_allow_html=True)

    # ── Main card ──
    splash_html = textwrap.dedent("""\
    <div style="
        max-width: 700px;
        margin: 40px auto;
        padding: 30px;
        background: var(--bg-card);
        border: 1px solid rgba(255,255,255,0.05);
        border-radius: 4px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        animation: fadeIn 0.6s ease both;
    ">

        <!-- HEADER -->
        <div style="border-left: 3px solid var(--gold); padding-left: 20px; margin-bottom: 40px;">
            <h1 style="
                font-family: var(--font-d);
                color: var(--gold);
                margin: 0;
                font-size: 2.5rem;
                letter-spacing: 2px;
            ">حبر وفكرة</h1>
            <span style="
                font-family: var(--font-m);
                font-size: 0.75rem;
                color: var(--text-dim);
                letter-spacing: 4px;
            ">INKOS V2026.4 // VELVETCODEX INITIATIVE</span>
        </div>

        <!-- INTRO -->
        <div style="
            margin-bottom: 30px;
            font-family: var(--font-m);
            font-size: 0.9rem;
            color: var(--text);
            line-height: 1.7;
        ">
            Most interfaces are soulless. InkOS is a highly opinionated intelligence terminal
            designed for precision, speed, and ethical rigor. It does not just generate text;
            it refracts intent through specialized cognitive frameworks.
        </div>

        <!-- ARCHITECTURE SPECS -->
        <div style="
            background: rgba(0,0,0,0.3);
            border: 1px solid rgba(255,255,255,0.03);
            padding: 20px;
            margin-bottom: 30px;
        ">
            <div style="
                font-family: var(--font-m);
                font-size: 0.65rem;
                color: var(--gold);
                letter-spacing: 2px;
                text-transform: uppercase;
                margin-bottom: 15px;
            ">&gt;&gt; System Architecture</div>

            <div style="margin-bottom: 12px;">
                <span style="color: var(--steel); font-weight: bold; font-family: var(--font-m); font-size: 0.8rem;">[ THE REFLEX ENGINE ]</span><br>
                <span style="color: var(--text-muted); font-size: 0.8rem;">Instantaneous logic routing powered by 8B open-source intelligence.</span>
            </div>

            <div style="margin-bottom: 12px;">
                <span style="color: var(--steel); font-weight: bold; font-family: var(--font-m); font-size: 0.8rem;">[ LIS&#x100;N AL-&#x2018;ARAB ]</span><br>
                <span style="color: var(--text-muted); font-size: 0.8rem;">Deep morphological rigor. Dialectal bleed is negated; classical Fusha is enforced.</span>
            </div>

            <div style="margin-bottom: 12px;">
                <span style="color: var(--steel); font-weight: bold; font-family: var(--font-m); font-size: 0.8rem;">[ MAQASID LAYER ]</span><br>
                <span style="color: var(--text-muted); font-size: 0.8rem;">Strict ethical filtering. Generative outputs are inherently aligned with foundational principles.</span>
            </div>
        </div>

        <!-- AUTHOR SIGNATURE -->
        <div style="
            display: flex;
            flex-wrap: wrap;
            gap: 16px;
            justify-content: space-between;
            align-items: flex-end;
            border-top: 1px solid rgba(255,255,255,0.05);
            padding-top: 20px;
        ">
            <div>
                <div style="font-family: var(--font-m); font-size: 0.6rem; color: var(--text-dim); letter-spacing: 2px;">ARCHITECT</div>
                <div style="color: var(--text); font-family: var(--font-m); font-size: 0.9rem;">AMEERINK</div>
            </div>

            <!-- THE PULSING LOCK -->
            <div style="text-align: right; animation: pulse 2s infinite;">
                <div style="font-family: var(--font-m); font-size: 0.65rem; color: var(--danger); letter-spacing: 2px; font-weight: bold;">[ &#x2298; ] TERMINAL LOCKED</div>
                <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--text-muted); letter-spacing: 1px;">AWAITING OPERATOR LATCH</div>
            </div>
        </div>

    </div>
    """)

    st.markdown(splash_html, unsafe_allow_html=True)

    # ── Hint bar ──
    hint_html = textwrap.dedent("""\
    <div style="text-align: center; margin-top: 20px;">
        <span style="
            background: rgba(229,62,62,0.05);
            border: 1px solid rgba(229,62,62,0.2);
            color: var(--danger);
            padding: 8px 15px;
            font-family: var(--font-m);
            font-size: 0.65rem;
            letter-spacing: 2px;
        ">
            [&lt;&lt;] ALIGN IDENTITY IN SIDEBAR TO UNLOCK
        </span>
    </div>
    """)

    st.markdown(hint_html, unsafe_allow_html=True)
