"""
workspace.py — v2.1
=====================
CLEAN-1 FIXED: extract_clean_output() was partially destroying Claude XML output.

  Root cause A: The tag-strip loop used hyphenated names ("quality-bar",
  "edge-cases") but Claude outputs use underscores (<quality_bar>, <edge_cases>).
  Those tags didn't match — their content was left as floating plain text.

  Root cause B: Tags that DID match ("role", "task", "constraints") had their
  entire content removed, not just their brackets. So the role description,
  task, and constraints were wiped from the displayed output entirely.

  Root cause C: The remaining <[^>]+> sweep stripped only the brackets,
  leaving tag content as unstructured plain text with no XML framing.

  Fix: Detect Claude XML structure (≥2 known block tags present).
  If detected → it IS the correct output format. Format it cleanly with
  consistent line breaks. Do NOT strip content.
  If not detected → strip leaked tag brackets from non-Claude outputs only.

CLEAN-2 FIXED: JSON audit block appearing in the copyable output text area.

  Root cause: The regex  r"\\{\\s*\\"score\\"\\s*:[\\s\\S]*?\\}\\s*$"  uses a
  non-greedy quantifier that stops at the FIRST } it encounters. If the
  critique string contains a } character, the match terminates mid-JSON
  and the remainder appears in the user's output.

  Fix: Replaced with a balanced-brace scanner that correctly handles
  nested structures and special characters inside string values.
  The audit JSON is now reliably stripped regardless of critique content.
"""

from __future__ import annotations

import json
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
from security.rate_limiter import check_rate_limit
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


# ── BALANCED-BRACE JSON STRIPPER ──────────────────────────────────────────────

def _find_audit_json_start(text: str) -> int:
    """
    Walk backwards through text to find the start of the audit JSON object.
    Uses balanced-brace scanning so critique strings containing } don't
    cause premature termination.
    Returns the index of the opening { or -1 if not found.
    """
    search_from = len(text)
    while search_from > 0:
        idx = text.rfind("{", 0, search_from)
        if idx == -1:
            break
        snippet = text[idx:]
        # Quick pre-check before the expensive scan
        if not re.match(r'\{\s*"score"\s*:', snippet):
            search_from = idx
            continue
        # Balanced-brace scan
        depth, in_string, escape = 0, False, False
        end = -1
        for i, ch in enumerate(snippet):
            if in_string:
                if escape:       escape = False
                elif ch == "\\": escape = True
                elif ch == '"':  in_string = False
                continue
            if ch == '"':    in_string = True
            elif ch == "{":  depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i
                    break
        if end == -1:
            search_from = idx
            continue
        candidate = snippet[:end + 1]
        try:
            json.loads(candidate)
            return idx          # valid audit JSON found at this position
        except json.JSONDecodeError:
            pass
        search_from = idx
    return -1


def _strip_audit_json(text: str) -> str:
    idx = _find_audit_json_start(text)
    if idx == -1:
        return text
    return text[:idx].rstrip()


# ── CLAUDE XML DETECTION & FORMATTING ────────────────────────────────────────

_CLAUDE_BLOCK_TAGS = (
    "role", "task", "constraints", "edge_cases",
    "output_format", "quality_bar", "thinking",
)

_CLAUDE_TAG_RE = re.compile(
    r"<(?:role|task|constraints|edge_cases|output_format|quality_bar|thinking)"
    r"(?:\s[^>]*)?>",
    re.IGNORECASE,
)


def _is_claude_xml(text: str) -> bool:
    """True if the text contains ≥2 Claude block-level XML tags."""
    return len(_CLAUDE_TAG_RE.findall(text)) >= 2


def _format_claude_xml(text: str) -> str:
    """
    Return the Claude XML prompt with consistent line breaks between tags.
    Does NOT strip any content — the XML structure is the correct output.
    """
    for tag in _CLAUDE_BLOCK_TAGS:
        # Opening tag → ensure it starts on its own line
        text = re.sub(
            rf"(?<!\n)(<{tag}(?:\s[^>]*)?>)",
            r"\n\1",
            text,
            flags=re.IGNORECASE,
        )
        # Closing tag → ensure it starts on its own line
        text = re.sub(
            rf"(?<!\n)(</{tag}>)",
            r"\n\1",
            text,
            flags=re.IGNORECASE,
        )
    # Collapse excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ── OUTPUT CLEANING ───────────────────────────────────────────────────────────

