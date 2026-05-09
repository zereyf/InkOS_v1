"""
ui/components/ghost_bar.py — Command Input
==========================================
v1.0: High-Contrast Terminal Input.
"""
import streamlit as st
from logic.commands import execute_command

def render_ghost_bar():
    # Tech-Noir CSS for the input bar
    st.markdown("""
        <style>
            .stTextInput input {
                background-color: rgba(10, 10, 10, 0.9) !important;
                color: #4CAF9A !important;
                font-family: var(--font-m) !important;
                border: 1px solid rgba(255,255,255,0.05) !important;
                font-size: 0.7rem !important;
                letter-spacing: 1px;
                border-radius: 2px !important;
            }
            .stTextInput input:focus {
                border-color: var(--gold) !important;
                box-shadow: 0 0 5px rgba(201, 168, 76, 0.2) !important;
            }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        # The input widget
        cmd_input = st.text_input(
            label="COMMAND_DECK",
            placeholder="TYPE /COMMAND...",
            label_visibility="collapsed",
            key="ghost_cmd_input"
        )
        
        # Intercept and process
        if cmd_input:
            success = execute_command(cmd_input)
            if not success:
                st.toast(f"[!] UNKNOWN COMMAND: {cmd_input}", icon="⚠️")
