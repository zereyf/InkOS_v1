"""
ui/tabs/workspace.py
=====================
"""

from __future__ import annotations

import re
import time
from datetime import datetime, timezone

import streamlit as st
import streamlit.components.v1 as components

from config.targets import AUTO_SELECT_LABEL
from config.thresholds import INPUT_MAX_CHARS, INPUT_WARN_THRESHOLD
from engine.refiner import stream_refinement
from forge.intelligence import resolve_target_model
from forge.prompt_assembler import assemble_master_payload, make_dna_context
from security.sanitizer import sanitize_input
from state import K
from vault.vault_engine import save_prompt

UTC = timezone.utc

AUDIENCE_OPTIONS = ["Students", "Professionals", "General"]

QUICK_EXAMPLES = [
    ("EN", "AI in education article"),
    ("AR", "مقال عن الذكاء الاصطناعي"),
    ("EN", "Marketing copy — productivity app"),
    ("AR", "رسالة متابعة احترافية"),
]


# ── INSTRUCTION BUILDERS ──────────────────────────────────────────────────────

def _tone_instruction(v: int) -> str:
    if v <= 33: return "Use a formal, professional tone"
    if v <= 66: return "Use a neutral, balanced tone"
    return "Use a casual, conversational tone"

def _tone_label(v: int) -> str:
    if v <= 33: return "FORMAL"
    if v <= 66: return "NEUTRAL"
    return "CASUAL"

def _length_instruction(v: int) -> str:
    if v <= 33: return "Keep response under 100 words, concise"
    if v <= 66: return "Aim for 100–250 words, medium length"
    return "Provide a detailed response, 250+ words"

def _creativity_instruction(v: int) -> str:
    if v <= 33: return "Be conservative and logical"
    if v <= 66: return "Balance creativity with clarity"
    return "Be highly creative and imaginative"

def _audience_instruction(a: str) -> str:
    return {
        "Students":      "Use simple, educational language",
        "Professionals": "Use technical, precise language",
        "General":       "Use accessible, clear language",
    }.get(a, "Use accessible, clear language")


# ── OUTPUT CLEANING ───────────────────────────────────────────────────────────

def extract_clean_output(raw: str) -> str:
    t = str(raw or "")
    m = re.search(r"REFINED_PROMPT\s*:\s*(.+)", t, flags=re.I | re.S)
    if m: t = m.group(1)
    t = re.sub(r"\*\*\s*PART\s*\d+\s*:[^\n]*\**", "", t, flags=re.I)
    t = re.sub(r"(?:System\s*Prompt|PROMPT|OUTPUT|thinking)\s*:\s*", "", t, flags=re.I)
    t = re.sub(r"A\.I\.Z\.E\.N\.[\s\S]*?(?=\n\n|$)", "", t, flags=re.I)
    for tag in ("quality-bar", "constraints", "role", "task", "edge-cases"):
        t = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", t, flags=re.I | re.S)
    t = re.sub(r"```[\s\S]*?```", "", t)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"^\s*#{1,6}\s.*$", "", t, flags=re.M)
    t = re.sub(r"\{\s*\"score\"\s*:[\s\S]*?\}\s*$", "", t, flags=re.I)
    t = re.sub(r"REFINED_PROMPT\s*:\s*", "", t, flags=re.I)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


# ── UI COMPONENTS ─────────────────────────────────────────────────────────────