_LABEL_PREFIX_RE = re.compile(
    r"^(?:REFINED_PROMPT|System\s*Prompt|PROMPT|OUTPUT|thinking)\s*:\s*",
    flags=re.IGNORECASE | re.MULTILINE,
)
_PART_HEADER_RE  = re.compile(r"\*\*\s*PART\s*\d+\s*:[^\n]*\**", re.IGNORECASE)
_AIZEN_RE        = re.compile(r"A\.I\.Z\.E\.N\.[\s\S]*?(?=\n\n|$)", re.IGNORECASE)
_CODE_FENCE_RE   = re.compile(r"```[\s\S]*?```")
_HEADING_RE      = re.compile(r"^\s*#{1,6}\s.*$", re.MULTILINE)
_MULTI_BLANK_RE  = re.compile(r"\n{3,}")
_XML_TAG_RE      = re.compile(r"</?[a-zA-Z_][a-zA-Z0-9_\-]*(?:\s[^>]*)?>")


def extract_clean_output(raw: str) -> str:
    """
    Clean a refined prompt for display and copy.

    CLEAN-1: Claude XML is detected and returned with clean formatting.
             The XML structure IS the correct Claude prompt format —
             stripping it produces an unusable broken output.

    CLEAN-2: Audit JSON stripped via balanced-brace scanner.
             Handles critique strings containing } without early termination.
    """
    t = str(raw or "")

    # CLEAN-2: strip audit JSON block first
    t = _strip_audit_json(t)

    # Strip label prefixes
    m = re.search(r"REFINED_PROMPT\s*:\s*(.+)", t, flags=re.I | re.S)
    if m:
        t = m.group(1)
    t = _LABEL_PREFIX_RE.sub("", t)
    t = _PART_HEADER_RE.sub("", t)
    t = _AIZEN_RE.sub("", t)
    t = _CODE_FENCE_RE.sub("", t)

    # CLEAN-1: detect and format Claude XML — do not strip
    if _is_claude_xml(t):
        return _format_claude_xml(t)

    # Non-Claude: strip any accidentally leaked XML tag brackets
    # (preserve content, remove only the < > brackets and tag names)
    t = _XML_TAG_RE.sub("", t)
    t = _HEADING_RE.sub("", t)
    t = _MULTI_BLANK_RE.sub("\n\n", t)
    return t.strip()


# ── UI COMPONENTS ─────────────────────────────────────────────────────────────

def _audit_score_component(audit: dict) -> None:
    score      = audit.get("score",      0)
    precision  = audit.get("precision",  0)
    alignment  = audit.get("alignment",  0)
    efficiency = audit.get("efficiency", 0)
    critique   = audit.get("critique",   "")

    if score >= 85:
        score_color, score_label = "#4CAF9A", "HIGH FIDELITY"
    elif score >= 70:
        score_color, score_label = "var(--gold, #C9A84C)", "ACCEPTABLE"
    else:
        score_color, score_label = "#E57373", "NEEDS WORK"

    prec_pct  = int((precision  / 40) * 100)
    align_pct = int((alignment  / 40) * 100)
    effic_pct = int((efficiency / 20) * 100)


    audit_html = f"""
<div style="display:flex;align-items:center;gap:16px;padding:10px 14px;
            background:rgba(0,0,0,0.3);border:1px solid rgba(255,255,255,0.05);
            border-radius:4px;margin-bottom:14px;flex-wrap:wrap;">
    <div style="display:flex;flex-direction:column;align-items:center;
                padding-right:16px;border-right:1px solid rgba(255,255,255,0.06);">
        <div style="font-family:'Cinzel',Georgia,serif;font-size:1.4rem;
                    line-height:1;color:{score_color};">{score}</div>
        <div style="font-family:'IBM Plex Mono',monospace;font-size:8px;
                    color:{score_color};letter-spacing:0.15em;margin-top:2px;">
            {score_label}
        </div>
    </div>
    <div style="display:flex;gap:20px;flex-wrap:wrap;">
        <div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                        color:rgba(93,109,126,1);letter-spacing:0.1em;
                        text-transform:uppercase;margin-bottom:2px;">Precision</div>
            <div style="height:3px;border-radius:1px;background:rgba(255,255,255,0.05);
                        width:80px;overflow:hidden;">
                <div style="height:100%;width:{prec_pct}%;border-radius:1px;
                             background:#7C9EBF;"></div>
            </div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                        color:#7C9EBF;margin-top:2px;">{precision}/40</div>
        </div>
        <div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                        color:rgba(93,109,126,1);letter-spacing:0.1em;
                        text-transform:uppercase;margin-bottom:2px;">Alignment</div>
            <div style="height:3px;border-radius:1px;background:rgba(255,255,255,0.05);
                        width:80px;overflow:hidden;">
                <div style="height:100%;width:{align_pct}%;border-radius:1px;
                             background:#C9A84C;"></div>
            </div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                        color:#C9A84C;margin-top:2px;">{alignment}/40</div>
        </div>
        <div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                        color:rgba(93,109,126,1);letter-spacing:0.1em;
                        text-transform:uppercase;margin-bottom:2px;">Efficiency</div>
            <div style="height:3px;border-radius:1px;background:rgba(255,255,255,0.05);
                        width:80px;overflow:hidden;">
                <div style="height:100%;width:{effic_pct}%;border-radius:1px;
                             background:#4CAF9A;"></div>
            </div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                        color:#4CAF9A;margin-top:2px;">{efficiency}/20</div>
        </div>
    </div>
    <div style="margin-left:auto;">
        <div style="display:inline-flex;align-items:center;gap:5px;padding:2px 8px;
                    background:rgba(124,158,191,0.08);border:1px solid rgba(124,158,191,0.2);
                    border-radius:100px;font-family:'IBM Plex Mono',monospace;
                    font-size:10px;color:#7C9EBF;">
            ❖ {st.session_state.get(K.AUTO_TARGET, "—")}
        </div>
    </div>
</div>
"""
    if critique:
        audit_html += (
            f'<div style="font-family:\'IBM Plex Mono\',monospace;font-size:11px;'
            f'color:rgba(93,109,126,1);padding:8px 14px;background:rgba(0,0,0,0.2);'
            f'border-radius:4px;margin-bottom:10px;">✦ {critique}</div>'
        )

    st.markdown(audit_html, unsafe_allow_html=True)


