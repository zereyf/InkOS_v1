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
    ("Analyzing prompt structure", "Mapping clauses, constraints, and ambiguity..."),
    ("Detecting intent & target model", "Resolving best model path for the mission..."),
    ("Applying CIPHER identity layer", "Injecting role, guardrails, and objective spine..."),
    ("Assembling forge & persona layers", "Applying rhetoric and DNA layers..."),
    ("Running primary refiner loop", "Executing refinement passes with evaluator gates..."),
    ("Evaluator audit — scoring output", "Scoring clarity, specificity, and actionability..."),
    ("Security & sanitizer scan", "Verifying clean output and safety posture..."),
    ("Finalizing refined prompt", "Packaging final output and telemetry..."),
]

def _get_dna_context() -> dict:
    return {K.INK_DNA:str(st.session_state.get(K.INK_DNA) or ""),K.INTEL_DNA:str(st.session_state.get(K.INTEL_DNA) or ""),K.HIKMAH_DNA:str(st.session_state.get(K.HIKMAH_DNA) or "")}

def _extract_telemetry(result: str, start_time: float) -> Dict[str, Any]:
    latency_ms = int((time.perf_counter() - start_time) * 1000)
    words = result.split(); word_count = len(words)
    density = round(len(result) / word_count, 2) if word_count > 0 else 0
    return {"latency_ms":latency_ms,"word_count":word_count,"density":density}

def extract_clean_output(raw_response: str) -> str:
    text = str(raw_response or "")
    text = re.sub(r"\*\*\s*PART\s*1:.*?(?=\*\*\s*PART\s*2:|$)", "", text, flags=re.I|re.S)
    text = re.sub(r"\*\*\s*PART\s*2:\s*", "", text, flags=re.I)
    for tag in ("quality-bar", "edge-cases", "constraints", "quality_bar", "edge_cases"):
        text = re.sub(rf"<{tag}[^>]*>.*?</{tag}>", "", text, flags=re.I|re.S)
    text = re.sub(r"```(?:json|xml)?[\s\S]*?```", "", text, flags=re.I)
    text = re.sub(r"\{\s*\"score\"[\s\S]*?\}\s*$", "", text, flags=re.I)
    text = text.replace("**", "")
    text = re.sub(r"^\s*#{1,6}.*$", "", text, flags=re.M)
    text = re.sub(r"System\s*Prompt\s*:\s*", "", text, flags=re.I)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"^(?:REFINED_PROMPT|PROMPT|OUTPUT|thinking)\s*:\s*", "", text, flags=re.I|re.M)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def _analysis_report(prompt: str) -> Dict[str, Any]:
    words = prompt.split()
    clarity = min(95, 35 + len(words) // 2)
    specificity = min(95, 20 + sum(1 for w in words if len(w) > 6) * 3)
    context = min(95, 15 + prompt.count("\n") * 8 + (20 if "for" in prompt.lower() else 0))
    effectiveness = min(95, int((clarity + specificity + context) / 3) + 10)
    return {"clarity":clarity,"specificity":specificity,"context":context,"effectiveness":effectiveness,"notes":[]}

def _save_local(uid: str, title: str, tags: str, cfg: dict) -> None:
    local_items = st.session_state.get(LOCAL_VAULT_KEY, [])
    local_items.insert(0, {
        "id": f"local-{int(time.time()*1000)}",
        "user_hash": uid,
        "title": title,
        "tags": tags,
        "content": st.session_state.get(K.LAST_RESULT, ""),
        "target": st.session_state.get(K.AUTO_TARGET, "ChatGPT"),
        "framework": cfg["framework"],
        "score": (st.session_state.get(K.LAST_AUDIT) or {}).get("score", 0),
        "created_at": datetime.now(timezone.utc).isoformat(),
    })
    st.session_state[LOCAL_VAULT_KEY] = local_items[:200]

def render_workspace(cfg: dict) -> None:
    st.markdown("<div class='topbar'><div style='display:flex;gap:8px;align-items:center'><span class='brand'>InkOS</span><span class='tag mono'>v1</span></div></div>", unsafe_allow_html=True)
    intent_val = st.text_area("Prompt", height=190, placeholder="Describe what you want to create...", label_visibility="collapsed", key="ta_input_widget")
    execute = st.button("⚡ Refine Prompt", use_container_width=True, type="primary", key="btn_refine_prompt")
    if execute and intent_val.strip():
        cleaned, violations = sanitize_input(intent_val)
        if violations:
            st.error("Input blocked by security policy.")
        else:
            payload = assemble_master_payload(cleaned, cfg, _get_dna_context()); start = time.perf_counter()
            result, audit, _ = run_refinement_and_audit(payload, resolve_target_model(cfg.get("target_model"), cleaned)[0], cfg["framework"], cfg["source_lang"], cfg["aesthetic_choice"], hikmah_style=str(cfg.get("hikmah_style") or "None"), skip_security=False)
            result = extract_clean_output(result)
            st.session_state[K.LAST_RESULT] = result
            st.session_state[K.LAST_AUDIT] = audit
            st.session_state[K.LAST_INPUT] = cleaned
            st.session_state[K.HISTORY] = (st.session_state.get(K.HISTORY, []) + [{"input": cleaned, "output": result, "time": datetime.now(WAT_TZ).isoformat()}])[-50:]
            _extract_telemetry(result, start)
    if st.session_state.get(K.LAST_RESULT):
        st.text_area("Refined Output", value=st.session_state.get(K.LAST_RESULT,""), height=260)
        st.text_input("Designation", key="v_t")
        st.text_input("Forensic Tags", key="v_g")
        if st.button("Secure to Vault", use_container_width=True, key="btn_secure_vault"):
            uid = st.session_state.get(K.USER_HASH)
            title_val = st.session_state.get("v_t", "").strip()
            tags_val = st.session_state.get("v_g", "").strip()
            if not title_val:
                st.error("Please add a designation before securing")
            elif not uid or "GUEST_" in str(uid).upper():
                st.error("Vault unavailable — check connection")
            else:
                if SUPABASE_MISSING:
                    _save_local(uid, title_val, tags_val, cfg)
                    st.session_state["vault_local_banner"] = True
                    st.session_state["vault_refresh_nonce"] = time.time()
                    st.session_state["vault_saved_until"] = time.time() + 2
                    st.rerun()
                else:
                    _, err = save_prompt(uid, title=title_val, tags=tags_val, content=st.session_state.get(K.LAST_RESULT), target=st.session_state.get(K.AUTO_TARGET), framework=cfg["framework"], score=(st.session_state.get(K.LAST_AUDIT) or {}).get("score", 0))
                    if err:
                        st.error("Vault unavailable — check connection")
                    else:
                        st.session_state["vault_refresh_nonce"] = time.time()
                        st.session_state["vault_saved_until"] = time.time() + 2
                        st.rerun()
        if st.session_state.get("vault_saved_until", 0) > time.time():
            st.success("✓ Secured!")
    else:
        st.markdown("<div class='empty-state'><div>Your refined prompt will appear here</div><div>ستظهر نتيجتك هنا</div></div>", unsafe_allow_html=True)
