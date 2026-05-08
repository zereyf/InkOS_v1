"""
ui/tabs/workspace.py — Workspace Tab
======================================
v30.7: Master Sync — Full Module Restoration.
       - Fixed HUD Live Badges (Expert/Islamic).
       - Repaired all Indentation and Syntax traps.
       - Optimized for Mobile HUD display.
"""

import hashlib
import textwrap
import streamlit as st
from datetime import datetime, timezone
from typing import Optional, Tuple

from state import K
from security.sanitizer import sanitize_input
from security.rate_limiter import check_rate_limit
from engine.refiner import run_refinement_and_audit, detect_best_target
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
    efficiency = int(safe_audit.get("efficiency", 0))
    critique = str(safe_audit.get("critique", ""))
    
    thermal_status = "STABLE" if score > 80 else "CRITICAL" if score < 40 else "FLUCTUATING"
    target, reason = st.session_state.get(K.AUTO_TARGET, "Unknown"), st.session_state.get(K.AUTO_REASON, "Manual")
    status_label, status_color = ("OPTIMIZED", "#4CAF9A") if score > 85 else ("SUB-OPTIMAL", "var(--gold)")
    
    p_pct, a_pct, e_pct = min(100, (precision/40)*100), min(100, (alignment/40)*100), min(100, (efficiency/20)*100)

    hud_html = textwrap.dedent(f"""
        <div style="background: var(--bg-card); border: 1px solid rgba(255,255,255,0.05); padding: 22px; position: relative; overflow: hidden; margin-bottom: 15px;">
            <div style="position: absolute; top: 0; left: 0; width: 40px; height: 2px; background: {status_color};"></div>
            <div style="position: absolute; top: 10px; right: 10px; text-align: right;">
                <div style="font-family: var(--font-m); font-size: 0.4rem; color: var(--text-dim); letter-spacing: 1px;">THERMAL_EFFICIENCY</div>
                <div style="font-family: var(--font-m); font-size: 0.5rem; color: {status_color}; font-weight: bold;">{thermal_status}</div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px;">
                <div>
                    <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--text-muted); letter-spacing: 2px; text-transform: uppercase;">Overall Fidelity</div>
                    <div style="font-family: var(--font-d); font-size: 3.2rem; color: {status_color}; line-height: 0.9; margin-top: 4px;">{score}<span style="font-size: 1.2rem;">%</span></div>
                </div>
            </div>
            <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); width: 80px;">PRECISION</span>
                    <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.08); margin: 0 15px; position: relative;"><div style="position: absolute; left: 0; top: -1px; height: 3px; width: {p_pct}%; background: var(--gold);"></div></div>
                    <span style="font-family: var(--font-m); font-size: 0.65rem; color: var(--gold);">{precision}/40</span>
                </div>
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); width: 80px;">ALIGNMENT</span>
                    <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.08); margin: 0 15px; position: relative;"><div style="position: absolute; left: 0; top: -1px; height: 3px; width: {a_pct}%; background: var(--steel);"></div></div>
                    <span style="font-family: var(--font-m); font-size: 0.65rem; color: var(--steel);">{alignment}/40</span>
                </div>
            </div>
            <div style="background: rgba(201,168,76,0.03); border-left: 2px solid var(--gold-border); padding: 12px 16px;">
                <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--gold); text-transform: uppercase; margin-bottom: 6px;">> Forensic Log</div>
                <div style="font-family: var(--font-m); font-size: 0.75rem; color: var(--text); line-height: 1.6;">
                    <span style="color:var(--gold); font-weight:bold;">[ CIPHER ]: {target.upper()}</span> — {reason}<br>
                    {critique}
                </div>
            </div>
        </div>
    """)
    st.markdown(hud_html, unsafe_allow_html=True)
    if expert_mode:
        with st.expander("🛠️ NEURAL UPLINK DIAGNOSTICS"):
            st.json(safe_audit)

# ── MAIN RENDERER ─────────────────────────────────────────────────────────────

