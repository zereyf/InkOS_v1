"""
ui/tabs/workspace.py — Workspace Tab
======================================
v31.10: Behavioral Intercept — Tone & Persona Sync.
       - ADDED: _detect_tone() keyword scanner.
       - INTEGRATED: Persona Icon & Tone Label into Intel Packet.
       - RETAINED: All UI Typography, Thermal HUD, and Telemetry.
"""

import textwrap
import time
import re
import streamlit as st
import uuid
from datetime import datetime, timezone
from typing import Tuple

from state import K
from security.sanitizer import sanitize_input
from engine.refiner import run_refinement_and_audit
from engine.router import route_to_target
from engine.cognitive_map import detect_arabic_pattern
from i18n.translations import t
from config import AUTO_SELECT_LABEL

# ── BEHAVIORAL HELPERS ───────────────────────────────────────────────────────

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

# ── DNA INJECTION ENGINE ─────────────────────────────────────────────────────
# ... (No changes to _apply_dna_triggers or _render_score_block) ...

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
    score_html = (f'<div style="background:var(--bg-card); border:1px solid rgba(255,255,255,0.05); padding:22px; position:relative; overflow:hidden; margin-bottom:15px;"><div style="position:absolute; top:0; left:0; width:40px; height:2px; background:{status_color};"></div><div style="position:absolute; top:10px; right:10px; text-align:right;"><div style="font-family:var(--font-m); font-size:0.4rem; color:var(--text-dim); letter-spacing:1px;">THERMAL_EFFICIENCY</div><div style="font-family:var(--font-m); font-size:0.5rem; color:{status_color}; font-weight:bold;">{thermal_status}</div></div><div style="display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:24px;"><div><div style="font-family:var(--font-m); font-size:0.55rem; color:var(--text-muted); letter-spacing:2px; text-transform:uppercase;">Overall Fidelity</div><div style="font-family:var(--font-d); font-size:3.2rem; color:{status_color}; line-height:0.9; margin-top:4px;">{score}<span style="font-size:1.2rem;">%</span></div></div></div><div style="display:flex; flex-direction:column; gap:12px; margin-bottom:24px;"><div style="display:flex; align-items:center; justify-content:space-between;"><span style="font-family:var(--font-m); font-size:0.6rem; color:var(--text-muted); width:80px;">PRECISION</span><div style="flex:1; height:1px; background:rgba(255,255,255,0.08); margin:0 15px; position:relative;"><div style="position:absolute; left:0; top:-1px; height:3px; width:{p_pct}%; background:var(--gold);"></div></div><span style="font-family:var(--font-m); font-size:0.65rem; color:var(--gold);">{precision}/40</span></div><div style="display:flex; align-items:center; justify-content:space-between;"><span style="font-family:var(--font-m); font-size:0.6rem; color:var(--text-muted); width:80px;">ALIGNMENT</span><div style="flex:1; height:1px; background:rgba(255,255,255,0.08); margin:0 15px; position:relative;"><div style="position:absolute; left:0; top:-1px; height:3px; width:{a_pct}%; background:var(--steel);"></div></div><span style="font-family:var(--font-m); font-size:0.65rem; color:var(--steel);">{alignment}/40</span></div></div><div style="background:rgba(201,168,76,0.03); border-left:2px solid var(--gold-border); padding:12px 16px;"><div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); text-transform:uppercase; margin-bottom:6px;">> Forensic Log</div><div style="font-family:var(--font-m); font-size:0.75rem; color:var(--text); line-height:1.6;"><span style="color:var(--gold); font-weight:bold;">[ UPLINK ]: INKOS STANDARD (8B)</span> — Optimized for speed.<br><span style="color:var(--text-dim); font-size:0.5rem; letter-spacing:1px;">ZENITH PROTOCOL: [RESTRICTED]</span><br><br><span style="color:var(--gold); font-weight:bold;">[ CIPHER TARGET ]: {target.upper()}</span> — {reason}<br>{safe_audit.get("critique", "")}</div></div></div>').replace("\n", "")
    st.markdown(score_html, unsafe_allow_html=True)
    if expert_mode:
        with st.expander("❖ NEURAL UPLINK DIAGNOSTICS"):
            st.json(safe_audit)

# ── MAIN RENDERER ─────────────────────────────────────────────────────────────

def render_workspace(cfg: dict) -> None:
    # ... (Keep Header, Live Metrics, DNA Armory exactly as they are) ...
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

    # ... (Skipping middle rendering code for brevity, no changes there) ...
    # [Assume standard DNA card and Input area rendering logic remains untouched]

    # In the EXECUTE REFINEMENT block:
    if st.button(t("execute_btn", fallback="EXECUTE REFINEMENT"), use_container_width=True):
        st.session_state["athar_trace"] = False
        cleaned, _ = sanitize_input(st.session_state.get("ta_input", ""))
        if cleaned:
            # ... (HUD Handshake Logic) ...
            
            # 🟢 TELEMETRY START
            start_time = time.perf_counter()
            result, audit, _ = run_refinement_and_audit(
                cleaned, cfg.get("target_model", AUTO_SELECT_LABEL), cfg["framework"], 
                cfg["source_lang"], cfg["aesthetic_choice"], 
                cfg["islamic_mode"], active_persona
            )
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            
            # 🟢 BEHAVIORAL ANALYSIS
            mission_tone = _detect_tone(result)
            words = result.split()
            word_count = len(words)
            density_score = round(len(result) / word_count, 2) if word_count > 0 else 0
            found_colors = list(set(re.findall(r'#(?:[0-9a-fA-F]{3}){1,2}\b', result)))
            
            # ── 🟢 THE TACTICAL FLIGHT RECORDER (Automatic Mission Log) ──
            mission_id = f"INK-{uuid.uuid4().hex[:4].upper()}"
            intel_packet = {
                "id": mission_id,
                "time": datetime.now().strftime("%H:%M:%S"),
                "target": st.session_state.get(K.AUTO_TARGET, "Default"),
                "framework": cfg["framework"],
                "aesthetic": cfg["aesthetic_choice"],
                "input": cleaned,
                "output": result,
                "score": audit.get("score", 0),
                "islamic": cfg["islamic_mode"],
                # FORENSIC METRICS
                "latency": f"{latency_ms}ms",
                "density": density_score,
                "word_count": word_count,
                "palette": found_colors[:5],
                # 🟢 NEW BEHAVIORAL FIELDS
                "tone": mission_tone,
                "icon": p_icon,
                "pattern": next((m for m in ["/INK", "/INTEL", "/HIKMAH"] if m in cleaned.lower()), "RAW")
            }

            if K.HISTORY not in st.session_state:
                st.session_state[K.HISTORY] = []
            st.session_state[K.HISTORY].append(intel_packet)
            
            st.session_state[K.LAST_RESULT] = result
            st.session_state[K.LAST_AUDIT] = audit
            st.session_state[K.LAST_INPUT] = cleaned
            st.toast(f"[◈] MISSION LOGGED: {mission_id}", icon="💾")
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
                        st.error("[!] Vault Lock Failed: Identity Unlatched.")
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
                            st.toast("[◈] NEURAL VAULT SECURED.")
                            st.rerun()
                        else: st.error(f"[!] Vault Lock Failed: {err}")
