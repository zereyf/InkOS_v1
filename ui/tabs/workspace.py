"""
ui/tabs/workspace.py — Workspace Tab
======================================
v33.3: Zenith Neural Edition (Markdown Patch).
       - FIXED: Markdown Code Block bleeding (removed HTML indentation).
       - FIXED: TypeError (NoneType len) caused by NULL database values.
       - STABLE: Autonomous Neural Routing & 3-Layer Composite Assembler.
"""

import time
import re
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
    """Extracts the full brand DNA context, strictly casting to strings."""
    return {
        K.INK_DNA: str(st.session_state.get(K.INK_DNA) or ""),
        K.INTEL_DNA: str(st.session_state.get(K.INTEL_DNA) or ""),
        K.HIKMAH_DNA: str(st.session_state.get(K.HIKMAH_DNA) or "")
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

# ── 🟢 UI COMPONENTS (FLATTENED TO PREVENT MARKDOWN BLEED) ────────────────────

def _render_dna_status_grid():
    """Compact status chips for brand DNA."""
    dna = _get_dna_context()
    labels = [("INK", dna[K.INK_DNA]), ("INTEL", dna[K.INTEL_DNA]), ("HIKMAH", dna[K.HIKMAH_DNA])]
    chips = []
    for label, content in labels:
        active = len(str(content or "")) > 130
        chips.append(f"<span class='pill'>{label}: {'Custom' if active else 'Default'}</span>")
    st.markdown("<div class='premium-caption'>DNA Profiles " + " ".join(chips) + "</div>", unsafe_allow_html=True)


def _render_score_block(audit: dict, expert_mode: bool = False) -> None:
    safe_audit = audit or {}
    score = int(safe_audit.get("score", 0))
    score_label = "Excellent" if score >= 90 else "Strong" if score >= 80 else "Needs work"
    dot_color = "var(--ok)" if score >= 90 else "var(--warn)" if score >= 80 else "#ef4444"
    st.markdown(
        f"<div class='premium-card'><div class='score'><span class='score-dot' style='background:{dot_color}'></span>"
        f"<strong>Prompt Quality: {score_label}</strong><span class='premium-caption'>{score}% confidence</span></div>"
        f"<div class='premium-caption'>{safe_audit.get('critique', 'No critique available.')}</div></div>",
        unsafe_allow_html=True,
    )
    if expert_mode:
        with st.expander("Diagnostics"):
            st.json(safe_audit)


def _highlight_diff(source: str, result: str) -> str:
    words = set(source.lower().split())
    marked = []
    for token in result.split():
        if token.lower().strip('.,!?;:') not in words:
            marked.append(f"<mark>{token}</mark>")
        else:
            marked.append(token)
    return " ".join(marked)
# ── 🟢 MAIN RENDERER ──────────────────────────────────────────────────────────

def render_workspace(cfg: dict) -> None:
    # ── 1. HEADER & BADGES ──
    hikmah_style = str(cfg.get("hikmah_style") or "None")
    p_active = cfg.get("active_persona")
    p_name = p_active.get("name", "").upper() if p_active else ""
    
    h_badge = f"<span class='pill'>{hikmah_style.upper()}</span>" if hikmah_style != "None" else ""
    p_badge = f"<span class='pill'>{p_name[:12]}</span>" if p_name else ""
    st.markdown(
        f"<section class='premium-card'><div class='premium-header'><div><div class='premium-title'>{t('tab_workspace', fallback='Workspace')}</div>"
        f"<div class='premium-caption'>Focused refinement workspace built for clarity and speed. {h_badge} {p_badge}</div></div>"
        f"<div class='premium-caption'>Session {str(st.session_state.get(K.USER_HASH, 'GHOST'))[:8]}</div></div>",
        unsafe_allow_html=True,
    )
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
        intent_val = st.text_area("Prompt", height=190, placeholder=t("workspace_placeholder"), key="ta_input_widget")

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
                cfg["framework"],
                cfg["source_lang"],
                cfg["aesthetic_choice"],
                hikmah_style=hikmah_style,
                skip_security=st.session_state.get(K.IS_ADMIN, False) and cfg.get("expert_mode", False)
            )
            
            telemetry = _extract_telemetry(result, start_time)
            history = st.session_state.get(K.HISTORY, [])
            history.insert(0, {"input": cleaned[:180], "score": (audit or {}).get("score", 0), "latency": telemetry.get("latency_ms", 0)})
            st.session_state[K.HISTORY] = history[:MAX_HISTORY_ITEMS]
            prog.progress(100)
            status.empty()
            prog.empty()

            st.session_state[K.LAST_RESULT] = result
            st.session_state[K.LAST_AUDIT] = audit
            st.session_state[K.LAST_INPUT] = cleaned
            st.rerun()

    # ── 5. RESULTS RENDERING ──
    if st.session_state.get(K.LAST_RESULT):
        _render_score_block(st.session_state.get(K.LAST_AUDIT), cfg.get("expert_mode"))
        before, after = st.columns(2)
        with before:
            st.markdown("**Before**")
            st.markdown(f"<div class='diff'>{st.session_state.get(K.LAST_INPUT, '')}</div>", unsafe_allow_html=True)
        with after:
            st.markdown("**After**")
            highlighted = _highlight_diff(st.session_state.get(K.LAST_INPUT, ''), st.session_state.get(K.LAST_RESULT, ''))
            st.markdown(f"<div class='diff'>{highlighted}</div>", unsafe_allow_html=True)

        c1,c2=st.columns([1,1])
        with c1:
            if st.button("Copy Refined Output", use_container_width=True):
                st.code(st.session_state.get(K.LAST_RESULT), language=None)
                st.toast("Copied output ready.", icon="✅")
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 10px 0;'>", unsafe_allow_html=True)
        
        v1, v2, v3 = st.columns([2, 2, 1.5])
        with v1: st.text_input("Title", key="v_t", label_visibility="collapsed", placeholder="DESIGNATION...")
        with v2: st.text_input("Tags", key="v_g", label_visibility="collapsed", placeholder="Forensic Tags...")
        with v3: 
            if st.button("SECURE TO VAULT", type="primary", use_container_width=True):
                uid = st.session_state.get(K.USER_HASH)
                title_val = st.session_state.get("v_t", "").strip()
                tags_val = st.session_state.get("v_g", "").strip()

                if title_val and tags_val and uid and "GUEST_" not in uid.upper():
                    from vault.vault_engine import save_prompt
                    res, err = save_prompt(
                        uid, title=title_val, tags=tags_val, 
                        content=st.session_state.get(K.LAST_RESULT), 
                        target=st.session_state.get(K.AUTO_TARGET), 
                        framework=cfg["framework"], 
                        score=(st.session_state.get(K.LAST_AUDIT) or {}).get("score", 0)
                    )
                    if not err:
                        st.session_state[K.LAST_SAVED] = datetime.now(WAT_TZ).strftime("%H:%M:%S")
                        st.toast("[◈] ASSET SECURED.", icon="✅")
                    else: st.error(err)
                else:
                    st.toast("[!] Designation and Identity required.", icon="⚠️")
