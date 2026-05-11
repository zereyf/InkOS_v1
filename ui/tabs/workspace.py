from __future__ import annotations
import json, re, time, os
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
import streamlit as st
from groq import Groq
from state import K
from security.sanitizer import sanitize_input
from engine.refiner import run_refinement_and_audit
from forge.prompt_assembler import assemble_master_payload
from forge.intelligence import resolve_target_model
from vault.supabase_client import SUPABASE_MISSING
from vault.vault_engine import save_prompt

WAT_TZ = timezone(timedelta(hours=1))
LOCAL_VAULT_KEY = "local_vault_items"

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

ROTATING_QUOTES = [
    "A great prompt is architecture, not words.",
    "الكلمة الصحيحة تغيّر كل شيء",
    "Precision is the highest form of intelligence.",
    "الوضوح قوة. الغموض ضعف.",
    "The best prompt anticipates the answer.",
    "حبر وفكرة — ink and idea, refined.",
]

TEMPLATES = [
    ("Blog Post", "Write a detailed blog post about [topic] targeting [audience]. Include an engaging introduction, structured sections with headers, and a compelling conclusion."),
    ("Email",     "Write a professional email to [recipient] about [topic]. Tone: [formal/casual]. Goal: [what you want them to do]."),
    ("Code",      "Write [language] code that [does what]. Requirements: [list requirements]. Handle edge cases and include comments."),
    ("Image",     "Create a [style] image of [subject]. Mood: [mood]. Lighting: [lighting]. Color palette: [colors]. Camera angle: [angle]."),
    ("Research",  "Research and summarize [topic]. Cover: key findings, current debates, practical implications. Audience: [audience level]."),
]

def _get_dna_context() -> dict:
    return {
        K.INK_DNA:   str(st.session_state.get(K.INK_DNA)   or ""),
        K.INTEL_DNA: str(st.session_state.get(K.INTEL_DNA) or ""),
        K.HIKMAH_DNA:str(st.session_state.get(K.HIKMAH_DNA)or ""),
    }

def _extract_telemetry(result: str, start_time: float) -> Dict[str, Any]:
    latency_ms = int((time.perf_counter() - start_time) * 1000)
    words = result.split(); word_count = len(words)
    density = round(len(result) / word_count, 2) if word_count > 0 else 0
    return {"latency_ms": latency_ms, "word_count": word_count, "density": density}

