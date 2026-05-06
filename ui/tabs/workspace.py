"""
ui/tabs/workspace.py — Workspace Tab
======================================
Tab 1: Input stream, live pattern preview, execution, results display.

Responsibilities:
  - Render text input with char counter
  - Run live pattern detection before execution (zero cost)
  - Execute sanitize → rate_limit → refine pipeline
  - Display pattern card, score block, and refined asset
  - Write results to session state via K keys
"""

import hashlib
import streamlit as st
from datetime import datetime
from typing import Optional

from state import K
from security.sanitizer import sanitize_input
from security.rate_limiter import check_rate_limit
from engine.cognitive_map import detect_arabic_pattern
from engine.refiner import run_refinement_and_audit, detect_best_target
from config import INPUT_MAX_CHARS, INPUT_WARN_THRESHOLD, AUTO_SELECT_LABEL
from i18n.translations import t


def _escape(text: str) -> str:
    """XSS-safe HTML rendering of user-supplied strings."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _render_pattern_card(pattern: dict, label: str = None) -> None:
    color = pattern.get("color", "#C9A84C")
    lbl = label or t("pattern_identified")
    st.markdown(f"""
    <div class="pattern-card">
        <span class="p-label">{lbl}</span>
        <span class="p-arabic" style="color:{color};">{pattern['pattern']}</span>
        <span class="p-paradigm" style="color:{color};">→ {pattern['prompt_paradigm']}</span>
    </div>
    """, unsafe_allow_html=True)


def _render_score_block(audit: dict, pattern: Optional[dict]) -> None:
    score      = int(audit.get("score",     0))
    precision  = int(audit.get("precision",  0))
    alignment  = int(audit.get("alignment",  0))
    efficiency = int(audit.get("efficiency", 0))
    critique   = str(audit.get("critique",  ""))

    p_pct = round((precision  / 40) * 100)
    a_pct = round((alignment  / 40) * 100)
    e_pct = round((efficiency / 20) * 100)

    # Pattern card inside results
    if pattern:
        color = pattern.get("color", "#C9A84C")
        st.markdown(f"""
        <div class="pattern-card" style="margin-bottom:12px;">
            <span class="p-label">Engine Applied</span>
            <span class="p-arabic" style="color:{color};">{pattern['pattern']}</span>
            <span class="p-paradigm" style="color:{color};">→ {pattern['prompt_paradigm']}</span>
        </div>
        """, unsafe_allow_html=True)

    critique_html = f'<div class="critique-line">{critique}</div>' if critique else ''
    st.markdown(f"""
    <div class="score-block">
        <div class="score-num">{score}<span>%</span></div>
        <div class="score-lbl">{t("refinement_quality")}</div>
        <div class="bar-row">
            <span class="bar-lbl">{t("precision")}</span>
            <div class="bar-track"><div class="bar-fill" style="width:{p_pct}%;background:#C9A84C;"></div></div>
            <span class="bar-val">{precision}/40</span>
        </div>
        <div class="bar-row">
            <span class="bar-lbl">{t("alignment")}</span>
            <div class="bar-track"><div class="bar-fill" style="width:{a_pct}%;background:#7C9EBF;"></div></div>
            <span class="bar-val">{alignment}/40</span>
        </div>
        <div class="bar-row">
            <span class="bar-lbl">{t("efficiency")}</span>
            <div class="bar-track"><div class="bar-fill" style="width:{e_pct}%;background:#4CAF9A;"></div></div>
            <span class="bar-val">{efficiency}/20</span>
        </div>
        {critique_html}
    </div>
    """, unsafe_allow_html=True)


def render_workspace(cfg: dict) -> None:
    """
    Renders Tab 1 — Workspace.
    cfg: SidebarConfig dict from ui/sidebar.py
    """
    st.markdown(
        f'<div class="vc-header"><span class="status-dot"></span>{t("workspace_header")}</div>',
        unsafe_allow_html=True,
    )

    # Active persona badge — shown when a persona is loaded
    active_persona = cfg.get("active_persona")
    if active_persona:
        from forge.persona_engine import get_persona_display_name
        pname = get_persona_display_name(active_persona)
        st.markdown(f"""
        <div style="
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
        Write or speak your raw intent in plain English or Arabic.
        InkOS restructures it into a precision prompt for your selected AI.
        No format required — just say what you want.
    </div>
    """, unsafe_allow_html=True)

    # ── VOICE ENGINE ──────────────────────────────────────────────────────────
    # FIX 1: Hash-based deduplication guard.
    #   st.audio_input returns a BytesIO object on every rerun.
    #   BytesIO equality compares by identity not content —
    #   two objects with identical bytes are NOT equal.
    #   We hash the bytes with MD5 and compare hashes instead.
    #   This guarantees each unique recording is transcribed exactly once.
    #
    # FIX 2: WHISPER_CONTEXT_PROMPT passed to API.
    #   Without it Whisper auto-translates Arabic → English.
    #   The context prompt forces transcription in the spoken language.
    #
    # FIX 3: Read bytes once, reuse for both hash and API call.
    #   audio_value.read() consumes the stream — calling it twice returns
    #   an empty bytes object on the second call.
    from config import WHISPER_CONTEXT_PROMPT, client as _audio_client

    st.markdown(
        '<div style="font-size:0.7rem;color:var(--gold);'
        'margin-bottom:4px;letter-spacing:1px;font-family:var(--font-m);">'
        '⎙ VOICE INPUT</div>',
        unsafe_allow_html=True,
    )
    audio_value = st.audio_input("Record your intent", label_visibility="collapsed")

    if audio_value is not None:
        # Read bytes once — stream is consumed on first read
        audio_bytes = audio_value.read()
        audio_hash  = hashlib.md5(audio_bytes).hexdigest()

        if st.session_state.get("last_audio_hash") != audio_hash:
            with st.spinner("Transcribing via Groq Whisper..."):
                try:
                    transcription = _audio_client.audio.transcriptions.create(
                        file=("audio.wav", audio_bytes),
                        model="whisper-large-v3-turbo",
                        prompt=WHISPER_CONTEXT_PROMPT,   # FIX 2: language guard
                        response_format="text",
                    )
                    current_text = st.session_state.get("ta_input", "")
                    new_text = f"{current_text} {transcription}".strip() if current_text else transcription
                    st.session_state["ta_input"]        = new_text
                    st.session_state["last_audio_hash"] = audio_hash  # FIX 1: store hash
                    st.rerun()
                except Exception as e:
                    st.error(f"Voice Engine Error: {str(e)}")

    raw_input: str = st.text_area(
        "intent",
        height=145,
        placeholder=(
            "English: Act as a senior analyst. Review this pitch deck and flag every "
            "assumption that lacks supporting evidence.\n\n"
            "عربي: اشرح لي هذا المفهوم تدريجياً بأسلوب تقني للمحترفين"
        ),
        label_visibility="collapsed",
        key="ta_input",
    )

    # ── CHAR COUNTER + LIVE PATTERN PREVIEW ───────────────────────────────────
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

    # ── EXECUTE ────────────────────────────────────────────────────────────────
    if st.button(t("execute_btn"), use_container_width=True, key="btn_execute",
                 help=t("execute_help")):
        cleaned, violations = sanitize_input(raw_input or "")

        if not cleaned:
            st.warning(t("empty_input"))

        elif violations:
            st.error(t("injection_blocked"))
            st.session_state[K.SECURITY_LOG].append({
                "time":     datetime.now().strftime("%H:%M:%S"),
                "hash":     hashlib.md5((raw_input or "").encode()).hexdigest()[:10],
                "patterns": violations,
            })

        elif not check_rate_limit(consume=1):
            st.warning(t("rate_limit"))

        else:
            with st.status(t("status_processing"), expanded=True) as status:
                st.write(t("status_mapping"))

                # ── AUTO TARGET RESOLUTION ─────────────────────────────────
                # If user left target on Auto, CIPHER analyses the input
                # and selects the best target before refinement begins.
                # If user manually selected a target, respect that choice.
                resolved_target = cfg["target_model"]

                if cfg["target_model"] == AUTO_SELECT_LABEL:
                    st.write("🎯 CIPHER analysing best target for this input...")
                    auto_target, auto_reason = detect_best_target(cleaned)
                    resolved_target = auto_target
                    st.session_state[K.AUTO_TARGET] = auto_target
                    st.session_state[K.AUTO_REASON] = auto_reason
                    st.write(f"✓ Target selected: **{auto_target}** — {auto_reason}")
                else:
                    # Clear auto state when user manually selects
                    st.session_state[K.AUTO_TARGET] = None
                    st.session_state[K.AUTO_REASON] = None

                # CIPHER may fire a retry if first score < 80
                result, audit, pattern = run_refinement_and_audit(
                    user_text        = cleaned,
                    target           = resolved_target,
                    framework        = cfg["framework"],
                    lang             = cfg["source_lang"],
                    aesthetic_choice = cfg["aesthetic_choice"],
                    islamic_mode     = cfg["islamic_mode"],
                    persona          = cfg.get("active_persona"),
                    brand_identity   = cfg.get("brand_identity"), # 🚨 FIXED: Priority 1 Audit Bug
                )
                
                score = (audit or {}).get("score", 0)
                retry_msg = " (retry applied)" if score >= 80 else ""
                st.write(t("status_compiling") + retry_msg)

                if not result.startswith("[REFINEMENT ERROR]"):
                    st.write(t("status_done"))
                    status.update(label=t("status_complete"), state="complete", expanded=False)

                    st.session_state[K.LAST_RESULT]  = result
                    st.session_state[K.LAST_AUDIT]   = audit
                    st.session_state[K.LAST_INPUT]   = cleaned
                    st.session_state[K.LAST_PATTERN] = pattern

                    st.session_state[K.HISTORY].insert(0, {
                        "id":        hashlib.md5(
                                         f"{cleaned}{datetime.now().isoformat()}".encode()
                                     ).hexdigest()[:8],
                        "time":      datetime.now().strftime("%H:%M:%S"),
                        "target":    resolved_target,
                        "framework": cfg["framework"],
                        "aesthetic": cfg["aesthetic_choice"],
                        "input":     cleaned,
                        "output":    result,
                        "score":     audit.get("score", 0),
                        "pattern":   pattern["pattern"] if pattern else None,
                        "islamic":   cfg["islamic_mode"],
                    })
                else:
                    status.update(label=t("status_error"), state="error", expanded=False)
                    st.error(result)

    # ── RESULTS ────────────────────────────────────────────────────────────────
    last_result  = st.session_state.get(K.LAST_RESULT)
    last_audit   = st.session_state.get(K.LAST_AUDIT) or {}
    last_input   = st.session_state.get(K.LAST_INPUT) or ""
    last_pattern = st.session_state.get(K.LAST_PATTERN)

    if last_result and not last_result.startswith("[REFINEMENT ERROR]"):
        st.markdown("<hr>", unsafe_allow_html=True)

        # Show CIPHER auto-selection explanation if it was used
        auto_target = st.session_state.get(K.AUTO_TARGET)
        auto_reason = st.session_state.get(K.AUTO_REASON)
        if auto_target and auto_reason:
            st.markdown(f"""
            <div style="
                display:inline-flex;align-items:center;gap:8px;
                background:rgba(201,168,76,0.07);
                border:1px solid rgba(201,168,76,0.25);
                border-radius:3px;padding:5px 14px;
                font-family:var(--font-m);font-size:0.65rem;
                color:var(--gold);margin-bottom:12px;
            ">
                <span class="status-dot"></span>
                CIPHER auto-selected: <strong>{auto_target}</strong>
                &nbsp;—&nbsp;
                <span style="color:var(--text-muted);">{auto_reason}</span>
            </div>
            """, unsafe_allow_html=True)

        left, right = st.columns([1, 2], gap="large")

        with left:
            _render_score_block(last_audit, last_pattern)

        with right:
            st.markdown(
                f'<div class="vc-header" style="font-size:0.6rem;">{t("original_intent")}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="vc-card" style="font-size:0.8rem;line-height:1.75;min-height:72px;">'
                f'{_escape(last_input)}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="vc-header" style="font-size:0.6rem;margin-top:16px;">{t("refined_asset")}</div>',
                unsafe_allow_html=True,
            )
            # WHY text_area over st.code:
            # st.code renders in a fixed-height non-resizable box.
            # Users cannot easily select, copy, or read long prompts.
            # text_area is resizable, fully selectable, and copyable.
            # disabled=True makes it read-only while keeping it interactive.
            st.text_area(
                "refined_output",
                value=last_result,
                height=220,
                disabled=False,
                label_visibility="collapsed",
                key="refined_output_area",
                help=t("refined_help"),
            )
            st.download_button(
                t("download_prompt"),
                data=last_result,
                file_name=(
                    f"vc_{cfg['target_model'].lower().replace(' ', '_')}"
                    f"_{datetime.now().strftime('%H%M%S')}.txt"
                ),
                key="btn_dl_result",
            )
            # ── SAVE TO VAULT ──────────────────────────────────────────────────
            from vault.supabase_client import SUPABASE_MISSING as _SB_MISSING
            if not _SB_MISSING:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                st.markdown(
                    f'<div class="vc-header" style="font-size:0.6rem;margin-top:4px;">{t("save_to_vault")}</div>',
                    unsafe_allow_html=True,
                )
                v1, v2 = st.columns([3, 2])
                with v1:
                    vault_title = st.text_input(
                        "Title",
                        placeholder=t("vault_title_ph"),
                        key="vault_title_input",
                        label_visibility="collapsed",
                    )
                with v2:
                    vault_tags = st.text_input(
                        "Tags",
                        placeholder=t("vault_tags_ph"),
                        key="vault_tags_input",
                        label_visibility="collapsed",
                    )

                if st.button(t("save_vault_btn"), use_container_width=True, key="btn_save_vault"):
                    if not vault_title.strip():
                        st.warning(t("save_vault_warning"))
                    else:
                        # Spinner gives immediate feedback — user knows click registered
                        with st.spinner(t("saving_vault")):
                            from vault.vault_engine import save_prompt
                            audit_data   = st.session_state.get(K.LAST_AUDIT) or {}
                            pattern_data = st.session_state.get(K.LAST_PATTERN)
                            _, save_err = save_prompt(
                                user_hash  = st.session_state.get(K.USER_HASH, ""),
                                title      = vault_title,
                                tags       = vault_tags,
                                content    = last_result,
                                target     = cfg.get("target_model", ""),
                                framework  = cfg.get("framework", ""),
                                score      = audit_data.get("score", 0),
                                pattern    = pattern_data["pattern"] if pattern_data else "",
                                islamic    = cfg.get("islamic_mode", False),
                                aesthetic  = cfg.get("aesthetic_choice", ""),
                            )
                        # Feedback always visible — success or failure, never silence
                        if save_err:
                            st.error(t('save_vault_error', error=save_err))
                        else:
                            st.session_state[K.VAULT_STATS] = {}
                            st.success(t('save_vault_success', title=vault_title))