def _copy_to_clipboard_btn(text: str, key: str) -> None:
    escaped = (
        text
        .replace("\\", "\\\\")
        .replace("`",  "\\`")
        .replace("\n", "\\n")
        .replace("\r", "")
    )
    components.html(f"""
    <style>
        .copy-btn {{
            background:rgba(255,255,255,0.02);
            border:1px solid rgba(255,255,255,0.08);
            color:#7C9EBF;
            font-family:'IBM Plex Mono',monospace;
            font-size:10px;letter-spacing:0.1em;
            padding:5px 14px;border-radius:2px;
            cursor:pointer;transition:all 0.2s ease;
        }}
        .copy-btn:hover {{ border-color:rgba(124,158,191,0.4);color:#B0C4DE; }}
        .copy-btn.copied {{ border-color:rgba(76,175,154,0.4);color:#4CAF9A; }}
    </style>
    <button class="copy-btn" id="copy_{key}"
            onclick="
                navigator.clipboard.writeText(`{escaped}`).then(() => {{
                    const btn = document.getElementById('copy_{key}');
                    btn.textContent = '✓  COPIED';
                    btn.classList.add('copied');
                    setTimeout(() => {{
                        btn.textContent = '📋  COPY';
                        btn.classList.remove('copied');
                    }}, 2000);
                }});
            ">📋&nbsp;&nbsp;COPY</button>
    """, height=40)


# ── VAULT SAVE ────────────────────────────────────────────────────────────────

def _save_to_vault(user_hash: str, output: str, audit: dict, cfg: dict) -> None:
    score = (audit or {}).get("score", 0)
    title = (st.session_state.get(K.LAST_INPUT) or "Untitled")[:80]

    try:
        record, err = save_prompt(
            user_hash,
            title     = title,
            tags      = st.session_state.get(K.AUTO_TARGET, "").lower(),
            content   = output,
            target    = st.session_state.get(K.AUTO_TARGET, "ChatGPT"),
            framework = cfg.get("framework", "RACE"),
            score     = score,
            aesthetic = cfg.get("aesthetic_choice", "Default"),
            intent    = st.session_state.get(K.LAST_INPUT, ""),
        )
    except Exception as exc:
        _save_local_fallback(output, title, score)
        st.warning(
            f"Vault unreachable ({type(exc).__name__}: {exc}). "
            "Saved to local session instead."
        )
        return

    if err:
        st.error(f"Vault save failed: {err}\n\nSaved to local session as fallback.")
        _save_local_fallback(output, title, score)
        return

    st.success("✓  Saved to Vault.")
    st.session_state["_archive_cache_dirty"] = True


