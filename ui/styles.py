"""
ui/styles.py — Global CSS Injector
"""
import streamlit as st
import os

def load_css() -> None:
    """Reads ui/style.css and injects it into the Streamlit app."""
    # Ensure we get the correct path regardless of where the script is called from
    base_path = os.path.dirname(__file__)
    css_path = os.path.join(base_path, "style.css")
    
    if os.path.exists(css_path):
        try:
            with open(css_path, "r", encoding="utf-8") as f:
                css_content = f.read()
            
            # CRITICAL: We add the <style> tags here. 
            # The .css file itself must not contain them.
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"CSS Loading Exception: {e}")
    else:
        st.error(f"CSS file not found at: {css_path}")