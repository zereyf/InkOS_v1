"""
ui/tabs/archive.py — The Black Box (Neural Archive)
===================================================
v2026.4.24: Behavioral HUD — Tone Radar & Persona Sync.
           - ADDED: Persona Icon sync to Expander labels.
           - ADDED: Tone Radar cell to the Telemetry Dossier.
           - AESTHETIC: High-Density 6-Cell Grid.
"""

import json
import streamlit as st
import textwrap
from datetime import datetime, timezone
from state import K

def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _handle_rehydrate(target, framework, aesthetic, mission_id):
    st.session_state["sb_target"] = target
    st.session_state["sb_framework"] = framework
    st.session_state["sb_aesthetic"] = aesthetic
    st.session_state["rehydrate_msg"] = f"SYSTEM REHYDRATED: {mission_id}"

def render_archive() -> None:
    # ── 🟢 PREMIUM HERO SYNC ──
    # [Keep brand_html exactly as it was in v2026.4.23]

    if "rehydrate_msg" in st.session_state:
        st.toast(st.session_state.pop("rehydrate_msg"), icon="🧪")

    history = st.session_state.get(K.HISTORY, [])
    if not history:
        st.markdown('<div style="text-align:center; padding: 40px; border: 1px dashed rgba(255,255,255,0.1); border-radius: 4px;"><p style="font-family:var(--font-m);font-size:0.75rem;color:var(--text-dim);">[ ⨂ ] Archive empty.</p></div>', unsafe_allow_html=True)
        return

    # Filter Logic
    all_targets  = sorted({e["target"]  for e in history})
    all_tones    = sorted({e.get("tone", "NEUTRAL") for e in history})
    
    st.markdown('<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-dim); letter-spacing:2px; margin-bottom:10px;">FILTER_MATRIX</div>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns([1, 1, 1])
    with f1: ft = st.selectbox("Target", ["All"] + all_targets, key="arc_ft", label_visibility="collapsed")
    with f2: fp = st.selectbox("Tone", ["All"] + all_tones, key="arc_tone_filter", label_visibility="collapsed")
    with f3: st.markdown(f'<div style="font-family:var(--font-m); font-size:0.65rem; color:var(--gold); text-align:right; padding-top:10px;">PACKETS: {len(history)}</div>', unsafe_allow_html=True)

    filtered = [e for e in history if (ft == "All" or e["target"] == ft) and (fp == "All" or e.get("tone", "NEUTRAL") == fp)]

    # ── 🟢 THE DOSSIER LIST ──
    for item in reversed(filtered):
        score = item.get('score', 0)
        dot_color = "#4CAF9A" if score >= 90 else "var(--gold)" if score >= 80 else "#E53E3E"
        
        # 🟢 OPTION B: Persona Avatar Sync (Placed in label)
        p_icon = item.get("icon", "❖")

        label_html = f"""
            <div style="display:flex; justify-content:space-between; width:100%; font-family:var(--font-m); font-size:0.7rem; letter-spacing:1px;">
                <span><span style="color:{dot_color}; margin-right:8px;">●</span> {p_icon} [{item['id']}] {item['time']}</span>
                <span style="color:var(--text-dim);">{item['target']} // {score}%</span>
            </div>
        """

        with st.expander(label_html, expanded=False):
            st.button("⚡ REHYDRATE SYSTEM STATE", key=f"rehy_{item['id']}", use_container_width=True, on_click=_handle_rehydrate, args=(item.get("target"), item.get("framework"), item.get("aesthetic"), item['id']))

            # ── 🟢 HIGH-DENSITY 6-CELL GRID (Telemetry + Tone Radar) ──
            palette = item.get("palette", [])
            chips = "".join([f'<div style="width:8px; height:8px; background:{c}; border-radius:1px; border:1px solid rgba(255,255,255,0.1);"></div>' for c in palette]) if palette else '<span style="font-size:0.4rem; color:var(--text-dim);">NONE</span>'
            
            # Tone Color Mapping
            tone_val = item.get("tone", "NEUTRAL")
            tone_color = "var(--gold)" if tone_val != "NEUTRAL" else "var(--text-dim)"

            st.markdown(f"""
            <div style="
                display:grid; grid-template-columns: repeat(6, 1fr); gap:1px;
                background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
                border-radius: 4px; margin: 15px 0; overflow: hidden;
            ">
                <div style="background:rgba(10,12,16,0.6); padding:8px 5px; text-align:center; border-right:1px solid rgba(255,255,255,0.05);">
                    <div style="font-size:0.45rem; color:var(--text-dim); margin-bottom:2px;">LATENCY</div>
                    <div style="font-size:0.65rem; color:var(--gold);">{item.get('latency', '0ms')}</div>
                </div>
                <div style="background:rgba(10,12,16,0.6); padding:8px 5px; text-align:center; border-right:1px solid rgba(255,255,255,0.05);">
                    <div style="font-size:0.45rem; color:var(--text-dim); margin-bottom:2px;">DENSITY</div>
                    <div style="font-size:0.65rem; color:var(--gold);">{item.get('density', '0.0')}</div>
                </div>
                <div style="background:rgba(10,12,16,0.6); padding:8px 5px; text-align:center; border-right:1px solid rgba(255,255,255,0.05);">
                    <div style="font-size:0.45rem; color:var(--text-dim); margin-bottom:2px;">VOLUME</div>
                    <div style="font-size:0.65rem; color:var(--gold);">{item.get('word_count', '0')}W</div>
                </div>
                <div style="background:rgba(10,12,16,0.6); padding:8px 5px; text-align:center; border-right:1px solid rgba(255,255,255,0.05);">
                    <div style="font-size:0.45rem; color:var(--text-dim); margin-bottom:2px;">DNA_SIG</div>
                    <div style="font-size:0.65rem; color:var(--gold);">{item.get('pattern', 'RAW')}</div>
                </div>
                <div style="background:rgba(10,12,16,0.6); padding:8px 5px; text-align:center; border-right:1px solid rgba(255,255,255,0.05);">
                    <div style="font-size:0.45rem; color:var(--text-dim); margin-bottom:2px;">TONE_RADAR</div>
                    <div style="font-size:0.6rem; color:{tone_color}; font-weight:bold;">{tone_val}</div>
                </div>
                <div style="background:rgba(10,12,16,0.6); padding:8px 5px; text-align:center;">
                    <div style="font-size:0.45rem; color:var(--text-dim); margin-bottom:4px;">VISUAL_DNA</div>
                    <div style="display:flex; gap:2px; justify-content:center;">{chips}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ... [Rest of content/input display from v2026.4.23] ...
            st.markdown('<div style="font-size:0.6rem;color:var(--text-dim);font-family:var(--font-m);margin-bottom:5px;">[01] ORIGINAL_INTENT</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="background:rgba(255,255,255,0.02); padding:12px; border-radius:3px; border:1px solid rgba(255,255,255,0.05); font-size:0.75rem; line-height:1.6; margin-bottom:15px;">{_escape(item["input"])}</div>', unsafe_allow_html=True)
            st.markdown('<div style="font-size:0.6rem;color:var(--text-dim);font-family:var(--font-m);margin-bottom:5px;">[02] REFINED_ASSET</div>', unsafe_allow_html=True)
            st.code(item["output"], language="markdown")
            st.download_button("💾 DOWNLOAD LOCAL COPY", data=item["output"], file_name=f"inkos_asset_{item['id']}.txt", key=f"dl_{item['id']}", use_container_width=True)


    
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