def _save_local_fallback(output: str, title: str, score: int) -> None:
    items = st.session_state.get("local_vault_items", [])
    items.append({
        "title":    title,
        "content":  output,
        "score":    score,
        "target":   st.session_state.get(K.AUTO_TARGET, ""),
        "saved_at": datetime.now(UTC).isoformat(),
        "local":    True,
    })
    st.session_state["local_vault_items"] = items


# ── STREAMING PIPELINE ────────────────────────────────────────────────────────

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
            "Remove injection or override patterns and try again."
        )
        return

    if not check_rate_limit():
        remaining_secs = 60
        st.warning(
            f"Rate limit reached — maximum 10 refinements per minute. "
            f"Please wait {remaining_secs}s before trying again."
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

    selected = cfg.get("target_model", AUTO_SELECT_LABEL)
    if selected == AUTO_SELECT_LABEL:
        resolved_target, routing_reason = resolve_target_model(
            AUTO_SELECT_LABEL, cleaned
        )
    else:
        resolved_target = selected
        routing_reason  = "Manual selection"

    st.session_state[K.AUTO_TARGET] = resolved_target
    st.session_state[K.AUTO_REASON] = routing_reason

    cfg_with_target = {**cfg, "target_model": resolved_target}
    payload = assemble_master_payload(
        f"{cleaned}\n\n{control_block}",
        cfg_with_target,
        dna_ctx,
    )

    t0     = time.time()
    result = {}

    # ── Silent accumulation — user never sees raw tokens ──────────────────────
    # stream_refinement() is a generator. We consume it silently here — tokens
    # accumulate in the result dict but are never rendered to the page.
    # After all tokens are consumed, we commit session state and call st.rerun().
    # The rerun wipes the spinner and renders the clean output panel from state.
    # This is the only approach that guarantees the user sees ONLY the final
    # clean prompt — no XML tags, no JSON audit block, no partial output.
    with st.spinner(""):
        for _ in stream_refinement(
            master_payload   = payload,
            intent           = cleaned,
            target           = resolved_target,
            framework        = cfg.get("framework", "RACE"),
            lang             = cfg.get("source_lang", "English"),
            aesthetic_choice = cfg.get("aesthetic_choice", "Default"),
            hikmah_style     = str(cfg.get("hikmah_style") or "None"),
            skip_security    = True,
            result           = result,
        ):
            pass   # tokens accumulate in result dict; not rendered

    latency_ms  = int((time.time() - t0) * 1000)
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

    # Commit all session state BEFORE rerun
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
        "title":      clean[:40],
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
        "icon":       "\u2756",
        "pattern":    "RAW",
        "palette":    [],
    })
    st.session_state[K.HISTORY] = history[-50:]

    # Rerun: wipes spinner, renders clean output panel from session state
    st.rerun()


# ── RENDERER ─────────────────────────────────────────────────────────────────

