"""
ui/styles.py — Global CSS Injector
====================================
Reads the external style.css file and injects it into the Streamlit app.
Fixes the "CSS Swamp" technical debt by keeping CSS and Python separated.
"""

import streamlit as st
import os

def load_css() -> None:
    """
    Reads ui/style.css and injects it into the Streamlit DOM.
    Fails silently if the file is missing to prevent app crashes.
    """
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    
    try:
        with open(css_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.warning("System Warning: `ui/style.css` not found. Falling back to default Streamlit theme.")
        print(f"[UI ERROR] CSS file missing at: {css_path}")