"""
ui/tabs/archive.py — Neural Archive Tab
=========================================
v7.0: Hardened for InkOS. Fixed 0-byte export bug, added metadata UI, 
      removed old legacy branding.
"""

import json
import streamlit as st
from datetime import datetime, timezone
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

    st.markdown(
        '<div style="font-size:0.65rem;color:var(--text-muted);font-family:var(--font-m);margin-bottom:4px;">'
        'FILTER ARCHIVE</div>', 
        unsafe_allow_html=True
    )
    
    fc1, fc2 = st.columns(2)
    with fc1:
        ft = st.selectbox("Target Filter", ["All"] + all_targets, key="arc_ft", label_visibility="collapsed")
    with fc2:
        fp = st.selectbox("Pattern Filter", ["All"] + all_patterns, key="arc_fp", label_visibility="collapsed")

    filtered = [
        e for e in history
        if (ft == "All" or e["target"] == ft)
        and (fp == "All" or e.get("pattern") == fp)
    ]

    st.markdown(
        f'<div style="font-family:var(--font-m);font-size:0.62rem;'
        f'color:var(--gold);letter-spacing:0.1em;margin-top:10px;margin-bottom:10px;">'
        f'✦ {len(filtered)} ENTRIES FOUND</div>',
        unsafe_allow_html=True,
    )

    for item in filtered:
        p_tag = f" · {item['pattern']}" if item.get("pattern") else ""
        i_tag = " · ☪"                  if item.get("islamic")  else ""
        score = item.get('score', 0)
        
        # Visual score severity indicator
        if score >= 90:
            score_indicator = "🟢"
        elif score >= 80:
            score_indicator = "🟡"
        else:
            score_indicator = "🔴"

        label = (
            f"{score_indicator} [{item['id']}]  {item['time']}  ·  "
            f"{item['target']}  ·  {score}%{p_tag}{i_tag}"
        )

        with st.expander(label):
            # Injection of tactical metadata context
            st.markdown(f"""
            <div style="
                display:flex; gap:15px; flex-wrap:wrap;
                background:rgba(201,168,76,0.05);
                border:1px solid rgba(201,168,76,0.15);
                border-radius:4px; padding:8px 12px;
                font-family:var(--font-m); font-size:0.65rem;
                color:var(--gold); margin-bottom:12px;
            ">
                <span><strong>FRAMEWORK:</strong> {item.get('framework', 'N/A')}</span>
                <span><strong>AESTHETIC:</strong> {item.get('aesthetic', 'Raw')}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="arc-meta" style="font-size:0.6rem;color:var(--text-muted);margin-bottom:4px;font-family:var(--font-m);">ORIGINAL INTENT</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="vc-card" style="font-size:0.77rem;line-height:1.65;'
                f'margin-bottom:12px;">{_escape(item["input"])}</div>',
                unsafe_allow_html=True,
            )
            
            st.markdown('<div class="arc-meta" style="font-size:0.6rem;color:var(--text-muted);margin-bottom:4px;font-family:var(--font-m);">REFINED ASSET</div>', unsafe_allow_html=True)
            st.code(item["output"], language="markdown")
            
            st.download_button(
                "Download Prompt",
                data=item["output"],
                file_name=f"inkos_prompt_{item['id']}.txt",
                key=f"dl_{item['id']}", 
                use_container_width=True
            )

    st.markdown("<hr>", unsafe_allow_html=True)
    
    # FIX: Freeze export filename to prevent Streamlit 0-byte re-render bug
    if "arc_export_filename" not in st.session_state:
        dl_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        st.session_state["arc_export_filename"] = f"inkos_archive_{dl_timestamp}.json"
        
    st.download_button(
        "Export Full Archive (JSON)",
        data=json.dumps(history, ensure_ascii=False, indent=2),
        file_name=st.session_state["arc_export_filename"],
        mime="application/json",
        key="btn_export_arc",
        use_container_width=True
    )
