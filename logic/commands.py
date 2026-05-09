"""
logic/commands.py — Local Dispatcher
=====================================
v1.0: API-Free Command Processing.
"""
import streamlit as st
from state import K

def handle_profile():
    # Toggles the Dossier UI visibility
    st.session_state[K.SHOW_PROFILE] = not st.session_state.get(K.SHOW_PROFILE, False)
    st.rerun()

def handle_nuke():
    # Purges volatile RAM but preserves DNA/Identity
    from state import reset_session
    reset_session()
    st.toast("> SESSION PURGED. REBOOTING...", icon="⚡")
    st.rerun()

def handle_lock():
    # Instantly unlatches the user
    st.session_state[K.USER_HASH] = None
    st.session_state[K.SHOW_PROFILE] = False
    st.query_params.clear()
    st.toast("> IDENTITY UNLATCHED. RETURNING TO GHOST MODE.", icon="🔒")
    st.rerun()

# ── COMMAND MAP ──
COMMANDS = {
    "/profile": handle_profile,
    "/nuke": handle_nuke,
    "/lock": handle_lock,
}

def execute_command(raw_input: str) -> bool:
    """Intercepts and executes terminal commands locally."""
    cmd = raw_input.strip().lower()
    if cmd in COMMANDS:
        COMMANDS[cmd]()
        return True
    return False
