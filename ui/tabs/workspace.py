"""
ui/tabs/workspace.py — InkOS Desk + Studio
============================================
v5.0: Two-screen architecture matching design proposal.
      - Desk: Home screen, centered input, recent inks
      - Studio: Refinement result, stacked cards, split view
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
    ("🖊", "Refine",  "Refine and improve the following prompt:\n\n"),
    ("💡", "Expand",  "Expand this prompt with more detail and context:\n\n"),
    ("🎯", "Focus",   "Make this prompt more focused and precise:\n\n"),
    ("⚙️", "Adjust",  "Adjust this prompt for a professional audience:\n\n"),
]

# Arabic thumbnail words — cycle through for history items
_AR_THUMBS = ["خلق", "فكر", "كتب", "نور", "حبر", "علم", "إبد", "صنع", "فكرة", "إلهام"]

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

ROTATING_QUOTES = [
    "A great prompt is architecture, not words.",
    "الكلمة الصحيحة تغيّر كل شيء",
    "Precision is the highest form of intelligence.",
    "حبر وفكرة — ink and idea, refined.",
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
    if hour < 12:   return "Good morning.", "Let's craft something exceptional."
    elif hour < 17: return "Good afternoon.", "Ready to refine something great?"
    else:           return "Good evening.", "Let's ink something remarkable."


def _word_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0


def _thumb(idx: int) -> str:
    return _AR_THUMBS[idx % len(_AR_THUMBS)]


def _format_date(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%b %d, %Y")
    except Exception:
        return ""


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
# PIPELINE
# ────────────────────────────────────────────────

def _run_pipeline(payload, cfg: dict, cleaned: str):
    quote     = ROTATING_QUOTES[int(time.time() / 4) % len(ROTATING_QUOTES)]
    container = st.empty()
    dark_mode = st.session_state.get("dark_mode", True)

    bg      = "#1a1825" if dark_mode else "#FFFFFF"
    border  = "#D4AF3733" if dark_mode else "#E8E4DC"
    text1   = "#F5F0E8"  if dark_mode else "#1A1A1A"
    text3   = "#4a4535"  if dark_mode else "#B0A898"
    accent  = "#D4AF37"  if dark_mode else "#2C3E50"
    success = "#2ECC71"  if dark_mode else "#27AE60"

    def _render(step_idx: int):
        steps_html = ""
        for j, (name, desc) in enumerate(PIPELINE_STEPS):
            if j < step_idx:
                icon, color, alpha = "✓", success, "1"
                border_l, bg_s, sub = f"border-left:3px solid {success}22;", "", ""
            elif j == step_idx:
                icon, color, alpha = "⟳", accent, "1"
                border_l = f"border-left:3px solid {accent};"
                bg_s     = f"background:{accent}08;"
                sub      = f"<div style='font-size:11px;color:{text3};margin-top:2px;'>{desc}</div>"
            else:
                icon, color, alpha = "○", text3, "0.4"
                border_l, bg_s, sub = "border-left:3px solid transparent;", "", ""

            steps_html += f"""
            <div style='display:flex;align-items:flex-start;gap:12px;
                        padding:9px 14px;border-radius:0 8px 8px 0;
                        margin-bottom:3px;opacity:{alpha};{border_l}{bg_s}'>
              <span style='font-size:14px;color:{color};width:18px;
                           text-align:center;flex-shrink:0;'>{icon}</span>
              <div>
                <div style='font-size:13px;font-family:"JetBrains Mono",monospace;
                            color:{text1 if j<=step_idx else text3};'>{name}</div>
                {sub}
              </div>
            </div>"""

        pct = int((step_idx / len(PIPELINE_STEPS)) * 100)
        container.markdown(f"""
        <div style='background:{bg};border:1px solid {border};
                    border-radius:20px;padding:28px 24px;
                    max-width:500px;margin:20px auto;
                    box-shadow:0 8px 32px rgba(0,0,0,.15);'>
          <div style='display:flex;justify-content:space-between;
                      align-items:center;margin-bottom:20px;'>
            <span style='font-size:11px;font-family:"JetBrains Mono",monospace;
                         color:{accent};letter-spacing:.12em;'>
              ✦ CIPHER ENGINE — REFINING
            </span>
            <span style='font-size:11px;font-family:monospace;color:{text3};'>
              {step_idx+1}/{len(PIPELINE_STEPS)}
            </span>
          </div>
          <div style='background:{"#0f0e17" if dark_mode else "#F0EEE9"};
                      border-radius:999px;height:3px;
                      margin-bottom:24px;overflow:hidden;'>
            <div style='width:{pct}%;height:3px;border-radius:999px;
                        background:linear-gradient(90deg,{accent},{accent}cc);
                        box-shadow:0 0 8px {accent}50;
                        transition:width .3s ease;'></div>
          </div>
          {steps_html}
          <div style='margin-top:20px;padding-top:14px;
                      border-top:1px solid {border};text-align:center;
                      font-size:12px;font-style:italic;color:{text3};'>
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
# REFINEMENT RUNNER
# ────────────────────────────────────────────────

