"""
ui/tabs/about.py — System Manifesto
=====================================
v1.3: Tabular Refactor.
      - Integrated textwrap.dedent for HTML integrity.
      - Decoupled from primary bootloader for global access.
"""

import streamlit as st
import textwrap

def render_about():
    about_html = textwrap.dedent("""
    <div style="border-left: 3px solid var(--gold); padding-left: 15px; margin-bottom: 30px; margin-top: 10px;">
        <h2 style="font-family: var(--font-d); color: var(--gold); margin: 0; letter-spacing: 2px;">حبر وفكرة</h2>
        <span style="font-family: var(--font-m); font-size: 0.8rem; color: var(--text-dim); letter-spacing: 3px;">INKOS V2026.4 // INITIALIZATION</span>
    </div>
    
    <div style="background: rgba(255,255,255,0.02); padding: 20px; border: 1px solid rgba(255,255,255,0.05); border-radius: 4px; margin-bottom: 20px;">
        <h4 style="color: var(--steel); font-family: var(--font-m); font-size: 0.9rem; letter-spacing: 1px;">> THE ARCHITECTURE</h4>
        <p style="color: var(--text-muted); font-size: 0.85rem; line-height: 1.6;">
            InkOS is a specialized Prompt Engineering and Cybersecurity interface. 
            It utilizes an 8B Reflex Engine to execute high-speed logical audits, enforce strict 
            Arabic linguistic rules (Fusha), and align outputs with a Maqasid ethical framework.
        </p>
    </div>
    """)
    st.markdown(about_html, unsafe_allow_html=True)
