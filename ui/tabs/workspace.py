"""
ui/tabs/workspace.py — Premium Studio
=======================================
v4.0: Gold design system. Matches mockup.
      - Time-based greeting
      - Stacked before/after cards with connector
      - Copy / Share / Re-ink action row
      - Recent inks history list
      - Fixed bottom input bar (pill style)
      - Quick action pills
      - Live pipeline animation
"""
from __future__ import annotations
import re, time
from datetime import datetime, timezone, timedelta
from typing import Dict

import streamlit as st
from state import K
from security.sanitizer import sanitize_input
from engine.refiner import run_refinement_and_audit
from forge.prompt_assembler import assemble_master_payload
from forge.intelligence import resolve_target_model
from vault.supabase_client import SUPABASE_MISSING
from vault.vault_engine import save_prompt

WAT_TZ          = timezone(timedelta(hours=1))
LOCAL_VAULT_KEY = "local_vault_items"

TARGET_MODELS = [
    ("✦ AUTO-SELECT", "auto"),
    ("ChatGPT",       "chatgpt"),
    ("Claude",        "claude"),
    ("Gemini",        "gemini"),
    ("Midjourney",    "midjourney"),
    ("DALL·E",        "dalle"),
    ("FLUX",          "flux"),
]

QUICK_ACTIONS = [
    ("🖊", "Refine",   "Refine and improve the following prompt:\n\n"),
    ("💡", "Expand",   "Expand this prompt with more detail, context, and specificity:\n\n"),
    ("🎯", "Focus",    "Make this prompt more focused and precise. Remove vagueness:\n\n"),
    ("⚙️", "Adjust",   "Adjust this prompt for a professional audience with clear structure:\n\n"),
]

ROTATING_QUOTES = [
    "A great prompt is architecture, not words.",
    "الكلمة الصحيحة تغيّر كل شيء",
    "Precision is the highest form of intelligence.",
    "الوضوح قوة — clarity is power.",
    "The best prompt anticipates the answer.",
    "حبر وفكرة — ink and idea, refined.",
]

PIPELINE_STEPS = [
    ("Analyzing prompt structure",        "Mapping clauses and ambiguity..."),
    ("Detecting intent & target model",   "Resolving best model path..."),
    ("Applying CIPHER identity layer",    "Injecting role and guardrails..."),
    ("Assembling forge & persona layers", "Applying rhetoric and DNA..."),
    ("Running primary refiner loop",      "Executing refinement passes..."),
    ("Evaluator audit — scoring output",  "Scoring clarity and alignment..."),
    ("Security & sanitizer scan",         "Verifying clean output..."),
    ("Finalizing refined prompt",         "Packaging final output..."),
]

# Arabic thumbnail letters for history items
_AR_THUMBS = ["خلق", "فكر", "كتب", "نور", "حبر", "علم", "إبد", "صنع"]


# ────────────────────────────────────────────────
# HELPERS
# ────────────────────────────────────────────────

def _get_dna_context() -> dict:
    return {
        K.INK_DNA:    str(st.session_state.get(K.INK_DNA)    or ""),
        K.INTEL_DNA:  str(st.session_state.get(K.INTEL_DNA)  or ""),
        K.HIKMAH_DNA: str(st.session_state.get(K.HIKMAH_DNA) or ""),
    }


