"""
ui/tabs/workspace.py — Workspace Tab
======================================
v33.2: Zenith Neural Edition (Null-Safe Patch).
       - FIXED: TypeError crash caused by NoneType database returns in DNA grid.
       - INTEGRATED: Autonomous Neural Routing (Auto-Switch logic).
       - INTEGRATED: 3-Layer Composite Assembler (Persona + Rhetoric + DNA).
       - RESTORED: Full Groq Transcription and Supabase Vault persistence.
"""

import textwrap
import time
import re
import uuid
import os
import streamlit as st
from datetime import datetime, timezone, timedelta
from typing import Tuple, Dict, Any
from groq import Groq

from state import K
from security.sanitizer import sanitize_input
from engine.refiner import run_refinement_and_audit 
from forge.prompt_assembler import assemble_master_payload
from forge.intelligence import resolve_target_model
from i18n.translations import t
from config import AUTO_SELECT_LABEL

# ── 🟢 SYSTEM CONSTANTS ───────────────────────────────────────────────────────

WAT_TZ = timezone(timedelta(hours=1))
MAX_HISTORY_ITEMS = 50

# ── 🟢 BEHAVIORAL & FORENSIC ADAPTERS ─────────────────────────────────────────

def _get_dna_context() -> dict:
    """Extracts the full brand DNA context from the session state safely."""
    # 🟢 FIXED: Added 'or ""' to ensure NoneTypes from DB become empty strings
    return {
        K.INK_DNA: st.session_state.get(K.INK_DNA) or "",
        K.INTEL_DNA: st.session_state.get(K.INTEL_DNA) or "",
        K.HIKMAH_DNA: st.session_state.get(K.HIKMAH_DNA) or ""
    }

def _detect_tone(text: str) -> str:
    tones = {
        "FORENSIC": ["analysis", "audit", "technical", "vulnerability", "precision"],
        "POETIC": ["symphony", "ethereal", "shadow", "chiaroscuro", "aesthetic"],
        "TACTICAL": ["execute", "intercept", "lockdown", "mission", "protocol"],
        "HIKMAH": ["balagha", "linguistic", "iijaz", "wisdom", "adab"]
    }
    text_lower = text.lower()
    for tone, keywords in tones.items():
        if any(kw in text_lower for kw in keywords): return tone
    return "NEUTRAL"

