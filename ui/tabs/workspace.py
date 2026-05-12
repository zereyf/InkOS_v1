"""
ui/tabs/workspace.py — Tech-Noir Workspace
=============================================
v9.1: Native Architecture Patch.
      - Removed invalid 'size' argument from st.button.
"""
import streamlit as st
import re
from datetime import datetime, timezone, timedelta
from state import K
from security.sanitizer import sanitize_input
from engine.refiner import run_refinement_and_audit
from forge.prompt_assembler import assemble_master_payload
from forge.intelligence import resolve_target_model

WAT_TZ = timezone(timedelta(hours=1))

AVAILABLE_MODELS = ["A.I.Z.E.N. Core", "Claude 3.5", "Gemini 1.5"]

def _get_dna_context() -> dict:
    return {
        K.INK_DNA:    str(st.session_state.get(K.INK_DNA)    or ""),
        K.INTEL_DNA:  str(st.session_state.get(K.INTEL_DNA)  or ""),
        K.HIKMAH_DNA: str(st.session_state.get(K.HIKMAH_DNA) or ""),
    }

def extract_clean_output(raw: str) -> str:
    t = str(raw or "")
    t = re.sub(r"Claude Target Specific Output\s*", "", t, flags=re.I)
    t = re.sub(r"JSON Audit Object[\s\S]*", "", t, flags=re.I)
    t = re.sub(r"\*\*\s*PART\s*\d+\s*:.*?(?=\*\*\s*PART\s*\d+\s*:|$)", "", t, flags=re.I | re.S)
    t = re.sub(r"(?:Claude|GPT|ChatGPT|Gemini|DALL-?E|Midjourney|FLUX|OpenAI)\s*(?:Target\s*)?Prompt\s*:\s*", "", t, flags=re.I)
    t = re.sub(r"A\.I\.Z\.E\.N\..*?(?:InkOS\.|(?=\n\n))", "", t, flags=re.I | re.S)
    t = re.sub(r"You are a highly advanced.*?(?:InkOS\.|(?=\n\n))", "", t, flags=re.I | re.S)
    for tag in ("quality-bar","edge-cases","constraints","role","task","visual-aesthetic","strategic-focus"):
        t = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", t, flags=re.I | re.S)
    t = re.sub(r"<[^>]+>", "", t)
    t = re.sub(r"```[\s\S]*?```", "", t)
    t = re.sub(r"^\s*#{1,6}\s.*$", "", t, flags=re.M)
    t = t.replace("**", "").replace("__", "")
    t = re.sub(r"^(?:System\s*Prompt|REFINED_PROMPT|PROMPT|OUTPUT|thinking)\s*:\s*", "", t, flags=re.I | re.M)
    return re.sub(r"\n{3,}", "\n\n", t).strip()

def _render_header():
    st.markdown("""
        <div class="brand-title">İnkOS</div>
        <div class="brand-subtitle">Terminal Refinement Engine</div>
        <br><br>
    """, unsafe_allow_html=True)

def _render_desk(cfg: dict):
    _render_header()
    
    # Quick Actions
    st.caption("QUICK ACTIONS")
    cols = st.columns(4)
    actions = [("Refine", "Refine this:\n"), ("Expand", "Expand this:\n"), ("Focus", "Focus this:\n"), ("Format", "Format this:\n")]
    
    prefill = st.session_state.get("prefill_input", "")
    
    for i, (label, prompt) in enumerate(actions):
        if cols[i].button(label, use_container_width=True):
            prefill = prompt
            st.session_state["prefill_input"] = prompt
            st.rerun()

    # The Input Area
    with st.container(border=True):
        intent_val = st.text_area("TARGET INTENT", value=prefill, height=150, placeholder="Initialize prompt sequence...", label_visibility="collapsed")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            target_model = st.selectbox("MODEL", AVAILABLE_MODELS, label_visibility="collapsed")
        with col2:
            send = st.button("EXECUTE", type="primary", use_container_width=True)

    if send and intent_val.strip():
        _process_prompt(intent_val, target_model, cfg)

def _process_prompt(intent_val: str, model_selection: str, cfg: dict):
    cleaned, violations = sanitize_input(intent_val)
    if violations: st.error("⚠ Blocked by security policy."); return

    with st.spinner("Compiling sequence..."):
        run_cfg = dict(cfg)
        payload = assemble_master_payload(cleaned, run_cfg, _get_dna_context())
        
        target_map = {"A.I.Z.E.N. Core": "auto", "Claude 3.5": "claude", "Gemini 1.5": "gemini"}
        actual_target = target_map.get(model_selection, "auto")

        try:
            result, audit, _ = run_refinement_and_audit(
                payload, resolve_target_model(actual_target, cleaned)[0],
                cfg.get("framework", "RACE"), cfg.get("source_lang", "English"),
                cfg.get("aesthetic_choice", "Default"), hikmah_style=str(cfg.get("hikmah_style") or "None"), skip_security=False,
            )
            result = extract_clean_output(result)
            if not result or result.strip() == "": result = "Engine returned an empty response. Verify AI uplink."
        except Exception as e:
            result = f"[ UPLINK FAILED ]\n\nThe A.I.Z.E.N. core encountered an error:\n{str(e)}"

        history = st.session_state.get(K.HISTORY, [])
        history.append({"input": cleaned, "output": result, "time": datetime.now(WAT_TZ).isoformat()})
        st.session_state[K.HISTORY] = history[-50:]
        
        st.session_state[K.LAST_RESULT] = str(result)
        st.session_state[K.LAST_INPUT] = str(cleaned)
        st.rerun()

def _render_studio():
    _render_header()
    
    raw_input = st.session_state.get(K.LAST_INPUT, "")
    result = st.session_state.get(K.LAST_RESULT, "")

    st.caption("SOURCE INTENT")
    with st.container(border=True):
        st.write(raw_input)
        # BUG FIX: Removed size="small" argument
        if st.button("Edit Source", use_container_width=False):
            st.session_state[K.LAST_RESULT] = None
            st.session_state["prefill_input"] = raw_input
            st.rerun()

    st.caption("REFINED OUTPUT")
    with st.container(border=True):
        st.markdown(f"**{result}**") 
        
        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.button("Copy Output", use_container_width=True)
        c2.button("Share", use_container_width=True)
        if c3.button("Reset Terminal", use_container_width=True):
            st.session_state[K.LAST_RESULT] = None
            st.session_state["prefill_input"] = ""
            st.rerun()

def render_workspace(cfg: dict) -> None:
    if st.session_state.get(K.LAST_RESULT):
        _render_studio()
    else:
        _render_desk(cfg)
