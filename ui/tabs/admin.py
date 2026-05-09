"""
ui/tabs/admin.py — The Overwatch Board
======================================
v1.0: Phase 1 — Core Directives & UI Grid.
"""
import streamlit as st
import sys
from state import K

def render_admin_board():
    # ── SECURITY PERIMETER ──
    if not st.session_state.get(K.IS_ADMIN):
        st.error("[ ⨂ ] CLEARANCE REJECTED. THIS ANOMALY HAS BEEN LOGGED.")
        return

    # ── OVERWATCH CSS ──
    st.markdown("""
        <style>
            .ow-header { font-family: var(--font-m); color: var(--danger); font-size: 1.5rem; letter-spacing: 4px; border-bottom: 1px solid rgba(229, 62, 62, 0.3); padding-bottom: 10px; margin-bottom: 20px; }
            .ow-panel { background: rgba(15, 5, 5, 0.8); border: 1px solid rgba(229, 62, 62, 0.2); padding: 20px; border-radius: 3px; margin-bottom: 20px; box-shadow: 0 0 15px rgba(0,0,0,0.5); }
            .ow-title { color: var(--danger); font-family: var(--font-d); font-size: 1.1rem; letter-spacing: 2px; margin-bottom: 15px; }
            .ow-title-gold { color: var(--gold); font-family: var(--font-d); font-size: 1.1rem; letter-spacing: 2px; margin-bottom: 15px; }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ow-header">❖ VELVETCODEX OVERWATCH // ROOT_ACCESS</div>', unsafe_allow_html=True)

    # ── GRID LAYOUT ──
    col_left, col_right = st.columns([1.5, 1])

    # ==========================================
    # LEFT COLUMN: ACTIONS & OVERRIDES
    # ==========================================
    with col_left:
        # PANEL 1: GLOBAL DIRECTIVES
        st.markdown('<div class="ow-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ow-title">GLOBAL DIRECTIVES</div>', unsafe_allow_html=True)
        
        is_locked = st.session_state.get(K.MAINTENANCE_MODE, False)
        if st.toggle("🔒 INITIATE SYSTEM LOCKDOWN (GUEST EXPULSION)", value=is_locked, key="admin_lockdown_toggle"):
            if not is_locked:
                st.session_state[K.MAINTENANCE_MODE] = True
                st.toast("[!] SYSTEM LOCKED. ALL GUESTS EXPELLED.", icon="🚨")
        else:
            if is_locked:
                st.session_state[K.MAINTENANCE_MODE] = False
                st.toast("> SYSTEM UNLOCKED.", icon="✅")

        st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 15px 0;'>", unsafe_allow_html=True)
        
        if st.button("⚠️ PURGE GLOBAL CACHE", use_container_width=True, type="primary"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.toast("> SERVER CACHE OBLITERATED.", icon="🔥")
        st.markdown('</div>', unsafe_allow_html=True)

        # PANEL 2: DATABASE CONTROLS (Placeholder for Phase 2)
        st.markdown('<div class="ow-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ow-title" style="color: var(--steel);">THE PANOPTICON [ SUPABASE ]</div>', unsafe_allow_html=True)
        st.markdown("<span style='font-family: var(--font-m); font-size: 0.7rem; color: var(--text-dim);'>Awaiting Phase 2 Neural Wiring...</span>", unsafe_allow_html=True)
        with st.expander("View Global Personas"):
            st.info("Will pull all personas from DB.")
        with st.expander("Manage Locked Accounts"):
            st.info("Will allow unbanning SIDs.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ==========================================
    # RIGHT COLUMN: TELEMETRY & SURVEILLANCE
    # ==========================================
    with col_right:
        # PANEL 3: LIVE TELEMETRY
        st.markdown('<div class="ow-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ow-title-gold">LIVE TELEMETRY</div>', unsafe_allow_html=True)
        
        st.metric("Root Identity", st.session_state.get(K.USER_HASH))
        st.metric("Session State Load", f"{sys.getsizeof(st.session_state) // 1024} KB")
        st.metric("UI Language", st.session_state.get(K.UI_LANG).upper())
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 15px 0;'>", unsafe_allow_html=True)
        st.markdown("<span style='font-family: var(--font-m); font-size: 0.7rem; color: var(--text-dim);'>Active Broadcasts: 0</span>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