def extract_clean_output(raw: str) -> str:
    t = str(raw or "")
    t = re.sub(r"\*\*\s*PART\s*\d+\s*:.*?(?=\*\*\s*PART\s*\d+\s*:|$)", "", t, flags=re.I | re.S)
    t = re.sub(
        r"(?:Claude|GPT|ChatGPT|Gemini|DALL-?E|Midjourney|FLUX|OpenAI)"
        r"\s*(?:Target\s*)?Prompt\s*:\s*", "", t, flags=re.I,
    )
    t = re.sub(r"A\.I\.Z\.E\.N\..*?(?:InkOS\.|(?=\n\n))", "", t, flags=re.I | re.S)
    t = re.sub(r"You are a highly advanced.*?(?:InkOS\.|(?=\n\n))", "", t, flags=re.I | re.S)
    for tag in ("quality-bar","edge-cases","constraints","quality_bar",
                "edge_cases","role","task","visual-aesthetic",
                "strategic-focus","philosophical-bounds"):
        t = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", t, flags=re.I | re.S)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"```[\s\S]*?```", "", t)
    t = re.sub(r"\{[^{}]{0,800}\}", "", t)
    t = re.sub(r"^\s*#{1,6}\s.*$", "", t, flags=re.M)
    t = t.replace("**", "").replace("__", "")
    t = re.sub(
        r"^(?:System\s*Prompt|REFINED_PROMPT|PROMPT|OUTPUT|thinking|"
        r"Refined\s*Prompt|Final\s*Prompt|User\s*Prompt)\s*:\s*",
        "", t, flags=re.I | re.M,
    )
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _greeting() -> tuple:
    hour = datetime.now(WAT_TZ).hour
    if hour < 12:
        return "Good morning.", "Let's craft something exceptional."
    elif hour < 17:
        return "Good afternoon.", "Ready to refine something great?"
    else:
        return "Good evening.", "Let's ink something remarkable."


def _word_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0


def _thumb_for(idx: int, text: str) -> str:
    """Pick an Arabic thumbnail letter based on index."""
    return _AR_THUMBS[idx % len(_AR_THUMBS)]