def _audit_score_component(audit: dict) -> None:
    """
    BUG-2 FIX: No HTML comments. No nested f-string.
    Two separate st.markdown() calls — score strip first, critique second.
    Each call is a flat concatenated string — no multiline f-string ambiguity.
    """
    score      = audit.get("score",      0)
    precision  = audit.get("precision",  0)
    alignment  = audit.get("alignment",  0)
    efficiency = audit.get("efficiency", 0)
    critique   = audit.get("critique",   "")

    if score >= 85:
        score_color = "#4CAF9A"
        score_label = "HIGH FIDELITY"
    elif score >= 70:
        score_color = "var(--gold)"
        score_label = "ACCEPTABLE"
    else:
        score_color = "#E57373"
        score_label = "NEEDS WORK"

    prec_pct  = int((precision  / 40) * 100)
    align_pct = int((alignment  / 40) * 100)
    effic_pct = int((efficiency / 20) * 100)
    target    = st.session_state.get(K.AUTO_TARGET, "—")

    # Score strip — single flat string, no comments, no nested expressions
    st.markdown(
        '<div class="audit-strip fade-in">'
        '<div style="display:flex;flex-direction:column;align-items:center;'
        'padding-right:16px;border-right:1px solid rgba(255,255,255,0.06);">'
        f'<div class="audit-main-score" style="color:{score_color};">{score}</div>'
        f'<div style="font-family:var(--font-m);font-size:8px;color:{score_color};'
        f'letter-spacing:0.15em;margin-top:2px;">{score_label}</div>'
        '</div>'
        '<div style="display:flex;gap:20px;flex-wrap:wrap;">'
        '<div>'
        '<div class="audit-dim-label">Precision</div>'
        '<div class="audit-dim-bar">'
        f'<div class="audit-dim-fill" style="width:{prec_pct}%;background:var(--steel);"></div>'
        '</div>'
        f'<div style="font-family:var(--font-m);font-size:9px;color:var(--steel);margin-top:2px;">{precision}/40</div>'
        '</div>'
        '<div>'
        '<div class="audit-dim-label">Alignment</div>'
        '<div class="audit-dim-bar">'
        f'<div class="audit-dim-fill" style="width:{align_pct}%;background:var(--gold);"></div>'
        '</div>'
        f'<div style="font-family:var(--font-m);font-size:9px;color:var(--gold);margin-top:2px;">{alignment}/40</div>'
        '</div>'
        '<div>'
        '<div class="audit-dim-label">Efficiency</div>'
        '<div class="audit-dim-bar">'
        f'<div class="audit-dim-fill" style="width:{effic_pct}%;background:#4CAF9A;"></div>'
        '</div>'
        f'<div style="font-family:var(--font-m);font-size:9px;color:#4CAF9A;margin-top:2px;">{efficiency}/20</div>'
        '</div>'
        '</div>'
        '<div style="margin-left:auto;">'
        f'<div class="routing-tag">❖ {target}</div>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Critique — separate call, plain if-block, no nested f-string
    if critique:
        st.markdown(
            '<div style="font-family:var(--font-m);font-size:11px;'
            'color:var(--text-muted);padding:8px 14px;'
            'background:rgba(0,0,0,0.2);border-radius:var(--radius-sm);'
            f'margin-bottom:10px;">✦ {critique}</div>',
            unsafe_allow_html=True,
        )


def _copy_to_clipboard_btn(text: str, key: str) -> None:
    escaped = text.replace("`", "\\`").replace("\\", "\\\\").replace("\n", "\\n")
    components.html(f"""
    <style>
        .copy-btn {{
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.08);
            color: #7C9EBF;
            font-family: 'IBM Plex Mono', monospace;
            font-size: 10px;
            letter-spacing: 0.1em;
            padding: 5px 14px;
            border-radius: 2px;
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        .copy-btn:hover {{ border-color: rgba(124,158,191,0.4); color: #B0C4DE; }}
        .copy-btn.copied {{ border-color: rgba(76,175,154,0.4); color: #4CAF9A; }}
    </style>
    <button class="copy-btn" id="copy_{key}"
            onclick="navigator.clipboard.writeText(`{escaped}`).then(() => {{
                const btn = document.getElementById('copy_{key}');
                btn.textContent = '✓  COPIED';
                btn.classList.add('copied');
                setTimeout(() => {{
                    btn.textContent = '📋  COPY';
                    btn.classList.remove('copied');
                }}, 2000);
            }});">
        📋&nbsp;&nbsp;COPY
    </button>
    """, height=40)


# ── CORE STREAMING PIPELINE ───────────────────────────────────────────────────

def _run_stream(
    intent_val: str,
    cfg:        dict,
    tone:       int,
    length:     int,
    creativity: int,
    audience:   str,
) -> None:
    cleaned, violations = sanitize_input(intent_val)
    if violations:
        st.error(
            "Blocked by security policy. "
            "Remove any injection or override patterns and try again."
        )
        return

    control_block = "\n".join([
        "[REFINEMENT CONTROLS]",
        _tone_instruction(tone),
        _length_instruction(length),
        _creativity_instruction(creativity),
        _audience_instruction(audience),
        "[/REFINEMENT CONTROLS]",
    ])

    dna_ctx = make_dna_context(
        ink    = str(st.session_state.get(K.INK_DNA)    or ""),
        intel  = str(st.session_state.get(K.INTEL_DNA)  or ""),
        hikmah = str(st.session_state.get(K.HIKMAH_DNA) or ""),
    )

    payload = assemble_master_payload(
        f"{cleaned}\n\n{control_block}",
        dict(cfg),
        dna_ctx,
    )

    resolved_target, routing_reason = resolve_target_model(AUTO_SELECT_LABEL, cleaned)
    st.session_state[K.AUTO_TARGET] = resolved_target
    st.session_state[K.AUTO_REASON] = routing_reason

    t0     = time.time()
    result = {}

    st.markdown(
        '<div style="font-family:var(--font-m);font-size:9px;color:var(--text-dim);'
        'letter-spacing:0.2em;text-transform:uppercase;margin-bottom:8px;">❖ Refining...</div>',
        unsafe_allow_html=True,
    )

    with st.container():
        st.write_stream(
            stream_refinement(
                master_payload   = payload,
                target           = resolved_target,
                framework        = cfg.get("framework", "RACE"),
                lang             = cfg.get("source_lang", "English"),
                aesthetic_choice = cfg.get("aesthetic_choice", "Default"),
                hikmah_style     = str(cfg.get("hikmah_style") or "None"),
                skip_security    = True,
                result           = result,
            )
        )

    latency_ms = int((time.time() - t0) * 1000)

    raw_refined = result.get("refined", "")
    audit       = result.get("audit",   {})
    error       = result.get("error")

    if error and not raw_refined:
        st.error(error)
        return

    clean      = extract_clean_output(raw_refined)
    score      = (audit or {}).get("score", 0)
    word_count = len(clean.split())
    density    = round(word_count / max(len(cleaned.split()), 1), 2)

    st.session_state[K.LAST_RESULT]  = clean
    st.session_state[K.LAST_AUDIT]   = audit or {}
    st.session_state[K.LAST_INPUT]   = cleaned
    st.session_state[K.PROMPT_COUNT] = st.session_state.get(K.PROMPT_COUNT, 0) + 1

    history = st.session_state.get(K.HISTORY, [])
    run_id  = f"RUN_{len(history) + 1:03d}"
    history.append({
        "id":         run_id,
        "time":       datetime.now(UTC).strftime("%H:%M:%S"),
        "timestamp":  datetime.now(UTC).isoformat(),
        "title":      cleaned[:40],
        "input":      cleaned,
        "output":     clean,
        "intent":     cleaned,
        "asset":      clean,
        "target":     resolved_target,
        "framework":  cfg.get("framework", "RACE"),
        "aesthetic":  cfg.get("aesthetic_choice", "Default"),
        "score":      score,
        "latency":    f"{latency_ms}ms",
        "density":    str(density),
        "word_count": str(word_count),
        "tone":       _tone_label(tone),
        "icon":       "❖",
        "pattern":    "RAW",
        "palette":    [],
    })
    st.session_state[K.HISTORY] = history[-50:]


# ── RENDERER ─────────────────────────────────────────────────────────────────

def render_workspace(cfg: dict) -> None:

    st.markdown(
        '<div class="vc-header">'
        '<span class="status-dot"></span>'
        'WORKSPACE'
        '<span style="margin-left:auto;font-size:9px;color:var(--text-dim);'
        'letter-spacing:0.1em;">مساحة العمل</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    if "workspace_text" not in st.session_state:
        st.session_state["workspace_text"] = st.session_state.get(K.LAST_INPUT, "")

    # Quick example chips
    st.markdown(
        '<div style="font-family:var(--font-m);font-size:9px;color:var(--text-dim);'
        'letter-spacing:0.15em;text-transform:uppercase;margin-bottom:8px;">'
        'Quick examples</div>',
        unsafe_allow_html=True,
    )

    example_texts = [
        "Write an article about AI in education",
        "اكتب مقالاً عن الذكاء الاصطناعي في التعليم",
        "Write marketing copy for a productivity app",
        "اكتب رسالة متابعة احترافية لعميل",
    ]
    chip_cols = st.columns(4)
    for i, (col, (lang, label), full_text) in enumerate(
        zip(chip_cols, QUICK_EXAMPLES, example_texts)
    ):
        with col:
            if st.button(
                f"{lang}  {label[:22]}{'…' if len(label) > 22 else ''}",
                key=f"chip_{i}",
                use_container_width=True,
            ):
                st.session_state["workspace_text"] = full_text
                st.rerun()

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # Input area
    st.markdown(
        '<div class="ws-panel-label">[ 01 ]  SOURCE INTENT</div>',
        unsafe_allow_html=True,
    )

    source = st.text_area(
        "source_prompt",
        value            = st.session_state["workspace_text"],
        height           = 200,
        placeholder      = (
            "Describe what you want the AI to do — in English or Arabic.\n"
            "اكتب ما تريد من الذكاء الاصطناعي أن يفعله..."
        ),
        max_chars        = INPUT_MAX_CHARS,
        label_visibility = "collapsed",
    )
    st.session_state["workspace_text"] = source

    char_count = len(source)
    if char_count >= INPUT_WARN_THRESHOLD:
        remaining = INPUT_MAX_CHARS - char_count
        st.warning(
            f"Approaching character limit — {remaining} remaining. "
            "Long inputs reduce refinement quality."
        )
    else:
        pct        = int((char_count / INPUT_MAX_CHARS) * 100)
        bar_color  = "var(--gold)" if char_count > 1500 else "var(--steel)"
        st.markdown(
            '<div style="display:flex;justify-content:space-between;align-items:center;'
            'margin-top:-8px;margin-bottom:8px;">'
            '<div style="flex:1;height:2px;background:rgba(255,255,255,0.04);'
            'border-radius:1px;overflow:hidden;margin-right:10px;">'
            f'<div style="height:100%;width:{pct}%;background:{bar_color};'
            'transition:width 0.3s ease;"></div>'
            '</div>'
            f'<div style="font-family:var(--font-m);font-size:10px;color:var(--text-dim);'
            f'white-space:nowrap;">{char_count:,} / {INPUT_MAX_CHARS:,}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # Controls
    st.markdown(
        '<div class="ws-panel-label">[ 02 ]  REFINEMENT CONTROLS</div>',
        unsafe_allow_html=True,
    )

    ctrl1, ctrl2, ctrl3 = st.columns(3)
    with ctrl1: tone       = st.slider("Tone",       0, 100, 50, key="sl_tone")
    with ctrl2: length     = st.slider("Length",     0, 100, 50, key="sl_length")
    with ctrl3: creativity = st.slider("Creativity", 0, 100, 50, key="sl_creativity")

    aud_col, _, run_col = st.columns([2, 1, 1])
    with aud_col:
        audience = st.selectbox("Audience", AUDIENCE_OPTIONS, label_visibility="collapsed")
    with run_col:
        run_clicked = st.button(
            "⚡  REFINE",
            type                = "primary",
            use_container_width = True,
            disabled            = not source.strip(),
            key                 = "refine_btn",
        )

    act1, act2, *_ = st.columns([1, 1, 2, 2])
    with act1:
        if st.button("✕  Clear", use_container_width=True, key="clear_btn"):
            st.session_state["workspace_text"] = ""
            st.session_state[K.LAST_RESULT]    = None
            st.session_state[K.LAST_AUDIT]     = {}
            st.rerun()
    with act2:
        if st.button("↺  Reset", use_container_width=True, key="reset_btn"):
            st.rerun()

    if run_clicked:
        _run_stream(source, cfg, tone, length, creativity, audience)
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Output panel
    output = st.session_state.get(K.LAST_RESULT)
    audit  = st.session_state.get(K.LAST_AUDIT, {})

    if not output:
        st.markdown(
            '<div style="border:1px dashed rgba(255,255,255,0.06);'
            'border-radius:var(--radius-lg);padding:40px 20px;text-align:center;margin-top:8px;">'
            '<div style="font-family:var(--font-m);font-size:0.65rem;color:var(--text-dim);'
            'letter-spacing:0.15em;text-transform:uppercase;">[ ❖ ]  Refined output will appear here</div>'
            '<div style="font-family:var(--font-a);font-size:12px;color:var(--text-dim);'
            'margin-top:6px;opacity:0.5;">سيظهر الناتج المحسّن هنا</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        return

    # Output header
    st.markdown(
        '<div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">'
        '<div style="font-family:var(--font-m);font-size:9px;color:var(--gold);'
        'letter-spacing:0.2em;text-transform:uppercase;">[ 03 ]  REFINED OUTPUT</div>'
        '<div style="flex:1;height:1px;background:linear-gradient(90deg,'
        'var(--gold-border),transparent);"></div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Audit score — BUG-2 fixed function
    _audit_score_component(audit)

    # Output text area
    st.text_area(
        "refined_output",
        value            = output,
        height           = 280,
        key              = "output_area",
        label_visibility = "collapsed",
    )

    # Metadata strip
    words   = len(output.split())
    chars   = len(output)
    minutes = max(1, round(words / 200))
    history = st.session_state.get(K.HISTORY, [])
    latency = history[-1].get("latency", "") if history else ""

    latency_span = f"<span>⚡ {latency}</span>" if latency else ""
    st.markdown(
        f'<div style="display:flex;gap:16px;flex-wrap:wrap;font-family:var(--font-m);'
        f'font-size:10px;color:var(--text-dim);margin-top:-4px;margin-bottom:14px;">'
        f'<span>📄 {words:,} words</span>'
        f'<span>Aa {chars:,} chars</span>'
        f'<span>⏱ ~{minutes} min read</span>'
        f'{latency_span}'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Action bar
    copy_col, save_col, _ = st.columns([1, 1, 2])

    with copy_col:
        _copy_to_clipboard_btn(output, key="main_output")

    with save_col:
        user_hash = st.session_state.get(K.USER_HASH, "")
        is_guest  = not user_hash or "GUEST_" in str(user_hash).upper()

        if is_guest:
            st.markdown(
                '<div style="font-family:var(--font-m);font-size:10px;'
                'color:var(--text-dim);padding:5px 0;letter-spacing:0.06em;">'
                'Login to save to Vault</div>',
                unsafe_allow_html=True,
            )
        else:
            if st.button("💾  Save to Vault", use_container_width=True, key="vault_save_btn"):
                score  = (audit or {}).get("score", 0)
                # BUG-1 FIX: intent= removed — vault table has no intent column
                record, err = save_prompt(
                    user_hash,
                    title     = st.session_state.get(K.LAST_INPUT, "")[:80] or "Untitled",
                    tags      = st.session_state.get(K.AUTO_TARGET, "").lower(),
                    content   = output,
                    target    = st.session_state.get(K.AUTO_TARGET, "ChatGPT"),
                    framework = cfg.get("framework", "RACE"),
                    score     = score,
                    aesthetic = cfg.get("aesthetic_choice", "Default"),
                )
                if err:
                    st.error(f"Vault save failed: {err}")
                else:
                    st.success("✓  Saved to Vault.")
                    st.session_state["_archive_cache_dirty"] = True
