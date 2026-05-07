"""
ui/tabs/workspace.py — Workspace Tab
======================================
v24.0: Terminal Aesthetic Restored.
       Pure HTML Flexbox for [ /INK ] [ /INTEL ] [ /HIKMAH ] Standby Bar.
"""

import hashlib
import streamlit as st
from datetime import datetime, timezone
from typing import Optional, Tuple

from state import K
from security.sanitizer import sanitize_input
from security.rate_limiter import check_rate_limit
from engine.cognitive_map import detect_arabic_pattern
from engine.refiner import run_refinement_and_audit, detect_best_target
from config import INPUT_MAX_CHARS, INPUT_WARN_THRESHOLD, AUTO_SELECT_LABEL
from i18n.translations import t


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── ADVANCED TRIGGER LOGIC ────────────────────────────────────────────────────

def _apply_dna_triggers(text: str) -> Tuple[str, list]:
    """Forensic scanning for slash commands to inject stored DNA."""
    detected = []
    processed = text
    
    triggers = {
        "/ink":    st.session_state.get(K.INK_DNA, ""),
        "/intel":  st.session_state.get(K.INTEL_DNA, ""),
        "/hikmah": st.session_state.get(K.HIKMAH_DNA, "")
    }
    
    for trigger, dna in triggers.items():
        if trigger.lower() in text.lower():
            processed = f"[DNA INJECTION: {trigger.upper()}]\n{dna}\n\n[USER INTENT]\n{processed}"
            detected.append(trigger.upper())
            
    return processed, detected