def _save_local(uid: str, title: str, tags: str, cfg: dict) -> None:
    items = st.session_state.get(LOCAL_VAULT_KEY, [])
    items.insert(0, {
        "id":         f"local-{int(time.time()*1000)}",
        "user_hash":  uid,
        "title":      title,
        "tags":       tags,
        "content":    st.session_state.get(K.LAST_RESULT, ""),
        "target":     st.session_state.get(K.AUTO_TARGET, "ChatGPT"),
        "framework":  cfg.get("framework", ""),
        "score":      (st.session_state.get(K.LAST_AUDIT) or {}).get("score", 0),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    st.session_state[LOCAL_VAULT_KEY] = items[:200]


# ────────────────────────────────────────────────
# PIPELINE ANIMATION
# ────────────────────────────────────────────────

def _run_pipeline(payload, cfg: dict, cleaned: str):
    quote = ROTATING_QUOTES[int(time.time() / 4) % len(ROTATING_QUOTES)]
    container = st.empty()

    def _render(step_idx: int):
        steps_html = ""
        for j, (name, desc) in enumerate(PIPELINE_STEPS):
            if j < step_idx:
                icon, color, alpha = "✓", "#4ade80", "1"
                border = "border-left:3px solid #4ade8022;"
                bg, sub = "", ""
            elif j == step_idx:
                icon, color, alpha = "⟳", "#c9a84c", "1"
                border = "border-left:3px solid #c9a84c;"
                bg  = "background:#c9a84c08;"
                sub = f"<div style='font-size:11px;color:#8a8070;margin-top:2px;'>{desc}</div>"
            else:
                icon, color, alpha = "○", "#4a4535", "0.4"
                border, bg, sub = "border-left:3px solid transparent;", "", ""

            steps_html += f"""
            <div style='display:flex;align-items:flex-start;gap:12px;
                        padding:9px 14px;border-radius:0 8px 8px 0;
                        margin-bottom:3px;opacity:{alpha};{border}{bg}'>
              <span style='font-size:14px;color:{color};width:18px;
                           text-align:center;flex-shrink:0;'>{icon}</span>
              <div>
                <div style='font-size:13px;font-family:"JetBrains Mono",monospace;
                            color:{"#f5f0e8" if j <= step_idx else "#4a4535"};'>{name}</div>
                {sub}
              </div>
            </div>"""

        pct = int((step_idx / len(PIPELINE_STEPS)) * 100)
        container.markdown(f"""
        <div style='background:#1a1825;border:1px solid #c9a84c33;
                    border-radius:20px;padding:28px 24px;
                    max-width:500px;margin:20px auto 140px;
                    box-shadow:0 8px 32px #00000050;'>
          <div style='display:flex;justify-content:space-between;
                      align-items:center;margin-bottom:20px;'>
            <span style='font-size:11px;font-family:"JetBrains Mono",monospace;
                         color:#c9a84c;letter-spacing:.12em;'>✦ CIPHER ENGINE — REFINING</span>
            <span style='font-size:11px;font-family:monospace;color:#8a8070;'>
              {step_idx + 1}/{len(PIPELINE_STEPS)}
            </span>
          </div>
          <div style='background:#0f0e17;border-radius:999px;height:3px;
                      margin-bottom:24px;overflow:hidden;'>
            <div style='width:{pct}%;height:3px;border-radius:999px;
                        background:linear-gradient(90deg,#c9a84c,#e8c97a);
                        box-shadow:0 0 8px #c9a84c50;
                        transition:width .3s ease;'></div>
          </div>
          {steps_html}
          <div style='margin-top:20px;padding-top:14px;
                      border-top:1px solid #c9a84c15;text-align:center;
                      font-size:12px;font-style:italic;color:#4a4535;'>
            "{quote}"
          </div>
        </div>
        """, unsafe_allow_html=True)

    for i in range(6):
        _render(i)
        time.sleep(0.28)

    _render(6)
    result, audit, _ = run_refinement_and_audit(
        payload,
        resolve_target_model(cfg.get("target_model"), cleaned)[0],
        cfg["framework"],
        cfg["source_lang"],
        cfg["aesthetic_choice"],
        hikmah_style=str(cfg.get("hikmah_style") or "None"),
        skip_security=False,
    )

    _render(7)
    time.sleep(0.18)
    container.empty()
    return result, audit


# ────────────────────────────────────────────────
# RENDER COMPONENTS
# ────────────────────────────────────────────────

def _render_greeting():
    main_text, sub_text = _greeting()
    st.markdown(f"""
    <div class='ws-greeting'>
      <div class='ws-greeting-main'>{main_text}</div>
      <div class='ws-greeting-sub'>{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)


def _render_model_picker():
    selected = st.session_state.get("selected_model_label", "✦ AUTO-SELECT")
    st.markdown("""
    <div style='font-size:10px;font-family:"JetBrains Mono",monospace;
                color:#c9a84c;letter-spacing:.1em;margin-bottom:10px;'>
      SELECT TARGET MODEL
    </div>
    """, unsafe_allow_html=True)
    for label, value in TARGET_MODELS:
        is_active = selected == label
        if st.button(
            ("✓  " if is_active else "    ") + label,
            key=f"mpick_{value}",
            use_container_width=True,
        ):
            st.session_state["selected_model_label"] = label
            st.session_state["selected_model_value"] = value
            st.session_state["show_model_picker"]    = False
            st.rerun()


def _render_stacked_cards():
    """Render before/after stacked cards with connector — matching mockup."""
    raw_input = st.session_state.get(K.LAST_INPUT, "")
    result    = st.session_state.get(K.LAST_RESULT, "")
    audit     = st.session_state.get(K.LAST_AUDIT) or {}
    score     = audit.get("score", 0)

    if score >= 80:   badge = "✦ Excellent"
    elif score >= 60: badge = "✦ Good"
    else:             badge = "✦ Refined"

    in_words  = _word_count(raw_input)
    out_words = _word_count(result)

    # ── Original Prompt Card ──
    st.markdown(f"""
    <div class='prompt-card'>
      <div class='prompt-card-header'>
        <div class='prompt-card-label'>
          <div class='prompt-card-icon'>🖊</div>
          Original Prompt
        </div>
        <span style='font-size:12px;color:#c9a84c;cursor:pointer;'>Edit ✏</span>
      </div>
      <div class='prompt-card-text'>{raw_input}</div>
      <div class='prompt-card-meta'>{in_words} words</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Connector ──
    st.markdown("""
    <div class='card-connector'>
      <div class='card-connector-dot'>✦</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Refined Ink Card ──
    st.markdown(f"""
    <div class='refined-card'>
      <div class='refined-card-header'>
        <div class='refined-card-label'>
          <div class='refined-card-icon'>✦</div>
          Refined Ink
        </div>
        <div class='refined-badge'>✦ {badge}</div>
      </div>
      <div class='refined-card-text'>{result}</div>
      <div class='refined-card-divider'></div>
      <div class='refined-card-meta'>{out_words} words</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── Action Row ── Copy / Share / Re-ink
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⎘  Copy", key="act_copy", use_container_width=True):
            st.session_state["act_copied"] = True
            st.rerun()
    with c2:
        st.button("↗  Share", key="act_share", use_container_width=True)
    with c3:
        if st.button("↺  Re-ink", key="act_reink", use_container_width=True):
            # Re-run refinement on same input
            st.session_state["prefill_input"] = raw_input
            st.session_state[K.LAST_RESULT]   = None
            st.session_state[K.LAST_INPUT]    = ""
            st.rerun()

    if st.session_state.pop("act_copied", False):
        st.markdown("""
        <div style='text-align:center;font-size:12px;color:#4ade80;
                    padding:6px;font-family:"JetBrains Mono",monospace;'>
          ✓ Copied to clipboard
        </div>
        """, unsafe_allow_html=True)

    # ── Vault Save ──
    with st.expander("🔒  Save to Vault", expanded=False):
        st.text_input("Designation", placeholder="Name this prompt...", key="v_t")
        st.text_input("Tags", placeholder="e.g. blog, ai, arabic", key="v_g")
        if st.button("⚡ Secure to Vault", type="primary",
                     use_container_width=True, key="btn_vault"):
            uid       = st.session_state.get(K.USER_HASH)
            title_val = st.session_state.get("v_t", "").strip()
            tags_val  = st.session_state.get("v_g", "").strip()
            if not title_val:
                st.error("⚠ Add a designation first.")
            elif not uid or "GUEST_" in str(uid).upper():
                st.error("⚠ Please log in to use the Vault.")
            else:
                if SUPABASE_MISSING:
                    _save_local(uid, title_val, tags_val, {})
                    st.success("✓ Saved locally")
                else:
                    _, err = save_prompt(
                        uid, title=title_val, tags=tags_val,
                        content=result,
                        target=st.session_state.get(K.AUTO_TARGET),
                        framework="",
                        score=score,
                    )
                    if err:
                        st.error(f"⚠ {err}")
                    else:
                        st.success("✓ Secured to Vault")


def _render_recent_inks():
    """Recent inks history list — matching mockup."""
    history = st.session_state.get(K.HISTORY, [])
    if not history:
        return

    st.markdown("""
    <div class='section-header'>
      <div class='section-title'>Recent Inks</div>
      <div class='section-link'>View all ›</div>
    </div>
    """, unsafe_allow_html=True)

    for idx, entry in enumerate(reversed(history[-6:])):
        user_msg = entry.get("input", "")
        bot_msg  = entry.get("output", "")
        ts       = entry.get("time", "")
        thumb    = _thumb_for(idx, user_msg)

        # Format date
        try:
            dt = datetime.fromisoformat(ts)
            date_str = dt.strftime("%b %d, %Y")
        except Exception:
            date_str = ""

        title   = user_msg[:48] + ("..." if len(user_msg) > 48 else "")
        preview = bot_msg[:80] + ("..." if len(bot_msg) > 80 else "")

        st.markdown(f"""
        <div class='ink-item'>
          <div class='ink-thumb'>{thumb}</div>
          <div class='ink-content'>
            <div class='ink-title'>{title}</div>
            <div class='ink-preview'>{preview}</div>
          </div>
          <div style='display:flex;flex-direction:column;
                      align-items:flex-end;gap:8px;'>
            <div class='ink-date'>{date_str}</div>
            <div style='color:#4a4535;font-size:16px;cursor:pointer;'>⋯</div>
          </div>
        </div>
        """, unsafe_allow_html=True)


def _render_empty_state():
    st.markdown("""
    <div class='empty-state' style='padding:60px 24px;'>
      <div style='font-size:36px;margin-bottom:16px;opacity:.2;'>✦</div>
      <div class='en'>Refine your thoughts.<br>Ink with clarity.</div>
      <div style='height:12px'></div>
      <div class='ar'>حبر وفكرة</div>
    </div>
    """, unsafe_allow_html=True)


# ────────────────────────────────────────────────
# MAIN ENTRY POINT
# ────────────────────────────────────────────────

def render_workspace(cfg: dict) -> None:

    # ── Layout CSS override ──
    st.markdown("""
    <style>
    .main .block-container {
      padding-bottom: 150px !important;
      padding-top:    0 !important;
      max-width:      640px !important;
      margin:         0 auto !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Greeting ──
    _render_greeting()

    # ── Model picker overlay ──
    if st.session_state.get("show_model_picker"):
        with st.container():
            st.markdown("""
            <div style='background:#1a1825;border:1px solid #c9a84c33;
                        border-radius:16px;padding:16px;
                        max-width:240px;margin-bottom:12px;
                        box-shadow:0 8px 32px #00000060;'>
            """, unsafe_allow_html=True)
            _render_model_picker()
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Quick action pills (when no result) ──
    if not st.session_state.get(K.LAST_RESULT):
        qa_cols = st.columns(4)
        for i, (icon, label, starter) in enumerate(QUICK_ACTIONS):
            with qa_cols[i]:
                if st.button(f"{icon} {label}", key=f"qa_{i}",
                             use_container_width=True):
                    st.session_state["prefill_input"] = starter
                    st.rerun()
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Content area ──
    if st.session_state.get(K.LAST_RESULT):
        _render_stacked_cards()
        _render_recent_inks()
    else:
        if st.session_state.get(K.HISTORY):
            _render_recent_inks()
        else:
            _render_empty_state()

    # ── Selected model chip ──
    selected_label = st.session_state.get("selected_model_label", "AUTO-SELECT")
    chip = selected_label.replace("✦ ", "")
    st.markdown(f"""
    <div style='position:fixed;bottom:88px;
                left:50%;transform:translateX(-50%);
                z-index:999;'>
      <span style='background:#1a1825;border:1px solid #c9a84c33;
                   border-radius:999px;padding:3px 12px;
                   font-size:11px;color:#c9a84c;
                   font-family:"JetBrains Mono",monospace;
                   box-shadow:0 2px 12px #00000040;'>
        ✦ {chip}
      </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Fixed bottom input bar ──
    st.markdown("<div id='ws-bar'>", unsafe_allow_html=True)

    col_plus, col_input, col_mic, col_send = st.columns([1, 12, 1, 1])

    with col_plus:
        if st.button("＋", key="btn_plus", help="Select model"):
            st.session_state["show_model_picker"] = not st.session_state.get(
                "show_model_picker", False)
            st.rerun()

    with col_input:
        prefill    = st.session_state.pop("prefill_input", "")
        intent_val = st.text_area(
            "prompt",
            value=prefill,
            height=48,
            placeholder="Draft your prompt...",
            label_visibility="collapsed",
            key="ws_input",
        )

    with col_mic:
        st.button("🎤", key="btn_mic", help="Voice input")

    with col_send:
        has_text = bool((intent_val or "").strip())
        if has_text:
            send = st.button("→", key="btn_send", type="primary")
        else:
            st.markdown("<div style='width:40px;height:40px'></div>",
                        unsafe_allow_html=True)
            send = False

    st.markdown("</div>", unsafe_allow_html=True)

    # ── Handle send ──
    if send and intent_val and intent_val.strip():
        cleaned, violations = sanitize_input(intent_val)
        if violations:
            st.error("⚠ Input blocked by security policy.")
            return

        run_cfg   = dict(cfg)
        model_val = st.session_state.get("selected_model_value", "auto")
        if model_val != "auto":
            run_cfg["target_model"] = model_val

        payload       = assemble_master_payload(cleaned, run_cfg, _get_dna_context())
        result, audit = _run_pipeline(payload, run_cfg, cleaned)
        result        = extract_clean_output(result)
        score         = (audit or {}).get("score", 0)

        history = st.session_state.get(K.HISTORY, [])
        history.append({
            "input":  cleaned,
            "output": result,
            "score":  score,
            "time":   datetime.now(WAT_TZ).isoformat(),
        })
        st.session_state[K.HISTORY]     = history[-50:]
        st.session_state[K.LAST_RESULT] = result
        st.session_state[K.LAST_AUDIT]  = audit
        st.session_state[K.LAST_INPUT]  = cleaned
        st.rerun()
