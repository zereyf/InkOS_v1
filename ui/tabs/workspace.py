"""ui/tabs/workspace.py — Workspace Tab."""
import time, re, os, difflib
import streamlit as st
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from groq import Groq
from state import K
from security.sanitizer import sanitize_input
from engine.refiner import run_refinement_and_audit
from forge.prompt_assembler import assemble_master_payload
from forge.intelligence import resolve_target_model

WAT_TZ = timezone(timedelta(hours=1))

def _get_dna_context() -> dict:
    return {K.INK_DNA:str(st.session_state.get(K.INK_DNA) or ""),K.INTEL_DNA:str(st.session_state.get(K.INTEL_DNA) or ""),K.HIKMAH_DNA:str(st.session_state.get(K.HIKMAH_DNA) or "")}

def _extract_telemetry(result: str, start_time: float) -> Dict[str, Any]:
    latency_ms = int((time.perf_counter() - start_time) * 1000)
    words = result.split(); word_count = len(words)
    density = round(len(result) / word_count, 2) if word_count > 0 else 0
    palette = list(set(re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', result)))
    return {"latency_ms":latency_ms,"word_count":word_count,"density":density,"palette":palette[:5]}

def _render_score(audit: dict):
    score = int((audit or {}).get("score", 0))
    tier, klass = ("Excellent", "score-excellent") if score >= 90 else (("Good", "score-good") if score >= 75 else ("Fair", "score-fair"))
    st.markdown(f"<div style='text-align:right; margin: 8px 0 12px'><span class='score-pill {klass}'>{tier}</span></div>", unsafe_allow_html=True)

def _render_diff(before: str, after: str):
    b_lines, a_lines = before.splitlines(), after.splitlines(); out=[]
    for line in difflib.ndiff(b_lines, a_lines):
        esc = line[2:].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        if line.startswith('+ '): out.append(f"<div class='diff-add'>+ {esc}</div>")
        elif line.startswith('- '): out.append(f"<div class='diff-del'>- {esc}</div>")
        elif line.startswith('  '): out.append(f"<div>  {esc}</div>")
    st.markdown("<div class='diff-box'>" + "".join(out) + "</div>", unsafe_allow_html=True)

def render_workspace(cfg: dict) -> None:
    st.markdown("<div class='topbar'><div style='display:flex;gap:8px;align-items:center'><span class='brand'>InkOS</span><span class='tag mono'>v1</span></div><a href='https://github.com' target='_blank' style='color:#71717a;text-decoration:none'>⌁</a></div>", unsafe_allow_html=True)
    mode = st.radio("Mode", ["Balanced", "Precision", "Creative"], horizontal=True, label_visibility="collapsed", key="refine_mode_pills")
    st.session_state["refinement_mode"] = mode

    audio_bytes = st.audio_input("Voice", label_visibility="collapsed")
    st.markdown("<div class='voice mono'><span>🎙 Voice input</span><span>00:00</span></div>", unsafe_allow_html=True)
    if audio_bytes:
        current_audio_hash = hash(audio_bytes.getvalue())
        if st.session_state.get("last_audio_hash") != current_audio_hash:
            try:
                client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                tx = client.audio.transcriptions.create(file=("audio.wav", audio_bytes.read()), model="whisper-large-v3", prompt="Arabic Education terminology and dialectal nuance.")
                if tx.text:
                    st.session_state["ta_input_widget"] = f"{st.session_state.get('ta_input_widget','')} {tx.text}".strip(); st.session_state["last_audio_hash"] = current_audio_hash; st.rerun()
            except Exception as e: st.error(f"[!] Voice Uplink Failed: {e}")

    intent_val = st.text_area("Prompt", height=190, placeholder="Describe what you want to create...", label_visibility="collapsed", key="ta_input_widget")
    st.caption(f"{len(intent_val)} characters")

    st.markdown("<div class='primary-btn'>", unsafe_allow_html=True)
    execute = st.button("⚡ Refine Prompt", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if execute:
        cleaned, violations = sanitize_input(intent_val)
        if not cleaned: st.warning("Please enter an input prompt before executing.")
        elif violations: st.error("Input blocked by security policy. Remove prompt-injection directives and try again.")
        else:
            try:
                resolved_target, resolved_reason = resolve_target_model(cfg.get("target_model"), cleaned)
                st.session_state[K.AUTO_TARGET] = resolved_target; st.session_state[K.AUTO_REASON] = resolved_reason
                payload = assemble_master_payload(cleaned, cfg, _get_dna_context()); start = time.perf_counter()
                result, audit, _ = run_refinement_and_audit(payload, resolved_target, cfg["framework"], cfg["source_lang"], cfg["aesthetic_choice"], hikmah_style=str(cfg.get("hikmah_style") or "None"), skip_security=st.session_state.get(K.IS_ADMIN, False) and cfg.get("expert_mode", False))
                _extract_telemetry(result, start)
                st.session_state[K.LAST_RESULT]=result; st.session_state[K.LAST_AUDIT]=audit; st.session_state[K.LAST_INPUT]=cleaned
                hist = st.session_state.get(K.HISTORY, []); hist.append({"input": cleaned, "output": result, "ts": datetime.now(WAT_TZ).isoformat(timespec='seconds')}); st.session_state[K.HISTORY] = hist[-50:]
            except Exception as e: st.error(f"Execution failed: {e}")

    if st.session_state.get(K.LAST_RESULT):
        _render_score(st.session_state.get(K.LAST_AUDIT))
        left,right = st.columns(2)
        with left: st.text_area("Before", value=st.session_state.get(K.LAST_INPUT,""), height=260)
        with right: st.text_area("After", value=st.session_state.get(K.LAST_RESULT,""), height=260)
        _render_diff(st.session_state.get(K.LAST_INPUT,""), st.session_state.get(K.LAST_RESULT,""))
        c1,c2 = st.columns(2)
        with c1:
            if st.button("Copy Result"): st.toast("✓ Copied", icon="✅")
        with c2: st.download_button("Export .txt", data=st.session_state.get(K.LAST_RESULT,""), file_name="inkos_refined_prompt.txt", mime="text/plain")

        st.text_input("Designation", key="v_t")
        st.text_input("Forensic Tags", key="v_g")
        if st.button("Secure to Vault", use_container_width=True):
            uid = st.session_state.get(K.USER_HASH); title_val = st.session_state.get("v_t", "").strip(); tags_val = st.session_state.get("v_g", "").strip()
            if title_val and tags_val and uid and "GUEST_" not in uid.upper():
                from vault.vault_engine import save_prompt
                _, err = save_prompt(uid, title=title_val, tags=tags_val, content=st.session_state.get(K.LAST_RESULT), target=st.session_state.get(K.AUTO_TARGET), framework=cfg["framework"], score=(st.session_state.get(K.LAST_AUDIT) or {}).get("score", 0))
                if not err: st.toast("[◈] ASSET SECURED.", icon="✅")
                else: st.error(err)
            else: st.toast("[!] Designation and Identity required.", icon="⚠️")
