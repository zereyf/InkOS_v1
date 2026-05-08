"""
ui/tabs/workspace.py — Workspace Tab
======================================
v31.2: Hardened Header Build — The AmeerInk Protocol.
       - Eliminated HTML Leaks (Atomic String Concatenation).
       - Fixed Tag Fractures (Removed textwrap.dedent).
       - Stabilized Thermal HUD (Zero-Lag Cognitive Metrics).
       - Fully Consolidated Section Flow (No duplicate keys).
"""

import textwrap
import streamlit as st
from datetime import datetime, timezone
from typing import Tuple

from state import K
from security.sanitizer import sanitize_input
from engine.refiner import run_refinement_and_audit
from engine.router import route_to_target
from engine.cognitive_map import detect_arabic_pattern
from i18n.translations import t

# ── DNA INJECTION ENGINE ─────────────────────────────────────────────────────

def _apply_dna_triggers(text: str) -> Tuple[str, list]:
    detected = []
    processed = text
    triggers = {"/ink": K.INK_DNA, "/intel": K.INTEL_DNA, "/hikmah": K.HIKMAH_DNA}
    for trigger, dna_key in triggers.items():
        if trigger.lower() in text.lower():
            dna = st.session_state.get(dna_key, "")
            processed = f"[DNA INJECTION: {trigger.upper()}]\n{dna}\n\n[USER INTENT]\n{processed}"
            detected.append(trigger.upper())
    return processed, detected

# ── UI COMPONENTS ─────────────────────────────────────────────────────────────

def _render_score_block(audit: dict, expert_mode: bool = False) -> None:
    safe_audit = audit or {}
    score = int(safe_audit.get("score", 0))
    precision = int(safe_audit.get("precision", 0))
    alignment = int(safe_audit.get("alignment", 0))
    
    thermal_status = "STABLE" if score > 80 else "CRITICAL" if score < 40 else "FLUCTUATING"
    target = st.session_state.get(K.AUTO_TARGET, "Unknown")
    reason = st.session_state.get(K.AUTO_REASON, "Manual")
    status_color = "#4CAF9A" if score > 85 else "var(--gold)"
    
    p_pct, a_pct = min(100, (precision/40)*100), min(100, (alignment/40)*100)

    # 🟢 ATOMIC UI: Collapsed score block to prevent rendering fractures
    score_html = (
        f'<div style="background:var(--bg-card); border:1px solid rgba(255,255,255,0.05); padding:22px; position:relative; overflow:hidden; margin-bottom:15px;">'
        f'<div style="position:absolute; top:0; left:0; width:40px; height:2px; background:{status_color};"></div>'
        f'<div style="position:absolute; top:10px; right:10px; text-align:right;">'
        f'<div style="font-family:var(--font-m); font-size:0.4rem; color:var(--text-dim); letter-spacing:1px;">THERMAL_EFFICIENCY</div>'
        f'<div style="font-family:var(--font-m); font-size:0.5rem; color:{status_color}; font-weight:bold;">{thermal_status}</div></div>'
        f'<div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:24px;"><div>'
        f'<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-muted); letter-spacing:2px; text-transform:uppercase;">Overall Fidelity</div>'
        f'<div style="font-family:var(--font-d); font-size:3.2rem; color:{status_color}; line-height:0.9; margin-top:4px;">{score}<span style="font-size:1.2rem;">%</span></div></div></div>'
        f'<div style="display:flex; flex-direction:column; gap:12px; margin-bottom:24px;">'
        f'<div style="display:flex; align-items:center; justify-content:space-between;"><span style="font-family:var(--font-m); font-size:0.6rem; color:var(--text-muted); width:80px;">PRECISION</span>'
        f'<div style="flex:1; height:1px; background:rgba(255,255,255,0.08); margin:0 15px; position:relative;"><div style="position:absolute; left:0; top:-1px; height:3px; width:{p_pct}%; background:var(--gold);"></div></div>'
        f'<span style="font-family:var(--font-m); font-size:0.65rem; color:var(--gold);">{precision}/40</span></div>'
        f'<div style="display:flex; align-items:center; justify-content:space-between;"><span style="font-family:var(--font-m); font-size:0.6rem; color:var(--text-muted); width:80px;">ALIGNMENT</span>'
        f'<div style="flex:1; height:1px; background:rgba(255,255,255,0.08); margin:0 15px; position:relative;"><div style="position:absolute; left:0; top:-1px; height:3px; width:{a_pct}%; background:var(--steel);"></div></div>'
        f'<span style="font-family:var(--font-m); font-size:0.65rem; color:var(--steel);">{alignment}/40</span></div></div>'
        f'<div style="background:rgba(201,168,76,0.03); border-left:2px solid var(--gold-border); padding:12px 16px;">'
        f'<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); text-transform:uppercase; margin-bottom:6px;">> Forensic Log</div>'
        f'<div style="font-family:var(--font-m); font-size:0.75rem; color:var(--text); line-height:1.6;">'
        f'<span style="color:var(--gold); font-weight:bold;">[ CIPHER ]: {target.upper()}</span> — {reason}<br>{safe_audit.get("critique", "")}</div></div></div>'
    ).replace("\n", "")
    
    st.markdown(score_html, unsafe_allow_html=True)
    if expert_mode:
        with st.expander("🛠️ NEURAL UPLINK DIAGNOSTICS"):
            st.json(safe_audit)

