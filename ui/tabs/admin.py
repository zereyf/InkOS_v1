"""
ui/tabs/admin.py — The Overwatch Board
======================================
v1.4: Tactical Synchronization — Global Lockdown Patch.
      - UPDATED: Global Lockdown toggle now writes to shared server memory.
      - RETAINED: Cyber-Noir HUD, Panopticon Feed, and Broadcast Matrix.
"""

import streamlit as st
import pandas as pd
from state import K, get_global_memory
from logic.admin_telemetry import get_global_metrics, get_recent_activity


def render_admin_board():
    # Clearance Verification
    if not st.session_state.get(K.IS_ADMIN):
        st.error("[ ⨂ ] CLEARANCE REJECTED: ROOT_ACCESS_REQUIRED.")
        return

    # Fetch Live Telemetry Data
    stats = get_global_metrics()
    recent_logs = get_recent_activity()
    global_mem = get_global_memory()

    # ── TACTICAL CSS INJECTION ──
    st.markdown("""
    <style>
        @keyframes breathe-alert {
            0% { box-shadow: -5px 0 15px -5px rgba(229,62,62,0.1); border-left-color: #9C4E4E; }
            50% { box-shadow: -5px 0 25px -5px rgba(229,62,62,0.6); border-left-color: #E53E3E; }
            100% { box-shadow: -5px 0 15px -5px rgba(229,62,62,0.1); border-left-color: #9C4E4E; }
        }
        .neural-card {
            background: rgba(18, 22, 30, 0.4);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.05);
            clip-path: polygon(8px 0, 100% 0, 100% calc(100% - 8px), calc(100% - 8px) 100%, 0 100%, 0 8px);
            padding: 16px 20px;
            margin-bottom: 10px;
            transition: all 0.3s ease;
        }
        .neural-card:hover {
            background: rgba(25, 30, 40, 0.6);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .alert-pulse {
            animation: breathe-alert 2.5s infinite ease-in-out;
        }
        .panopticon-feed {
            background-image: radial-gradient(rgba(255, 255, 255, 0.03) 1px, transparent 1px);
            background-size: 12px 12px;
            background-color: rgba(10, 12, 16, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 2px;
            padding: 15px;
        }
        .ow-header {
            font-family: var(--font-m);
            font-size: 0.9rem;
            color: var(--gold);
            letter-spacing: 3px;
            border-bottom: 1px solid var(--gold);
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .ow-title {
            font-family: var(--font-m);
            font-size: 0.75rem;
            color: var(--steel);
            letter-spacing: 2px;
            margin-bottom: 15px;
        }
        .ow-title-gold {
            font-family: var(--font-m);
            font-size: 0.75rem;
            color: var(--gold);
            letter-spacing: 2px;
            margin-bottom: 15px;
        }
        .ow-panel {
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 4px;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ow-header">❖ INKOS OVERWATCH // ROOT_ACCESS</div>', unsafe_allow_html=True)

    # ── NEURAL CARD UI COMPONENT ──
    def _neural_card(title, value, border_color, val_color="#E2E8F0", is_alert=False):
        alert_class = "alert-pulse" if is_alert and str(value) != "0" else ""
        return f"""
        <div class="neural-card {alert_class}" style="border-left: 4px solid {border_color};">
            <div style="font-family:var(--font-m); font-size:0.65rem; color:var(--steel); letter-spacing:1.5px; text-transform:uppercase; margin-bottom:12px;">
                {title}
            </div>
            <div style="font-family:'Times New Roman', Times, serif; font-size:2.2rem; color:{val_color}; line-height:1; letter-spacing: 0.5px;">
                {value}
            </div>
        </div>
        """

    # ── TOP LEVEL METRICS ──
    st.markdown("<div style='height:5px'></div>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(_neural_card("TOTAL OPERATORS", stats.get("users", 0), "#5B85AA"), unsafe_allow_html=True) 
    with m2:
        st.markdown(_neural_card("FORGED PERSONAS", stats.get("personas", 0), "#4E9C81"), unsafe_allow_html=True) 
    with m3:
        st.markdown(_neural_card("SECURITY EVENTS", stats.get("logs", 0), "#9C4E4E", is_alert=True), unsafe_allow_html=True) 
    with m4:
        st.markdown(_neural_card("SYSTEM_UPLINK", "STABLE", "var(--gold)", "var(--gold)"), unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown("---")

    col_left, col_right = st.columns([1.5, 1])

    with col_left:
        # THE PANOPTICON: LIVE LOGS
        st.markdown('<div class="ow-title">THE PANOPTICON // LIVE_SECURITY_FEED</div>', unsafe_allow_html=True)
        st.markdown('<div class="panopticon-feed">', unsafe_allow_html=True)
        if recent_logs:
            df = pd.DataFrame(recent_logs)
            st.dataframe(
                df[['created_at', 'user_hash', 'event_type', 'status']], 
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No recent security anomalies detected.")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        # ── SYSTEM CONTROLS ──
        st.markdown('<div class="ow-panel">', unsafe_allow_html=True)
        st.markdown('<div class="ow-title-gold">SYSTEM DIRECTIVES</div>', unsafe_allow_html=True)
        
        # Maintenance Switch (Global Memory Sync)
        current_lockdown = global_mem.get("maintenance_mode", False)
        lockdown_active = st.toggle("🔒 GLOBAL LOCKDOWN", value=current_lockdown, help="Sever all non-admin neural uplinks across the server.")
        
        if lockdown_active != current_lockdown:
            global_mem["maintenance_mode"] = lockdown_active
            st.toast("SYSTEM LOCKED." if lockdown_active else "UPLINKS RESTORED.", icon="🚨" if lockdown_active else "✅")
            st.rerun()
            
        if st.button("🔥 PURGE SERVER CACHE", use_container_width=True):
            st.cache_data.clear()
            st.toast("CACHE OBLITERATED.")

        # BROADCAST FIELD
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 15px 0;'>", unsafe_allow_html=True)
        st.markdown('<div class="ow-title">TERMINAL BROADCAST</div>', unsafe_allow_html=True)
        broadcast_msg = st.text_input("Message Label", placeholder="Enter directive for all operators...", label_visibility="collapsed")
        
        b1, b2 = st.columns([3, 1])
        with b1:
            if st.button("📡 TRANSMIT", use_container_width=True):
                if broadcast_msg:
                    global_mem["broadcast"] = broadcast_msg
                    st.toast("GLOBAL TRANSMISSION SENT.")
                else:
                    st.warning("Enter a message to transmit.")
        with b2:
            if st.button("🛑 CUT", use_container_width=True, help="Revoke current broadcast banner"):
                global_mem["broadcast"] = None
                st.toast("TRANSMISSION REVOKED.")
        st.markdown('</div>', unsafe_allow_html=True)

        # ARABIC BRANDING METRICS
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="ow-panel" style="border-color: var(--gold);">', unsafe_allow_html=True)
        st.markdown('<div class="ow-title-gold">LISAAN AL-ARAB // حبر وفكرة</div>', unsafe_allow_html=True)
        st.markdown("<div style='font-family: var(--font-m); font-size: 0.65rem; color: var(--gold); letter-spacing:1px;'>تحديثات النظام نشطة // STATUS: OPERATIONAL</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
