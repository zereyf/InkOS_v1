"""
ui/tabs/workspace.py — Workspace Tab
======================================
Tab 1: Input stream, live pattern preview, execution, results display.

v12.4: Type-Safe Refinement Execution.
Fixed AttributeError on result.startswith() by implementing res_str validation.
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
    # Safe extraction of audit metrics
    audit_data = audit or {}
    score      = int(audit_data.get("score",     0))
    precision  = int(audit_data.get("precision",  0))
    alignment  = int(audit_data.get("alignment",  0))
    efficiency = int(audit_data.get("efficiency", 0))
    critique   = str(audit_data.get("critique",  ""))

    p_pct = round((precision  / 40) * 100) if precision else 0
    a_pct = round((alignment  / 40) * 100) if alignment else 0
    e_pct = round((efficiency / 20) * 100) if efficiency else 0

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
    """Renders the Workspace (Tab 1) logic and UI."""
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
        No format required — just say what you want.
    </div>
    """, unsafe_allow_html=True)

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

    # ── EXECUTION PIPELINE ───────────────────────────────────────────────────
    if st.button(t("execute_btn"), use_container_width=True, key="btn_execute"):
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

                resolved_target = cfg["target_model"]

                if cfg["target_model"] == AUTO_SELECT_LABEL:
                    st.write("🎯 CIPHER analysing best target...")
                    auto_target, auto_reason = detect_best_target(cleaned)
                    resolved_target = auto_target
                    st.session_state[K.AUTO_TARGET] = auto_target
                    st.session_state[K.AUTO_REASON] = auto_reason
                    st.write(f"✓ Target selected: **{auto_target}**")
                else:
                    st.session_state[K.AUTO_TARGET] = None
                    st.session_state[K.AUTO_REASON] = None

                # Execute Refinement and Audit
                result, audit, pattern = run_refinement_and_audit(
                    user_text        = cleaned,
                    target           = resolved_target,
                    framework        = cfg["framework"],
                    lang             = cfg["source_lang"],
                    aesthetic_choice = cfg["aesthetic_choice"],
                    islamic_mode     = cfg["islamic_mode"],
                    persona          = cfg.get("active_persona"),
                )
                
                # ── TYPE-SAFE VALIDATION ─────────────────────────────────────
                # Defensive check: Ensure result is a string before calling startswith
                res_str = str(result) if result is not None else ""
                
                audit_safe = audit or {}
                score = audit_safe.get("score", 0)
                retry_msg = " (retry applied)" if score >= 80 else ""
                st.write(t("status_compiling") + retry_msg)

                if res_str.startswith("[CIPHER ERROR]"):
                    status.update(label="Engine Offline", state="error", expanded=False)
                    st.warning("**The Cognitive Engine is currently busy.** Please try again.", icon="⚠️")
                    print(f"Backend API Error: {res_str}")
                else:
                    st.write(t("status_done"))
                    status.update(label=t("status_complete"), state="complete", expanded=False)

                    st.session_state[K.LAST_RESULT]  = result
                    st.session_state[K.LAST_AUDIT]   = audit
                    st.session_state[K.LAST_INPUT]   = cleaned
                    st.session_state[K.LAST_PATTERN] = pattern

                    st.session_state[K.HISTORY].insert(0, {
                        "id":        hashlib.md5(f"{cleaned}{datetime.now()}".encode()).hexdigest()[:8],
                        "time":      datetime.now().strftime("%H:%M:%S"),
                        "target":    resolved_target,
                        "framework": cfg["framework"],
                        "aesthetic": cfg["aesthetic_choice"],
                        "input":     cleaned,
                        "output":    result,
                        "score":     score,
                        "pattern":   pattern["pattern"] if pattern else None,
                        "islamic":   cfg["islamic_mode"],
                    })

    # ── RESULTS RENDERING ─────────────────────────────────────────────────────
    last_result  = st.session_state.get(K.LAST_RESULT)
    last_audit   = st.session_state.get(K.LAST_AUDIT) or {}
    last_input   = st.session_state.get(K.LAST_INPUT) or ""
    last_pattern = st.session_state.get(K.LAST_PATTERN)

    # Safe string conversion for display check
    last_res_str = str(last_result) if last_result is not None else ""

    if last_result and not last_res_str.startswith("[CIPHER ERROR]"):
        st.markdown("<hr>", unsafe_allow_html=True)

        auto_target = st.session_state.get(K.AUTO_TARGET)
        auto_reason = st.session_state.get(K.AUTO_REASON)
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
                CIPHER selected: <strong>{auto_target}</strong>
                &nbsp;—&nbsp;
                <span style="color:var(--text-muted);">{auto_reason}</span>
            </div>
            """, unsafe_allow_html=True)

        l_col, r_col = st.columns([1, 2], gap="large")

        with l_col:
            _render_score_block(last_audit, last_pattern)

        with r_col:
            st.markdown(f'<div class="vc-header" style="font-size:0.6rem;">{t("original_intent")}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="vc-card" style="font-size:0.8rem;line-height:1.75;">{_escape(last_input)}</div>', unsafe_allow_html=True)
            
            st.markdown(f'<div class="vc-header" style="font-size:0.6rem;margin-top:16px;">{t("refined_asset")}</div>', unsafe_allow_html=True)
            st.text_area(
                "refined_output",
                value=last_result,
                height=220,
                key="refined_output_area",
                label_visibility="collapsed",
            )
            st.download_button(
                t("download_prompt"),
                data=last_result,
                file_name=f"inkos_{datetime.now().strftime('%H%M%S')}.txt",
                key="btn_dl_result",
            )
            
            # Save to Vault Section
            from vault.supabase_client import SUPABASE_MISSING
            if not SUPABASE_MISSING:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                st.markdown(f'<div class="vc-header" style="font-size:0.6rem;margin-top:4px;">{t("save_to_vault")}</div>', unsafe_allow_html=True)
                v1, v2 = st.columns([3, 2])
                with v1:
                    v_title = st.text_input("Title", placeholder=t("vault_title_ph"), label_visibility="collapsed", key="v_title")
                with v2:
                    v_tags = st.text_input("Tags", placeholder=t("vault_tags_ph"), label_visibility="collapsed", key="v_tags")

                if st.button(t("save_vault_btn"), use_container_width=True, key="btn_save_v"):
                    if not v_title.strip():
                        st.warning(t("save_vault_warning"))
                    else:
                        with st.spinner(t("saving_vault")):
                            from vault.vault_engine import save_prompt
                            _, save_err = save_prompt(
                                user_hash  = st.session_state.get(K.USER_HASH, ""),
                                title      = v_title,
                                tags       = v_tags,
                                content    = last_result,
                                target     = cfg.get("target_model", ""),
                                framework  = cfg.get("framework", ""),
                                score      = (last_audit or {}).get("score", 0),
                                pattern    = last_pattern["pattern"] if last_pattern else "",
                                islamic    = cfg.get("islamic_mode", False),
                                aesthetic  = cfg.get("aesthetic_choice", ""),
                            )
                        if save_err:
                            st.error(t('save_vault_error', error=save_err))
                        else:
                            st.success(t('save_vault_success', title=v_title))