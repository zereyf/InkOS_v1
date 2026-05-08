"""
ui/tabs/workspace.py — Workspace Tab
======================================
v30.3: The "Full Spectrum" Build.
       - Integrated DNA Status Bar & Original Intent Card.
       - 40/40/20 Forensic HUD with CIPHER Routing Badge.
       - Athar Persistence (Visual Decay) & Neural Flush.
       - Synchronized with Master Rehydration (v2026.4).
"""

import hashlib
import textwrap
import streamlit as st
from datetime import datetime
from typing import Optional, Tuple

from state import K
from security.sanitizer import sanitize_input
from security.rate_limiter import check_rate_limit
from engine.cognitive_map import detect_arabic_pattern
from engine.refiner import run_refinement_and_audit, detect_best_target
from config import INPUT_MAX_CHARS, INPUT_WARN_THRESHOLD, AUTO_SELECT_LABEL
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

def _render_score_block(audit: dict, pattern: Optional[dict], archived: bool = False) -> None:
    # 🛡️ NEURAL SHIELD
    safe_audit = audit or {}
    score = int(safe_audit.get("score", 0))
    precision = int(safe_audit.get("precision", 0))
    alignment = int(safe_audit.get("alignment", 0))
    efficiency = int(safe_audit.get("efficiency", 0))
    critique = str(safe_audit.get("critique", ""))
    
    target, reason = st.session_state.get(K.AUTO_TARGET, "Unknown"), st.session_state.get(K.AUTO_REASON, "Manual")
    hud_opacity = "0.3" if archived else "1.0"
    
    if archived:
        status_label, status_color = "ARCHIVED", "var(--gold)"
        log_content = f"> HASH_SECURED [0x{hashlib.md5(critique.encode()).hexdigest()[:6].upper()}] ASSET_ARCHIVED."
    elif "[TERMINAL THROTTLED]" in critique:
        status_label, status_color = "THROTTLED", "#E53E3E"
        log_content = critique
    elif score == 0:
        status_label, status_color = "NOT OPTIMIZED", "var(--text-dim)"
        log_content = critique or "Awaiting neural uplink..."
    else:
        status_label, status_color = "OPTIMIZED", "#4CAF9A"
        log_content = textwrap.dedent(f"""
            <div style="color:var(--gold); font-weight:bold; margin-bottom:4px; font-size:0.6rem;">[ CIPHER_UPLINK ]: {target.upper()}</div>
            <div style="color:var(--text-muted); font-size:0.65rem; font-style:italic; margin-bottom:8px;">// {reason}</div>
            <div>{critique}</div>
        """)

    # Bar Percentage Logic (40/40/20)
    p_pct, a_pct, e_pct = min(100, (precision/40)*100), min(100, (alignment/40)*100), min(100, (efficiency/20)*100)

    hud_html = textwrap.dedent(f"""
        <div style="background: var(--bg-card); border: 1px solid rgba(255,255,255,0.05); padding: 22px; position: relative; overflow: hidden; margin-bottom: 15px; opacity: {hud_opacity}; transition: 0.4s ease;">
            <div style="position: absolute; top: 0; left: 0; width: 40px; height: 2px; background: {status_color}; box-shadow: 0 0 10px {status_color};"></div>
            <div style="position: absolute; top: 10px; right: 10px; background: rgba(201,168,76,0.1); border: 1px solid var(--gold-border); padding: 2px 8px; border-radius: 2px;">
                <span style="font-family: var(--font-m); font-size: 0.45rem; color: var(--gold); letter-spacing: 1.5px; font-weight: bold;">CIPHER SELECTED</span>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px;">
                <div>
                    <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--text-muted); letter-spacing: 2px; text-transform: uppercase;">Overall Fidelity</div>
                    <div style="font-family: var(--font-d); font-size: 3.2rem; color: {status_color}; line-height: 0.9; margin-top: 4px;">{score}<span style="font-size: 1.2rem;">%</span></div>
                </div>
                <div style="text-align: right;">
                    <div style="font-family: var(--font-m); font-size: 0.5rem; color: var(--steel);">STATUS</div>
                    <div style="font-family: var(--font-m); font-size: 0.75rem; color: {status_color}; font-weight: bold;">{status_label}</div>
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
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <span style="font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); width: 80px;">EFFICIENCY</span>
                    <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.08); margin: 0 15px; position: relative;"><div style="position: absolute; left: 0; top: -1px; height: 3px; width: {e_pct}%; background: #4CAF9A;"></div></div>
                    <span style="font-family: var(--font-m); font-size: 0.65rem; color: #4CAF9A;">{efficiency}/20</span>
                </div>
            </div>
            <div style="background: rgba(201,168,76,0.03); border-left: 2px solid var(--gold-border); padding: 12px 16px;">
                <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--gold); text-transform: uppercase; margin-bottom: 6px;">> Forensic Log</div>
                <div style="font-family: var(--font-m); font-size: 0.75rem; color: var(--text); line-height: 1.6;">{log_content}</div>
            </div>
        </div>
    """)
    st.markdown(hud_html, unsafe_allow_html=True)

