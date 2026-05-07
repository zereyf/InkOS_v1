"""
ui/tabs/security_log.py — Security Ledger Tab
===============================================
v7.0: Upgraded for InkOS. Advanced threat display, export functionality,
      and detailed pattern attribution.
Tab 3: Displays all blocked injection attempts for the session.
Entries are shown newest-first with hash attribution.
"""

import json
import streamlit as st
from datetime import datetime, timezone
from state import K


def render_security_log() -> None:
    st.markdown(
        '<div class="vc-header"><span class="status-dot" style="background:#E53E3E;box-shadow:0 0 8px #E53E3E;"></span>Threat Intel Ledger</div>',
        unsafe_allow_html=True,
    )

    log = st.session_state.get(K.SECURITY_LOG, [])

    if not log:
        st.markdown(
            '<div style="'
            'background:rgba(39, 174, 96, 0.05); border:1px solid rgba(39, 174, 96, 0.25); '
            'border-radius:4px; padding:16px; text-align:center; '
            'font-family:var(--font-m); font-size:0.75rem; color:#27AE60;'
            '">'
            '<span class="status-dot green"></span>SYSTEM SECURE. ZERO INTRUSIONS DETECTED.'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    count = len(log)
    plural = "S" if count > 1 else ""
    st.markdown(
        f'<div style="font-family:var(--font-m); font-size:0.68rem; color:#FC8181; '
        f'letter-spacing:0.1em; margin-bottom:16px;">'
        f'✦ {count} HOSTILE ATTEMPT{plural} INTERCEPTED</div>',
        unsafe_allow_html=True,
    )

    for entry in reversed(log):
        # Format the specific regex patterns that triggered the block
        patterns_html = "".join([
            f"<code style='color:#FC8181; background:rgba(252, 129, 129, 0.1); "
            f"margin-right:6px; padding:3px 6px; border-radius:3px; display:inline-block; margin-bottom:4px;'>"
            f"{p}</code>" for p in entry.get("patterns", [])
        ])
        
        st.markdown(f"""
        <div style="
            background:rgba(229, 62, 62, 0.05); 
            border-left:3px solid #E53E3E; 
            padding:12px 14px; margin-bottom:14px; 
            border-radius:0 4px 4px 0;
        ">
            <div style="font-family:var(--font-m); font-size:0.65rem; color:var(--text-muted); margin-bottom:8px;">
                <span style="color:#E53E3E; font-weight:bold;">[{entry["time"]}]</span> &nbsp;|&nbsp; 
                TARGET HASH: <code style="color:var(--gold); background:transparent; padding:0;">{entry["hash"]}</code>
            </div>
            <div style="font-family:var(--font-m); font-size:0.7rem; color:#E2E8F0;">
                <div style="font-size:0.6rem; color:var(--text-muted); margin-bottom:4px; letter-spacing:0.05em;">VIOLATION SIGNATURE(S):</div>
                <div>{patterns_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # FIX: Freeze export filename to prevent Streamlit 0-byte re-render bug
    if "sec_export_filename" not in st.session_state:
        dl_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        st.session_state["sec_export_filename"] = f"inkos_threat_report_{dl_timestamp}.json"
        
    st.download_button(
        "Export Threat Report (JSON)",
        data=json.dumps(log, ensure_ascii=False, indent=2),
        file_name=st.session_state["sec_export_filename"],
        mime="application/json",
        key="btn_export_sec",
        use_container_width=True
    )
