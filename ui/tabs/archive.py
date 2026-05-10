"""
ui/tabs/archive.py — The Black Box (Neural Archive)
===================================================
v2026.4.23: Visual DNA Sync — Color Palette HUD.
           - ADDED: 5-Cell Telemetry Grid including Visual DNA Chips.
           - STABILIZED: Rehydration Callback Protocol.
           - AESTHETIC: High-Density Dossier HUD.
"""

import json
import streamlit as st
import textwrap
from datetime import datetime, timezone
from state import K


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── 🟢 THE REHYDRATION CALLBACK ──
def _handle_rehydrate(target, framework, aesthetic, mission_id):
    """Updates state BEFORE the script renders the sidebar to avoid API Exceptions."""
    st.session_state["sb_target"] = target
    st.session_state["sb_framework"] = framework
    st.session_state["sb_aesthetic"] = aesthetic
    st.session_state["rehydrate_msg"] = f"SYSTEM REHYDRATED: {mission_id}"


def render_archive() -> None:
    # ── 🟢 PREMIUM HERO SYNC ──────────────────────────────────────────────────
    brand_html = textwrap.dedent(f"""
        <div style="text-align:center; margin-bottom: 30px; padding-top: 10px;">
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 8px;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" style="width: 42px; height: 42px; fill: var(--gold); filter: drop-shadow(0px 0px 10px rgba(201, 168, 76, 0.4));">
                    <path d="M73.4 182.6C60.9 170.1 60.9 149.8 73.4 137.3C85.9 124.8 106.2 124.8 118.7 137.3L278.7 297.3C291.2 309.8 291.2 330.1 278.7 342.6L118.7 502.6C106.2 515.1 85.9 515.1 73.4 502.6C60.9 490.1 60.9 469.8 73.4 457.3L210.7 320L73.4 182.6zM288 448L544 448C561.7 448 576 462.3 576 480C576 497.7 561.7 512 544 512L288 512C270.3 512 256 497.7 256 480C256 462.3 270.3 448 288 448z"/>
                </svg>
                <span style="font-family: var(--font-m); font-size: 2rem; color: var(--text); letter-spacing: 8px; margin-left: 18px; font-weight: bold; text-transform: uppercase;">
                    INK<span style="color: var(--gold);">OS</span> // <span style="color: var(--text-dim);">ARCHIVE</span>
                </span>
            </div>
            <div style="font-family:var(--font-m); font-size:0.6rem; color:var(--gold); letter-spacing:0.25em; text-transform:uppercase; opacity:0.8;">
                BLACK BOX TELEMETRY // SECURE_ACCESS_NODE
            </div>
            <hr style="border:none; height:1px; background:linear-gradient(90deg, transparent, var(--gold), transparent); width: 40%; margin: 20px auto; opacity:0.3;">
        </div>
    """)
    st.markdown(brand_html, unsafe_allow_html=True)

    # ── 🟢 TOAST HANDLER ──
    if "rehydrate_msg" in st.session_state:
        st.toast(st.session_state.pop("rehydrate_msg"), icon="🧪")

    history = st.session_state.get(K.HISTORY, [])

    if not history:
        st.markdown(
            '<div style="text-align:center; padding: 40px; border: 1px dashed rgba(255,255,255,0.1); border-radius: 4px;">'
            '<p style="font-family:var(--font-m);font-size:0.75rem;color:var(--text-dim);">'
            '[ ⨂ ] Archive empty. No tactical logs detected in the current uplink.</p></div>',
            unsafe_allow_html=True,
        )
        return

    # Filter Matrix (Neater 3-Column Layout)
    all_targets  = sorted({e["target"]  for e in history})
    all_patterns = sorted({e["pattern"] for e in history if e.get("pattern")})
    
    st.markdown('<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-dim); letter-spacing:2px; margin-bottom:10px;">FILTER_MATRIX</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1, 1, 1])
    with f1: ft = st.selectbox("Target", ["All"] + all_targets, key="arc_ft", label_visibility="collapsed")
    with f2: fp = st.selectbox("Pattern", ["All"] + all_patterns, key="arc_fp", label_visibility="collapsed")
    with f3: st.markdown(f'<div style="font-family:var(--font-m); font-size:0.65rem; color:var(--gold); text-align:right; padding-top:10px;">PACKETS: {len(history)}</div>', unsafe_allow_html=True)

    filtered = [
        e for e in history
        if (ft == "All" or e["target"] == ft)
        and (fp == "All" or e.get("pattern") == fp)
    ]

    # ── 🟢 THE DOSSIER LIST ──────────────────────────────────────────────────
    for item in reversed(filtered):
        p_tag = f" · {item['pattern']}" if item.get("pattern") else ""
        i_tag = " · ☪" if item.get("islamic") else ""
        score = item.get('score', 0)
        
        # Color coding for the indicator dot
        dot_color = "#4CAF9A" if score >= 90 else "var(--gold)" if score >= 80 else "#E53E3E"

        label_html = f"""
            <div style="display:flex; justify-content:space-between; width:100%; font-family:var(--font-m); font-size:0.7rem; letter-spacing:1px;">
                <span><span style="color:{dot_color};">●</span> [{item['id']}] {item['time']}</span>
                <span style="color:var(--text-dim);">{item['target']} // {score}%</span>
            </div>
        """

        with st.expander(label_html, expanded=False):
            # ── 🔵 ACTION BAR ──
            st.button(
                "⚡ REHYDRATE SYSTEM STATE", 
                key=f"rehy_{item['id']}", 
                use_container_width=True,
                on_click=_handle_rehydrate,
                args=(item.get("target"), item.get("framework"), item.get("aesthetic"), item['id'])
            )

            # ── 🔵 TELEMETRY GRID WITH VISUAL DNA ──
            palette = item.get("palette", [])
            palette_html = ""
            if palette:
                chips = "".join([f'<div style="width:10px; height:10px; background:{c}; border-radius:2px; border:1px solid rgba(255,255,255,0.1);"></div>' for c in palette])
                palette_html = f'<div style="display:flex; gap:3px; justify-content:center; margin-top:2px;">{chips}</div>'
            else:
                palette_html = '<div style="font-size:0.6rem; color:var(--text-dim);">NONE</div>'

            st.markdown(f"""
            <div style="
                display:grid; grid-template-columns: repeat(5, 1fr); gap:1px;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px; margin: 15px 0; overflow: hidden;
            ">
                <div style="background:rgba(10,12,16,0.6); padding:10px; text-align:center; border-right:1px solid rgba(255,255,255,0.05);">
                    <div style="font-size:0.5rem; color:var(--text-dim); margin-bottom:4px;">LATENCY</div>
                    <div style="font-size:0.7rem; color:var(--gold);">{item.get('latency', '0ms')}</div>
                </div>
                <div style="background:rgba(10,12,16,0.6); padding:10px; text-align:center; border-right:1px solid rgba(255,255,255,0.05);">
                    <div style="font-size:0.5rem; color:var(--text-dim); margin-bottom:4px;">DENSITY</div>
                    <div style="font-size:0.7rem; color:var(--gold);">{item.get('density', '0.0')} CPW</div>
                </div>
                <div style="background:rgba(10,12,16,0.6); padding:10px; text-align:center; border-right:1px solid rgba(255,255,255,0.05);">
                    <div style="font-size:0.5rem; color:var(--text-dim); margin-bottom:4px;">VOLUME</div>
                    <div style="font-size:0.7rem; color:var(--gold);">{item.get('word_count', '0')} W</div>
                </div>
                <div style="background:rgba(10,12,16,0.6); padding:10px; text-align:center; border-right:1px solid rgba(255,255,255,0.05);">
                    <div style="font-size:0.5rem; color:var(--text-dim); margin-bottom:4px;">DNA_SIG</div>
                    <div style="font-size:0.7rem; color:var(--gold);">{item.get('pattern', 'RAW')}</div>
                </div>
                <div style="background:rgba(10,12,16,0.6); padding:10px; text-align:center;">
                    <div style="font-size:0.5rem; color:var(--text-dim); margin-bottom:2px;">VISUAL_DNA</div>
                    {palette_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Content Columns
            st.markdown('<div style="font-size:0.6rem;color:var(--text-dim);font-family:var(--font-m);margin-bottom:5px;">[01] ORIGINAL_INTENT</div>', unsafe_allow_html=True)
            st.markdown(
                f'<div style="background:rgba(255,255,255,0.02); padding:12px; border-radius:3px; border:1px solid rgba(255,255,255,0.05); font-size:0.75rem; line-height:1.6; margin-bottom:15px;">{_escape(item["input"])}</div>',
                unsafe_allow_html=True,
            )
            
            st.markdown('<div style="font-size:0.6rem;color:var(--text-dim);font-family:var(--font-m);margin-bottom:5px;">[02] REFINED_ASSET</div>', unsafe_allow_html=True)
            st.code(item["output"], language="markdown")
            
            st.download_button(
                "💾 DOWNLOAD LOCAL COPY",
                data=item["output"],
                file_name=f"inkos_asset_{item['id']}.txt",
                key=f"dl_{item['id']}", 
                use_container_width=True
            )

    st.markdown("<div style='height:40px'></div>", unsafe_allow_html=True)
    
    # ── 🟢 FOOTER EXPORT ──
    if "arc_export_filename" not in st.session_state:
        dl_timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        st.session_state["arc_export_filename"] = f"inkos_full_archive_{dl_timestamp}.json"
        
    st.download_button(
        "📦 EXPORT FULL INTEL ARCHIVE (JSON)",
        data=json.dumps(history, ensure_ascii=False, indent=2),
        file_name=st.session_state["arc_export_filename"],
        mime="application/json",
        key="btn_export_arc",
        use_container_width=True
    )
