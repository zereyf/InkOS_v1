"""
ui/tabs/admin.py — The Command Nexus
======================================
v3.0: Zenith Redesign — High-Density IDS Terminal.
      - REFACTORED: Asymmetric Control Rod & Threat Matrix layout.
      - INTEGRATED: Dynamic Threat Level (DEFCON) calculation.
      - INTEGRATED: Custom Webkit scrollbars and CLI-style typography.
      - RETAINED: Core administrative capabilities and state bounds.
"""

import streamlit as st
import pandas as pd
from state import K, get_global_memory
from logic.admin_telemetry import get_global_metrics

def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_admin_board():
    # ── 🟢 CLEARANCE REHYDRATION ──
    if str(st.session_state.get(K.USER_HASH)).upper() == "AMEERINK":
        st.session_state[K.IS_ADMIN] = True

    if not st.session_state.get(K.IS_ADMIN):
        st.error("[ ⨂ ] CLEARANCE REJECTED: ROOT_ACCESS_REQUIRED.")
        return

    stats = get_global_metrics()
    global_mem = get_global_memory()
    quarantine_log = st.session_state.get("QUARANTINE_LOG", [])
    threat_count = len(quarantine_log)

    # ── 🟢 DYNAMIC THREAT CALCULATION ──
    if threat_count == 0:
        defcon, t_color, t_text = "5", "#4CAF9A", "CLEAR"
    elif threat_count < 5:
        defcon, t_color, t_text = "3", "var(--gold)", "ELEVATED"
    else:
        defcon, t_color, t_text = "1", "#E53E3E", "CRITICAL"

    # ── 🟢 TERMINAL CSS INJECTION ──
    st.markdown(f"""
    <style>
        /* Custom Terminal Scrollbar */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-track {{ background: rgba(10, 12, 16, 0.8); border-left: 1px solid rgba(255,255,255,0.05); }}
        ::-webkit-scrollbar-thumb {{ background: {t_color}; border-radius: 0px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #fff; }}

        /* Animations */
        @keyframes pulse-dot {{
            0% {{ opacity: 0.4; box-shadow: 0 0 4px {t_color}; }}
            50% {{ opacity: 1; box-shadow: 0 0 12px {t_color}; }}
            100% {{ opacity: 0.4; box-shadow: 0 0 4px {t_color}; }}
        }}
        .live-dot {{
            height: 8px; width: 8px; background-color: {t_color}; 
            border-radius: 50%; display: inline-block;
            animation: pulse-dot 2s infinite; margin-right: 8px;
        }}

        /* Layout Panels */
        .nexus-header {{
            font-family: var(--font-m); font-size: 1.2rem; color: var(--text);
            letter-spacing: 4px; border-bottom: 1px solid rgba(255,255,255,0.1);
            padding-bottom: 15px; margin-bottom: 25px; display: flex; align-items: center; justify-content: space-between;
        }}
        .ctrl-rod {{
            background: linear-gradient(180deg, rgba(18,22,30,0.8) 0%, rgba(10,12,16,0.9) 100%);
            border: 1px solid rgba(255,255,255,0.05); border-top: 3px solid var(--gold);
            padding: 20px; border-radius: 2px;
        }}
        .metric-block {{
            margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px dashed rgba(255,255,255,0.05);
        }}
        .metric-label {{
            font-family: var(--font-m); font-size: 0.55rem; color: var(--text-muted); letter-spacing: 2px;
        }}
        .metric-val {{
            font-family: var(--font-d); font-size: 1.8rem; color: var(--text); line-height: 1.2;
        }}
        
        /* Threat Matrix Panopticon */
        .matrix-container {{
            background: #050608; border: 1px solid rgba(255,255,255,0.05);
            border-left: 2px solid {t_color}; border-radius: 2px; padding: 0;
            min-height: 500px; display: flex; flex-direction: column;
        }}
        .matrix-header {{
            background: rgba(255,255,255,0.02); border-bottom: 1px solid rgba(255,255,255,0.05);
            padding: 10px 15px; font-family: var(--font-m); font-size: 0.65rem; color: var(--text-dim);
            display: flex; justify-content: space-between; align-items: center;
        }}
        .matrix-body {{
            padding: 15px; overflow-y: auto; max-height: 550px; flex: 1;
        }}
        .payload-box {{
            background: repeating-linear-gradient(0deg, rgba(20,20,20,0.8), rgba(20,20,20,0.8) 1px, transparent 1px, transparent 2px);
            border: 1px solid rgba(229,62,62,0.2); border-left: 3px solid #E53E3E;
            padding: 12px; font-family: monospace; font-size: 0.75rem; color: #ff8a8a;
            margin-top: 10px; border-radius: 2px; line-height: 1.4;
        }}
    </style>
    """, unsafe_allow_html=True)

    # ── 🟢 GLOBAL HEADER ──
    st.markdown(f"""
        <div class="nexus-header">
            <div><span style="color:var(--gold);">INK</span>OS // COMMAND_NEXUS</div>
            <div style="font-size: 0.65rem; color: {t_color};"><span class="live-dot"></span>DEFCON {defcon}: {t_text}</div>
        </div>
    """, unsafe_allow_html=True)

    # ── 🟢 ASYMMETRIC GRID (1 : 2.5) ──
    col_ctrl, col_matrix = st.columns([1, 2.5], gap="large")

    with col_ctrl:
        st.markdown('<div class="ctrl-rod">', unsafe_allow_html=True)
        
        # Telemetry Stack
        st.markdown(f"""
            <div class="metric-block">
                <div class="metric-label">TOTAL OPERATORS</div>
                <div class="metric-val" style="color: #5B85AA;">{stats.get("users", 0)}</div>
            </div>
            <div class="metric-block">
                <div class="metric-label">ACTIVE PERSONAS</div>
                <div class="metric-val" style="color: #4E9C81;">{stats.get("personas", 0)}</div>
            </div>
            <div class="metric-block" style="border-bottom: none;">
                <div class="metric-label">HOSTILE INTERCEPTS</div>
                <div class="metric-val" style="color: {t_color};">{threat_count}</div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color:rgba(255,255,255,0.1); margin:10px 0 20px 0;'>", unsafe_allow_html=True)
        
        # Action Stack
        st.markdown('<div class="metric-label" style="margin-bottom:10px;">SYS_DIRECTIVES</div>', unsafe_allow_html=True)
        
        current_lockdown = global_mem.get("maintenance_mode", False)
        lockdown_active = st.toggle("🔒 GLOBAL LOCKDOWN", value=current_lockdown)
        if lockdown_active != current_lockdown:
            global_mem["maintenance_mode"] = lockdown_active
            st.toast("SYSTEM LOCKED." if lockdown_active else "UPLINKS RESTORED.", icon="🚨" if lockdown_active else "✅")
            st.rerun()

        st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
        if st.button("🔥 PURGE CACHE", use_container_width=True):
            st.cache_data.clear()
            st.toast("CACHE OBLITERATED.")
            
        if st.button("🛑 CLEAR THREATS", use_container_width=True, type="primary"):
            st.session_state["QUARANTINE_LOG"] = []
            st.toast("QUARANTINE LOG PURGED.")
            st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_matrix:
        st.markdown(f"""
            <div class="matrix-container">
                <div class="matrix-header">
                    <span>>_ THE_PANOPTICON // IDS_FEED</span>
                    <span>PACKETS: {threat_count}</span>
                </div>
                <div class="matrix-body">
        """, unsafe_allow_html=True)

        if quarantine_log:
            for item in reversed(quarantine_log):
                critique = item.get("score", {}).get("critique", "") if isinstance(item.get("score"), dict) else "UNKNOWN_VECTOR"
                threat_sig = critique.split("Vector: ")[-1] if "Vector: " in critique else "PAYLOAD_ESCAPE"
                
                # Custom Terminal-Style Expander logic
                with st.expander(f"[{item['time']}] {item['id']} // SIG: {threat_sig}"):
                    st.markdown(f"""
                        <div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-dim); display:flex; justify-content:space-between; margin-bottom:5px;">
                            <span>ORIGIN: {(st.session_state.get(K.USER_HASH) or "GHOST")[:8]}</span>
                            <span>TARGET: {item.get('target', 'UNKNOWN')}</span>
                        </div>
                        <div class="payload-box">
                            {_escape(item["input"])}
                        </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
                <div style="height: 100%; display: flex; flex-direction: column; align-items: center; justify-content: center; opacity: 0.5; margin-top: 80px;">
                    <div style="font-family: var(--font-d); font-size: 3rem; color: {t_color}; margin-bottom: 10px;">{defcon}</div>
                    <div style="font-family: var(--font-m); font-size: 0.8rem; letter-spacing: 2px;">ALL SYSTEMS NOMINAL</div>
                    <div style="font-family: monospace; font-size: 0.6rem; color: var(--text-muted); margin-top: 5px;">> Awaiting hostile patterns...</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown('</div></div>', unsafe_allow_html=True)

    # ── 🟢 BROADCAST FOOTER ──
    st.markdown("<hr style='border-color:rgba(255,255,255,0.05); margin:30px 0 20px 0;'>", unsafe_allow_html=True)
    
    b1, b2, b3 = st.columns([1, 4, 1], vertical_alignment="bottom")
    with b1:
        st.markdown('<div style="font-family:var(--font-m); font-size:0.6rem; color:var(--text-dim); letter-spacing:2px; padding-bottom:10px;">GLOBAL_BROADCAST</div>', unsafe_allow_html=True)
    with b2:
        broadcast_msg = st.text_input("Broadcast", placeholder="Enter directive for all operators...", label_visibility="collapsed")
    with b3:
        if st.button("📡 TRANSMIT", use_container_width=True):
            if broadcast_msg:
                global_mem["broadcast"] = broadcast_msg
                st.toast("TRANSMISSION SENT.")
            else:
                global_mem["broadcast"] = None
                st.toast("TRANSMISSION REVOKED.")
