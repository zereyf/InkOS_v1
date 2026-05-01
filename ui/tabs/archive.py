"""
ui/tabs/archive.py — Neural Archive Tab
=========================================
Tab 2: Filterable history of all refinements.
Sorted filter options prevent random ordering across reruns.
Unique download button keys prevent DuplicateWidgetID errors.
"""

import json
import streamlit as st
from datetime import datetime
from state import K


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_archive() -> None:
    st.markdown(
        '<div class="vc-header"><span class="status-dot"></span>Neural Archive</div>',
        unsafe_allow_html=True,
    )

    history = st.session_state.get(K.HISTORY, [])

    if not history:
        st.markdown(
            '<p style="font-family:var(--font-m);font-size:0.75rem;color:var(--text-muted);">'
            'Archive is empty. Execute a refinement to populate.</p>',
            unsafe_allow_html=True,
        )
        return

    # Sorted sets — deterministic order across reruns
    all_targets  = sorted({e["target"]  for e in history})
    all_patterns = sorted({e["pattern"] for e in history if e.get("pattern")})

    fc1, fc2 = st.columns(2)
    with fc1:
        ft = st.selectbox("Filter Target",  ["All"] + all_targets,  key="arc_ft")
    with fc2:
        fp = st.selectbox("Filter Pattern", ["All"] + all_patterns, key="arc_fp")

    filtered = [
        e for e in history
        if (ft == "All" or e["target"] == ft)
        and (fp == "All" or e.get("pattern") == fp)
    ]

    st.markdown(
        f'<p style="font-family:var(--font-m);font-size:0.62rem;'
        f'color:var(--text-muted);letter-spacing:0.1em;">'
        f'{len(filtered)} ENTRIES</p>',
        unsafe_allow_html=True,
    )

    for item in filtered:
        p_tag = f" · {item['pattern']}" if item.get("pattern") else ""
        i_tag = " · ☪"                  if item.get("islamic")  else ""
        label = (
            f"[{item['id']}]  {item['time']}  ·  "
            f"{item['target']}  ·  {item['score']}%{p_tag}{i_tag}"
        )

        with st.expander(label):
            st.markdown('<div class="arc-meta">Original Input</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="vc-card" style="font-size:0.77rem;line-height:1.65;'
                f'margin-bottom:10px;">{_escape(item["input"])}</div>',
                unsafe_allow_html=True,
            )
            st.code(item["output"], language="markdown")
            st.download_button(
                "Download",
                data=item["output"],
                file_name=f"vc_{item['id']}.txt",
                key=f"dl_{item['id']}",  # unique key — prevents DuplicateWidgetID
            )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.download_button(
        "Export Full Archive (JSON)",
        data=json.dumps(history, ensure_ascii=False, indent=2),
        file_name=f"velvetcodex_archive_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
        mime="application/json",
        key="btn_export_arc",
    )