# ── MAIN RENDERER ─────────────────────────────────────────────────────────────

def render_workspace(cfg: dict) -> None:
    # ── 1. HEADER & LIVE METRICS ─────────────────────────────────────────────
    source_lang = cfg.get("source_lang", "English")
    raw_text = st.session_state.get("ta_input_widget") or ""
    cognitive_load = len(raw_text)

    # Active Persona Logic
    active_persona = st.session_state.get(K.ACTIVE_PERSONA)
    p_name, p_target = "", "All"
    if isinstance(active_persona, dict):
        p_name, p_target = active_persona.get("name", "").upper(), active_persona.get("target", "All")

    # Thermal Drift Warning
    current_global_target = cfg.get("target_model")
    is_misaligned = p_target != "All" and p_target != current_global_target
    misalignment_badge = f"&nbsp;<span style='background:rgba(229,62,62,0.15); color:#FF4B4B; border:1px solid #FF4B4B; padding:2px 6px; border-radius:2px; margin-left:8px; font-size:0.45rem; letter-spacing:1px; flex-shrink:0;'>⚠️ THERMAL DRIFT: TARGET MISMATCH</span>" if is_misaligned else ""

    # Badge Logic
    expert_badge = f"&nbsp;<span style='background:rgba(229,62,62,0.1); color:var(--danger); border:1px solid rgba(229,62,62,0.3); padding:2px 6px; border-radius:2px; margin-left:8px; font-size:0.45rem; letter-spacing:1px; flex-shrink:0;'>EXPERT</span>" if cfg.get("expert_mode") else ""
    islamic_badge = f"&nbsp;<span style='background:rgba(76,175,154,0.1); color:#4CAF9A; border:1px solid rgba(76,175,154,0.3); padding:2px 6px; border-radius:2px; margin-left:8px; font-size:0.45rem; letter-spacing:1px; flex-shrink:0;'>HIKMAH LATCH</span>" if cfg.get("islamic_mode") else ""
    persona_badge = f"&nbsp;<span style='background:rgba(201,168,76,0.1); color:var(--gold); border:1px solid rgba(201,168,76,0.3); padding:2px 6px; border-radius:2px; margin-left:8px; font-size:0.45rem; letter-spacing:1px; flex-shrink:0;'>PERSONA: {p_name}</span>" if p_name else ""

    # 🟢 ATOMIC HEADER: No newlines or indentation to prevent raw HTML leaks
    header_html = (
        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">'
        f'<div class="vc-header" style="margin:0; display:flex; align-items:center; flex-wrap:nowrap;">'
        f'<span class="status-dot"></span><span style="padding-right:15px; flex-shrink:0;">{t("tab_workspace", fallback="WORKSPACE")}</span>'
        f'{expert_badge}{islamic_badge}{persona_badge}{misalignment_badge}</div>'
        f'<div style="font-family:var(--font-a); color:var(--gold); font-size:1.1rem; opacity:0.9; flex-shrink:0;">حبر وفكرة</div></div>'
        f'<div style="display:flex; justify-content:space-between; font-family:var(--font-m); font-size:0.55rem; color:var(--text-dim); letter-spacing:1px; margin-bottom:15px; text-transform:uppercase; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:8px;">'
        f'<div>A.I.Z.E.N. // REF: {(st.session_state.get(K.USER_HASH) or "GHOST_ID")[:8]}</div>'
        f'<div>LOAD: {cognitive_load} B</div></div>'
    ).replace("\n", "")
    
    st.markdown(header_html, unsafe_allow_html=True)

    # ── 2. DNA ARMORY BAR ─────────────────────────────────────────────────────
    if "GUEST_" not in str(st.session_state.get(K.USER_HASH, "")).upper():
        dna_html = (
            f'<div style="display:flex; gap:10px; margin-bottom:20px;">'
            f'<div style="flex:1; background:rgba(201,168,76,0.02); border:1px solid rgba(201,168,76,0.1); padding:8px; border-radius:3px; text-align:center;">'
            f'<div style="font-size:0.5rem; color:var(--gold); font-family:var(--font-m);">DNA: /INK</div>'
            f'<div style="font-size:0.4rem; color:var(--text-muted);">{"ARMED" if st.session_state.get(K.INK_DNA) else "OFFLINE"}</div></div>'
            f'<div style="flex:1; background:rgba(201,168,76,0.02); border:1px solid rgba(201,168,76,0.1); padding:8px; border-radius:3px; text-align:center;">'
            f'<div style="font-size:0.5rem; color:var(--gold); font-family:var(--font-m);">DNA: /INTEL</div>'
            f'<div style="font-size:0.4rem; color:var(--text-muted);">{"ARMED" if st.session_state.get(K.INTEL_DNA) else "OFFLINE"}</div></div>'
            f'<div style="flex:1; background:rgba(201,168,76,0.02); border:1px solid rgba(201,168,76,0.1); padding:8px; border-radius:3px; text-align:center;">'
            f'<div style="font-size:0.5rem; color:var(--gold); font-family:var(--font-m);">DNA: /HIKMAH</div>'
            f'<div style="font-size:0.4rem; color:var(--text-muted);">{"ARMED" if st.session_state.get(K.HIKMAH_DNA) else "OFFLINE"}</div></div></div>'
        ).replace("\n", "")
        st.markdown(dna_html, unsafe_allow_html=True)

    # ── 3. INPUT AREA & VOICE UPLINK ──────────────────────────────────────────
    if "ta_input_widget" not in st.session_state:
        st.session_state["ta_input_widget"] = ""

    v_col1, v_col2 = st.columns([1, 6])
    with v_col1:
        audio_bytes = st.audio_input("Voice Uplink", label_visibility="collapsed")
        if audio_bytes:
            current_audio_hash = hash(audio_bytes.getvalue())
            if st.session_state.get("last_audio_hash") != current_audio_hash:
                with st.spinner("Transcribing..."):
                    import os
                    from groq import Groq
                    try:
                        client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
                        transcription = client.audio.transcriptions.create(
                            file=("audio.wav", audio_bytes.read()),
                            model="whisper-large-v3",
                            prompt="Arabic Education terminology and dialectal nuance."
                        )
                        if transcription.text:
                            curr_val = st.session_state.get("ta_input_widget", "")
                            st.session_state["ta_input_widget"] = f"{curr_val} {transcription.text}".strip()
                            st.session_state["last_audio_hash"] = current_audio_hash
                            st.toast("Voice Transcribed.", icon="🎙️")
                            st.rerun()
                    except Exception as e:
                        st.error(f"Voice Uplink Failed: {e}")

    with v_col2:
        # THE ONLY TEXT AREA (Key: ta_input_widget)
        intent_val = st.text_area(
            "intent", 
            height=145, 
            placeholder=t("workspace_placeholder", fallback="Input your raw idea or use Voice Uplink..."), 
            label_visibility="collapsed", 
            key="ta_input_widget" 
        )
        st.session_state["ta_input"] = intent_val

    # ── 4. 📡 LIVE LINGUISTIC INTERCEPT ──────────────────────────────────────
    if intent_val and source_lang == "Arabic (العربية)":
        p_data = detect_arabic_pattern(intent_val)
        if p_data:
            intercept_html = (
                f'<div style="margin-top:-15px; margin-bottom:15px; display:flex; align-items:center; gap:8px; opacity:0.8;">'
                f'<span style="height:6px; width:6px; background:var(--gold); border-radius:50%; box-shadow: 0 0 5px var(--gold);"></span>'
                f'<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:1px;">'
                f'PATTERN_INTERCEPT: <span style="color:var(--text); font-weight:bold;">{p_data["pattern"].upper()}</span></div></div>'
            ).replace("\n", "")
            st.markdown(intercept_html, unsafe_allow_html=True)

    if st.button(t("execute_btn", fallback="EXECUTE REFINEMENT"), use_container_width=True):
        st.session_state["athar_trace"] = False
        cleaned, _ = sanitize_input(st.session_state.get("ta_input", ""))
        if cleaned:
            import time
            
            # ── HUD INITIALIZATION ──
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            ui_text = st.empty()
            prog_bar = st.progress(0)
            
            # Phase 1: Handshake
            ui_text.markdown("`< 15% >` **[SYSTEM]** Validating payload integrity and parsing logic gates...")
            prog_bar.progress(15)
            time.sleep(0.3)
            
            # Phase 2: Routing & DNA
            final_text, detected = _apply_dna_triggers(cleaned)
            auto_target, auto_reason = route_to_target(final_text)
            st.session_state[K.AUTO_TARGET], st.session_state[K.AUTO_REASON] = auto_target, auto_reason
            
            dna_log = f" | DNA: {', '.join(detected)}" if detected else ""
            ui_text.markdown(f"`< 45% >` **[ROUTER]** Locking trajectory to **{auto_target.upper()}**{dna_log}...")
            prog_bar.progress(45)
            time.sleep(0.4)
            
            # Phase 3: Execution
            ui_text.markdown("`< 80% >` **[CORE]** Compiling refinement matrix. Executing handshake...")
            prog_bar.progress(80)
            
            # API CALL (Real wait time happens here)
            result, audit, _ = run_refinement_and_audit(
                final_text, auto_target, cfg["framework"], 
                cfg["source_lang"], cfg["aesthetic_choice"], 
                cfg["islamic_mode"], cfg.get("active_persona")
            )
            
            # Phase 4: Resolution
            ui_text.markdown(f"`< 100% >` **[SECURE]** Asset refraction complete. Closing uplink.")
            prog_bar.progress(100)
            time.sleep(0.3)
            
            # Clear HUD for clean layout
            ui_text.empty()
            prog_bar.empty()
            
            # State Saving...
            st.session_state[K.LAST_RESULT] = result
            st.session_state[K.LAST_AUDIT] = audit
            st.session_state[K.LAST_INPUT] = cleaned
            st.session_state[K.HISTORY].append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "intent": cleaned, "target": auto_target,
                "score": audit.get("score", 0), "asset": result
            })
            st.rerun()

    # ── 5. OUTPUT LAYER ───────────────────────────────────────────────────────
    if st.session_state.get(K.LAST_RESULT):
        left, right = st.columns([1, 2], gap="large")
        with left:
            _render_score_block(st.session_state.get(K.LAST_AUDIT) or {}, expert_mode=cfg.get("expert_mode", False))
        with right:
            st.markdown(f'<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:2px; margin-bottom:8px;">[ REFINED_ASSET ]</div>', unsafe_allow_html=True)
            st.text_area("Asset", value=st.session_state.get(K.LAST_RESULT), height=320, label_visibility="collapsed")
            
            st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
            v1, v2, v3 = st.columns([2, 2, 1])
            with v1: st.text_input("Title", key="v_t", label_visibility="collapsed", placeholder=t("asset_title_placeholder", fallback="DESIGNATION..."))
            with v2: st.text_input("Tags", key="v_g", label_visibility="collapsed", placeholder="Forensic Tags...")
            with v3: 
                if st.button("SECURE"):
                    uid = st.session_state.get(K.USER_HASH)
                    if not uid or "GUEST_" in str(uid).upper():
                        st.error("Vault Lock Failed: Identity Unlatched.")
                    else:
                        from vault.vault_engine import save_prompt
                        res, err = save_prompt(
                            uid, title=st.session_state.get("v_t"), 
                            tags=st.session_state.get("v_g"), 
                            content=st.session_state.get(K.LAST_RESULT), 
                            target=st.session_state.get(K.AUTO_TARGET), 
                            framework=cfg["framework"], 
                            score=(st.session_state.get(K.LAST_AUDIT) or {}).get("score", 0)
                        )
                        if not err:
                            st.session_state[K.LAST_SAVED] = datetime.now().strftime("%H:%M")
                            st.toast("Neural Vault Updated.")
                            st.rerun()
                        else: st.error(f"Vault Lock Failed: {err}")
