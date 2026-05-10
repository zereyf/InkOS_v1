"""
ui/tabs/archive.py — The Black Box (Neural Archive)
===================================================
v2026.4.20: Tactical Rehydration Update.
           - ADDED: Neural Rehydration (Restores past app states).
           - ADDED: InkOS Premium Branding Sync.
           - FIXED: Streamlit 0-byte export bug via session-state filename persistence.
"""

import json
import streamlit as st
import textwrap
from datetime import datetime, timezone
from state import K


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_archive() -> None:
    # ── 🟢 PREMIUM HERO SYNC ──────────────────────────────────────────────────
    brand_html = textwrap.dedent(f"""
        <div style="text-align:center; margin-bottom: 30px; padding-top: 10px;">
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" style="width: 40px; height: 40px; fill: var(--gold); filter: drop-shadow(0px 0px 8px rgba(201, 168, 76, 0.4));">
                    <path d="M73.4 182.6C60.9 170.1 60.9 149.8 73.4 137.3C85.9 124.8 106.2 124.8 118.7 137.3L278.7 297.3C291.2 309.8 291.2 330.1 278.7 342.6L118.7 502.6C106.2 515.1 85.9 515.1 73.4 502.6C60.9 490.1 60.9 469.8 73.4 457.3L210.7 320L73.4 182.6zM288 448L544 448C561.7 448 576 462.3 576 480C576 497.7 561.7 512 544 512L288 512C270.3 512 256 497.7 256 480C256 462.3 270.3 448 288 448z"/>
                </svg>
                <span style="font-family: var(--font-m); font-size: 1.8rem; color: var(--text); letter-spacing: 6px; margin-left: 15px; font-weight: bold; text-transform: uppercase;">
                    INK<span style="color: var(--gold);">OS</span> // ARCHIVE
                </span>
            </div>
            <div style="font-family:var(--font-m); font-size:0.6rem; color:var(--text-dim); letter-spacing:0.15em; text-transform:uppercase;">
                Black Box Telemetry // [ RECORD_ID: {datetime.now().strftime('%Y-%m')} ]
            </div>
            <hr style="border-color:rgba(255,255,255,0.05); width: 25%; margin: 15px auto;">
        </div>
    """)
    st.markdown(brand_html, unsafe_allow_html=True)

    history = st.session_state.get(K.HISTORY, [])

    if not history:
        st.markdown(
            '<p style="font-family:var(--font-m);font-size:0.75rem;color:var(--text-muted);text-align:center;">'
            '[ ⨂ ] Archive empty. No tactical logs detected.</p>',
            unsafe_allow_html=True,
        )
        return

    # Filter Setup
    all_targets  = sorted({e["target"]  for e in history})
    all_patterns = sorted({e["pattern"] for e in history if e.get("pattern")})
    
    fc1, fc2 = st.columns(2)
    with fc1:
        ft = st.selectbox("Filter: Target Model", ["All"] + all_targets, key="arc_ft")
    with fc2:
        fp = st.selectbox("Filter: Pattern DNA", ["All"] + all_patterns, key="arc_fp")

    filtered = [
        e for e in history
        if (ft == "All" or e["target"] == ft)
        and (fp == "All" or e.get("pattern") == fp)
    ]

    st.markdown(
        f'<div style="font-family:var(--font-m);font-size:0.62rem;'
        f'color:var(--gold);letter-spacing:0.1em;margin-bottom:15px;text-align:right;">'
        f'ANALYSIS: {len(filtered)} INTEL PACKETS RECOVERED</div>',
        unsafe_allow_html=True,
    )

    for item in reversed(filtered):
        p_tag = f" · {item['pattern']}" if item.get("pattern") else ""
        i_tag = " · ☪" if item.get("islamic") else ""
        score = item.get('score', 0)
        
        # Visual Status Indicators
        score_indicator = "🟢" if score >= 90 else "🟡" if score >= 80 else "🔴"

        label = (
            f"{score_indicator} [{item['id']}] {item['time']}  ·  "
            f"{item['target']}  ·  {score}%{p_tag}{i_tag}"
        )

        with st.expander(label):
            # ── 🔵 REHYDRATION BUTTON (The "Interesting" Feature) ──
            # This allows the user to instantly set their app back to this state
            if st.button(f"⚡ REHYDRATE SYSTEM STATE", key=f"rehy_{item['id']}", use_container_width=True):
                st.session_state["sb_target"] = item.get("target")
                st.session_state["sb_framework"] = item.get("framework")
                st.session_state["sb_aesthetic"] = item.get("aesthetic")
                st.toast(f"SYSTEM REHYDRATED: {item['id']}", icon="🧪")
                st.rerun()

            # Metadata Display
            st.markdown(f"""
            <div style="
                display:flex; gap:15px; flex-wrap:wrap;
                background:rgba(201,168,76,0.05);
                border:1px solid rgba(201,168,76,0.15);
                border-radius:4px; padding:8px 12px;
                font-family:var(--font-m); font-size:0.65rem;
                color:var(--gold); margin-top:10px; margin-bottom:12px;
            ">
                <span><strong>FRAMEWORK:</strong> {item.get('framework', 'N/A')}</span>
                <span><strong>AESTHETIC:</strong> {item.get('aesthetic', 'Raw')}</span>
            </div>
            """, unsafe_allow_html=True)

            st.markdown('<div class="arc-meta" style="font-size:0.6rem;color:var(--text-dim);font-family:var(--font-m);">ORIGINAL INTENT</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="vc-card" style="font-size:0.77rem;line-height:1.65;'
                f'margin-bottom:12px; background:rgba(0,0,0,0.2);">{_escape(item["input"])}</div>',
                unsafe_allow_html=True,
            )
            
            st.markdown('<div class="arc-meta" style="font-size:0.6rem;color:var(--text-dim);font-family:var(--font-m);">REFINED ASSET</div>', unsafe_allow_html=True)
            st.code(item["output"], language="markdown")
            
            st.download_button(
                "💾 SAVE ASSET TO LOCAL",
                data=item["output"],
                file_name=f"inkos_prompt_{item['id']}.txt",
                key=f"dl_{item['id']}", 
                use_container_width=True
            )

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    
    # Export Handling
    if "arc_export_filename" not in st.session_state:
        dl_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        st.session_state["arc_export_filename"] = f"inkos_archive_{dl_timestamp}.json"
        
    st.download_button(
        "📦 EXPORT FULL BLACK BOX (JSON)",
        data=json.dumps(history, ensure_ascii=False, indent=2),
        file_name=st.session_state["arc_export_filename"],
        mime="application/json",
        key="btn_export_arc",
        use_container_width=True
    )
