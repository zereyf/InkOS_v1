"""
ui/tabs/workspace.py — Workspace Tab
======================================
v32.0: Architect Edition — Structural Hardening & HUD Refactor.
       - REFACTORED: Compact Glass-HUD for High-Density Mobile view.
       - HARDENED: 50-item Circular Buffer prevents state memory leaks.
       - HARDENED: Mission IDs expanded to 8-character entropy.
       - PATCHED: Strict UTC+1 (WAT) timezone sync for all logs.
       - PATCHED: Form Validation on Vault Saves (Title/Tags required).
       - ISOLATED: Telemetry extraction decoupled from UI render loop.
"""

import textwrap
import time
import re
import uuid
import streamlit as st
from datetime import datetime, timezone, timedelta
from typing import Tuple, Dict, Any

from state import K
from security.sanitizer import sanitize_input
from engine.refiner import run_refinement_and_audit
from engine.router import route_to_target
from engine.cognitive_map import detect_arabic_pattern
from i18n.translations import t
from config import AUTO_SELECT_LABEL

# ── 🟢 SYSTEM CONSTANTS ───────────────────────────────────────────────────────

# Calibrated to Lagos, Nigeria (UTC+1)
WAT_TZ = timezone(timedelta(hours=1))
MAX_HISTORY_ITEMS = 50

# ── 🟢 BEHAVIORAL & FORENSIC ADAPTER ──────────────────────────────────────────

def _detect_tone(text: str) -> str:
    """Scans for stylistic markers to determine the mission psychology."""
    tones = {
        "FORENSIC": ["analysis", "audit", "technical", "vulnerability", "precision", "forensic", "breach"],
        "POETIC": ["symphony", "dance", "ethereal", "glow", "rhythm", "aesthetic", "shadow", "chiaroscuro"],
        "TACTICAL": ["execute", "intercept", "lockdown", "mission", "latch", "uplink", "protocol"],
        "HIKMAH": ["balagha", "linguistic", "concept", "scholarly", "iijaz", "wisdom", "authenticity"]
    }
    text_lower = text.lower()
    for tone, keywords in tones.items():
        if any(kw in text_lower for kw in keywords):
            return tone
    return "NEUTRAL"

