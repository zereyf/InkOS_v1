from __future__ import annotations
import re, time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

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

# ── Target models shown in + picker ──
TARGET_MODELS = [
    ("✦ AUTO-SELECT",  "auto"),
    ("ChatGPT",        "chatgpt"),
    ("Claude",         "claude"),
    ("Gemini",         "gemini"),
    ("Midjourney",     "midjourney"),
    ("DALL·E",         "dalle"),
    ("FLUX",           "flux"),
]

# ── Quick actions ──
QUICK_ACTIONS = [
    ("⚡", "Refine a prompt",    "Refine and improve the following prompt:\n\n"),
    ("🎭", "Apply a persona",    "Apply a persona to this prompt. Target audience: [audience]. Tone: [tone]. Goal: [goal].\n\nPrompt:\n"),
    ("🔒", "Secure to vault",    "Write a production-ready prompt that I can save to my vault for reuse:\n\n"),
    ("🧠", "Build from template","Create a complete, detailed prompt for the following use case:\n\n"),
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
    ("Analyzing prompt structure",        "Mapping clauses, constraints, and ambiguity..."),
    ("Detecting intent & target model",   "Resolving best model path for the mission..."),
    ("Applying CIPHER identity layer",    "Injecting role, guardrails, and objective spine..."),
    ("Assembling forge & persona layers", "Applying rhetoric and DNA layers..."),
    ("Running primary refiner loop",      "Executing refinement passes with evaluator gates..."),
    ("Evaluator audit — scoring output",  "Scoring clarity, specificity, and actionability..."),
    ("Security & sanitizer scan",         "Verifying clean output and safety posture..."),
    ("Finalizing refined prompt",         "Packaging final output and telemetry..."),
]


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
    """Strip ALL internal structure — return only the clean user-facing prompt."""
    t = str(raw or "")
    # PART blocks
    t = re.sub(r"\*\*\s*PART\s*\d+\s*:.*?(?=\*\*\s*PART\s*\d+\s*:|$)", "", t, flags=re.I | re.S)
    # Target prompt headers
    t = re.sub(
        r"(?:Claude|GPT|ChatGPT|Gemini|DALL-?E|Midjourney|FLUX|OpenAI)"
        r"\s*(?:Target\s*)?Prompt\s*:\s*",
        "", t, flags=re.I,
    )
    # AIZEN / identity blocks
    t = re.sub(r"A\.I\.Z\.E\.N\..*?(?:InkOS\.|(?=\n\n))", "", t, flags=re.I | re.S)
    t = re.sub(r"You are a highly advanced.*?(?:InkOS\.|(?=\n\n))", "", t, flags=re.I | re.S)
    # XML tags
    for tag in ("quality-bar","edge-cases","constraints","quality_bar",
                "edge_cases","role","task","visual-aesthetic",
                "strategic-focus","philosophical-bounds"):
        t = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", t, flags=re.I | re.S)
    t = re.sub(r"<[^>]+>", "", t)
    # Code / JSON
    t = re.sub(r"```[\s\S]*?```", "", t)
    t = re.sub(r"\{[^{}]{0,800}\}", "", t)
    # Markdown
    t = re.sub(r"^\s*#{1,6}\s.*$", "", t, flags=re.M)
    t = t.replace("**", "").replace("__", "")
    # Label prefixes
    t = re.sub(
        r"^(?:System\s*Prompt|REFINED_PROMPT|PROMPT|OUTPUT|thinking|"
        r"Refined\s*Prompt|Final\s*Prompt|User\s*Prompt)\s*:\s*",
        "", t, flags=re.I | re.M,
    )
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def _score_label(audit: dict) -> tuple:
    score = (audit or {}).get("score", 0)
    if score >= 80:   return "Excellent", "#22c55e"
    elif score >= 60: return "Good",      "#f59e0b"
    else:             return "Fair",      "#ef4444"


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
    """Show live pipeline animation while running refinement."""
    quote = ROTATING_QUOTES[int(time.time() / 4) % len(ROTATING_QUOTES)]
    container = st.empty()

    def _render(step_idx: int):
        steps_html = ""
        for j, (name, desc) in enumerate(PIPELINE_STEPS):
            if j < step_idx:
                icon, color, alpha = "✓", "#22c55e", "1"
                border, bg, sub = "border-left:3px solid #22c55e22;", "", ""
            elif j == step_idx:
                icon, color, alpha = "⟳", "#6366f1", "1"
                border = "border-left:3px solid #6366f1;"
                bg     = "background:#6366f108;"
                sub    = f"<div style='font-size:11px;color:#71717a;margin-top:2px;'>{desc}</div>"
            else:
                icon, color, alpha = "○", "#3f3f46", "0.4"
                border, bg, sub = "border-left:3px solid transparent;", "", ""

            steps_html += f"""
            <div style='display:flex;align-items:flex-start;gap:12px;
                        padding:9px 14px;border-radius:0 8px 8px 0;
                        margin-bottom:3px;opacity:{alpha};
                        {border}{bg}'>
              <span style='font-size:14px;color:{color};width:18px;
                           text-align:center;flex-shrink:0;'>{icon}</span>
              <div>
                <div style='font-size:13px;font-family:JetBrains Mono,monospace;
                            color:{"#f1f1f3" if j <= step_idx else "#3f3f46"};'>
                  {name}
                </div>{sub}
              </div>
            </div>"""

        pct = int((step_idx / len(PIPELINE_STEPS)) * 100)
        container.markdown(f"""
        <div style='background:#111118;border:1px solid #ffffff0f;
                    border-radius:16px;padding:24px 20px;
                    max-width:500px;margin:0 auto 120px;'>
          <div style='display:flex;justify-content:space-between;
                      align-items:center;margin-bottom:16px;'>
            <span style='font-size:11px;font-family:JetBrains Mono,monospace;
                         color:#6366f1;letter-spacing:.1em;'>
              ⚡ CIPHER ENGINE — EXECUTING
            </span>
            <span style='font-size:11px;font-family:monospace;color:#71717a;'>
              {step_idx + 1}/{len(PIPELINE_STEPS)}
            </span>
          </div>
          <div style='background:#0a0a0f;border-radius:999px;height:3px;
                      margin-bottom:20px;overflow:hidden;'>
            <div style='width:{pct}%;height:3px;border-radius:999px;
                        background:linear-gradient(90deg,#6366f1,#818cf8);
                        box-shadow:0 0 6px #6366f160;
                        transition:width .3s ease;'></div>
          </div>
          {steps_html}
          <div style='margin-top:16px;padding-top:12px;
                      border-top:1px solid #ffffff08;text-align:center;
                      font-size:11px;font-style:italic;color:#3f3f46;'>
            "{quote}"
          </div>
        </div>
        """, unsafe_allow_html=True)

    # Animate first 6 steps visually
    for i in range(6):
        _render(i)
        time.sleep(0.28)

    # Step 6 — actual API call
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

    # Step 7 — finalizing
    _render(7)
    time.sleep(0.20)
    container.empty()
    return result, audit


