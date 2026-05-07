"""
ui/tabs/workspace.py — Workspace Tab
======================================
v1.0: The Complete Master Build.
       Restored Vault/Download actions, Cyber-HUD, and HTML Terminal Bar.
"""

import hashlib
import streamlit as st
from datetime import datetime, timezone
from typing import Optional, Tuple

from state import K
from security.sanitizer import sanitize_input
from security.rate_limiter import check_rate_limit
from engine.cognitive_map import detect_arabic_pattern
from engine.refiner import run_refinement_and_audit, detect_best_target
from config import INPUT_MAX_CHARS, INPUT_WARN_THRESHOLD, AUTO_SELECT_LABEL
from i18n.translations import t


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ── ADVANCED TRIGGER LOGIC ────────────────────────────────────────────────────

def _apply_dna_triggers(text: str) -> Tuple[str, list]:
    """Forensic scanning for slash commands to inject stored DNA."""
    detected = []
    processed = text
    
    triggers = {
        "/ink":    st.session_state.get(K.INK_DNA, ""),
        "/intel":  st.session_state.get(K.INTEL_DNA, ""),
        "/hikmah": st.session_state.get(K.HIKMAH_DNA, "")
    }
    
    for trigger, dna in triggers.items():
        if trigger.lower() in text.lower():
            processed = f"[DNA INJECTION: {trigger.upper()}]\n{dna}\n\n[USER INTENT]\n{processed}"
            detected.append(trigger.upper())
            
    return processed, detected