def render_workspace(cfg: dict) -> None:

    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;
                font-family:'IBM Plex Mono',monospace;font-size:0.7rem;
                color:#C9A84C;letter-spacing:0.2em;text-transform:uppercase;
                border-bottom:1px solid rgba(201,168,76,0.15);
                padding-bottom:12px;margin-bottom:20px;">
        <span style="width:7px;height:7px;border-radius:50%;background:#C9A84C;
                     box-shadow:0 0 6px #C9A84C;display:inline-block;
                     flex-shrink:0;"></span>
        WORKSPACE
        <span style="margin-left:auto;font-size:9px;color:rgba(44,53,69,1);
                     letter-spacing:0.1em;">مساحة العمل</span>
    </div>
    """, unsafe_allow_html=True)

    if "workspace_text" not in st.session_state:
        st.session_state["workspace_text"] = st.session_state.get(K.LAST_INPUT, "")

    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                color:rgba(44,53,69,1);letter-spacing:0.15em;
                text-transform:uppercase;margin-bottom:8px;">
        Quick examples
    </div>
    """, unsafe_allow_html=True)

    chip_cols     = st.columns(4)
    example_texts = [
        "Write an article about AI in education",
        "اكتب مقالاً عن الذكاء الاصطناعي في التعليم",
        "Write marketing copy for a productivity app",
        "اكتب رسالة متابعة احترافية لعميل",
    ]
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

    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                color:rgba(44,53,69,1);letter-spacing:0.2em;
                text-transform:uppercase;margin-bottom:6px;">
        [ 01 ]  SOURCE INTENT
    </div>
    """, unsafe_allow_html=True)

    source = st.text_area(
        "source_prompt",
        value       = st.session_state["workspace_text"],
        height      = 200,
        placeholder = (
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
        pct       = int((char_count / INPUT_MAX_CHARS) * 100)
        bar_color = "#C9A84C" if char_count > 1500 else "#7C9EBF"
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;align-items:center;
                    margin-top:-8px;margin-bottom:8px;">
            <div style="flex:1;height:2px;background:rgba(255,255,255,0.04);
                        border-radius:1px;overflow:hidden;margin-right:10px;">
                <div style="height:100%;width:{pct}%;background:{bar_color};
                             transition:width 0.3s ease;"></div>
            </div>
            <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                        color:rgba(44,53,69,1);white-space:nowrap;">
                {char_count:,} / {INPUT_MAX_CHARS:,}
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                color:rgba(44,53,69,1);letter-spacing:0.2em;
                text-transform:uppercase;margin-bottom:6px;margin-top:4px;">
        [ 02 ]  REFINEMENT CONTROLS
    </div>
    """, unsafe_allow_html=True)

    ctrl1, ctrl2, ctrl3 = st.columns(3)
    with ctrl1: tone       = st.slider("Tone",       0, 100, 50, key="sl_tone")
    with ctrl2: length     = st.slider("Length",     0, 100, 50, key="sl_length")
    with ctrl3: creativity = st.slider("Creativity", 0, 100, 50, key="sl_creativity")

    aud_col, _, run_col = st.columns([2, 1, 1])
    with aud_col:
        audience = st.selectbox(
            "Audience", AUDIENCE_OPTIONS, label_visibility="collapsed"
        )
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

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    output = st.session_state.get(K.LAST_RESULT)
    audit  = st.session_state.get(K.LAST_AUDIT, {})

    if not output:
        st.markdown("""
        <div style="border:1px dashed rgba(255,255,255,0.06);border-radius:8px;
                    padding:40px 20px;text-align:center;margin-top:8px;">
            <div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
                        color:rgba(44,53,69,1);letter-spacing:0.15em;
                        text-transform:uppercase;">
                [ ❖ ]  Refined output will appear here
            </div>
            <div style="font-family:'Cairo',serif;font-size:12px;
                        color:rgba(44,53,69,1);margin-top:6px;opacity:0.5;">
                سيظهر الناتج المحسّن هنا
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    st.markdown("""
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
        <div style="font-family:'IBM Plex Mono',monospace;font-size:9px;
                    color:#C9A84C;letter-spacing:0.2em;text-transform:uppercase;">
            [ 03 ]  REFINED OUTPUT
        </div>
        <div style="flex:1;height:1px;background:linear-gradient(90deg,
                    rgba(201,168,76,0.28),transparent);"></div>
    </div>
    """, unsafe_allow_html=True)

    _audit_score_component(audit)

    st.text_area(
        "refined_output",
        value            = output,
        height           = 320,
        key              = "output_area",
        label_visibility = "collapsed",
    )

    words   = len(output.split())
    chars   = len(output)
    minutes = max(1, round(words / 200))
    history = st.session_state.get(K.HISTORY, [])
    latency = history[-1].get("latency", "") if history else ""

    st.markdown(f"""
    <div style="display:flex;gap:16px;flex-wrap:wrap;font-family:'IBM Plex Mono',monospace;
                font-size:10px;color:rgba(44,53,69,1);margin-top:-4px;margin-bottom:14px;">
        <span>📄 {words:,} words</span>
        <span>Aa {chars:,} chars</span>
        <span>⏱ ~{minutes} min read</span>
        {"<span>⚡ " + latency + "</span>" if latency else ""}
    </div>
    """, unsafe_allow_html=True)

    copy_col, save_col, _ = st.columns([1, 1, 2])

    with copy_col:
        _copy_to_clipboard_btn(output, key="main_output")

    with save_col:
        user_hash = st.session_state.get(K.USER_HASH, "")
        is_guest  = not user_hash or "GUEST_" in str(user_hash).upper()

        if is_guest:
            st.markdown("""
            <div style="font-family:'IBM Plex Mono',monospace;font-size:10px;
                        color:rgba(44,53,69,1);padding:5px 0;">
                Login to save to Vault
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button(
                "💾  Save to Vault",
                use_container_width = True,
                key                 = "vault_save_btn",
            ):
                _save_to_vault(user_hash, output, audit, cfg)