def _do_refine(intent_val: str, cfg: dict) -> None:
    """Run sanitize → pipeline → store result → rerun."""
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


# ────────────────────────────────────────────────
# SCREEN 1 — THE DESK
# ────────────────────────────────────────────────

def _render_desk(cfg: dict) -> None:
    dark_mode = st.session_state.get("dark_mode", True)

    bg       = "#0f0e17" if dark_mode else "#F9F9F9"
    surface  = "#1a1825" if dark_mode else "#FFFFFF"
    border   = "#ffffff0a" if dark_mode else "#E8E4DC"
    text1    = "#F5F0E8"  if dark_mode else "#1A1A1A"
    text2    = "#8a8070"  if dark_mode else "#7F8C8D"
    text3    = "#4a4535"  if dark_mode else "#B0A898"
    accent   = "#4A90D9"  if dark_mode else "#2C3E50"
    gold     = "#D4AF37"
    shadow   = "0 4px 16px rgba(0,0,0,.08)"

    # ── InkOS Logo ──
    st.markdown(f"""
    <div style='text-align:center;padding:32px 0 8px;'>
      <div style='font-size:32px;font-family:"Playfair Display",Georgia,serif;
                  font-weight:700;color:{accent};letter-spacing:-.02em;'>
        InkOS
      </div>
      <div style='font-size:10px;font-family:"JetBrains Mono",monospace;
                  color:{text3};letter-spacing:.2em;margin-top:4px;'>
        PREMIUM AI PROMPT REFINER
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Greeting ──
    main_text, sub_text = _greeting()
    st.markdown(f"""
    <div style='padding:24px 0 16px;'>
      <div style='font-size:34px;font-family:"Playfair Display",Georgia,serif;
                  font-weight:600;color:{text1};line-height:1.2;margin-bottom:6px;'>
        {main_text}
      </div>
      <div style='font-size:15px;color:{text2};'>{sub_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Centered Input Bar ──
    st.markdown(f"""
    <div style='background:{surface};border:1px solid {border};
                border-radius:16px;padding:4px 4px 4px 16px;
                display:flex;align-items:center;gap:8px;
                box-shadow:{shadow};margin-bottom:16px;'>
      <span style='font-size:20px;color:{text3};flex-shrink:0;'>✦</span>
    </div>
    """, unsafe_allow_html=True)

    # Actual input — Streamlit widget
    col_input, col_send = st.columns([10, 1])
    with col_input:
        prefill    = st.session_state.pop("desk_prefill", "")
        intent_val = st.text_area(
            "desk_input",
            value=prefill,
            height=52,
            placeholder="Draft your prompt...",
            label_visibility="collapsed",
            key="desk_input_widget",
        )
    with col_send:
        has_text = bool((intent_val or "").strip())
        if has_text:
            send = st.button("→", key="desk_send", type="primary")
        else:
            st.markdown(
                f"<div style='width:44px;height:44px;border-radius:999px;"
                f"background:{surface};border:1px solid {border};'></div>",
                unsafe_allow_html=True,
            )
            send = False

    # ── Quick Action Pills ──
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    qa_cols = st.columns(4)
    for i, (icon, label, starter) in enumerate(QUICK_ACTIONS):
        with qa_cols[i]:
            if st.button(
                f"{icon} {label}",
                key=f"desk_qa_{i}",
                use_container_width=True,
            ):
                st.session_state["desk_prefill"] = starter
                st.rerun()

    # ── Recent Inks ──
    history = st.session_state.get(K.HISTORY, [])
    if history:
        st.markdown(f"""
        <div style='display:flex;justify-content:space-between;
                    align-items:center;margin:28px 0 16px;'>
          <div style='font-size:22px;font-family:"Playfair Display",Georgia,serif;
                      font-weight:600;color:{text1};'>Recent Inks</div>
          <div style='font-size:13px;color:{accent};cursor:pointer;'>View all ›</div>
        </div>
        """, unsafe_allow_html=True)

        for idx, entry in enumerate(reversed(history[-6:])):
            user_msg = entry.get("input", "")
            bot_msg  = entry.get("output", "")
            ts       = entry.get("time", "")
            thumb    = _thumb(idx)
            date_str = _format_date(ts)
            title    = user_msg[:52] + ("..." if len(user_msg) > 52 else "")
            preview  = bot_msg[:90]  + ("..." if len(bot_msg)  > 90  else "")

            st.markdown(f"""
            <div style='display:flex;align-items:flex-start;gap:14px;
                        padding:16px;background:{surface};
                        border:1px solid {border};border-radius:14px;
                        margin-bottom:10px;cursor:pointer;
                        box-shadow:{shadow};transition:all 150ms ease;'>
              <div style='width:52px;height:52px;border-radius:12px;
                          background:{"#211f2e" if dark_mode else "#F0EEE9"};
                          border:1px solid {border};display:flex;
                          align-items:center;justify-content:center;
                          font:600 20px "Amiri","Noto Naskh Arabic",serif;
                          color:{accent};flex-shrink:0;'>
                {thumb}
              </div>
              <div style='flex:1;min-width:0;'>
                <div style='font-size:14px;font-weight:600;color:{text1};
                            margin-bottom:4px;white-space:nowrap;
                            overflow:hidden;text-overflow:ellipsis;'>
                  {title}
                </div>
                <div style='font-size:12px;color:{text2};line-height:1.45;
                            display:-webkit-box;-webkit-line-clamp:2;
                            -webkit-box-orient:vertical;overflow:hidden;'>
                  {preview}
                </div>
              </div>
              <div style='display:flex;flex-direction:column;
                          align-items:flex-end;gap:8px;flex-shrink:0;'>
                <div style='font-size:11px;color:{text3};
                            font-family:"JetBrains Mono",monospace;
                            white-space:nowrap;'>
                  {date_str}
                </div>
                <div style='color:{text3};font-size:18px;cursor:pointer;'>⋯</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Tap to restore
            if st.button(
                "Open",
                key=f"desk_open_{idx}",
                use_container_width=False,
            ):
                st.session_state[K.LAST_INPUT]  = user_msg
                st.session_state[K.LAST_RESULT] = bot_msg
                st.rerun()

    else:
        # Empty state
        st.markdown(f"""
        <div style='text-align:center;padding:60px 24px;'>
          <div style='font-size:40px;margin-bottom:16px;opacity:.15;'>✦</div>
          <div style='font-size:18px;font-family:"Playfair Display",Georgia,serif;
                      color:{text3};margin-bottom:8px;'>
            Refine your thoughts.<br>Ink with clarity.
          </div>
          <div style='font-size:15px;color:{text3};
                      font-family:"Amiri","Noto Naskh Arabic",serif;'>
            حبر وفكرة
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Handle send ──
    if send and intent_val and intent_val.strip():
        _do_refine(intent_val.strip(), cfg)


# ────────────────────────────────────────────────
# SCREEN 2 — THE STUDIO
# ────────────────────────────────────────────────

def _render_studio(cfg: dict) -> None:
    dark_mode = st.session_state.get("dark_mode", True)

    bg      = "#0f0e17" if dark_mode else "#F9F9F9"
    surface = "#1a1825" if dark_mode else "#FFFFFF"
    surf_up = "#211f2e" if dark_mode else "#F0EEE9"
    border  = "#ffffff0a" if dark_mode else "#E8E4DC"
    gold_b  = "#D4AF3733"
    text1   = "#F5F0E8"  if dark_mode else "#1A1A1A"
    text2   = "#8a8070"  if dark_mode else "#7F8C8D"
    text3   = "#4a4535"  if dark_mode else "#B0A898"
    accent  = "#4A90D9"  if dark_mode else "#2C3E50"
    gold    = "#D4AF37"
    shadow  = "0 4px 16px rgba(0,0,0,.08)"

    raw_input = st.session_state.get(K.LAST_INPUT, "")
    result    = st.session_state.get(K.LAST_RESULT, "")
    audit     = st.session_state.get(K.LAST_AUDIT) or {}
    score     = audit.get("score", 0)
    in_words  = _word_count(raw_input)
    out_words = _word_count(result)

    if score >= 80:   badge = "✦ Excellent"
    elif score >= 60: badge = "✦ Refined"
    else:             badge = "✦ Refined"

    split_view = st.session_state.get("split_view", False)

    # ── Studio Header ──
    st.markdown(f"""
    <div style='padding:20px 0 16px;'>
      <div style='display:flex;justify-content:space-between;
                  align-items:flex-start;'>
        <div>
          <div style='font-size:32px;font-family:"Playfair Display",Georgia,serif;
                      font-weight:600;color:{text1};line-height:1.1;'>
            Studio
          </div>
          <div style='font-size:14px;color:{text2};margin-top:4px;'>
            Refine your thoughts. Ink with clarity.
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Split View toggle
    col_hdr, col_split = st.columns([3, 1])
    with col_split:
        if st.button(
            "⊟ Split" if split_view else "⊞ Split View",
            key="split_toggle",
            use_container_width=True,
        ):
            st.session_state["split_view"] = not split_view
            st.rerun()

    # ── Back to Desk ──
    if st.button("← New Prompt", key="back_to_desk"):
        st.session_state[K.LAST_RESULT] = None
        st.session_state[K.LAST_INPUT]  = ""
        st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── SPLIT VIEW ──
    if split_view:
        left, right = st.columns(2)
        with left:
            st.markdown(f"""
            <div style='background:{surface};border:1px solid {border};
                        border-radius:16px;padding:20px;
                        box-shadow:{shadow};height:100%;'>
              <div style='display:flex;align-items:center;gap:8px;
                          margin-bottom:14px;'>
                <div style='width:28px;height:28px;border-radius:999px;
                            background:{surf_up};border:1px solid {border};
                            display:flex;align-items:center;justify-content:center;
                            font-size:13px;'>🖊</div>
                <span style='font-size:13px;color:{text2};font-weight:500;'>
                  Original Prompt
                </span>
              </div>
              <div style='font-size:15px;color:{text1};line-height:1.65;
                          margin-bottom:14px;'>{raw_input}</div>
              <div style='font-size:12px;color:{text3};'>{in_words} words</div>
            </div>
            """, unsafe_allow_html=True)

        with right:
            st.markdown(f"""
            <div style='background:{surface};border:1px solid {gold_b};
                        border-radius:16px;padding:20px;
                        box-shadow:0 4px 20px #D4AF3715;height:100%;
                        position:relative;overflow:hidden;'>
              <div style='position:absolute;inset:0;
                          background:linear-gradient(135deg,#D4AF3708 0%,transparent 60%);
                          pointer-events:none;'></div>
              <div style='display:flex;align-items:center;gap:8px;
                          margin-bottom:14px;'>
                <div style='width:30px;height:30px;border-radius:999px;
                            background:#D4AF3712;border:1px solid {gold_b};
                            display:flex;align-items:center;justify-content:center;
                            font-size:14px;'>✦</div>
                <span style='font-size:15px;color:{gold};font-weight:600;
                             font-family:"Playfair Display",Georgia,serif;'>
                  Refined Ink
                </span>
                <span style='margin-left:auto;background:#D4AF3712;
                             border:1px solid {gold_b};border-radius:999px;
                             padding:3px 10px;font-size:11px;color:{gold};
                             font-family:"JetBrains Mono",monospace;'>
                  {badge}
                </span>
              </div>
              <div style='font-size:15px;color:{gold};line-height:1.75;
                          margin-bottom:14px;
                          font-family:"Playfair Display",Georgia,serif;'>
                {result}
              </div>
              <div style='height:1px;background:linear-gradient(90deg,
                transparent,{gold_b},transparent);margin:12px 0;'></div>
              <div style='font-size:12px;color:{text3};'>{out_words} words</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        # ── STACKED VIEW ──

        # Original Prompt Card
        st.markdown(f"""
        <div style='background:{surface};border:1px solid {border};
                    border-radius:16px;padding:20px;box-shadow:{shadow};'>
          <div style='display:flex;justify-content:space-between;
                      align-items:center;margin-bottom:14px;'>
            <div style='display:flex;align-items:center;gap:8px;'>
              <div style='width:28px;height:28px;border-radius:999px;
                          background:{surf_up};border:1px solid {border};
                          display:flex;align-items:center;justify-content:center;
                          font-size:13px;'>🖊</div>
              <span style='font-size:13px;color:{text2};font-weight:500;'>
                Original Prompt
              </span>
            </div>
            <span style='font-size:12px;color:{accent};cursor:pointer;'>
              Edit ✏
            </span>
          </div>
          <div style='font-size:16px;color:{text1};line-height:1.65;
                      margin-bottom:14px;'>{raw_input}</div>
          <div style='display:flex;justify-content:space-between;
                      align-items:center;'>
            <span style='font-size:12px;color:{text3};'>{in_words} words</span>
            <span style='font-size:16px;color:{text3};cursor:pointer;'>⎘</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Connector
        st.markdown(f"""
        <div style='display:flex;justify-content:center;align-items:center;
                    height:40px;position:relative;'>
          <div style='position:absolute;top:0;bottom:0;left:50%;width:1px;
                      background:linear-gradient(to bottom,{border},{gold},{border});'>
          </div>
          <div style='width:32px;height:32px;border-radius:999px;
                      background:{surface};border:1px solid {gold_b};
                      display:flex;align-items:center;justify-content:center;
                      font-size:14px;color:{gold};position:relative;z-index:2;
                      box-shadow:0 0 12px #D4AF3720;'>
            ∨
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Refined Ink Card
        st.markdown(f"""
        <div style='background:{surface};border:1px solid {gold_b};
                    border-radius:16px;padding:20px;position:relative;
                    overflow:hidden;box-shadow:0 4px 20px #D4AF3715;'>
          <div style='position:absolute;inset:0;
                      background:linear-gradient(135deg,#D4AF3708 0%,transparent 60%);
                      pointer-events:none;'></div>
          <div style='display:flex;justify-content:space-between;
                      align-items:center;margin-bottom:14px;'>
            <div style='display:flex;align-items:center;gap:8px;'>
              <div style='width:30px;height:30px;border-radius:999px;
                          background:#D4AF3712;border:1px solid {gold_b};
                          display:flex;align-items:center;justify-content:center;
                          font-size:14px;'>✦</div>
              <span style='font-size:15px;color:{gold};font-weight:600;
                           font-family:"Playfair Display",Georgia,serif;'>
                Refined Ink
              </span>
            </div>
            <div style='background:#D4AF3712;border:1px solid {gold_b};
                        border-radius:999px;padding:4px 12px;
                        font-size:11px;color:{gold};
                        font-family:"JetBrains Mono",monospace;
                        letter-spacing:.04em;'>
              ✦ {badge}
            </div>
          </div>
          <div style='font-size:16px;color:{gold};line-height:1.75;
                      margin-bottom:16px;
                      font-family:"Playfair Display",Georgia,serif;'>
            {result}
          </div>
          <div style='height:1px;background:linear-gradient(90deg,
              transparent,{gold_b},transparent);margin:12px 0;'></div>
          <div style='display:flex;justify-content:space-between;align-items:center;'>
            <span style='font-size:12px;color:{text3};'>{out_words} words</span>
            <span style='font-size:16px;color:{text3};cursor:pointer;'>⎘</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Action Row: Copy / Share / Re-ink ──
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⎘  Copy", key="studio_copy", use_container_width=True):
            st.session_state["studio_copied"] = True
            st.rerun()
    with c2:
        st.button("↗  Share", key="studio_share", use_container_width=True)
    with c3:
        if st.button("↺  Re-ink", key="studio_reink", use_container_width=True):
            st.session_state["desk_prefill"]   = raw_input
            st.session_state[K.LAST_RESULT]    = None
            st.session_state[K.LAST_INPUT]     = ""
            st.rerun()

    if st.session_state.pop("studio_copied", False):
        st.markdown(f"""
        <div style='text-align:center;font-size:12px;color:#27AE60;
                    padding:6px;font-family:"JetBrains Mono",monospace;'>
          ✓ Copied to clipboard
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Vault Save (collapsed) ──
    with st.expander("🔒  Save to Vault", expanded=False):
        st.text_input("Designation",
                      placeholder="Name this prompt...", key="v_t")
        st.text_input("Tags",
                      placeholder="e.g. blog, ai, arabic", key="v_g")
        if st.button("⚡ Secure to Vault", type="primary",
                     use_container_width=True, key="studio_vault"):
            uid       = st.session_state.get(K.USER_HASH)
            title_val = st.session_state.get("v_t", "").strip()
            tags_val  = st.session_state.get("v_g", "").strip()
            if not title_val:
                st.error("⚠ Add a designation first.")
            elif not uid or "GUEST_" in str(uid).upper():
                st.error("⚠ Log in to use the Vault.")
            else:
                if SUPABASE_MISSING:
                    _save_local(uid, title_val, tags_val, cfg)
                    st.success("✓ Saved locally")
                else:
                    _, err = save_prompt(
                        uid, title=title_val, tags=tags_val,
                        content=result,
                        target=st.session_state.get(K.AUTO_TARGET),
                        framework=cfg.get("framework", ""),
                        score=score,
                    )
                    if err: st.error(f"⚠ {err}")
                    else:   st.success("✓ Secured to Vault")

    # ── New prompt input at bottom ──
    st.markdown("<div style='height:60px'></div>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='position:fixed;bottom:0;left:0;right:0;z-index:1000;
                background:linear-gradient(to top,{bg} 65%,transparent);
                padding:12px 16px 24px;'>
      <div style='max-width:680px;margin:0 auto;'>
    """, unsafe_allow_html=True)

    col_input, col_send = st.columns([10, 1])
    with col_input:
        new_prompt = st.text_area(
            "new_prompt",
            height=48,
            placeholder="Refine another prompt...",
            label_visibility="collapsed",
            key="studio_new_input",
        )
    with col_send:
        has_text = bool((new_prompt or "").strip())
        if has_text:
            new_send = st.button("→", key="studio_send", type="primary")
        else:
            new_send = False

    st.markdown("</div></div>", unsafe_allow_html=True)

    if new_send and new_prompt and new_prompt.strip():
        _do_refine(new_prompt.strip(), cfg)


# ────────────────────────────────────────────────
# MAIN ENTRY POINT
# ────────────────────────────────────────────────

def render_workspace(cfg: dict) -> None:
    # Layout
    st.markdown("""
    <style>
    .main .block-container {
      padding-bottom: 140px !important;
      padding-top:    0 !important;
      max-width:      680px !important;
      margin:         0 auto !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Route to Desk or Studio based on whether result exists
    if st.session_state.get(K.LAST_RESULT):
        _render_studio(cfg)
    else:
        _render_desk(cfg)