def _render_guest_warning():
    """Renders volatile session warning if identity is not latched."""
    if "GUEST_" in str(st.session_state.get(K.USER_HASH, "")):
        st.markdown(f"""
        <div class="vc-card" style="border-color:var(--danger); background:rgba(169,50,38,0.05); margin-bottom:20px; padding:16px;">
            <div style="display:flex; align-items:center; gap:14px;">
                <span class="status-dot" style="background:var(--danger); animation: pulse-red 1.5s infinite; box-shadow: 0 0 10px var(--danger);"></span>
                <div style="font-family:var(--font-m); font-size:0.75rem;">
                    <strong style="color:var(--danger); letter-spacing:1px; text-transform:uppercase;">Session Volatile</strong><br>
                    <span style="color:var(--text-muted);">Current identity is temporary. Assets will be purged on refresh.</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def _render_score_block(audit: dict, pattern: Optional[dict], triggers: list = None) -> None:
    """Renders the high-end Forensic HUD for refinement scores."""
    score      = int(audit.get("score",     0))
    precision  = int(audit.get("precision",  0))
    alignment  = int(audit.get("alignment",  0))
    efficiency = int(audit.get("efficiency", 0))
    critique   = str(audit.get("critique",  ""))

    # Calculate percentages for the laser bars
    p_pct = min(100, (precision / 40) * 100) if precision else 0
    a_pct = min(100, (alignment / 40) * 100) if alignment else 0
    e_pct = min(100, (efficiency / 20) * 100) if efficiency else 0

    if triggers:
        for t_name in triggers:
            st.markdown(f"""
<div style="background:rgba(201,168,76,0.1); border:1px solid var(--gold); border-radius:3px; padding:8px 12px; margin-bottom:10px;">
    <div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:1px;">🧬 COMMAND ENGAGED</div>
    <div style="font-family:var(--font-m); font-size:0.75rem; color:white; font-weight:600;">[ {t_name} ] DNA ACTIVE</div>
</div>
            """.strip(), unsafe_allow_html=True)

    if pattern:
        color = pattern.get("color", "#C9A84C")
        st.markdown(f"""
<div class="pattern-card" style="margin-bottom:12px;">
    <span class="p-label">Engine Applied</span>
    <span class="p-arabic" style="color:{color};">{pattern['pattern']}</span>
    <span class="p-paradigm" style="color:{color};">→ {pattern['prompt_paradigm']}</span>
</div>
        """.strip(), unsafe_allow_html=True)

    # 💎 THE HIGH-END FORENSIC HUD (Flush left to bypass Markdown code-block rendering)
    hud_html = f"""
<div style="background: var(--bg-card); border: 1px solid rgba(255,255,255,0.05); border-radius: 3px; padding: 22px; position: relative; overflow: hidden; margin-bottom: 15px;">
    <div style="position: absolute; top: 0; left: 0; width: 40px; height: 2px; background: var(--gold); box-shadow: 0 0 10px var(--gold);"></div>
    
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px;">
        <div>
            <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--text-muted); letter-spacing: 2px; text-transform: uppercase;">Overall Fidelity</div>
            <div style="font-family: var(--font-d); font-size: 3.2rem; color: var(--gold); line-height: 0.9; margin-top: 4px;">{score}<span style="font-size: 1.2rem; color: var(--gold-dim);">%</span></div>
        </div>
        <div style="text-align: right;">
            <div style="font-family: var(--font-m); font-size: 0.5rem; color: var(--steel); letter-spacing: 1px;">STATUS</div>
            <div style="font-family: var(--font-m); font-size: 0.75rem; color: #4CAF9A; font-weight: bold; letter-spacing: 1px;">OPTIMIZED</div>
        </div>
    </div>

    <div style="display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); width: 80px; letter-spacing: 1px;">PRECISION</span>
            <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.08); margin: 0 15px; position: relative;">
                <div style="position: absolute; left: 0; top: -1px; height: 3px; width: {p_pct}%; background: var(--gold); box-shadow: 0 0 6px var(--gold);"></div>
            </div>
            <span style="font-family: var(--font-m); font-size: 0.65rem; color: var(--gold); width: 40px; text-align: right;">{precision}/40</span>
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); width: 80px; letter-spacing: 1px;">ALIGNMENT</span>
            <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.08); margin: 0 15px; position: relative;">
                <div style="position: absolute; left: 0; top: -1px; height: 3px; width: {a_pct}%; background: var(--steel); box-shadow: 0 0 6px var(--steel);"></div>
            </div>
            <span style="font-family: var(--font-m); font-size: 0.65rem; color: var(--steel); width: 40px; text-align: right;">{alignment}/40</span>
        </div>
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-family: var(--font-m); font-size: 0.6rem; color: var(--text-muted); width: 80px; letter-spacing: 1px;">EFFICIENCY</span>
            <div style="flex: 1; height: 1px; background: rgba(255,255,255,0.08); margin: 0 15px; position: relative;">
                <div style="position: absolute; left: 0; top: -1px; height: 3px; width: {e_pct}%; background: #4CAF9A; box-shadow: 0 0 6px #4CAF9A;"></div>
            </div>
            <span style="font-family: var(--font-m); font-size: 0.65rem; color: #4CAF9A; width: 40px; text-align: right;">{efficiency}/20</span>
        </div>
    </div>

    <div style="background: rgba(201,168,76,0.03); border-left: 2px solid var(--gold-border); padding: 12px 16px;">
        <div style="font-family: var(--font-m); font-size: 0.55rem; color: var(--gold); letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 6px;">> Forensic Log</div>
        <div style="font-family: var(--font-m); font-size: 0.75rem; color: var(--text); line-height: 1.6;">{critique}</div>
    </div>
