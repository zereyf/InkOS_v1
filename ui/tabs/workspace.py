"""
ui/tabs/workspace.py — InkOS Official Workspace
=================================================
Matches the Mobile UX/UI Design Considerations (Section 5).
- Branch conflict resolution note: kept workspace tab implementation from feature branch.
- Stacked, sequential flow (Input -> Controls -> Output).
- Bilingual headers (English / Arabic).
- Targeted AI Model dropdown replacing sliders.
"""
from __future__ import annotations
import re
from datetime import datetime, timezone, timedelta

import streamlit as st

from state import K
from security.sanitizer import sanitize_input
from engine.refiner import run_refinement_and_audit
from forge.prompt_assembler import assemble_master_payload
from forge.intelligence import resolve_target_model

WAT_TZ = timezone(timedelta(hours=1))

AVAILABLE_MODELS = ["A.I.Z.E.N. Core", "Claude 3.5 Sonnet", "Gemini 1.5 Pro"]
INTENT_ACTIONS = ["✨ Auto-Refine", "💡 Expand & Detail", "🎯 Focus & Clarify", "⚙️ Format as Code/Structure"]

def _get_dna_context() -> dict:
    return {
        K.INK_DNA:    str(st.session_state.get(K.INK_DNA)    or ""),
        K.INTEL_DNA:  str(st.session_state.get(K.INTEL_DNA)  or ""),
        K.HIKMAH_DNA: str(st.session_state.get(K.HIKMAH_DNA) or ""),
    }

def extract_clean_output(raw: str) -> str:
    t = str(raw or "")
    # Prefer explicit refined-prompt payloads when present.
    refined_match = re.search(r"REFINED_PROMPT\s*:\s*(.+)", t, flags=re.I | re.S)
    if refined_match:
        t = refined_match.group(1)

    t = re.sub(r"Claude Target Specific Output\s*", "", t, flags=re.I)
    t = re.sub(r"JSON Audit Object[\s\S]*", "", t, flags=re.I)
    t = re.sub(r"^\s*\*\*\s*PART\s*\d+\s*:.*$", "", t, flags=re.I | re.M)
    t = re.sub(r"(?:Claude|GPT|ChatGPT|Gemini|DALL-?E|Midjourney|FLUX|OpenAI)\s*(?:Target\s*)?Prompt\s*:\s*", "", t, flags=re.I)
    t = re.sub(r"A\.I\.Z\.E\.N\..*?(?:InkOS\.|(?=\n\n))", "", t, flags=re.I | re.S)
    t = re.sub(r"You are a highly advanced.*?(?:InkOS\.|(?=\n\n))", "", t, flags=re.I | re.S)
    for tag in ("quality-bar", "edge-cases", "constraints", "role", "task", "visual-aesthetic", "strategic-focus"):
        t = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", t, flags=re.I | re.S)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"```[\s\S]*?```", "", t)
    t = re.sub(r"^\s*\{[\s\S]*\}\s*$", "", t, flags=re.M)
    t = re.sub(r"^\s*#{1,6}\s.*$", "", t, flags=re.M)
    t = t.replace("**", "").replace("__", "")
    t = re.sub(r"^(?:System\s*Prompt|REFINED_PROMPT|PROMPT|OUTPUT|thinking)\s*:\s*", "", t, flags=re.I | re.M)
    return re.sub(r"\n{3,}", "\n\n", t).strip()

