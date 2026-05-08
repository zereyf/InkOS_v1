"""
ui/tabs/security_log.py — Security & Forensic Ledger Tab
==========================================================
v8.0: The "Black Box" Master Sync.
      Fused Threat Intel with the Live Neural Audit Trail.
      Tracks Divergence, CIPHER routing, and hostile intrusions.
"""

import json
import textwrap
import streamlit as st
from datetime import datetime, timezone
from state import K


def render_security_log() -> None:
    st.markdown(
        '<div class="vc-header"><span class="status-dot" style="background:var(--steel);"></span>Forensic Black Box</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-family:var(--font-m); font-size:0.6rem; color:var(--text-muted); margin-bottom:20px; letter-spacing:1px; text-transform:uppercase;">'
        'Terminal Audit Trail & Intrusion Ledger'
        '</div>',
        unsafe_allow_html=True
    )

    tab_audit, tab_threats = st.tabs(["Neural Audit Trail", "Threat Intrusions"])

    # ── TAB 1: NEURAL AUDIT TRAIL (The History Ledger) ────────────────────────
    with tab_audit:
        history = st.session_state.get(K.HISTORY, [])
        
        if not history:
            st.markdown(
                '<div style="background:rgba(255,255,255,0.02); border:1px dashed rgba(255,255,255,0.1); padding:20px; text-align:center; border-radius:3px;">'
                '<span style="font-family:var(--font-m); font-size:0.65rem; color:var(--text-dim);">AWAITING INITIAL NEURAL UPLINK...</span>'
                '</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(f'<div style="font-family:var(--font-m); font-size:0.6rem; color:var(--steel); margin-bottom:15px; letter-spacing:1px;">✦ {len(history)} UPLINK(S) RECORDED</div>', unsafe_allow_html=True)
            
            for idx, run in enumerate(reversed(history)):
                score = run.get("score", 0)
                dt_str = run.get("timestamp", "UNKNOWN")
                
                # Format time for cleaner UI
                try:
                    dt_obj = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
                    time_display = dt_obj.strftime("%H:%M:%S")
                except:
                    time_display = dt_str[:8]

                target = run.get("target", "UNKNOWN")
                intent = run.get("intent", "")
                
                # Truncate intent for the HUD
                short_intent = intent[:90] + "..." if len(intent) > 90 else intent
                
                # 🧪 GHOST METRIC: NEURAL DIVERGENCE (100 - Score)
                divergence = 100 - score
                div_color = "var(--danger)" if divergence > 40 else "var(--gold)" if divergence > 15 else "#4CAF9A"

                audit_html = textwrap.dedent(f"""
                    <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); border-left:2px solid var(--steel); padding:10px 14px; font-family:var(--font-m); margin-bottom:8px;">
                        <div style="display:flex; justify-content:space-between; font-size:0.55rem; color:var(--text-muted); margin-bottom:6px;">
                            <span>[{time_display}] // CIPHER: <b style="color:var(--text);">{target.upper()}</b></span>
                            <span>FIDELITY: <b style="color:var(--text);">{score}%</b> &nbsp;|&nbsp; DIVERGENCE: <b style="color:{div_color};">{divergence}%</b></span>
                        </div>
                        <div style="font-size:0.65rem; color:var(--text-dim); border-left:1px solid rgba(255,255,255,0.1); padding-left:8px; line-height:1.4;">
                            <span style="color:var(--steel);">INTENT:</span> <span style="color:var(--text);">{short_intent}</span>
                        </div>
                    </div>
                """)
                
                with st.expander(f"[{time_display}] Run {len(history)-idx} — {target} · {score}%"):
                    st.markdown(audit_html, unsafe_allow_html=True)
                    st.markdown("<div style='font-size:0.55rem; color:var(--gold); margin-bottom:4px; font-family:var(--font-m); letter-spacing:1px;'>[ REFINED_ASSET ]</div>", unsafe_allow_html=True)
                    st.code(run.get("asset", ""), language="markdown")
                    
        st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
        if "hist_export_filename" not in st.session_state:
            st.session_state["hist_export_filename"] = f"inkos_audit_trail_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.json"
        
        st.download_button(
            "💾 Download Audit Trail",
            data=json.dumps(history, ensure_ascii=False, indent=2),
            file_name=st.session_state["hist_export_filename"],
            mime="application/json",
            use_container_width=True,
            disabled=(len(history) == 0)
        )

    # ── TAB 2: THREAT INTRUSIONS (The Security Ledger) ────────────────────────
    with tab_threats:
        log = st.session_state.get(K.SECURITY_LOG, [])

        if not log:
            st.markdown(
                '<div style="background:rgba(39, 174, 96, 0.05); border:1px solid rgba(39, 174, 96, 0.25); border-radius:3px; padding:16px; text-align:center; font-family:var(--font-m); font-size:0.7rem; color:#27AE60;">'
                '<span class="status-dot green"></span>SYSTEM SECURE. ZERO INTRUSIONS DETECTED.'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            count = len(log)
            st.markdown(
                f'<div style="font-family:var(--font-m); font-size:0.65rem; color:#FC8181; letter-spacing:1px; margin-bottom:16px;">'
                f'✦ {count} HOSTILE ATTEMPT{"S" if count > 1 else ""} INTERCEPTED</div>',
                unsafe_allow_html=True,
            )

            for entry in reversed(log):
                patterns_html = "".join([
                    f"<code style='color:#FC8181; background:rgba(252, 129, 129, 0.1); margin-right:6px; padding:3px 6px; border-radius:2px; display:inline-block; margin-bottom:4px; font-size:0.6rem;'>"
                    f"{p}</code>" for p in entry.get("patterns", [])
                ])
                
                st.markdown(f"""
                <div style="background:rgba(229, 62, 62, 0.05); border-left:2px solid #E53E3E; padding:12px; margin-bottom:12px; border-radius:0 3px 3px 0;">
                    <div style="font-family:var(--font-m); font-size:0.6rem; color:var(--text-muted); margin-bottom:8px; display:flex; justify-content:space-between;">
                        <span><b style="color:#E53E3E;">[{entry["time"]}]</b></span> 
                        <span>TARGET HASH: <code style="color:var(--gold); background:transparent; padding:0;">{entry["hash"]}</code></span>
                    </div>
                    <div style="font-family:var(--font-m); font-size:0.7rem;">
                        <div style="font-size:0.55rem; color:var(--text-muted); margin-bottom:6px; letter-spacing:1px;">VIOLATION SIGNATURE(S):</div>
                        <div>{patterns_html}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
        if "sec_export_filename" not in st.session_state:
            st.session_state["sec_export_filename"] = f"inkos_threat_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}.json"
            
        st.download_button(
            "🚨 Export Threat Report",
            data=json.dumps(log, ensure_ascii=False, indent=2),
            file_name=st.session_state["sec_export_filename"],
            mime="application/json",
            key="btn_export_sec",
            use_container_width=True,
            disabled=(len(log) == 0)
        )
