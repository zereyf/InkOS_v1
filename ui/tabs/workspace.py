"""ui/tabs/workspace.py — Workspace Tab."""
import os
import time
import difflib
import random
import streamlit as st
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from groq import Groq
from state import K
from security.sanitizer import sanitize_input
from engine.refiner import run_refinement_and_audit
from forge.prompt_assembler import assemble_master_payload
from forge.intelligence import resolve_target_model

WAT_TZ = timezone(timedelta(hours=1))

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
QUOTES = [
    "A great prompt is architecture, not words.",
    "الكلمة الصحيحة تغيّر كل شيء",
    "Precision is the highest form of intelligence.",
]

def _get_dna_context() -> dict:
    return {K.INK_DNA:str(st.session_state.get(K.INK_DNA) or ""),K.INTEL_DNA:str(st.session_state.get(K.INTEL_DNA) or ""),K.HIKMAH_DNA:str(st.session_state.get(K.HIKMAH_DNA) or "")}

def _extract_telemetry(result: str, start_time: float) -> Dict[str, Any]:
    latency_ms = int((time.perf_counter() - start_time) * 1000)
    words = result.split(); word_count = len(words)
    density = round(len(result) / word_count, 2) if word_count > 0 else 0
    return {"latency_ms":latency_ms,"word_count":word_count,"density":density}

def _clean_output(text: str) -> str:
    for label in ("REFINED_PROMPT:", "PROMPT:", "OUTPUT:", "thinking:"):
        text = text.replace(label, "")
    return text.replace("<", "").replace(">", "").strip()