def render_workspace(cfg: dict) -> None:
    # 1. HEADER & COGNITIVE LOAD
    source_lang = cfg.get("source_lang", "English")
    cognitive_load = len(st.session_state.get("ta_input", ""))
    
    expert_badge = "<span style='background:rgba(229, 62, 62, 0.1); color:var(--danger); border:1px solid rgba(229, 62, 62, 0.3); padding:2px 6px; border-radius:2px; margin-left:8px; font-size:0.45rem; letter-spacing:1px; position:relative; top:-2px;'>EXPERT</span>" if cfg.get("expert_mode") else ""
    islamic_badge = "<span style='background:rgba(76, 175, 154, 0.1); color:#4CAF9A; border:1px solid rgba(76, 175, 154, 0.3); padding:2px 6px; border-radius:2px; margin-left:8px; font-size:0.45rem; letter-spacing:1px; position:relative; top:-2px;'>HIKMAH LATCH</span>" if cfg.get("islamic_mode") else ""

    header_html = textwrap.dedent(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
            <div class="vc-header" style="margin:0; display:flex; align-items:center;">
                <span class="status-dot"></span>{t("tab_workspace", fallback="WORKSPACE")}
                {expert_badge}
                {islamic_badge}
            </div>
            <div style="font-family:var(--font-a); color:var(--gold); font-size:1.1rem; opacity:0.9; letter-spacing:1px; text-shadow: 0 0 10px rgba(201,168,76,0.3);">حبر وفكرة</div>
        </div>
        <div style="display:flex; justify-content:space-between; font-family:var(--font-m); font-size:0.55rem; color:var(--text-dim); letter-spacing:1px; margin-bottom:15px; text-transform:uppercase; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:8px;">
            <div>A.I.Z.E.N. // REF: {(st.session_state.get(K.USER_HASH) or "GHOST_ID")[:8]}</div>
            <div>LOAD: {cognitive_load} B</div>
        </div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    # 2. DNA ARMORY BAR
    if "GUEST_" not in str(st.session_state.get(K.USER_HASH, "")).upper():
        dna_bar = textwrap.dedent(f"""
            <div style="display:flex; gap:10px; margin-bottom:20px;">
                <div style="flex:1; background:rgba(201,168,76,0.02); border:1px solid rgba(201,168,76,0.1); padding:8px; border-radius:3px; text-align:center;">
                    <div style="font-size:0.5rem; color:var(--gold); font-family:var(--font-m);">DNA: /INK</div>
                    <div style="font-size:0.4rem; color:var(--text-muted);">{"ARMED" if st.session_state.get(K.INK_DNA) else "OFFLINE"}</div>
                </div>
                <div style="flex:1; background:rgba(201,168,76,0.02); border:1px solid rgba(201,168,76,0.1); padding:8px; border-radius:3px; text-align:center;">
                    <div style="font-size:0.5rem; color:var(--gold); font-family:var(--font-m);">DNA: /INTEL</div>
                    <div style="font-size:0.4rem; color:var(--text-muted);">{"ARMED" if st.session_state.get(K.INTEL_DNA) else "OFFLINE"}</div>
                </div>
                <div style="flex:1; background:rgba(201,168,76,0.02); border:1px solid rgba(201,168,76,0.1); padding:8px; border-radius:3px; text-align:center;">
                    <div style="font-size:0.5rem; color:var(--gold); font-family:var(--font-m);">DNA: /HIKMAH</div>
                    <div style="font-size:0.4rem; color:var(--text-muted);">{"ARMED" if st.session_state.get(K.HIKMAH_DNA) else "OFFLINE"}</div>
                </div>
            </div>
        """)
        st.markdown(dna_bar, unsafe_allow_html=True)

    # 3. 📡 LIVE LINGUISTIC INTERCEPT
    raw_input = st.session_state.get("ta_input", "")
    live_pattern_html = '<div style="height:22px;"></div>'
    if raw_input and source_lang == "Arabic (العربية)":
        p_data = detect_arabic_pattern(raw_input)
        if p_data:
            live_pattern_html = textwrap.dedent(f"""
                <div style="margin-bottom:8px; display:flex; align-items:center; gap:8px; opacity:0.8;">
                    <span style="height:6px; width:6px; background:var(--gold); border-radius:50%; box-shadow: 0 0 5px var(--gold);"></span>
                    <div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:1px;">
                        PATTERN_INTERCEPT: <span style="color:var(--text); font-weight:bold;">{p_data['pattern'].upper()}</span>
                    </div>
                </div>
            """)
    st.markdown(live_pattern_html, unsafe_allow_html=True)

    # 4. INPUT AREA
    st.text_area("intent", height=145, placeholder=t("workspace_placeholder", fallback="Input your raw idea here..."), label_visibility="collapsed", key="ta_input")

    if st.button(t("execute_btn", fallback="EXECUTE REFINEMENT"), use_container_width=True):
        st.session_state["athar_trace"] = False
        cleaned, _ = sanitize_input(st.session_state.ta_input or "")
        
        if cleaned:
            with st.status("Neural Handshake...", expanded=True):
                final_text, _ = _apply_dna_triggers(cleaned)
                auto_target, auto_reason = detect_best_target(final_text)
                st.session_state[K.AUTO_TARGET], st.session_state[K.AUTO_REASON] = auto_target, auto_reason
                
                result, audit, _ = run_refinement_and_audit(final_text, auto_target, cfg["framework"], cfg["source_lang"], cfg["aesthetic_choice"], cfg["islamic_mode"], cfg.get("active_persona"))
                
                st.session_state[K.LAST_RESULT] = result
                st.session_state[K.LAST_AUDIT] = audit
                st.session_state[K.LAST_INPUT] = cleaned

                st.session_state[K.HISTORY].append({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "intent": cleaned,
                    "target": auto_target,
                    "score": audit.get("score", 0),
                    "asset": result
                })

                st.rerun()

    # 5. OUTPUT LAYER
    if st.session_state.get(K.LAST_RESULT):
        left, right = st.columns([1, 2], gap="large")
        with left:
            _render_score_block(st.session_state.get(K.LAST_AUDIT) or {}, expert_mode=cfg.get("expert_mode", False))
        with right:
            st.markdown(f'<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:2px; margin-bottom:8px;">[ REFINED_ASSET ]</div>', unsafe_allow_html=True)
            st.text_area("Asset", value=st.session_state.get(K.LAST_RESULT), height=320, label_visibility="collapsed")
            
            st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
            v1, v2, v3 = st.columns([2, 2, 1])
            with v1: st.text_input("Title", key="v_t", label_visibility="collapsed", placeholder="Asset Title...")
            with v2: st.text_input("Tags", key="v_g", label_visibility="collapsed", placeholder="Forensic Tags...")
            with v3: 
                if st.button("SECURE"):
                    from vault.vault_engine import save_prompt
                    res, err = save_prompt(
                        st.session_state.get(K.USER_HASH), 
                        title=st.session_state.get("v_t"), 
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
                    else:
                        st.error(f"Vault Lock Failed: {err}")