# ── MAIN RENDERER ─────────────────────────────────────────────────────────────

def render_workspace(cfg: dict) -> None:
    def flush_trace(): st.session_state["athar_trace"] = False

    # 1. HEADER & SESS_REF
    header_html = textwrap.dedent(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
            <div class="vc-header" style="margin:0;"><span class="status-dot"></span>{t("workspace_header")}</div>
            <div style="font-family:var(--font-a); color:var(--gold); font-size:1.1rem; opacity:0.9; letter-spacing:1px;">حبر وفكرة</div>
        </div>
        <div style="font-family:var(--font-m); font-size:0.5rem; color:var(--text-dim); letter-spacing:2px; margin-bottom:15px; text-transform:uppercase; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:8px;">
            A.I.Z.E.N. COGNITIVE TERMINAL // SESS_REF: {st.session_state.get(K.USER_HASH, "GUEST")[:8]}
        </div>
    """)
    st.markdown(header_html, unsafe_allow_html=True)

    # 2. DNA ARMORY BAR
    if "GUEST_" not in str(st.session_state.get(K.USER_HASH, "")).upper():
        dna_bar = textwrap.dedent(f"""
            <div style="display:flex; gap:10px; margin-bottom:20px;">
                <div style="flex:1; background:rgba(201,168,76,0.03); border:1px solid rgba(201,168,76,0.2); padding:8px; border-radius:3px; text-align:center;">
                    <div style="font-size:0.55rem; color:var(--gold); font-family:var(--font-m); letter-spacing:1px;">[ /INK ]</div>
                    <div style="font-size:0.45rem; color:var(--text-muted); font-weight:bold;">{"ARMED" if st.session_state.get(K.INK_DNA) else "EMPTY"}</div>
                </div>
                <div style="flex:1; background:rgba(124,158,191,0.03); border:1px solid rgba(124,158,191,0.2); padding:8px; border-radius:3px; text-align:center;">
                    <div style="font-size:0.55rem; color:#7C9EBF; font-family:var(--font-m); letter-spacing:1px;">[ /INTEL ]</div>
                    <div style="font-size:0.45rem; color:var(--text-muted); font-weight:bold;">{"READY" if st.session_state.get(K.INTEL_DNA) else "EMPTY"}</div>
                </div>
                <div style="flex:1; background:rgba(76,175,154,0.03); border:1px solid rgba(76,175,154,0.2); padding:8px; border-radius:3px; text-align:center;">
                    <div style="font-size:0.55rem; color:#4CAF9A; font-family:var(--font-m); letter-spacing:1px;">[ /HIKMAH ]</div>
                    <div style="font-size:0.45rem; color:var(--text-muted); font-weight:bold;">{"LOADED" if st.session_state.get(K.HIKMAH_DNA) else "EMPTY"}</div>
                </div>
            </div>
        """)
        st.markdown(dna_bar, unsafe_allow_html=True)

    # 3. INPUT LAYER
    st.audio_input("Record", label_visibility="collapsed")
    raw_input = st.text_area("intent", height=145, placeholder=t("workspace_placeholder"), label_visibility="collapsed", key="ta_input", on_change=flush_trace)

    if st.button(t("execute_btn"), use_container_width=True):
        st.session_state["athar_trace"] = False
        cleaned, _ = sanitize_input(raw_input or "")
        if cleaned and check_rate_limit(consume=1):
            with st.status("Initiating Uplink...", expanded=True):
                final_text, _ = _apply_dna_triggers(cleaned)
                auto_target, auto_reason = detect_best_target(final_text)
                st.session_state[K.AUTO_TARGET], st.session_state[K.AUTO_REASON] = auto_target, auto_reason
                result, audit, pattern = run_refinement_and_audit(final_text, auto_target, cfg["framework"], cfg["source_lang"], cfg["aesthetic_choice"], cfg["islamic_mode"], cfg.get("active_persona"))
                st.session_state[K.LAST_RESULT], st.session_state[K.LAST_AUDIT], st.session_state[K.LAST_INPUT], st.session_state[K.LAST_PATTERN] = result, audit, cleaned, pattern
                st.rerun()

    # 4. OUTPUT LAYER
    if st.session_state.get(K.LAST_RESULT):
        left, right = st.columns([1, 2], gap="large")
        with left:
            _render_score_block(st.session_state.get(K.LAST_AUDIT) or {}, st.session_state.get(K.LAST_PATTERN), archived=st.session_state.get("athar_trace", False))
        with right:
            # 🟢 ORIGINAL INTENT CARD
            st.markdown('<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:2.5px; text-transform:uppercase; margin-bottom:8px;">[ Original Intent ]</div>', unsafe_allow_html=True)
            st.markdown(f'<div style="padding:12px; margin-bottom:20px; border:1px solid rgba(255,255,255,0.05); background:rgba(255,255,255,0.01); color:var(--text-muted); font-size:0.75rem; border-radius:3px;">{st.session_state.get(K.LAST_INPUT)}</div>', unsafe_allow_html=True)
            
            st.markdown('<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:2.5px; text-transform:uppercase; margin-bottom:8px;">[ Refined Asset ]</div>', unsafe_allow_html=True)
            st.text_area("Asset", value=st.session_state.get(K.LAST_RESULT), height=320, label_visibility="collapsed")
            st.download_button("💾 Download", st.session_state.get(K.LAST_RESULT), file_name="Refined_Asset.txt", use_container_width=True)
            
            st.markdown("<div style='height:15px; border-bottom:1px solid rgba(255,255,255,0.05); margin-bottom:15px;'></div>", unsafe_allow_html=True)
            st.markdown("<div style='font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:2px; margin-bottom:12px;'>🔒 SECURE TO MEMORY VAULT</div>", unsafe_allow_html=True)
            v1, v2, v3 = st.columns([2, 2, 1])
            with v1: st.text_input("Title", key="v_t", label_visibility="collapsed", placeholder="Title...")
            with v2: st.text_input("Tags", key="v_g", label_visibility="collapsed", placeholder="Tags...")
            with v3: 
                if st.button("SECURE"):
                    from vault.vault_engine import save_prompt
                    l_audit = st.session_state.get(K.LAST_AUDIT) or {}
                    res, err = save_prompt(st.session_state.get(K.USER_HASH), title=st.session_state.get("v_t"), tags=st.session_state.get("v_g"), content=st.session_state.get(K.LAST_RESULT), target=st.session_state.get(K.AUTO_TARGET), framework=cfg["framework"], score=l_audit.get("score", 0), pattern=st.session_state.get(K.LAST_PATTERN, {}).get("pattern", ""), islamic=cfg["islamic_mode"], aesthetic=cfg["aesthetic_choice"])
                    if not err:
                        st.session_state[K.LAST_SAVED] = datetime.now().strftime("%H:%M")
                        st.session_state["athar_trace"] = True
                        st.toast("Asset secured to Vault.")
                        st.rerun()