def _analysis_report(prompt: str) -> Dict[str, Any]:
    words = prompt.split()
    clarity = min(95, 35 + len(words) // 2)
    specificity = min(95, 20 + sum(1 for w in words if len(w) > 6) * 3)
    context = min(95, 15 + prompt.count("\n") * 8 + (20 if "for" in prompt.lower() else 0))
    effectiveness = min(95, int((clarity + specificity + context) / 3) + 10)
    notes: List[str] = []
    if "audience" not in prompt.lower(): notes.append("⚠ Missing: target audience")
    if "cool" in prompt.lower(): notes.append("⚠ Vague: \"cool\" — be specific")
    if any(w in prompt.lower() for w in ["build", "create", "generate", "design"]): notes.append("✓ Strong action verb detected")
    return {"clarity":clarity,"specificity":specificity,"context":context,"effectiveness":effectiveness,"notes":notes[:3]}

def _bar(label: str, value: int):
    blocks = "█" * (value // 10) + "░" * (10 - value // 10)
    st.markdown(f"`{label:<12} {blocks}  {value}%`")

def _render_loader(shell, idx: int, started: float):
    elapsed = int(time.perf_counter() - started)
    quote = QUOTES[(elapsed // 4) % len(QUOTES)]
    progress = int((idx / len(PIPELINE_STEPS)) * 100)
    with shell.container():
        st.markdown(f"### ⚡ CIPHER ENGINE  //  EXECUTING  `[timer {elapsed//60:02d}:{elapsed%60:02d}]`")
        st.progress(progress)
        for i, (name, sub) in enumerate(PIPELINE_STEPS):
            if i < idx:
                st.markdown(f"✅ **{name}**")
            elif i == idx:
                st.markdown(f"🔄 **{name}...**")
                st.caption(sub)
            else:
                st.markdown(f"⚪ {name}")
        st.caption(f"*{quote}*")

def render_workspace(cfg: dict) -> None:
    st.markdown("<div class='topbar'><div style='display:flex;gap:8px;align-items:center'><span class='brand'>InkOS</span><span class='tag mono'>v1</span></div></div>", unsafe_allow_html=True)
    mode = st.segmented_control("Mode", ["Balanced", "Precision", "Creative"], default="Balanced", key="refine_mode_pills")
    st.session_state["refinement_mode"] = mode

    templates = {
        "Blog Post": "Write a blog post about [topic] for [audience] with 3 key takeaways and a CTA.",
        "Email": "Draft a concise email to [recipient] about [topic] with clear next steps.",
        "Code": "Generate [language] code that [task], include edge cases and tests.",
        "Image": "Create an image prompt for [subject] in [style], lighting, camera, and composition details.",
        "Research": "Create a research plan for [topic] including hypothesis, methods, and sources.",
    }
    picked = st.pills("Templates", list(templates.keys()), selection_mode="single", label_visibility="collapsed")
    if picked and st.button(f"Use template: {picked}"):
        st.session_state["ta_input_widget"] = templates[picked]

    audio_bytes = st.audio_input("Voice", label_visibility="collapsed")
    if audio_bytes:
        current_audio_hash = hash(audio_bytes.getvalue())
        if st.session_state.get("last_audio_hash") != current_audio_hash:
            try:
                client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                tx = client.audio.transcriptions.create(file=("audio.wav", audio_bytes.read()), model="whisper-large-v3", prompt="Arabic Education terminology and dialectal nuance.")
                if tx.text:
                    st.session_state["ta_input_widget"] = f"{st.session_state.get('ta_input_widget','')} {tx.text}".strip(); st.session_state["last_audio_hash"] = current_audio_hash; st.rerun()
            except Exception as e: st.error(f"Voice input failed: {e}")

    intent_val = st.text_area("Prompt", height=190, placeholder="Describe what you want to create...", label_visibility="collapsed", key="ta_input_widget")
    st.caption(f"{len(intent_val)} characters")
    execute = st.button("⚡ Refine Prompt", use_container_width=True, type="primary")

    if execute:
        cleaned, violations = sanitize_input(intent_val)
        if not cleaned: st.warning("Please enter an input prompt before executing.")
        elif violations: st.error("Input blocked by security policy. Remove prompt-injection directives and try again.")
        else:
            report = _analysis_report(cleaned)
            with st.container(border=True):
                st.markdown("**PROMPT INTELLIGENCE REPORT**")
                _bar("Clarity", report["clarity"])
                _bar("Specificity", report["specificity"])
                _bar("Context", report["context"])
                _bar("Effectiveness", report["effectiveness"])
                for n in report["notes"]: st.caption(n)
            loader = st.empty(); started = time.perf_counter()
            for idx in range(len(PIPELINE_STEPS)):
                _render_loader(loader, idx, started)
                time.sleep(0.25)
            try:
                resolved_target, resolved_reason = resolve_target_model(cfg.get("target_model"), cleaned)
                st.session_state[K.AUTO_TARGET] = resolved_target; st.session_state[K.AUTO_REASON] = resolved_reason
                payload = assemble_master_payload(cleaned, cfg, _get_dna_context()); start = time.perf_counter()
                result, audit, _ = run_refinement_and_audit(payload, resolved_target, cfg["framework"], cfg["source_lang"], cfg["aesthetic_choice"], hikmah_style=str(cfg.get("hikmah_style") or "None"), skip_security=st.session_state.get(K.IS_ADMIN, False) and cfg.get("expert_mode", False))
                if audit.get("score", 0) < 70:
                    result, audit, _ = run_refinement_and_audit(payload, resolved_target, cfg["framework"], cfg["source_lang"], cfg["aesthetic_choice"], hikmah_style=str(cfg.get("hikmah_style") or "None"), skip_security=st.session_state.get(K.IS_ADMIN, False) and cfg.get("expert_mode", False))
                    st.info("Enhanced — ran 2 refinement passes")
                result = _clean_output(result)
                telemetry = _extract_telemetry(result, start)
                st.session_state[K.LAST_RESULT]=result; st.session_state[K.LAST_AUDIT]=audit; st.session_state[K.LAST_INPUT]=cleaned
                hist = st.session_state.get(K.HISTORY, [])
                hist.append({"id":datetime.now().strftime('%H%M%S'),"input": cleaned, "output": result, "ts": datetime.now(WAT_TZ).isoformat(timespec='seconds'), "time": datetime.now(WAT_TZ).strftime('%Y-%m-%d %H:%M'), "target": resolved_target, "framework": cfg["framework"], "aesthetic": cfg["aesthetic_choice"], "score": audit.get("score", 0), "latency": f"{telemetry['latency_ms']}ms", "density": telemetry["density"], "word_count": telemetry["word_count"]})
                st.session_state[K.HISTORY] = hist[-50:]
            except Exception as e: st.error(f"Execution failed: {e}")
            finally:
                loader.empty()

    if st.session_state.get(K.LAST_RESULT):
        st.text_area("Refined Output", value=st.session_state.get(K.LAST_RESULT,""), height=260)
        c1,c2 = st.columns(2)
        with c1:
            if st.button("Copy Result"): st.toast("✓ Copied", icon="✅")
        with c2: st.download_button("Export .txt", data=st.session_state.get(K.LAST_RESULT,""), file_name="inkos_refined_prompt.txt", mime="text/plain")

        st.text_input("Designation", key="v_t")
        st.text_input("Forensic Tags", key="v_g")
        if st.button("Secure to Vault", use_container_width=True):
            uid = st.session_state.get(K.USER_HASH); title_val = st.session_state.get("v_t", "").strip(); tags_val = st.session_state.get("v_g", "").strip()
            if not title_val:
                st.error("Designation is required")
            elif uid and "GUEST_" not in uid.upper():
                from vault.vault_engine import save_prompt
                _, err = save_prompt(uid, title=title_val, tags=tags_val, content=st.session_state.get(K.LAST_RESULT), target=st.session_state.get(K.AUTO_TARGET), framework=cfg["framework"], score=(st.session_state.get(K.LAST_AUDIT) or {}).get("score", 0))
                if not err:
                    st.success("✓ Secured to Vault")
                    st.session_state["v_t"] = ""; st.session_state["v_g"] = ""
                else: st.error("Vault unavailable — check connection" if "Vault offline" in err else err)
            else: st.error("Vault unavailable — check connection")
    else:
        st.info("No refined output yet.\n\nلا يوجد مخرجات بعد")
