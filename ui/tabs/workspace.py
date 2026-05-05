"""
ui/tabs/workspace.py — Workspace Tab
======================================
Tab 1: Input stream, live pattern preview, execution, results display.

v14.0: THE MAJLIS VOICE ENGINE
- Integrated native st.audio_input for voice-to-prompt capability.
- Wired up Groq's whisper-large-v3-turbo for lightning-fast English/Arabic transcription.
- Added UX logic to append voice transcriptions to the text area dynamically.
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
from config import INPUT_MAX_CHARS, INPUT_WARN_THRESHOLD, AUTO_SELECT_LABEL, client
from i18n.translations import t


def _escape(text: str) -> str:
    """XSS-safe HTML rendering of user-supplied strings."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _render_pattern_card(pattern: dict, label: str = None) -> None:
    """Renders the rhetorical pattern identification card."""
    color = pattern.get("color", "#C9A84C")
    lbl = label or t("pattern_identified")
    st.markdown(f"""
    <div class="pattern-card">
        <span class="p-label">{lbl}</span>
        <span class="p-arabic" style="color:{color};">{pattern['pattern']}</span>
        <span class="p-paradigm" style="color:{color};">→ {pattern['prompt_paradigm']}</span>
    </div>
    """, unsafe_allow_html=True)