def _extract_telemetry(result: str, start_time: float) -> Dict[str, Any]:
    """Isolates telemetry calculation from the main UI thread."""
    latency_ms = int((time.perf_counter() - start_time) * 1000)
    words = result.split()
    word_count = len(words)
    density_score = round(len(result) / word_count, 2) if word_count > 0 else 0
    found_colors = list(set(re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', result)))
    tone = _detect_tone(result)
    
    return {
        "latency_ms": latency_ms,
        "word_count": word_count,
        "density": density_score,
        "palette": found_colors[:5],
        "tone": tone
    }

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

# ── 🟢 UI COMPONENTS ──────────────────────────────────────────────────────────

def _render_score_block(audit: dict, expert_mode: bool = False) -> None:
    """Renders a High-Density, Bounded Thermal HUD."""
    safe_audit = audit or {}
    score = int(safe_audit.get("score", 0))
    precision = int(safe_audit.get("precision", 0))
    alignment = int(safe_audit.get("alignment", 0))
    
    thermal_status = "STABLE" if score > 80 else "CRITICAL" if score < 40 else "FLUCTUATING"
    target = st.session_state.get(K.AUTO_TARGET, "Unknown")
    
    # Logic for Dynamic Status Color
    if score >= 90: status_color = "#4CAF9A"
    elif score >= 80: status_color = "var(--gold)"
    else: status_color = "#E53E3E"
        
    p_pct, a_pct = min(100, (precision/40)*100), min(100, (alignment/40)*100)

    score_html = f"""
    <div style="background: rgba(10,12,16,0.6); border: 1px solid rgba(255,255,255,0.05); border-left: 3px solid {status_color}; border-radius: 4px; padding: 15px; margin-bottom: 10px; display: flex; flex-direction: column; gap: 12px;">
        
        <div style="display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 10px;">
            <div>
                <div style="font-family: var(--font-m); font-size: 0.5rem; color: var(--text-muted); letter-spacing: 2px;">OVERALL FIDELITY</div>
                <div style="font-family: var(--font-d); font-size: 2.4rem; color: {status_color}; line-height: 1; margin-top: 2px;">{score}<span style="font-size: 1rem;">%</span></div>
            </div>
            <div style="text-align: right;">
                <div style="font-family: var(--font-m); font-size: 0.4rem; color: var(--text-dim); letter-spacing: 1px;">THERMAL_EFFICIENCY</div>
                <div style="font-family: var(--font-m); font-size: 0.55rem; color: {status_color}; font-weight: bold; letter-spacing: 1px;">{thermal_status}</div>
            </div>
        </div>

        <div style="display: flex; gap: 15px; align-items: center;">
            <div style="flex: 1;">
                <div style="display: flex; justify-content: space-between; font-family: var(--font-m); font-size: 0.5rem; color: var(--text-muted); margin-bottom: 4px;">
                    <span>PRECISION</span> <span style="color:var(--gold);">{precision}/40</span>
                </div>
                <div style="height: 2px; background: rgba(255,255,255,0.08); position: relative;">
                    <div style="position: absolute; left: 0; top: 0; height: 100%; width: {p_pct}%; background: var(--gold);"></div>
                </div>
            </div>
            <div style="flex: 1;">
                <div style="display: flex; justify-content: space-between; font-family: var(--font-m); font-size: 0.5rem; color: var(--text-muted); margin-bottom: 4px;">
                    <span>ALIGNMENT</span> <span style="color:var(--steel);">{alignment}/40</span>
                </div>
                <div style="height: 2px; background: rgba(255,255,255,0.08); position: relative;">
                    <div style="position: absolute; left: 0; top: 0; height: 100%; width: {a_pct}%; background: var(--steel);"></div>
                </div>
            </div>
        </div>

        <div style="background: rgba(0,0,0,0.3); border: 1px solid rgba(201,168,76,0.1); border-radius: 2px; padding: 8px 10px; height: 75px; overflow-y: auto; font-family: var(--font-m); font-size: 0.6rem; color: var(--text-dim); line-height: 1.5;">
            <span style="color:var(--gold);">> UPLINK_SIG:</span> INKOS_STANDARD // ZENITH<br>
            <span style="color:var(--gold);">> CIPHER_LOCK:</span> {target.upper()}<br>
            <span style="color:var(--text-muted);">> DIAGNOSTIC:</span> {safe_audit.get("critique", "No anomalies detected.")}
        </div>
        
    </div>
    """
    st.markdown(score_html, unsafe_allow_html=True)
    if expert_mode:
        with st.expander("❖ NEURAL UPLINK DIAGNOSTICS"):
            st.json(safe_audit)

# ── 🟢 MAIN RENDERER ──────────────────────────────────────────────────────────

def render_workspace(cfg: dict) -> None:
    # ── 1. HEADER & LIVE METRICS ──
    source_lang = cfg.get("source_lang", "English")
    raw_text = st.session_state.get("ta_input_widget") or ""
    cognitive_load = len(raw_text)

    active_persona = st.session_state.get(K.ACTIVE_PERSONA)
    p_name, p_target, p_icon = "", "All", "❖"
    if isinstance(active_persona, dict):
        raw_name = active_persona.get("name", "").upper()
        p_name = raw_name if len(raw_name) <= 10 else raw_name[:10] + "..."
        p_target = active_persona.get("target", "All")
        p_icon = active_persona.get("icon", "❖")

    current_global_target = cfg.get("target_model")
    is_misaligned = p_target != "All" and p_target != current_global_target and current_global_target != AUTO_SELECT_LABEL
    
    misalignment_badge = f"&nbsp;<span style='background:rgba(229,62,62,0.15); color:#FF4B4B; border:1px solid #FF4B4B; padding:2px 6px; border-radius:2px; margin-left:8px; font-size:0.45rem; letter-spacing:1px; flex-shrink:0;'>[!] MISMATCH</span>" if is_misaligned else ""
    expert_badge = f"&nbsp;<span style='background:rgba(229,62,62,0.1); color:var(--danger); border:1px solid rgba(229,62,62,0.3); padding:2px 6px; border-radius:2px; margin-left:8px; font-size:0.45rem; letter-spacing:1px; flex-shrink:0;'>EXPERT</span>" if cfg.get("expert_mode") else ""
    islamic_badge = f"&nbsp;<span style='background:rgba(76,175,154,0.1); color:#4CAF9A; border:1px solid rgba(76,175,154,0.3); padding:2px 6px; border-radius:2px; margin-left:8px; font-size:0.45rem; letter-spacing:1px; flex-shrink:0;'>HIKMAH</span>" if cfg.get("islamic_mode") else ""
    persona_badge = f"&nbsp;<span style='background:rgba(201,168,76,0.1); color:var(--gold); border:1px solid rgba(201,168,76,0.3); padding:2px 6px; border-radius:2px; margin-left:8px; font-size:0.45rem; letter-spacing:1px; flex-shrink:1; display:inline-block; vertical-align:middle; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:90px;'>{p_icon} {p_name}</span>" if p_name else ""

    header_html = (
        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">'
        f'<div class="vc-header" style="margin:0; display:flex; align-items:center; flex-wrap:nowrap;">'
        f'<span class="status-dot"></span><span style="padding-right:15px; flex-shrink:0;">{t("tab_workspace", fallback="WORKSPACE")}</span>'
        f'{expert_badge}{islamic_badge}{persona_badge}{misalignment_badge}</div>'
        f'</div>'
        f'<div style="display:flex; justify-content:space-between; font-family:var(--font-m); font-size:0.55rem; color:var(--text-dim); letter-spacing:1px; margin-bottom:15px; text-transform:uppercase; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:8px;">'
        f'<div>A.I.Z.E.N. // REF: {(st.session_state.get(K.USER_HASH) or "GHOST_ID")[:8]}</div>'
        f'<div>LOAD: {cognitive_load} B</div></div>'
    ).replace("\n", "")
    st.markdown(header_html, unsafe_allow_html=True)

    # ── 2. DNA ARMORY & GHOST WARNING ──
    current_uid = st.session_state.get(K.USER_HASH)
    is_guest = not current_uid or "GUEST_" in str(current_uid).upper()

    if not is_guest:
        ink_live = bool(st.session_state.get(K.INK_DNA))
        intel_live = bool(st.session_state.get(K.INTEL_DNA))
        hikmah_live = bool(cfg.get("islamic_mode") or st.session_state.get(K.HIKMAH_DNA))

        def _dna_card(label: str, is_live: bool) -> str:
            b_color = "rgba(201,168,76,0.4)" if is_live else "rgba(255,255,255,0.05)"
            t_color = "var(--gold)" if is_live else "var(--text-dim)"
            s_text  = "SYNCED" if is_live else "IDLE"
            s_color = "var(--text-muted)" if is_live else "var(--bg-card)"
            return (
                f'<div style="flex:1; border:1px solid {b_color}; border-radius:4px; padding:12px 5px; text-align:center; background:rgba(0,0,0,0.2);">'
                f'<div style="font-family:var(--font-m); font-size:0.75rem; color:{t_color}; letter-spacing:1px; margin-bottom:4px;">DNA: /{label}</div>'
                f'<div style="font-family:var(--font-m); font-size:0.55rem; color:{s_color}; letter-spacing:2px;">{s_text}</div></div>'
            )

        dna_html = f'<div style="display:flex; gap:10px; margin-bottom:20px;">{_dna_card("INK", ink_live)}{_dna_card("INTEL", intel_live)}{_dna_card("HIKMAH", hikmah_live)}</div>'
        st.markdown(dna_html, unsafe_allow_html=True)
    
    else:
        ghost_html = (
            f'<div style="background:linear-gradient(90deg, rgba(229,62,62,0.08) 0%, transparent 100%); border-left:2px solid var(--danger); padding:12px 15px; margin-bottom:10px; border-radius:2px;">'
            f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:6px;">'
            f'<span style="height:6px; width:6px; background:var(--danger); border-radius:50%; box-shadow: 0 0 6px var(--danger);"></span>'
            f'<span style="font-family:var(--font-m); font-size:0.65rem; color:var(--danger); letter-spacing:2px; font-weight:bold;">UNREGISTERED GHOST UPLINK</span></div>'
            f'<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-muted); line-height:1.6; margin-left:14px;">'
            f'Neural persistence is currently disabled. Assets generated during this session cannot be secured in the Vault.<br>'
            f'<span style="color:var(--text); opacity:0.7;">Awaiting Terminal Identity verification...</span></div></div>'
        )
        st.markdown(ghost_html, unsafe_allow_html=True)
        col_cta, _ = st.columns([1, 2])
        with col_cta:
            if st.button("[ INITIATE LATCH ]", key="btn_latch_ghost", use_container_width=True):
                st.toast("> AWAITING CREDENTIALS.")
        st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)

    # ── 3. INPUT AREA & VOICE UPLINK ──
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
                            st.toast("> AUDIO_IN TRANSCRIBED.")
                            st.rerun()
                    except Exception as e:
                        st.error(f"[!] Voice Uplink Failed: {e}")

    with v_col2:
        intent_val = st.text_area(
            "intent", 
            height=145, 
            placeholder=t("workspace_placeholder", fallback="Input your raw idea or use Voice Uplink..."), 
            label_visibility="collapsed", 
            key="ta_input_widget" 
        )
        st.session_state["ta_input"] = intent_val

    # ── 4. 📡 LIVE LINGUISTIC INTERCEPT ──
    if intent_val and source_lang == "Arabic (العربية)":
        p_data = detect_arabic_pattern(intent_val)
        if p_data:
            intercept_html = f'<div style="margin-top:-15px; margin-bottom:15px; display:flex; align-items:center; gap:8px; opacity:0.8;"><span style="height:6px; width:6px; background:var(--gold); border-radius:50%; box-shadow: 0 0 5px var(--gold);"></span><div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:1px;">PATTERN_INTERCEPT: <span style="color:var(--text); font-weight:bold;">{p_data["pattern"].upper()}</span></div></div>'
            st.markdown(intercept_html, unsafe_allow_html=True)

    if st.button(t("execute_btn", fallback="EXECUTE REFINEMENT"), use_container_width=True):
        st.session_state["athar_trace"] = False
        cleaned, _ = sanitize_input(st.session_state.get("ta_input", ""))
        
        if cleaned:
            st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
            ui_text, prog_bar = st.empty(), st.progress(0)
            
            ui_text.markdown("`< 15% >` **[SYSTEM]** Validating payload integrity and parsing logic gates...")
            prog_bar.progress(15)
            time.sleep(0.3)
            
            final_text, detected = _apply_dna_triggers(cleaned)
            target_model = cfg.get("target_model", AUTO_SELECT_LABEL)
            if target_model == AUTO_SELECT_LABEL:
                resolved_target, resolved_reason = route_to_target(final_text)
            else:
                resolved_target, resolved_reason = target_model, "Manual Override [CIPHER LOCK]"
                
            st.session_state[K.AUTO_TARGET] = resolved_target
            st.session_state[K.AUTO_REASON] = resolved_reason
            
            dna_log = f" | DNA: {', '.join(detected)}" if detected else ""
            ui_text.markdown(f"`< 45% >` **[ROUTER]** Locking trajectory to **{resolved_target.upper()}**{dna_log}...")
            prog_bar.progress(45)
            time.sleep(0.4)
            
            ui_text.markdown("`< 80% >` **[CORE]** Compiling refinement matrix. Executing handshake...")
            prog_bar.progress(80)
            
            start_time = time.perf_counter()
            result, audit, _ = run_refinement_and_audit(
                final_text, resolved_target, cfg["framework"], 
                cfg["source_lang"], cfg["aesthetic_choice"], 
                cfg["islamic_mode"], active_persona
            )
            
            # Extract Telemetry Data cleanly
            telemetry = _extract_telemetry(result, start_time)

            ui_text.markdown(f"`< 100% >` **[SECURE]** Asset refraction complete. Closing uplink.")
            prog_bar.progress(100)
            time.sleep(0.3)
            ui_text.empty()
            prog_bar.empty()
            
            # ── 🟢 HARDENED MISSION LOGGING ──
            # Fix 1: Expanded UUID entropy (8 chars)
            mission_id = f"INK-{uuid.uuid4().hex[:8].upper()}"
            
            intel_packet = {
                "id": mission_id,
                "time": datetime.now(WAT_TZ).strftime("%H:%M:%S"), # Fix 2: Strict WAT Sync
                "target": resolved_target,
                "framework": cfg["framework"],
                "aesthetic": cfg["aesthetic_choice"],
                "input": cleaned,
                "output": result,
                "score": audit.get("score", 0),
                "islamic": cfg["islamic_mode"],
                "latency": f"{telemetry['latency_ms']}ms",
                "density": telemetry['density'],
                "word_count": telemetry['word_count'],
                "palette": telemetry['palette'],
                "tone": telemetry['tone'],
                "icon": p_icon,
                "pattern": detected[0] if detected else "RAW"
            }

            if K.HISTORY not in st.session_state:
                st.session_state[K.HISTORY] = []
            
            st.session_state[K.HISTORY].append(intel_packet)
            
            # Fix 3: Memory Leak Prevention (Circular Buffer limit to 50)
            if len(st.session_state[K.HISTORY]) > MAX_HISTORY_ITEMS:
                st.session_state[K.HISTORY].pop(0)

            st.session_state[K.LAST_RESULT] = result
            st.session_state[K.LAST_AUDIT] = audit
            st.session_state[K.LAST_INPUT] = cleaned
            
            st.toast(f"[◈] MISSION LOGGED: {mission_id}", icon="💾")
            st.rerun()

    # ── 5. OUTPUT LAYER ───────────────────────────────────────────────────────
    if st.session_state.get(K.LAST_RESULT):
        # Apply the compact, mobile-friendly HUD layout
        _render_score_block(st.session_state.get(K.LAST_AUDIT) or {}, expert_mode=cfg.get("expert_mode", False))
        
        st.markdown(f'<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:2px; margin-bottom:4px; margin-top:5px;">[ REFINED_ASSET ]</div>', unsafe_allow_html=True)
        st.text_area("Asset", value=st.session_state.get(K.LAST_RESULT), height=280, label_visibility="collapsed")
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.05); margin: 10px 0;'>", unsafe_allow_html=True)
        
        v1, v2, v3 = st.columns([2, 2, 1.5])
        with v1: 
            st.text_input("Title", key="v_t", label_visibility="collapsed", placeholder=t("asset_title_placeholder", fallback="DESIGNATION..."))
        with v2: 
            st.text_input("Tags", key="v_g", label_visibility="collapsed", placeholder="Forensic Tags...")
        with v3: 
            if st.button("SECURE TO VAULT", type="primary", use_container_width=True):
                uid = st.session_state.get(K.USER_HASH)
                
                # Fix 4: Strict Save Validation
                title_val = st.session_state.get("v_t", "").strip()
                tags_val = st.session_state.get("v_g", "").strip()

                if not title_val or not tags_val:
                    st.toast("[!] UPLINK ABORTED: Designation and Tags are required.", icon="⚠️")
                elif not uid or "GUEST_" in str(uid).upper():
                    st.error("[!] Vault Lock Failed: Identity Unlatched.")
                else:
                    from vault.vault_engine import save_prompt
                    res, err = save_prompt(
                        uid, title=title_val, tags=tags_val, 
                        content=st.session_state.get(K.LAST_RESULT), 
                        target=st.session_state.get(K.AUTO_TARGET), 
                        framework=cfg["framework"], 
                        score=(st.session_state.get(K.LAST_AUDIT) or {}).get("score", 0)
                    )
                    if not err:
                        st.session_state[K.LAST_SAVED] = datetime.now(WAT_TZ).strftime("%H:%M:%S")
                        st.toast("[◈] ASSET SECURED IN NEURAL VAULT.", icon="✅")
                    else: 
                        st.error(f"[!] Vault Lock Failed: {err}")