def _extract_telemetry(result: str, start_time: float) -> Dict[str, Any]:
    latency_ms = int((time.perf_counter() - start_time) * 1000)
    words = result.split()
    word_count = len(words)
    density = round(len(result) / word_count, 2) if word_count > 0 else 0
    palette = list(set(re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', result)))
    return {
        "latency_ms": latency_ms,
        "word_count": word_count,
        "density": density,
        "palette": palette[:5],
        "tone": _detect_tone(result)
    }

# ── 🟢 UI COMPONENTS ──────────────────────────────────────────────────────────

def _render_dna_status_grid():
    """Renders the high-fidelity DNA synchronization HUD."""
    dna = _get_dna_context()
    
    def _dna_tile(label: str, content: str):
        # 🟢 FIXED: Safety clamp for content length calculation
        safe_content = content or ""
        is_custom = len(safe_content) > 130 
        b_color = "var(--gold)" if is_custom else "rgba(255,255,255,0.05)"
        t_color = "var(--gold)" if is_custom else "var(--text-dim)"
        status = "LOCKED" if is_custom else "DEFAULT"
        return f"""
            <div style="flex:1; border:1px solid {b_color}; border-radius:2px; padding:10px; text-align:center; background:rgba(0,0,0,0.2);">
                <div style="font-family:var(--font-m); font-size:0.5rem; color:{t_color}; letter-spacing:1.5px; margin-bottom:4px;">DNA: /{label}</div>
                <div style="font-family:var(--font-m); font-size:0.6rem; color:{b_color}; font-weight:bold; letter-spacing:1px;">{status}</div>
            </div>
        """

    grid_html = f"""<div style="display:flex; gap:10px; margin-bottom:20px;">
        {_dna_tile("INK", dna[K.INK_DNA])}
        {_dna_tile("INTEL", dna[K.INTEL_DNA])}
        {_dna_tile("HIKMAH", dna[K.HIKMAH_DNA])}
    </div>"""
    st.markdown(grid_html, unsafe_allow_html=True)

def _render_score_block(audit: dict, expert_mode: bool = False) -> None:
    safe_audit = audit or {}
    score = int(safe_audit.get("score", 0))
    status_color = "#4CAF9A" if score >= 90 else "var(--gold)" if score >= 80 else "#E53E3E"
    
    st.markdown(f"""
    <div style="background: rgba(10,12,16,0.6); border-left: 3px solid {status_color}; border-radius: 4px; padding: 15px; margin-bottom: 10px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom:10px;">
            <div>
                <div style="font-family: var(--font-m); font-size: 0.5rem; color: var(--text-muted); letter-spacing: 2px;">OVERALL FIDELITY</div>
                <div style="font-family: var(--font-d); font-size: 2.4rem; color: {status_color}; line-height: 1;">{score}<span style="font-size: 1rem;">%</span></div>
            </div>
            <div style="text-align: right; background: rgba(0,0,0,0.2); padding: 5px 10px; border-radius: 2px;">
                <div style="font-family: var(--font-m); font-size: 0.4rem; color: var(--text-dim); letter-spacing: 1px;">NODE_ID</div>
                <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--gold);">{st.session_state.get(K.AUTO_TARGET, "Unknown").upper()}</div>
            </div>
        </div>
        <div style="font-family: var(--font-m); font-size: 0.6rem; color: var(--text-dim); line-height: 1.5; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 10px;">
            <span style="color:var(--gold);">> DIAGNOSTIC:</span> {safe_audit.get("critique", "No anomalies detected.")}
        </div>
    </div>
    """, unsafe_allow_html=True)
    if expert_mode:
        with st.expander("❖ NEURAL UPLINK DIAGNOSTICS"): st.json(safe_audit)

# ── 🟢 MAIN RENDERER ──────────────────────────────────────────────────────────

def render_workspace(cfg: dict) -> None:
    # ── 1. HEADER & BADGES ──
    hikmah_style = cfg.get("hikmah_style", "None")
    p_active = cfg.get("active_persona")
    p_name = p_active.get("name", "").upper() if p_active else ""
    
    header_html = f"""
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:10px; margin-bottom:15px;">
            <div class="vc-header" style="margin:0; display:flex; align-items:center; gap:10px;">
                <span class="status-dot"></span>{t("tab_workspace", fallback="WORKSPACE")}
                {f'<span style="background:rgba(76,175,154,0.1); color:#4CAF9A; border:1px solid #4CAF9A; padding:2px 6px; border-radius:2px; font-size:0.45rem;">{hikmah_style.upper()}</span>' if hikmah_style != "None" else ""}
                {f'<span style="background:rgba(201,168,76,0.1); color:var(--gold); border:1px solid rgba(201,168,76,0.3); padding:2px 6px; border-radius:2px; font-size:0.45rem;">{p_name[:12]}</span>' if p_name else ""}
            </div>
            <div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-dim); letter-spacing:1px;">A.I.Z.E.N. // REF: {str(st.session_state.get(K.USER_HASH, "GHOST"))[:8]}</div>
        </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # ── 2. DNA GRID ──
    _render_dna_status_grid()

    # ── 3. INPUT AREA ──
    v_col1, v_col2 = st.columns([1, 6])
    with v_col1:
        audio_bytes = st.audio_input("Voice Uplink", label_visibility="collapsed")
        if audio_bytes:
            current_audio_hash = hash(audio_bytes.getvalue())
            if st.session_state.get("last_audio_hash") != current_audio_hash:
                with st.spinner("Transcribing..."):
                    try:
                        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                        transcription = client.audio.transcriptions.create(
                            file=("audio.wav", audio_bytes.read()),
                            model="whisper-large-v3",
                            prompt="Arabic Education terminology and dialectal nuance."
                        )
                        if transcription.text:
                            curr_val = st.session_state.get("ta_input_widget", "")
                            st.session_state["ta_input_widget"] = f"{curr_val} {transcription.text}".strip()
                            st.session_state["last_audio_hash"] = current_audio_hash
                            st.rerun()
                    except Exception as e:
                        st.error(f"[!] Voice Uplink Failed: {e}")

    with v_col2:
        intent_val = st.text_area("intent", height=145, placeholder=t("workspace_placeholder"), label_visibility="collapsed", key="ta_input_widget")

    # ── 4. EXECUTION LOOP ──
    if st.button(t("execute_btn", fallback="EXECUTE REFINEMENT"), use_container_width=True):
        cleaned, _ = sanitize_input(intent_val)
        if cleaned:
            status = st.empty()
            prog = st.progress(0)
            
            status.markdown("`< 20% >` **[ROUTER]** Resolving optimal neural architecture...")
            resolved_target, resolved_reason = resolve_target_model(cfg.get("target_model"), cleaned)
            st.session_state[K.AUTO_TARGET] = resolved_target
            st.session_state[K.AUTO_REASON] = resolved_reason
            prog.progress(20)

            status.markdown("`< 50% >` **[FORGE]** Synthesizing Persona, Rhetoric, and DNA layers...")
            master_payload = assemble_master_payload(cleaned, cfg, _get_dna_context())
            prog.progress(50)

            status.markdown(f"`< 80% >` **[CORE]** Handshake with **{resolved_target.upper()}**...")
            start_time = time.perf_counter()
            
            result, audit, _ = run_refinement_and_audit(
                master_payload, 
                resolved_target,