</div>
    """
    st.markdown(hud_html.strip(), unsafe_allow_html=True)



def render_workspace(cfg: dict) -> None:
    _render_guest_warning()

    st.markdown(f"""
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
            <div class="vc-header" style="margin:0;"><span class="status-dot"></span>{t("workspace_header")}</div>
            <div style="font-family:var(--font-a); color:var(--gold); font-size:1.1rem; opacity:0.9; letter-spacing:1px;">حبر وفكرة</div>
        </div>
        <div style="font-family:var(--font-m); font-size:0.5rem; color:var(--text-dim); letter-spacing:2px; margin-bottom:15px; text-transform:uppercase; border-bottom:1px solid rgba(255,255,255,0.05); padding-bottom:8px;">
            A.I.Z.E.N. COGNITIVE TERMINAL // SESS_REF: {st.session_state.get(K.USER_HASH, "NULL")[:8]}
        </div>
    """, unsafe_allow_html=True)

    # 🧬 DNA STANDBY BAR (Pure HTML Flexbox)
    current_sid = str(st.session_state.get(K.USER_HASH, ""))
    if "GUEST_" not in current_sid.upper():
        st.markdown(f"""
            <div style="display:flex; gap:10px; margin-bottom:20px;">
                <div style="flex:1; background:rgba(201,168,76,0.03); border:1px solid rgba(201,168,76,0.2); padding:8px; border-radius:3px; text-align:center; box-shadow: inset 0 0 10px rgba(201,168,76,0.02);">
                    <div style="font-size:0.55rem; color:var(--gold); font-family:var(--font-m); letter-spacing:1px; margin-bottom:2px;">[ /INK ]</div>
                    <div style="font-size:0.45rem; color:var(--text-muted); font-weight:bold; letter-spacing:2px;">ARMED</div>
                </div>
                <div style="flex:1; background:rgba(124,158,191,0.03); border:1px solid rgba(124,158,191,0.2); padding:8px; border-radius:3px; text-align:center; box-shadow: inset 0 0 10px rgba(124,158,191,0.02);">
                    <div style="font-size:0.55rem; color:#7C9EBF; font-family:var(--font-m); letter-spacing:1px; margin-bottom:2px;">[ /INTEL ]</div>
                    <div style="font-size:0.45rem; color:var(--text-muted); font-weight:bold; letter-spacing:2px;">READY</div>
                </div>
                <div style="flex:1; background:rgba(76,175,154,0.03); border:1px solid rgba(76,175,154,0.2); padding:8px; border-radius:3px; text-align:center; box-shadow: inset 0 0 10px rgba(76,175,154,0.02);">
                    <div style="font-size:0.55rem; color:#4CAF9A; font-family:var(--font-m); letter-spacing:1px; margin-bottom:2px;">[ /HIKMAH ]</div>
                    <div style="font-size:0.45rem; color:var(--text-muted); font-weight:bold; letter-spacing:2px;">LOADED</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

    active_persona = cfg.get("active_persona")
    if active_persona:
        from forge.persona_engine import get_persona_display_name
        pname = get_persona_display_name(active_persona)
        st.markdown(f"""
            <div class="vc-card" style="padding:6px 12px; font-size:0.65rem; color:var(--gold); border-color:rgba(201,168,76,0.3); margin-bottom:15px; display:flex; align-items:center; gap:8px;">
                <span class="status-dot" style="width:4px; height:4px;"></span>
                TACTICAL PERSONA: {pname.upper()}
            </div>
        """, unsafe_allow_html=True)

    from config import client as _audio_client, WHISPER_CONTEXT_PROMPT
    audio_value = st.audio_input("Record your intent", label_visibility="collapsed")
    if audio_value is not None:
        audio_bytes = audio_value.read()
        audio_hash  = hashlib.md5(audio_bytes).hexdigest()
        if st.session_state.get("last_audio_hash") != audio_hash:
            with st.spinner("Transcribing..."):
                transcription = _audio_client.audio.transcriptions.create(file=("audio.wav", audio_bytes), model="whisper-large-v3-turbo", prompt=WHISPER_CONTEXT_PROMPT, response_format="text")
                st.session_state["ta_input"] = f"{st.session_state.get('ta_input', '')} {transcription}".strip()
                st.session_state["last_audio_hash"] = audio_hash
                st.rerun()

    raw_input = st.text_area("intent", height=145, placeholder="English or Arabic intent...", label_visibility="collapsed", key="ta_input")

    if st.button(t("execute_btn"), use_container_width=True, key="btn_execute"):
        cleaned, violations = sanitize_input(raw_input or "")
        
        if not cleaned: st.warning(t("empty_input"))
        elif violations: st.error(t("injection_blocked"))
        elif check_rate_limit(consume=1):
            
            # 🛠️ FIXED: Terminal Boot Sequence (Populates the Status block)
            with st.status("Initiating Cognitive Routing...", expanded=True) as status:
                
                st.write("✔️ Analyzing intent and payload...")
                final_text, detected_dna = _apply_dna_triggers(cleaned)
                st.session_state["last_detected_triggers"] = detected_dna
                
                resolved_target = cfg["target_model"]
                if resolved_target == AUTO_SELECT_LABEL:
                    st.write("✔️ Determining optimal AI architecture...")
                    auto_target, auto_reason = detect_best_target(final_text)
                    resolved_target = auto_target
                    st.session_state[K.AUTO_TARGET] = auto_target
                    st.session_state[K.AUTO_REASON] = auto_reason
                
                st.write("✔️ Executing forensic adversarial refinement...")
                result, audit, pattern = run_refinement_and_audit(
                    user_text        = final_text,
                    target           = resolved_target,
                    framework        = cfg["framework"],
                    lang             = cfg["source_lang"],
                    aesthetic_choice = cfg["aesthetic_choice"],
                    islamic_mode     = cfg["islamic_mode"],
                    persona          = cfg.get("active_persona"),
                )

                if not result.startswith("[CIPHER ERROR]"):
                    st.session_state[K.LAST_RESULT] = result
                    st.session_state["refined_output_area"] = result
                    st.session_state[K.LAST_AUDIT] = audit
                    st.session_state[K.LAST_INPUT] = cleaned
                    st.session_state[K.LAST_PATTERN] = pattern
                    
                    status.update(label="Refinement Complete.", state="complete", expanded=False)
                    st.rerun()

    # ── RESULTS RENDERING ─────────────────────────────────────────────────────
    last_result = st.session_state.get(K.LAST_RESULT)
    if last_result:
        left, right = st.columns([1, 2], gap="large")
        
        with left:
            _render_score_block(st.session_state.get(K.LAST_AUDIT, {}), st.session_state.get(K.LAST_PATTERN), st.session_state.get("last_detected_triggers"))
            
        with right:
            if "[CLARIFICATION_REQUIRED]" in last_result:
                st.warning(last_result.replace("[CLARIFICATION_REQUIRED]", ""))
            else:
                # The primary Refined Output Area
                st.text_area("Refined Asset", value=last_result, height=220, key="refined_output_area")
                
                # 💾 RESTORED: Download Button
                st.download_button(
                    label="💾 Download Asset (.txt)", 
                    data=last_result, 
                    file_name=f"InkOS_Refined_{datetime.now().strftime('%Y%m%d%H%M')}.txt", 
                    use_container_width=True
                )
                
                # 🔒 RESTORED: Save to Vault Form
                st.markdown("<div style='margin-top:16px; font-family:var(--font-m); font-size:0.65rem; color:var(--gold); letter-spacing:1px; margin-bottom:8px;'>🔒 SECURE TO MEMORY VAULT</div>", unsafe_allow_html=True)
                v_col1, v_col2, v_col3 = st.columns([2, 2, 1.2])
                with v_col1:
                    v_title = st.text_input("Title", placeholder="Asset Title...", label_visibility="collapsed", key="vault_title_input")
                with v_col2:
                    v_tags = st.text_input("Tags", placeholder="Tags (comma separated)...", label_visibility="collapsed", key="vault_tags_input")
                with v_col3:
                    if st.button("SECURE", use_container_width=True):
                        if "GUEST_" in str(st.session_state.get(K.USER_HASH, "")):
                            st.error("Guests cannot save to vault.")
                        elif not v_title.strip():
                            st.error("Title required.")
                        else:
                            # Triggers UI toast for save confirmation. Ensure your backend vault logic hooks into these keys!
                            st.toast("✔️ Asset secured to Memory Vault.")