def _process_prompt(intent_val: str, model_selection: str, action_intent: str, cfg: dict):
    # If the user selected a specific action, prepend it to the raw prompt
    if action_intent != "✨ Auto-Refine":
        intent_val = f"[{action_intent}] {intent_val}"

    cleaned, violations = sanitize_input(intent_val)
    if violations:
        st.error("⚠ Blocked by security policy.")
        return

    with st.spinner("Distilling ink..."):
        run_cfg = dict(cfg)
        payload = assemble_master_payload(cleaned, run_cfg, _get_dna_context())
        
        target_map = {"A.I.Z.E.N. Core": "auto", "Claude 3.5 Sonnet": "claude", "Gemini 1.5 Pro": "gemini"}
        actual_target = target_map.get(model_selection, "auto")

        try:
            result, audit, _ = run_refinement_and_audit(
                payload, resolve_target_model(actual_target, cleaned)[0],
                cfg.get("framework", "RACE"), cfg.get("source_lang", "English"),
                cfg.get("aesthetic_choice", "Default"), hikmah_style=str(cfg.get("hikmah_style") or "None"), skip_security=False,
            )
            result = extract_clean_output(result)
            if not result or result.strip() == "":
                result = "Engine returned an empty response. Verify AI uplink."
        except Exception as e:
            result = f"[ UPLINK FAILED ]\n\nThe A.I.Z.E.N. core encountered an error:\n{str(e)}"

        history = st.session_state.get(K.HISTORY, [])
        history.append({"input": cleaned, "output": result, "time": datetime.now(WAT_TZ).isoformat()})
        st.session_state[K.HISTORY] = history[-50:]
        
        st.session_state[K.LAST_RESULT] = str(result)
        st.session_state[K.LAST_INPUT] = str(cleaned)

def render_workspace(cfg: dict) -> None:
    # Title Header
    st.markdown(
        '<div class="brand-title" style="font-size: 24px; text-align: left; margin-bottom: 20px;">'
        '<span style="color: #4299E1;">AmeerInk</span> <br> InkOS'
        '</div>', 
        unsafe_allow_html=True
    )
    
    prefill = st.session_state.get("prefill_input", st.session_state.get(K.LAST_INPUT, ""))

    # ── SECTION 1: SOURCE PROMPT ──
    st.markdown('<div style="font-family: Montserrat; font-size: 16px; font-weight: 600; margin-bottom: 8px;">1. Source Prompt <span style="font-family: Cairo; color: #4299E1;">الموجه الأصلي</span></div>', unsafe_allow_html=True)
    with st.container(border=True):
        intent_val = st.text_area(
            "Draft", 
            value=prefill, 
            height=150, 
            placeholder="Enter your original prompt here...\nاكتب موجهك الأصلي هنا...", 
            label_visibility="collapsed"
        )
        
        # Word count footer
        word_count = len(intent_val.split()) if intent_val.strip() else 0
        st.markdown(f'<div style="text-align: right; font-size: 10px; color: #7A7A7A; margin-top: -10px;">{word_count} / 2000</div>', unsafe_allow_html=True)

    st.write("") # Spacing

    # ── SECTION 2: REFINEMENT CONTROLS ──
    st.markdown('<div style="font-family: Montserrat; font-size: 16px; font-weight: 600; margin-bottom: 8px;">2. Refinement Controls <span style="font-family: Cairo; color: #4299E1;">عناصر التحسين</span></div>', unsafe_allow_html=True)
    with st.container(border=True):
        # Two-column layout inside the control box for compactness
        c1, c2 = st.columns(2)
        with c1:
            st.caption("TARGET AI MODEL")
            target_model = st.selectbox("Model", AVAILABLE_MODELS, label_visibility="collapsed")
        with c2:
            st.caption("REFINEMENT INTENT")
            action_intent = st.selectbox("Intent", INTENT_ACTIONS, label_visibility="collapsed")
        
        st.write("")
        execute = st.button("Refine Prompt / تحسين الموجه", type="primary", use_container_width=True)

    if execute and intent_val.strip():
        _process_prompt(intent_val, target_model, action_intent, cfg)
        st.rerun()

    st.write("") # Spacing

    # ── SECTION 3: REFINED PROMPT (Shows only if result exists) ──
    result = st.session_state.get(K.LAST_RESULT)
    if result:
        st.markdown('<div style="font-family: Montserrat; font-size: 16px; font-weight: 600; margin-bottom: 8px;">3. Refined Prompt <span style="font-family: Cairo; color: #4299E1;">الموجه المحسن</span></div>', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"<div style='white-space: pre-wrap; font-size: 15px; line-height: 1.6;'>{result}</div>", unsafe_allow_html=True)
            
            st.divider()
            
            col_reset, col_copy = st.columns(2)
            with col_reset:
                if st.button("Reset / إعادة تعيين", use_container_width=True):
                    st.session_state[K.LAST_RESULT] = None
                    st.session_state["prefill_input"] = ""
                    st.session_state[K.LAST_INPUT] = ""
                    st.rerun()
            with col_copy:
                st.button("Copy / نسخ", type="primary", use_container_width=True)
