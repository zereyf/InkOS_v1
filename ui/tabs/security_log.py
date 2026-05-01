"""
ui/tabs/security_log.py — Security Ledger Tab
===============================================
Tab 3: Displays all blocked injection attempts for the session.
Entries are shown newest-first with hash attribution.
"""

import streamlit as st
from state import K


def render_security_log() -> None:
    st.markdown(
        '<div class="vc-header"><span class="status-dot"></span>Security Ledger</div>',
        unsafe_allow_html=True,
    )

    log = st.session_state.get(K.SECURITY_LOG, [])

    if not log:
        st.markdown(
            '<p style="font-family:var(--font-m);font-size:0.75rem;color:#27AE60;">'
            '<span class="status-dot green"></span>NO THREATS DETECTED THIS SESSION</p>',
            unsafe_allow_html=True,
        )
        return

    count = len(log)
    plural = "S" if count > 1 else ""
    st.markdown(
        f'<p style="font-family:var(--font-m);font-size:0.68rem;color:#FC8181;letter-spacing:0.1em;">'
        f'<span class="status-dot red"></span>{count} ATTEMPT{plural} BLOCKED</p>',
        unsafe_allow_html=True,
    )

    for entry in reversed(log):
        st.markdown(
            f'<div class="threat-entry">'
            f'[{entry["time"]}] &nbsp;'
            f'HASH: <code>{entry["hash"]}</code> &nbsp;|&nbsp;'
            f'PATTERNS MATCHED: {len(entry["patterns"])}'
            f'</div>',
            unsafe_allow_html=True,
        )