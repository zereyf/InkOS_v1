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
from engine.refiner import run_refinement_and_audit
from config import INPUT_MAX_CHARS, INPUT_WARN_THRESHOLD


def _escape(text: str) -> str:
    """XSS-safe HTML rendering of user-supplied strings."""
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _render_pattern_card(pattern: dict) -> None:
    color = pattern.get("color", "#C9A84C")
    st.markdown(f"""
    <div class="pattern-card">
        <span class="p-label">Pattern Identified</span>
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
        <div class="score-lbl">Refinement Quality</div>
        <div class="bar-row">
            <span class="bar-lbl">Precision</span>
            <div class="bar-track"><div class="bar-fill" style="width:{p_pct}%;background:#C9A84C;"></div></div>
            <span class="bar-val">{precision}/40</span>
        </div>
        <div class="bar-row">
            <span class="bar-lbl">Alignment</span>
            <div class="bar-track"><div class="bar-fill" style="width:{a_pct}%;background:#7C9EBF;"></div></div>
            <span class="bar-val">{alignment}/40</span>
        </div>
        <div class="bar-row">
            <span class="bar-lbl">Efficiency</span>
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
        '<div class="vc-header"><span class="status-dot"></span>System Input</div>',
        unsafe_allow_html=True,
    )

    raw_input: str = st.text_area(
        "intent",
        height=145,
        placeholder=(
            "Define mission in English or Arabic...\n"
            "مثال: اشرح لي هذا المفهوم تدريجياً بأسلوب تقني"
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
   # ── EXECUTE ────────────────────────────────────────────────────────────────
    if st.button("⚡  Execute Refinement", use_container_width=True, key="btn_execute"):
        cleaned, violations = sanitize_input(raw_input or "")

        if not cleaned:
            st.warning("Intent stream is empty.")

        elif violations:
            st.error("BLOCKED — Injection pattern detected. Request logged.")
            st.session_state[K.SECURITY_LOG].append({
                "time":     datetime.now().strftime("%H:%M:%S"),
                "hash":     hashlib.md5((raw_input or "").encode()).hexdigest()[:10],
                "patterns": violations,
            })

        elif not check_rate_limit(consume=1):
            st.warning("Rate limit reached — 10 calls per 60 seconds.")

        else:
            with st.status("Processing...", expanded=True) as status:
                st.write("🗺️ Mapping cognitive pattern...")
                
                result, audit, pattern = run_refinement_and_audit(
                    user_text        = cleaned,
                    target           = cfg["target_model"],
                    framework        = cfg["framework"],
                    lang             = cfg["source_lang"],
                    aesthetic_choice = cfg["aesthetic_choice"],
                    islamic_mode     = cfg["islamic_mode"],
                )
                
                st.write("✅ Refinement complete. Compiling audit scores...")

                if not result.startswith("[REFINEMENT ERROR]"):
                    st.write("📊 Done.")
                    status.update(label="Complete", state="complete", expanded=False)

                    st.session_state[K.LAST_RESULT]  = result
                    st.session_state[K.LAST_AUDIT]   = audit
                    st.session_state[K.LAST_INPUT]   = cleaned
                    st.session_state[K.LAST_PATTERN] = pattern

                    st.session_state[K.HISTORY].insert(0, {
                        "id":        hashlib.md5(
                                         f"{cleaned}{datetime.now().isoformat()}".encode()
                                     ).hexdigest()[:8],
                        "time":      datetime.now().strftime("%H:%M:%S"),
                        "target":    cfg["target_model"],
                        "framework": cfg["framework"],
                        "aesthetic": cfg["aesthetic_choice"],
                        "input":     cleaned,
                        "output":    result,
                        "score":     audit.get("score", 0),
                        "pattern":   pattern["pattern"] if pattern else None,
                        "islamic":   cfg["islamic_mode"],
                    })
                else:
                    status.update(label="Error", state="error", expanded=False)
                    st.error(result)

    # ── RESULTS ────────────────────────────────────────────────────────────────
    last_result  = st.session_state.get(K.LAST_RESULT)
    last_audit   = st.session_state.get(K.LAST_AUDIT) or {}
    last_input   = st.session_state.get(K.LAST_INPUT) or ""
    last_pattern = st.session_state.get(K.LAST_PATTERN)

    if last_result and not last_result.startswith("[REFINEMENT ERROR]"):
        st.markdown("<hr>", unsafe_allow_html=True)

        left, right = st.columns([1, 2], gap="large")

        with left:
            _render_score_block(last_audit, last_pattern)

        with right:
            st.markdown(
                '<div class="vc-header" style="font-size:0.6rem;">Original Intent</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div class="vc-card" style="font-size:0.8rem;line-height:1.75;min-height:72px;">'
                f'{_escape(last_input)}</div>',
                unsafe_allow_html=True,
            )
            st.markdown(
                '<div class="vc-header" style="font-size:0.6rem;margin-top:16px;">Refined Asset</div>',
                unsafe_allow_html=True,
            )
            st.code(last_result, language="markdown")
            st.download_button(
                "Download Prompt",
                data=last_result,
                file_name=(
                    f"vc_{cfg['target_model'].lower().replace(' ', '_')}"
                    f"_{datetime.now().strftime('%H%M%S')}.txt"
                ),
                key="btn_dl_result",
            )