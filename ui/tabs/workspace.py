"""
ui/tabs/workspace.py — Workspace Tab
======================================
v16.1: THE RENDER-LOCK FIX
- Moved Voice Processing to the Top-Gate to avoid StreamlitAPIException.
- Implemented state-synced contextual swapping (Mic <-> Bolt).
- Preserved dynamic identity and telemetry logic.
"""

import hashlib
import streamlit as st
import urllib.parse
from datetime import datetime
from typing import Optional

from state import K
from security.sanitizer import sanitize_input
from security.rate_limiter import check_rate_limit
from engine.cognitive_map import detect_arabic_pattern
from engine.refiner import run_refinement_and_audit, detect_best_target
from config import INPUT_MAX_CHARS, INPUT_WARN_THRESHOLD, AUTO_SELECT_LABEL, client, AUDIO_MODEL_ID, WHISPER_CONTEXT_PROMPT
from i18n.translations import t

def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_workspace(cfg: dict) -> None:
    # ── 1. TOP-GATE VOICE PROCESSING ──────────────────────────────────────────
    # We check for voice input BEFORE rendering any other widgets.
    # We use the 'voice_pill' key from the session state.
    if "voice_pill" in st.session_state and st.session_state.voice_pill is not None:
        audio_data = st.session_state.voice_pill
        # Only process if this is a NEW recording
        if st.session_state.get("last_voice_id") != id(audio_data):
            with st.spinner("🎙️ MARCEL is listening..."):
                try:
                    transcription = client.audio.transcriptions.create(
                        file=("audio.wav", audio_data.read()),
                        model=AUDIO_MODEL_ID,
                        prompt=WHISPER_CONTEXT_PROMPT,
                        response_format="text"
                    )
                    # Update the state BEFORE the text area is instantiated
                    current_text = st.session_state.get("ta_input", "")
                    st.session_state["ta_input"] = f"{current_text} {transcription}".strip()
                    st.session_state["last_voice_id"] = id(audio_data)
                    st.rerun() # Refresh to show text in the pill
                except Exception as e:
                    st.error(f"Voice Engine Error: {e}")

    # ── 2. HEADER & BADGES ────────────────────────────────────────────────────
    st.markdown(f'<div class="vc-header"><span class="status-dot"></span>{t("workspace_header")}</div>', unsafe_allow_html=True)

    active_persona = cfg.get("active_persona")
    if active_persona:
        from forge.persona_engine import get_persona_display_name
        pname = get_persona_display_name(active_persona)
        st.markdown(f'<div class="persona-active-badge">PERSONA ACTIVE: {pname}</div>', unsafe_allow_html=True)

    # ── 3. THE COMMAND PILL (TRANSFORMATIVE UI) ───────────────────────────────
    st.markdown('<div style="font-size:0.7rem; color:var(--gold); margin-bottom:8px; letter-spacing:1px;">⚡ COMMAND CENTER</div>', unsafe_allow_html=True)
    
    col_input, col_action = st.columns([8, 1.5], gap="small", vertical_alignment="bottom")
    
    with col_input:
        raw_input: str = st.text_area(
            "intent",
            height=None,
            placeholder="Describe your intent or speak to MARCEL...",
            label_visibility="collapsed",
            key="ta_input", # This now stays in sync with the Top-Gate
        )

    with col_action:
        execute_triggered = False
        # CONTEXTUAL SWAP: If user has typed or spoken text, show Execute Bolt
        if len(raw_input.strip()) > 0:
            if st.button("⚡", key="btn_exec_pill", use_container_width=True):
                execute_triggered = True
        else:
            # If field is empty, show Mic
            st.audio_input("Record", label_visibility="collapsed", key="voice_pill")

    # ── 4. CHARACTER COUNTER & ARABIC PREVIEW ─────────────────────────────────
    if raw_input:
        char = len(raw_input)
        c_color = "#A93226" if char > INPUT_WARN_THRESHOLD else "var(--text-muted)"
        st.markdown(f'<div style="text-align: right; font-size: 0.62rem; color:{c_color}; margin-top:-10px; margin-right: 15px;">{char} / {INPUT_MAX_CHARS}</div>', unsafe_allow_html=True)

        if cfg["source_lang"] == "Arabic (العربية)":
            preview = detect_arabic_pattern(raw_input)
            if preview:
                _render_pattern_card(preview)

    # ── 5. EXECUTION LOGIC ────────────────────────────────────────────────────
    if execute_triggered:
        cleaned, violations = sanitize_input(raw_input or "")
        if not cleaned:
            st.warning(t("empty_input"))
        elif violations:
            st.error(t("injection_blocked"))
        elif not check_rate_limit(consume=1):
            st.warning(t("rate_limit"))
        else:
            with st.status("Initializing MARCEL Compiler...", expanded=True) as status:
                st.write("> Connecting to Groq Engine...")
                resolved_target = cfg["target_model"]
                if cfg["target_model"] == AUTO_SELECT_LABEL:
                    auto_target, auto_reason = detect_best_target(cleaned)
                    resolved_target = auto_target
                    st.session_state[K.AUTO_TARGET] = auto_target
                    st.session_state[K.AUTO_REASON] = auto_reason
                
                result, audit, pattern = run_refinement_and_audit(
                    user_text=cleaned, target=resolved_target, framework=cfg["framework"],
                    lang=cfg["source_lang"], aesthetic_choice=cfg["aesthetic_choice"],
                    islamic_mode=cfg["islamic_mode"], persona=cfg.get("active_persona"),
                    brand_identity=cfg.get("brand_identity")
                )
                
                if str(result).startswith("[CIPHER ERROR]"):
                    status.update(label="Engine Error", state="error", expanded=False)
                else:
                    status.update(label="Compilation Complete", state="complete", expanded=False)
                    st.session_state[K.LAST_RESULT] = result
                    st.session_state[K.LAST_AUDIT] = audit
                    st.session_state[K.LAST_INPUT] = cleaned
                    st.session_state[K.LAST_PATTERN] = pattern
                    st.session_state[K.HISTORY].insert(0, {
                        "id": hashlib.md5(f"{cleaned}{datetime.now()}".encode()).hexdigest()[:8],
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "target": resolved_target, "framework": cfg["framework"],
                        "output": result, "score": (audit or {}).get("score", 0),
                    })

    # ── 6. RESULTS RENDERING ──────────────────────────────────────────────────
    # (Keep your existing results rendering code here exactly as it was)