def _render_telemetry_block(audit: dict, pattern: Optional[dict], output_text: str, target_model: str) -> None:
    """Renders real system telemetry instead of fake progress bars."""
    audit_data = audit or {}
    critique   = str(audit_data.get("critique",  "Standard Text Compilation"))
    
    # Calculate real data
    est_tokens = int(len(output_text.split()) * 1.3)
    char_count = len(output_text)
    
    if pattern:
        color = pattern.get("color", "#C9A84C")
        st.markdown(f"""
        <div class="pattern-card" style="margin-bottom:12px;">
            <span class="p-label">Linguistic Engine</span>
            <span class="p-arabic" style="color:{color};">{pattern['pattern']}</span>
            <span class="p-paradigm" style="color:{color};">→ {pattern['prompt_paradigm']}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="score-block" style="padding: 16px;">
        <div class="score-lbl" style="font-size: 0.75rem; letter-spacing: 2px; color: var(--gold); margin-bottom: 12px;">
            [ SYSTEM TELEMETRY ]
        </div>
        <div style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--text-muted); line-height: 1.8;">
            <span style="color:#7C9EBF;">></span> <b>TARGET:</b> {target_model}<br>
            <span style="color:#7C9EBF;">></span> <b>ROUTING:</b> {critique}<br>
            <span style="color:#4CAF9A;">></span> <b>EST. TOKENS:</b> {est_tokens}<br>
            <span style="color:#4CAF9A;">></span> <b>CHARS:</b> {char_count}<br>
            <span style="color:#C9A84C;">></span> <b>STATUS:</b> OPTIMIZED
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_workspace(cfg: dict) -> None:
    """Main Workspace Tab (Tab 1) logic."""
    st.markdown(
        f'<div class="vc-header"><span class="status-dot"></span>{t("workspace_header")}</div>',
        unsafe_allow_html=True,
    )

    # Active persona badge
    active_persona = cfg.get("active_persona")
    if active_persona:
        from forge.persona_engine import get_persona_display_name
        pname = get_persona_display_name(active_persona)
        st.markdown(f"""
        <div class="persona-active-badge" style="
            display:inline-flex;align-items:center;gap:8px;
            background:rgba(201,168,76,0.07);
            border:1px solid rgba(201,168,76,0.25);
            border-radius:3px;padding:5px 12px;
            font-family:var(--font-m);font-size:0.65rem;
            color:var(--gold);margin-bottom:10px;
        ">
            <span class="status-dot"></span>
            PERSONA ACTIVE: {pname}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-family:var(--font-m);font-size:0.68rem;
                color:var(--text-muted);line-height:1.7;margin-bottom:8px;">
        Write your raw intent in plain English or Arabic.
        InkOS restructures it into a precision prompt for your selected AI.
    </div>
    """, unsafe_allow_html=True)

    # ── MAJLIS VOICE ENGINE ───────────────────────────────────────────────────
    st.markdown('<div style="font-size:0.7rem; color:var(--gold); margin-bottom:4px; letter-spacing:1px;">🎙️ MAJLIS VOICE ENGINE</div>', unsafe_allow_html=True)
    audio_value = st.audio_input("Record your intent", label_visibility="collapsed")
    
    if audio_value is not None:
        # Check if we already processed this exact audio snippet to prevent loop rendering
        if st.session_state.get("last_processed_audio") != audio_value:
            with st.spinner("Transcribing via Groq Whisper..."):
                try:
                    # Send audio bytes to Groq Whisper API
                    transcription = client.audio.transcriptions.create(
                        file=("audio.wav", audio_value.read()),
                        model="whisper-large-v3-turbo",
                        response_format="text"
                    )
                    
                    # Append the transcription to whatever is already in the text area
                    current_text = st.session_state.get("ta_input", "")
                    new_text = f"{current_text} {transcription}".strip() if current_text else transcription
                    
                    # Update session state and refresh
                    st.session_state["ta_input"] = new_text
                    st.session_state["last_processed_audio"] = audio_value
                    st.rerun()
                except Exception as e:
                    st.error(f"Voice Engine Error: {str(e)}")

    # ── TEXT AREA ─────────────────────────────────────────────────────────────
    raw_input: str = st.text_area(
        "intent",
        height=145,
        placeholder=(
            "English: Act as a senior analyst. Review this pitch deck...\n"
            "عربي: اشرح لي هذا المفهوم تدريجياً بأسلوب تقني للمحترفين"
        ),
        label_visibility="collapsed",
        key="ta_input",
    )

    if raw_input:
        char = len(raw_input)
        c_color = "#A93226" if char > INPUT_WARN_THRESHOLD else "#3A4455"
        st.markdown(
            f'<div class="char-counter" style="color:{c_color};">{char} / {INPUT_MAX_CHARS}</div>',
            unsafe_allow_html=True,
        )

        if cfg["source_lang"] == "Arabic (العربية)":
            preview = detect_arabic_pattern(raw_input)
            if preview:
                _render_pattern_card(preview)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── EXECUTION ─────────────────────────────────────────────────────────────
    if st.button(t("execute_btn"), use_container_width=True, key="btn_execute"):
        cleaned, violations = sanitize_input(raw_input or "")

        if not cleaned:
            st.warning(t("empty_input"))
        elif violations:
            st.error(t("injection_blocked"))
        elif not check_rate_limit(consume=1):
            st.warning(t("rate_limit"))
        else:
            # Sleek terminal-style loading state
            with st.status("Initializing MARCEL Compiler...", expanded=True) as status:
                st.write("> Connecting to Groq Engine...")

                resolved_target = cfg["target_model"]
                if cfg["target_model"] == AUTO_SELECT_LABEL:
                    st.write("> Analyzing semantic intent for auto-routing...")
                    auto_target, auto_reason = detect_best_target(cleaned)
                    resolved_target = auto_target
                    st.session_state[K.AUTO_TARGET] = auto_target
                    st.session_state[K.AUTO_REASON] = auto_reason
                else:
                    st.session_state[K.AUTO_TARGET] = None
                    st.session_state[K.AUTO_REASON] = None

                st.write(f"> Target locked: {resolved_target}. Compiling Expert Blueprint...")
                
                result, audit, pattern = run_refinement_and_audit(
                    user_text        = cleaned,
                    target           = resolved_target,
                    framework        = cfg["framework"],
                    lang             = cfg["source_lang"],
                    aesthetic_choice = cfg["aesthetic_choice"],
                    islamic_mode     = cfg["islamic_mode"],
                    persona          = cfg.get("active_persona"),
                )
                
                # Defensive type-check
                res_str = str(result) if result is not None else ""
                
                if res_str.startswith("[CIPHER ERROR]"):
                    status.update(label="Engine Error", state="error", expanded=False)
                    st.error(res_str)
                else:
                    status.update(label="Compilation Complete", state="complete", expanded=False)
                    st.session_state[K.LAST_RESULT]  = result
                    st.session_state[K.LAST_AUDIT]   = audit
                    st.session_state[K.LAST_INPUT]   = cleaned
                    st.session_state[K.LAST_PATTERN] = pattern
                    st.session_state[K.HISTORY].insert(0, {
                        "id": hashlib.md5(f"{cleaned}{datetime.now()}".encode()).hexdigest()[:8],
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "target": resolved_target,
                        "framework": cfg["framework"],
                        "aesthetic": cfg["aesthetic_choice"],
                        "input": cleaned,
                        "output": result,
                        "score": (audit or {}).get("score", 0),
                        "pattern": pattern["pattern"] if pattern else None,
                        "islamic": cfg["islamic_mode"],
                    })

    # ── RESULTS RENDERING ─────────────────────────────────────────────────────
    last_result  = st.session_state.get(K.LAST_RESULT)
    last_audit   = st.session_state.get(K.LAST_AUDIT) or {}
    last_input   = st.session_state.get(K.LAST_INPUT) or ""
    last_pattern = st.session_state.get(K.LAST_PATTERN)

    last_res_str = str(last_result) if last_result else ""

    if last_res_str and not last_res_str.startswith("[CIPHER ERROR]"):
        st.markdown("<hr>", unsafe_allow_html=True)
        
        auto_target = st.session_state.get(K.AUTO_TARGET)
        auto_reason = st.session_state.get(K.AUTO_REASON)
        
        # We need to know the final resolved target for Telemetry and Buttons
        final_target_display = auto_target if auto_target else cfg.get("target_model", "ChatGPT")

        if auto_target and auto_reason:
            st.markdown(f"""
            <div class="auto-target-pill" style="
                display:inline-flex;align-items:center;gap:8px;
                background:rgba(201,168,76,0.07);
                border:1px solid rgba(201,168,76,0.25);
                border-radius:3px;padding:5px 14px;
                font-family:var(--font-m);font-size:0.65rem;
                color:var(--gold);margin-bottom:12px;
            ">
                <span class="status-dot"></span>
                CIPHER selected: <strong>{auto_target}</strong> — {auto_reason}
            </div>
            """, unsafe_allow_html=True)

        left, right = st.columns([1, 2], gap="large")
        with left:
            # Replaced Fake metrics with Real Telemetry
            _render_telemetry_block(last_audit, last_pattern, last_res_str, final_target_display)
            
        with right:
            st.markdown(f'<div class="vc-header" style="font-size:0.6rem;">{t("original_intent")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="vc-card" style="font-size:0.8rem;line-height:1.75;">{_escape(last_input)}</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="vc-header" style="font-size:0.6rem;margin-top:16px;">{t("refined_asset")}</div>', unsafe_allow_html=True)
            st.text_area("output", value=last_res_str, height=220, label_visibility="collapsed", key="out_area")

            # ── 1-CLICK ACTION BUTTONS ────────────────────────────────────────
            dl_ts = datetime.now().strftime("%H%M%S")
            b1, b2, b3 = st.columns(3)
            
            with b1:
                st.download_button(
                    "💾 Download",
                    data=last_res_str,
                    file_name=f"inkos_{dl_ts}.txt",
                    key=f"dl_btn_{dl_ts}",
                    use_container_width=True
                )
            with b2:
                # ChatGPT supports prompt injection via URL param for Search/Chat
                gpt_url = f"https://chatgpt.com/?q={urllib.parse.quote(last_res_str)}"
                st.link_button("↗ Open in ChatGPT", gpt_url, use_container_width=True)
            with b3:
                # Claude URL (Anthropic doesn't support direct URL prompt injection yet, so it goes to new chat)
                st.link_button("↗ Open in Claude", "https://claude.ai/new", use_container_width=True)
            
            # Vault Saving Logic
            from vault.supabase_client import SUPABASE_MISSING
            if not SUPABASE_MISSING:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                v1, v2 = st.columns(2)
                with v1: v_title = st.text_input("Title", key="v_t", label_visibility="collapsed", placeholder="Title")
                with v2: v_tags = st.text_input("Tags", key="v_tg", label_visibility="collapsed", placeholder="Tags")
                if st.button(t("save_vault_btn"), key="v_save", use_container_width=True):
                    if v_title.strip():
                        from vault.vault_engine import save_prompt
                        save_prompt(user_hash=st.session_state.get(K.USER_HASH, ""), title=v_title, tags=v_tags, content=last_res_str, target=final_target_display, framework=cfg.get("framework", ""), score=(last_audit or {}).get("score", 0), pattern=last_pattern["pattern"] if last_pattern else "", islamic=cfg.get("islamic_mode", False), aesthetic=cfg.get("aesthetic_choice", ""))
                        st.success("Saved to Vault.")