def extract_clean_output(raw_response: str) -> str:
    """
    Strips ALL internal structure from the LLM response.
    Returns only the clean, user-facing refined prompt.
    """
    text = str(raw_response or "")

    # ── Remove PART 1 / PART 2 sections and everything before the actual prompt ──
    text = re.sub(r"\*\*\s*PART\s*1\s*:.*?(?=\*\*\s*PART\s*2\s*:|$)", "", text, flags=re.I | re.S)
    text = re.sub(r"\*\*\s*PART\s*2\s*:.*?(?=\*\*\s*PART\s*3\s*:|$)", "", text, flags=re.I | re.S)
    text = re.sub(r"\*\*\s*PART\s*\d+\s*:.*?\*\*", "", text, flags=re.I | re.S)

    # ── Remove target prompt headers (THE main culprit) ──
    text = re.sub(
        r"(?:Claude|GPT|ChatGPT|Gemini|DALL-?E|Midjourney|FLUX|OpenAI)\s*(?:Target\s*)?Prompt\s*:\s*",
        "", text, flags=re.I
    )

    # ── Remove A.I.Z.E.N. identity block ──
    text = re.sub(r"A\.I\.Z\.E\.N\..*?InkOS\.", "", text, flags=re.I | re.S)
    text = re.sub(r"Algorithmic Intelligence Zenith.*?InkOS\.", "", text, flags=re.I | re.S)

    # ── Remove XML tags and their content ──
    for tag in ("quality-bar", "edge-cases", "constraints", "quality_bar",
                "edge_cases", "role", "task", "visual-aesthetic",
                "strategic-focus", "philosophical-bounds"):
        text = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", "", text)  # strip any remaining tags

    # ── Remove JSON blocks ──
    text = re.sub(r"```(?:json|xml|python)?[\s\S]*?```", "", text, flags=re.I)
    text = re.sub(r"\{\s*\"score\"[\s\S]*?\}\s*$", "", text, flags=re.I)
    text = re.sub(r"\{[\s\S]{0,500}\"audit\"[\s\S]{0,500}\}", "", text, flags=re.I)

    # ── Remove markdown headers and bold markers ──
    text = re.sub(r"^\s*#{1,6}\s.*$", "", text, flags=re.M)
    text = text.replace("**", "").replace("__", "")

    # ── Remove common internal label prefixes ──
    text = re.sub(
        r"^(?:System\s*Prompt|REFINED_PROMPT|PROMPT|OUTPUT|thinking|"
        r"Refined\s*Prompt|Final\s*Prompt|User\s*Prompt)\s*:\s*",
        "", text, flags=re.I | re.M
    )

    # ── Remove "You are a highly advanced..." AIZEN opening if it slipped through ──
    text = re.sub(
        r"You are a highly advanced.*?InkOS\.",
        "", text, flags=re.I | re.S
    )

    # ── Clean up whitespace ──
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def _analysis_report(prompt: str) -> Dict[str, Any]:
    words = prompt.split()
    clarity      = min(95, 35 + len(words) // 2)
    specificity  = min(95, 20 + sum(1 for w in words if len(w) > 6) * 3)
    context      = min(95, 15 + prompt.count("\n") * 8 + (20 if "for" in prompt.lower() else 0))
    effectiveness= min(95, int((clarity + specificity + context) / 3) + 10)
    notes = []
    if len(words) < 5:  notes.append("⚠ Very short — add more context")
    if specificity < 40: notes.append("⚠ Too vague — be more specific")
    if context < 30:    notes.append("⚠ Missing target audience or goal")
    return {"clarity": clarity, "specificity": specificity,
            "context": context, "effectiveness": effectiveness, "notes": notes}

def _render_analysis(prompt: str) -> None:
    report = _analysis_report(prompt)
    st.markdown("""
    <div style='background:#16161f;border:1px solid #ffffff0f;border-radius:12px;
                padding:16px 20px;margin-bottom:16px;'>
      <div style='font-size:11px;font-family:JetBrains Mono,monospace;
                  color:#6366f1;letter-spacing:.1em;margin-bottom:12px;'>
        PROMPT INTELLIGENCE REPORT
      </div>
    """, unsafe_allow_html=True)

    for label, key in [("Clarity","clarity"),("Specificity","specificity"),
                       ("Context","context"),("Effectiveness","effectiveness")]:
        val = report[key]
        color = "#22c55e" if val >= 70 else "#f59e0b" if val >= 45 else "#ef4444"
        st.markdown(f"""
        <div style='display:flex;align-items:center;gap:10px;margin-bottom:8px;'>
          <span style='font-size:12px;color:#71717a;width:100px;'>{label}</span>
          <div style='flex:1;background:#0a0a0f;border-radius:999px;height:6px;'>
            <div style='width:{val}%;background:{color};height:6px;
                        border-radius:999px;transition:width .5s ease;'></div>
          </div>
          <span style='font-size:12px;font-family:monospace;color:{color};width:36px;
                       text-align:right;'>{val}%</span>
        </div>
        """, unsafe_allow_html=True)

    for note in report["notes"]:
        st.markdown(f"<div style='font-size:12px;color:#f59e0b;margin-top:4px;'>{note}</div>",
                    unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

def _render_pipeline_animation() -> None:
    quote_idx = int(time.time() / 4) % len(ROTATING_QUOTES)
    quote = ROTATING_QUOTES[quote_idx]

    container = st.empty()
    steps_done = []

    for i, (step_name, step_desc) in enumerate(PIPELINE_STEPS):
        steps_html = ""
        for j, (s, _) in enumerate(PIPELINE_STEPS):
            if j < i:
                state = "done"
                icon  = "✓"
                color = "#22c55e"
                alpha = "1"
            elif j == i:
                state = "active"
                icon  = "⟳"
                color = "#6366f1"
                alpha = "1"
            else:
                state = "pending"
                icon  = "○"
                color = "#3f3f46"
                alpha = "0.5"

            border = f"border-left:3px solid {color};" if j == i else "border-left:3px solid transparent;"
            bg     = "background:#6366f108;" if j == i else ""
            steps_html += f"""
            <div style='display:flex;align-items:flex-start;gap:12px;padding:10px 14px;
                        border-radius:8px;margin-bottom:4px;opacity:{alpha};
                        {border}{bg}transition:all .2s ease;'>
              <span style='font-size:16px;color:{color};width:20px;text-align:center;
                           {"animation:spin 1s linear infinite;" if j==i else ""}'>{icon}</span>
              <div>
                <div style='font-size:13px;font-family:JetBrains Mono,monospace;
                            color:{"#f1f1f3" if j<=i else "#3f3f46"};'>{s}</div>
                {"<div style='font-size:11px;color:#71717a;margin-top:2px;'>" + PIPELINE_STEPS[i][1] + "</div>" if j==i else ""}
              </div>
            </div>
            """

        progress_pct = int((i / len(PIPELINE_STEPS)) * 100)

        container.markdown(f"""
        <style>
        @keyframes spin {{ to {{ transform: rotate(360deg); }} }}
        @keyframes shimmer {{
          0%   {{ background-position: -200% 0; }}
          100% {{ background-position: 200% 0; }}
        }}
        </style>
        <div style='background:#111118;border:1px solid #ffffff0f;border-radius:16px;
                    padding:28px 24px;max-width:520px;margin:0 auto;'>

          <div style='display:flex;justify-content:space-between;align-items:center;
                      margin-bottom:20px;'>
            <span style='font-size:12px;font-family:JetBrains Mono,monospace;
                         color:#6366f1;letter-spacing:.12em;'>⚡ CIPHER ENGINE  //  EXECUTING</span>
            <span style='font-size:12px;font-family:monospace;color:#71717a;'>{i+1}/{len(PIPELINE_STEPS)}</span>
          </div>

          <div style='background:#0a0a0f;border-radius:999px;height:4px;
                      margin-bottom:24px;overflow:hidden;'>
            <div style='width:{progress_pct}%;height:4px;border-radius:999px;
                        background:linear-gradient(90deg,#6366f1,#818cf8);
                        box-shadow:0 0 8px #6366f160;
                        transition:width .4s ease;'></div>
          </div>

          {steps_html}

          <div style='margin-top:20px;padding-top:16px;border-top:1px solid #ffffff08;
                      text-align:center;font-size:12px;font-style:italic;color:#3f3f46;'>
            "{quote}"
          </div>
        </div>
        """, unsafe_allow_html=True)

        time.sleep(0.35)

    # Final — all done
    container.empty()

def _save_local(uid: str, title: str, tags: str, cfg: dict) -> None:
    local_items = st.session_state.get(LOCAL_VAULT_KEY, [])
    local_items.insert(0, {
        "id":         f"local-{int(time.time()*1000)}",
        "user_hash":  uid,
        "title":      title,
        "tags":       tags,
        "content":    st.session_state.get(K.LAST_RESULT, ""),
        "target":     st.session_state.get(K.AUTO_TARGET, "ChatGPT"),
        "framework":  cfg["framework"],
        "score":      (st.session_state.get(K.LAST_AUDIT) or {}).get("score", 0),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    st.session_state[LOCAL_VAULT_KEY] = local_items[:200]

def _score_badge(audit: dict) -> str:
    score = (audit or {}).get("score", 0)
    if score >= 80:   return "🟢 Excellent", "#22c55e"
    elif score >= 60: return "🟡 Good",      "#f59e0b"
    else:             return "🔴 Fair",       "#ef4444"

def render_workspace(cfg: dict) -> None:
    # ── Header ──
    st.markdown("""
    <div style='display:flex;align-items:center;gap:10px;margin-bottom:20px;'>
      <span style='font-size:14px;font-family:JetBrains Mono,monospace;
                   color:#71717a;letter-spacing:.08em;'>InkOS</span>
      <span style='font-size:11px;background:#16161f;color:#71717a;
                   padding:2px 8px;border-radius:999px;border:1px solid #ffffff0f;
                   font-family:monospace;'>v1</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Mode Selector ──
    mode_key = "workspace_mode"
    if mode_key not in st.session_state:
        st.session_state[mode_key] = "Balanced"

    col1, col2, col3 = st.columns(3)
    for col, mode in zip([col1, col2, col3], ["Balanced", "Precision", "Creative"]):
        with col:
            is_active = st.session_state[mode_key] == mode
            btn_style = (
                "background:#6366f1;color:#fff;border:1px solid #6366f1;"
                if is_active else
                "background:transparent;color:#71717a;border:1px solid #ffffff0f;"
            )
            if st.button(mode, key=f"mode_{mode}", use_container_width=True):
                st.session_state[mode_key] = mode
                st.rerun()

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # ── Template Quick-fill ──
    st.markdown("<div style='display:flex;gap:6px;flex-wrap:wrap;margin-bottom:12px;'>", unsafe_allow_html=True)
    tcols = st.columns(len(TEMPLATES))
    for i, (label, template_text) in enumerate(TEMPLATES):
        with tcols[i]:
            if st.button(label, key=f"tpl_{label}", use_container_width=True):
                st.session_state["tpl_inject"] = template_text
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    # ── Prompt Input ──
    default_val = st.session_state.pop("tpl_inject", "")
    intent_val = st.text_area(
        "Prompt",
        value=default_val,
        height=190,
        placeholder="Describe what you want to create...",
        label_visibility="collapsed",
        key="ta_input_widget",
    )

    char_count = len(intent_val)
    st.markdown(
        f"<div style='font-size:11px;color:#3f3f46;text-align:right;'>{char_count} characters</div>",
        unsafe_allow_html=True,
    )

    # ── Execute Button ──
    execute = st.button("⚡ Refine Prompt", use_container_width=True, type="primary", key="btn_refine_prompt")

    # ── Run Refinement ──
    if execute and intent_val.strip():
        # Show analysis report first
        _render_analysis(intent_val)

        cleaned, violations = sanitize_input(intent_val)
        if violations:
            st.error("⚠ Input blocked by security policy.")
        else:
            # Show pipeline animation
            _render_pipeline_animation()

            payload = assemble_master_payload(cleaned, cfg, _get_dna_context())
            start   = time.perf_counter()
            result, audit, _ = run_refinement_and_audit(
                payload,
                resolve_target_model(cfg.get("target_model"), cleaned)[0],
                cfg["framework"],
                cfg["source_lang"],
                cfg["aesthetic_choice"],
                hikmah_style=str(cfg.get("hikmah_style") or "None"),
                skip_security=False,
            )
            # ── CLEAN OUTPUT — strip all internals ──
            result = extract_clean_output(result)

            st.session_state[K.LAST_RESULT] = result
            st.session_state[K.LAST_AUDIT]  = audit
            st.session_state[K.LAST_INPUT]  = cleaned
            st.session_state[K.HISTORY] = (
                st.session_state.get(K.HISTORY, []) +
                [{"input": cleaned, "output": result,
                  "time": datetime.now(WAT_TZ).isoformat()}]
            )[-50:]
            _extract_telemetry(result, start)
            st.rerun()

    elif execute and not intent_val.strip():
        st.warning("Please enter a prompt first.")

    # ── Output Section ──
    if st.session_state.get(K.LAST_RESULT):
        audit = st.session_state.get(K.LAST_AUDIT) or {}
        badge_text, badge_color = _score_badge(audit)

        # Score badge
        st.markdown(f"""
        <div style='display:flex;justify-content:flex-end;margin-bottom:8px;'>
          <span style='background:{badge_color}22;color:{badge_color};
                       border:1px solid {badge_color}44;border-radius:999px;
                       padding:4px 14px;font-size:12px;font-weight:600;'>
            {badge_text}
          </span>
        </div>
        """, unsafe_allow_html=True)

        # Before / After
        raw_input = st.session_state.get(K.LAST_INPUT, "")
        if raw_input:
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("<div style='font-size:10px;font-family:monospace;color:#3f3f46;letter-spacing:.1em;margin-bottom:6px;'>BEFORE</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background:#111118;border:1px solid #ffffff0f;border-radius:12px;padding:14px;font-size:13px;color:#71717a;min-height:80px;'>{raw_input}</div>", unsafe_allow_html=True)
            with c2:
                st.markdown("<div style='font-size:10px;font-family:monospace;color:#3f3f46;letter-spacing:.1em;margin-bottom:6px;'>AFTER</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background:#111118;border:1px solid #6366f144;border-radius:12px;padding:14px;font-size:13px;color:#f1f1f3;min-height:80px;'>{st.session_state.get(K.LAST_RESULT,'')}</div>", unsafe_allow_html=True)
        else:
            st.text_area(
                "Refined Output",
                value=st.session_state.get(K.LAST_RESULT, ""),
                height=260,
                label_visibility="visible",
            )

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # ── Vault Section ──
        st.markdown("""
        <div style='border-top:1px solid #ffffff08;padding-top:16px;margin-top:8px;'>
          <div style='font-size:11px;font-family:monospace;color:#3f3f46;
                      letter-spacing:.1em;margin-bottom:12px;'>SECURE TO VAULT</div>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.get("vault_local_banner"):
            st.info("💾 Saving locally — Vault connection unavailable")
            st.session_state["vault_local_banner"] = False

        st.text_input("Designation", placeholder="Name this prompt...", key="v_t")
        st.text_input("Forensic Tags", placeholder="e.g. blog, marketing, ai", key="v_g")

        if st.button("🔒 Secure to Vault", use_container_width=True, key="btn_secure_vault"):
            uid       = st.session_state.get(K.USER_HASH)
            title_val = st.session_state.get("v_t", "").strip()
            tags_val  = st.session_state.get("v_g", "").strip()

            if not title_val:
                st.error("⚠ Please add a designation before securing.")
            elif not uid or "GUEST_" in str(uid).upper():
                st.error("⚠ Vault unavailable — please log in first.")
            else:
                if SUPABASE_MISSING:
                    _save_local(uid, title_val, tags_val, cfg)
                    st.session_state["vault_local_banner"]  = True
                    st.session_state["vault_refresh_nonce"] = time.time()
                    st.session_state["vault_saved_until"]   = time.time() + 3
                    st.rerun()
                else:
                    _, err = save_prompt(
                        uid,
                        title=title_val,
                        tags=tags_val,
                        content=st.session_state.get(K.LAST_RESULT),
                        target=st.session_state.get(K.AUTO_TARGET),
                        framework=cfg["framework"],
                        score=(st.session_state.get(K.LAST_AUDIT) or {}).get("score", 0),
                    )
                    if err:
                        st.error("⚠ Vault unavailable — check connection.")
                    else:
                        st.session_state["vault_refresh_nonce"] = time.time()
                        st.session_state["vault_saved_until"]   = time.time() + 3
                        st.rerun()

        if st.session_state.get("vault_saved_until", 0) > time.time():
            st.markdown("""
            <div style='background:#22c55e15;border:1px solid #22c55e44;border-radius:10px;
                        padding:12px 16px;text-align:center;color:#22c55e;
                        font-size:14px;font-weight:600;margin-top:8px;'>
              ✓ Secured to Vault
            </div>
            """, unsafe_allow_html=True)

    else:
        # ── Empty State ──
        st.markdown("""
        <div style='text-align:center;padding:48px 24px;'>
          <div style='font-size:32px;margin-bottom:16px;opacity:.3;'>⚡</div>
          <div style='font-size:14px;color:#3f3f46;margin-bottom:6px;'>
            Your refined prompt will appear here
          </div>
          <div style='font-size:12px;color:#3f3f46;font-family:Noto Naskh Arabic,serif;'>
            ستظهر نتيجتك هنا
          </div>
        </div>
        """, unsafe_allow_html=True)