# ────────────────────────────────────────────────
# CHAT HISTORY RENDERER
# ────────────────────────────────────────────────

def _render_chat_history():
    history = st.session_state.get(K.HISTORY, [])

    if not history:
        st.markdown("""
        <div style='display:flex;flex-direction:column;align-items:center;
                    justify-content:center;padding:80px 24px;text-align:center;'>
          <div style='font-size:40px;margin-bottom:16px;opacity:.12;'>⚡</div>
          <div style='font-size:15px;color:#3f3f46;margin-bottom:6px;'>
            Your refined prompts will appear here
          </div>
          <div style='font-size:13px;color:#3f3f46;
                      font-family:Noto Naskh Arabic,serif;'>
            ستظهر نتائجك هنا
          </div>
        </div>
        """, unsafe_allow_html=True)
        return

    for idx, entry in enumerate(history):
        user_msg = entry.get("input", "")
        bot_msg  = entry.get("output", "")
        score    = entry.get("score", 0)

        # User bubble
        st.markdown(f"""
        <div style='display:flex;justify-content:flex-end;
                    margin-bottom:6px;padding:0 4px;'>
          <div style='background:#6366f1;color:#fff;
                      border-radius:18px 18px 4px 18px;
                      padding:12px 16px;max-width:82%;
                      font-size:14px;line-height:1.5;
                      word-break:break-word;'>
            {user_msg}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Score badge
        if score:
            label, color = _score_label({"score": score})
            st.markdown(f"""
            <div style='display:flex;padding:0 4px;margin-bottom:4px;'>
              <span style='font-size:11px;color:{color};
                           background:{color}18;border:1px solid {color}33;
                           border-radius:999px;padding:2px 10px;'>
                ● {label}
              </span>
            </div>
            """, unsafe_allow_html=True)

        # Bot bubble
        st.markdown(f"""
        <div style='display:flex;justify-content:flex-start;
                    margin-bottom:4px;padding:0 4px;'>
          <div style='background:#16161f;border:1px solid #ffffff0f;
                      color:#f1f1f3;border-radius:18px 18px 18px 4px;
                      padding:14px 16px;max-width:92%;
                      font-size:14px;line-height:1.6;
                      word-break:break-word;white-space:pre-wrap;'>
            {bot_msg}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Copy button
        copy_key = f"copy_{idx}"
        if st.button("⎘ Copy", key=copy_key):
            st.session_state[f"{copy_key}_done"] = True
        if st.session_state.get(f"{copy_key}_done"):
            st.markdown(
                "<div style='font-size:11px;color:#22c55e;padding:0 6px;'>"
                "✓ Copied to clipboard</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


# ────────────────────────────────────────────────
# MODEL PICKER
# ────────────────────────────────────────────────

def _render_model_picker():
    selected = st.session_state.get("selected_model_label", "✦ AUTO-SELECT")
    st.markdown("""
    <div style='font-size:11px;font-family:JetBrains Mono,monospace;
                color:#6366f1;letter-spacing:.08em;margin-bottom:10px;'>
      SELECT TARGET MODEL
    </div>
    """, unsafe_allow_html=True)

    for label, value in TARGET_MODELS:
        is_active = selected == label
        if st.button(
            ("✓ " if is_active else "   ") + label,
            key=f"mpick_{value}",
            use_container_width=True,
        ):
            st.session_state["selected_model_label"] = label
            st.session_state["selected_model_value"] = value
            st.session_state["show_model_picker"]    = False
            st.rerun()


# ────────────────────────────────────────────────
# MAIN ENTRY POINT
# ────────────────────────────────────────────────

def render_workspace(cfg: dict) -> None:

    # ── Layout CSS ──
    st.markdown("""
    <style>
    /* Extra bottom padding so content clears the fixed bar */
    .main .block-container {
        padding-bottom: 150px !important;
        padding-top: 8px !important;
        max-width: 720px !important;
        margin: 0 auto !important;
    }
    /* Fixed bottom input bar */
    #ws-bar {
        position: fixed;
        bottom: 0; left: 0; right: 0;
        z-index: 1000;
        background: linear-gradient(to top, #0a0a0f 75%, transparent);
        padding: 12px 12px 20px;
    }
    @media (min-width: 768px) {
        #ws-bar { left: 260px; padding: 16px 24px 28px; }
    }
    /* Input bar inner container */
    .ws-bar-inner {
        background: #16161f;
        border: 1px solid #ffffff14;
        border-radius: 16px;
        padding: 6px 8px;
        display: flex;
        align-items: flex-end;
        gap: 6px;
        max-width: 680px;
        margin: 0 auto;
    }
    /* Override Streamlit textarea inside bar */
    #ws-bar .stTextArea textarea {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 8px 4px !important;
        font-size: 14px !important;
        min-height: 44px !important;
        max-height: 140px !important;
        resize: none !important;
        color: #f1f1f3 !important;
    }
    #ws-bar .stTextArea textarea:focus {
        border: none !important;
        box-shadow: none !important;
    }
    /* Plus / mic / send buttons inside bar */
    #ws-bar .stButton > button {
        background: transparent !important;
        border: none !important;
        border-radius: 999px !important;
        width: 36px !important;
        height: 36px !important;
        padding: 0 !important;
        font-size: 18px !important;
        color: #71717a !important;
        transition: all 150ms ease !important;
        flex-shrink: 0 !important;
    }
    #ws-bar .stButton > button:hover {
        background: #ffffff0a !important;
        color: #f1f1f3 !important;
    }
    /* Send button — accent when active */
    #ws-bar [data-testid="stButton"]:last-child > button {
        background: #6366f1 !important;
        color: #fff !important;
    }
    #ws-bar [data-testid="stButton"]:last-child > button:hover {
        background: #4f46e5 !important;
    }
    /* Quick action cards */
    .qa-row .stButton > button {
        background: #16161f !important;
        border: 1px solid #ffffff0f !important;
        border-radius: 14px !important;
        color: #71717a !important;
        font-size: 12px !important;
        height: auto !important;
        padding: 12px 8px !important;
        white-space: normal !important;
        line-height: 1.4 !important;
        text-align: left !important;
        transition: all 150ms ease !important;
    }
    .qa-row .stButton > button:hover {
        background: #1c1c2a !important;
        color: #f1f1f3 !important;
        border-color: #6366f133 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Chat history ──
    _render_chat_history()

    # ── Model picker overlay ──
    if st.session_state.get("show_model_picker"):
        with st.container():
            st.markdown("""
            <div style='background:#111118;border:1px solid #ffffff1a;
                        border-radius:16px;padding:16px 12px;
                        max-width:260px;margin-bottom:8px;
                        box-shadow:0 8px 32px #00000060;'>
            """, unsafe_allow_html=True)
            _render_model_picker()
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Quick actions (only when no history) ──
    if not st.session_state.get(K.HISTORY):
        st.markdown("<div class='qa-row'>", unsafe_allow_html=True)
        qa_cols = st.columns(4)
        for i, (icon, label, starter) in enumerate(QUICK_ACTIONS):
            with qa_cols[i]:
                if st.button(
                    f"{icon}  {label}",
                    key=f"qa_{i}",
                    use_container_width=True,
                ):
                    st.session_state["prefill_input"] = starter
                    st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Selected model chip ──
    selected_label = st.session_state.get("selected_model_label", "✦ AUTO-SELECT")
    st.markdown(f"""
    <div style='display:flex;padding:0 4px;margin-bottom:4px;'>
      <span style='background:#6366f11a;border:1px solid #6366f133;
                   border-radius:999px;padding:2px 10px;
                   font-size:11px;color:#6366f1;font-family:monospace;'>
        ✦ {selected_label.replace("✦ ","")}
      </span>
    </div>
    """, unsafe_allow_html=True)

    # ── Input bar ──
    st.markdown("<div id='ws-bar'><div class='ws-bar-inner'>", unsafe_allow_html=True)

    col_plus, col_input, col_mic, col_send = st.columns([1, 12, 1, 1])

    with col_plus:
        if st.button("＋", key="btn_plus", help="Select target model"):
            st.session_state["show_model_picker"] = not st.session_state.get(
                "show_model_picker", False
            )
            st.rerun()

    with col_input:
        prefill    = st.session_state.pop("prefill_input", "")
        intent_val = st.text_area(
            "input",
            value=prefill,
            height=52,
            placeholder="Describe what you want to refine...",
            label_visibility="collapsed",
            key="ws_input",
        )

    with col_mic:
        st.button("🎤", key="btn_mic", help="Voice input")

    with col_send:
        has_text = bool((intent_val or "").strip())
        if has_text:
            send = st.button("➤", key="btn_send", type="primary")
        else:
            st.markdown("<div style='width:36px;height:36px;'></div>",
                        unsafe_allow_html=True)
            send = False

    st.markdown("</div></div>", unsafe_allow_html=True)  # close ws-bar

    # ── Handle refinement ──
    if send and intent_val and intent_val.strip():
        cleaned, violations = sanitize_input(intent_val)
        if violations:
            st.error("⚠ Input blocked by security policy.")
            return

        # Override model from picker
        run_cfg = dict(cfg)
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
