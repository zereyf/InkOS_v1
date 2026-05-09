"""
ui/tabs/admin.py — The Overwatch Board
======================================
v1.0: Phase 1 — Core Directives & UI Grid.
"""

import streamlit as st
import pandas as pd
from state import K
from logic.admin_telemetry import get_global_metrics, get_recent_activity

def render_admin_board():
    if not st.session_state.get(K.IS_ADMIN):
        st.error("[ ⨂ ] CLEARANCE REJECTED.")
        return

    # Fetch Live Data
    stats = get_global_metrics()
    recent_logs = get_recent_activity()

    st.markdown('<div class="ow-header">❖ VELVETCODEX OVERWATCH // ROOT_ACCESS</div>', unsafe_allow_html=True)

    # ── TOP LEVEL METRICS ──
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("TOTAL OPERATORS", stats["users"])
    with m2:
        st.metric("FORGED PERSONAS", stats["personas"])
    with m3:
        st.metric("SECURITY EVENTS", stats["logs"], delta_color="inverse")
    with m4:
        # Subtle nod to your MLBB leadership
        st.metric("TEAM_REI_UPLINKS", "STABLE", help="Uplink status for Team Rei assets.")

    st.markdown("---")

    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        # THE PANOPTICON: LIVE LOGS
        st.markdown('<div class="ow-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ow-title">THE PANOPTICON // LIVE_SECURITY_FEED</div>', unsafe_allow_html=True)
        
        if recent_logs:
            df = pd.DataFrame(recent_logs)
            # Format the dataframe for a cleaner terminal look
            st.dataframe(
                df[['created_at', 'user_hash', 'event_type', 'status']], 
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No recent security anomalies detected.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        # SYSTEM CONTROLS
        st.markdown('<div class="ow-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ow-title-gold">SYSTEM DIRECTIVES</div>', unsafe_allow_html=True)
        
        # Maintenance Switch
        is_locked = st.session_state.get(K.MAINTENANCE_MODE, False)
        if st.toggle("🔒 GLOBAL LOCKDOWN", value=is_locked):
            st.session_state[K.MAINTENANCE_MODE] = True
            st.toast("SYSTEM LOCKED.", icon="🚨")
            
        if st.button("🔥 PURGE SERVER CACHE", use_container_width=True):
            st.cache_data.clear()
            st.toast("CACHE OBLITERATED.")
            
        st.markdown('</div>', unsafe_allow_html=True)
        
        # ARABIC BRANDING METRICS
        st.markdown('<div class="ow-panel" style="border-color: var(--gold);">', unsafe_allow_html=True)
        st.markdown('<div class="ow-title-gold">LISAAN AL-ARAB // حبر وفكرة</div>', unsafe_allow_html=True)
        st.markdown("<div style='font-family: var(--font-a); font-size: 0.9rem; color: var(--gold);'>تحديثات النظام نشطة</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)