def _render_guest_warning():
    if "GUEST_" in str(st.session_state.get(K.USER_HASH, "")):
        st.markdown(f"""
        <div class="vc-card" style="border-color:var(--danger); background:rgba(169,50,38,0.05); margin-bottom:20px; padding:16px;">
            <div style="display:flex; align-items:center; gap:14px;">
                <span class="status-dot" style="background:var(--danger); animation: pulse-red 1.5s infinite; box-shadow: 0 0 10px var(--danger);"></span>
                <div style="font-family:var(--font-m); font-size:0.75rem;">
                    <strong style="color:var(--danger); letter-spacing:1px; text-transform:uppercase;">Session Volatile</strong><br>
                    <span style="color:var(--text-muted);">Current identity is temporary. Assets will be purged on refresh.</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_score_block(audit: dict, pattern: Optional[dict], triggers: list = None) -> None:
    score      = int(audit.get("score",     0))
    precision  = int(audit.get("precision",  0))
    alignment  = int(audit.get("alignment",  0))
    efficiency = int(audit.get("efficiency", 0))
    critique   = str(audit.get("critique",  ""))

    if triggers:
        for t_name in triggers:
            st.markdown(f"""
            <div style="background:rgba(201,168,76,0.1); border:1px solid var(--gold); border-radius:3px; padding:8px 12px; margin-bottom:10px;">
                <div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:1px;">🧬 COMMAND ENGAGED</div>
                <div style="font-family:var(--font-m); font-size:0.75rem; color:white; font-weight:600;">[ {t_name} ] DNA ACTIVE</div>
            </div>
            """, unsafe_allow_html=True)

    if pattern:
        color = pattern.get("color", "#C9A84C")
        st.markdown(f"""
        <div class="pattern-card" style="margin-bottom:12px;">
            <span class="p-label">Engine Applied</span>
            <span class="p-arabic" style="color:{color};">{pattern['pattern']}</span>
            <span class="p-paradigm" style="color:{color};">→ {pattern['prompt_paradigm']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-block">
        <div class="score-num">{score}<span>%</span></div>
        <div class="score-lbl">{t("refinement_quality")}</div>
        <div class="bar-row">
            <span class="bar-lbl">{t("precision")}</span>
            <div class="bar-track"><div class="bar-fill" style="width:{round((precision/40)*100)}%;background:#C9A84C;"></div></div>
            <span class="bar-val">{precision}/40</span>
        </div>
        <div class="bar-row">
            <span class="bar-lbl">{t("alignment")}</span>
            <div class="bar-track"><div class="bar-fill" style="width:{round((alignment/40)*100)}%;background:#7C9EBF;"></div></div>
            <span class="bar-val">{alignment}/40</span>
        </div>
        <div class="critique-line">{critique}</div>
    </div>
    """, unsafe_allow_html=True)


def render_workspace(cfg: dict) -> None:
    _render_guest_warning()

    st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
            <div class="vc-header" style="margin:0;"><span class="status-dot"></span>{t("workspace_header")}</div>
            <div style="font-family:var(--font-a); color:var(--gold); font-size:1.1rem; opacity:0.9; letter-spacing:1px;">حبر وفكرة</div>
        </div>
        <div style="font-family:var(--font-m); font-size:0.5rem; color:var(--text-dim); letter-spacing:2px; margin-bottom:15px; text-transform:uppercase; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:8px;">
            A.I.Z.E.N. COGNITIVE TERMINAL // SESS_REF: {st.session_state.get(K.USER_HASH, "NULL")[:8]}
        </div>
    """, unsafe_allow_html=True)

    # 🧬 DNA STANDBY BAR (The Terminal Aesthetic)
    current_sid = str(st.session_state.get(K.USER_HASH, ""))
    if "GUEST_" not in current_sid.upper():
        st.markdown(f"""
            <div style="display:flex; gap:10px; margin-bottom:20px;">
                <div style="flex:1; background:rgba(201,168,76,0.03); border:1px solid rgba(201,168,76,0.2); padding:8px; border-radius:3px; text-align:center; box-shadow: inset 0 0 10px rgba(201,168,76,0.02);">
                    <div style="font-size:0.55rem; color:var(--gold); font-family:var(--font-m); letter-spacing:1px; margin-bottom:2px;">[ /INK ]</div>
                    <div style="font-size:0.45rem; color:var(--text-muted); font-weight:bold; letter-spacing:2px;">ARMED</div>
                </div>
                <div style="flex:1; background:rgba(124,158,191,0.03); border:1px solid rgba(124,158,191,0.2); padding:8px; border-radius:3px; text-align:center; box-shadow: inset 0 0 10px rgba(124,158,191,0.02);">
                    <div style="font-size:0.55rem; color:#7C9EBF; font-family:var(--font-m); letter-spacing:1px; margin-bottom:2px;">[ /INTEL ]</div>
                    <div style="font-size:0.45rem; color:var(--text-muted); font-weight:bold; letter-spacing:2px;">READY</div>
                </div>
                <div style="flex:1; background:rgba(76,175,154,0.03); border:1px solid rgba(76,175,154,0.2); padding:8px; border-radius:3px; text-align:center; box-shadow: inset 0 0 10px rgba(76,175,154,0.02);">
                    <div style="font-size:0.55rem; color:#4CAF9A; font-family:var(--font-m); letter-spacing:1px; margin-bottom:2px;">[ /HIKMAH ]</div>
                    <div style="font-size:0.45rem; color:var(--text-muted); font-weight:bold; letter-spacing:2px;">LOADED</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    active_persona = cfg.get("active_persona")
    if active_persona:
        from forge.persona_engine import get_persona_display_name
        pname = get_persona_display_name(active_persona)
        st.markdown(f"""
            <div class="vc-card" style="padding:6px 12px; font-size:0.65rem; color:var(--gold); border-color:rgba(201,168,76,0.3); margin-bottom:15px; display:flex; align-items:center; gap:8px;">
                <span class="status-dot" style="width:4px; height:4px;"></span>
                TACTICAL PERSONA: {pname.upper()}
            </div>
        """, unsafe_allow_html=True)

    from config import client as _audio_client, WHISPER_CONTEXT_PROMPT
    audio_value = st.audio_input("Record your intent", label_visibility="collapsed")
    if audio_value is not None:
        audio_bytes = audio_value.read()
        audio_hash  = hashlib.md5(audio_bytes).hexdigest()
        if st.session_state.get("last_audio_hash") != audio_hash:
            with st.spinner("Transcribing..."):
                transcription = _audio_client.audio.transcriptions.create(file=("audio.wav", audio_bytes), model="whisper-large-v3-turbo", prompt=WHISPER_CONTEXT_PROMPT, response_format="text")
                st.session_state["ta_input"] = f"{st.session_state.get('ta_input', '')} {transcription}".strip()
                st.session_state["last_audio_hash"] = audio_hash
                st.rerun()

    raw_input = st.text_area("intent", height=145, placeholder="English or Arabic intent...", label_visibility="collapsed", key="ta_input")

    if st.button(t("execute_btn"), use_container_width=True, key="btn_execute"):
        cleaned, violations = sanitize_input(raw_input or "")
        
        if not cleaned: st.warning(t("empty_input"))
        elif violations: st.error(t("injection_blocked"))
        elif check_rate_limit(consume=1):
            with st.status(t("status_processing"), expanded=True) as status:
                
                final_text, detected_dna = _apply_dna_triggers(cleaned)
                st.session_state["last_detected_triggers"] = detected_dna
                
                resolved_target = cfg["target_model"]
                if resolved_target == AUTO_SELECT_LABEL:
                    auto_target, auto_reason = detect_best_target(final_text)
                    resolved_target = auto_target
                    st.session_state[K.AUTO_TARGET] = auto_target
                    st.session_state[K.AUTO_REASON] = auto_reason
                
                result, audit, pattern = run_refinement_and_audit(
                    user_text        = final_text,
                    target           = resolved_target,
                    framework        = cfg["framework"],
                    lang             = cfg["source_lang"],
                    aesthetic_choice = cfg["aesthetic_choice"],
                    islamic_mode     = cfg["islamic_mode"],
                    persona          = cfg.get("active_persona"),
                )

                if not result.startswith("[CIPHER ERROR]"):
                    st.session_state[K.LAST_RESULT] = result
                    st.session_state["refined_output_area"] = result
                    st.session_state[K.LAST_AUDIT] = audit
                    st.session_state[K.LAST_INPUT] = cleaned
                    st.session_state[K.LAST_PATTERN] = pattern
                    st.rerun()

    last_result = st.session_state.get(K.LAST_RESULT)
    if last_result:
        left, right = st.columns([1, 2], gap="large")
        with left:
            _render_score_block(st.session_state.get(K.LAST_AUDIT, {}), st.session_state.get(K.LAST_PATTERN), st.session_state.get("last_detected_triggers"))
        with right:
            if "[CLARIFICATION_REQUIRED]" in last_result:
                st.warning(last_result.replace("[CLARIFICATION_REQUIRED]", ""))
            else:
                st.text_area("Refined Asset", value=last_result, height=220, key="refined_output_area")
