"""
ui/tabs/workspace.py — Dual-State Workspace (Desk & Studio)
=============================================================
v5.0: The Figma Sync.
      - Automatically routes between Light "Desk" (Ideation) and Dark "Studio" (Refinement).
      - Integrates native Streamlit widgets into the custom CSS grid.
"""
from __future__ import annotations
import re, time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

import streamlit as st
from state import K
from security.sanitizer import sanitize_input
from engine.refiner import run_refinement_and_audit
from forge.prompt_assembler import assemble_master_payload
from forge.intelligence import resolve_target_model

WAT_TZ = timezone(timedelta(hours=1))

# ── QUICK ACTIONS ──
QUICK_ACTIONS = [
    ("🖊", "Refine", "Refine and improve the following prompt:\n\n"),
    ("💡", "Expand", "Expand this prompt with more detail, context, and specificity:\n\n"),
    ("🎯", "Focus", "Make this prompt more focused and precise. Remove vagueness:\n\n"),
    ("⚙️", "Adjust", "Adjust this prompt for a professional audience with clear structure:\n\n"),
]

# ────────────────────────────────────────────────
# HELPERS & LOGIC (Retained from your core)
# ────────────────────────────────────────────────

def _get_dna_context() -> dict:
    return {
        K.INK_DNA:    str(st.session_state.get(K.INK_DNA)    or ""),
        K.INTEL_DNA:  str(st.session_state.get(K.INTEL_DNA)  or ""),
        K.HIKMAH_DNA: str(st.session_state.get(K.HIKMAH_DNA) or ""),
    }

def extract_clean_output(raw: str) -> str:
    t = str(raw or "")
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

def _word_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0

# ────────────────────────────────────────────────
# ────────────────────────────────────────────────
# STATE 1: THE DESK (LIGHT MODE IDEATION)
# ────────────────────────────────────────────────
def _render_desk(cfg: dict):
    st.markdown("""
    <style>
    /* Base Light Theme */
    .stApp { background-color: #F9F9F9 !important; color: #111827 !important; }
    .main .block-container { max-width: 600px !important; padding-top: 20px !important; padding-bottom: 100px !important; }
    
    /* Typography */
    .greet-main { font-family: 'Playfair Display', serif; font-size: 34px; color: #111827; margin-bottom: 5px; }
    .greet-sub { font-family: 'Inter', sans-serif; font-size: 15px; color: #6B7280; margin-bottom: 30px; }

    /* ── THE INPUT PILL (Forcing Horizontal on Mobile) ── */
    /* This overrides Streamlit's mobile stacking rule */
    div[data-testid="stHorizontalBlock"]:has(.input-marker) {
        flex-wrap: nowrap !important;
        background-color: #FFFFFF !important;
        border-radius: 30px !important;
        padding: 5px 15px !important;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03) !important;
        border: 1px solid #F3F4F6 !important;
        align-items: center !important;
        gap: 10px !important;
    }
    /* Hide text area borders to blend into the pill */
    div[data-testid="stHorizontalBlock"]:has(.input-marker) div[data-testid="stTextArea"] textarea {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 10px 0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 15px !important;
        color: #111827 !important;
    }
    /* Circular Send Button */
    div[data-testid="stHorizontalBlock"]:has(.input-marker) div[data-testid="stButton"] button {
        background-color: #111827 !important;
        color: #FFFFFF !important;
        border-radius: 999px !important;
        height: 45px !important;
        width: 45px !important;
        padding: 0 !important;
        font-size: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: none !important;
    }

    /* ── QUICK ACTIONS (Forcing Horizontal Scroll on Mobile) ── */
    div[data-testid="stHorizontalBlock"]:has(.qa-marker) {
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        padding-bottom: 15px !important;
        gap: 10px !important;
        scrollbar-width: none !important; /* Hide scrollbar Firefox */
    }
    div[data-testid="stHorizontalBlock"]:has(.qa-marker)::-webkit-scrollbar {
        display: none !important; /* Hide scrollbar Chrome/Safari */
    }
    div[data-testid="stHorizontalBlock"]:has(.qa-marker) > div[data-testid="column"] {
        min-width: 110px !important;
        width: auto !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.qa-marker) button {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 999px !important;
        color: #4B5563 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        padding: 8px 16px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
        white-space: nowrap !important;
    }

    /* ── RECENT INKS ── */
    .history-header { display: flex; justify-content: space-between; align-items: flex-end; margin-top: 20px; margin-bottom: 15px; }
    .history-title { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 600; color: #111827; }
    .history-link { font-size: 12px; color: #6B7280; font-family: 'Inter', sans-serif; }
    
    .history-card {
        background: #FFFFFF; border-radius: 16px; padding: 16px; display: flex; gap: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.03); margin-bottom: 12px; align-items: center;
        border: 1px solid #F9FAFB;
    }
    .history-avatar {
        width: 55px; height: 55px; border-radius: 999px; background: #F3F4F6; display: flex;
        align-items: center; justify-content: center; font-family: 'Noto Naskh Arabic', serif; font-size: 22px; color: #111827; flex-shrink: 0;
    }
    .history-content { flex-grow: 1; }
    .history-title-text { font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 4px; font-family: 'Inter', sans-serif; }
    .history-preview { font-size: 12px; color: #6B7280; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; font-family: 'Inter', sans-serif;}
    .history-date { font-size: 11px; color: #9CA3AF; font-family: 'Inter', sans-serif;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="greet-main">Good morning.</div>', unsafe_allow_html=True)
    st.markdown('<div class="greet-sub">Let\'s craft something exceptional.</div>', unsafe_allow_html=True)

    # ── INPUT PILL ──
    col_input, col_btn = st.columns([5, 1])
    with col_input:
        st.markdown("<div class='input-marker'></div>", unsafe_allow_html=True) # Invisible marker protects CSS layout
        prefill = st.session_state.pop("prefill_input", "")
        intent_val = st.text_area("Draft", value=prefill, height=68, placeholder="✨ Draft your prompt...", label_visibility="collapsed", key="desk_input")
    with col_btn:
        send = st.button("→", key="desk_send", use_container_width=True)

    # ── QUICK ACTIONS ──
    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    cols = [c1, c2, c3, c4]
    for i, (icon, label, starter) in enumerate(QUICK_ACTIONS):
        with cols[i]:
            if i == 0:
                st.markdown("<div class='qa-marker'></div>", unsafe_allow_html=True) # Invisible marker protects CSS layout
            if st.button(f"{icon} {label}", key=f"qa_{i}", use_container_width=True):
                st.session_state["prefill_input"] = starter
                st.rerun()

    # ── RECENT INKS ──
    history = st.session_state.get(K.HISTORY, [])
    st.markdown("""
        <div class="history-header">
            <div class="history-title">Recent Inks</div>
            <div class="history-link">View all ›</div>
        </div>
    """, unsafe_allow_html=True)
    
    if history:
        for idx, entry in enumerate(reversed(history[-3:])):
            out_text = entry.get("output", "")
            title = out_text[:40] + "..." if len(out_text) > 40 else out_text
            st.markdown(f"""
                <div class="history-card">
                    <div class="history-avatar">❖</div>
                    <div class="history-content">
                        <div class="history-title-text">{title}</div>
                        <div class="history-preview">{entry.get("input", "")[:80]}...</div>
                    </div>
                    <div><div class="history-date">Just now</div></div>
                </div>
            """, unsafe_allow_html=True)
    else:
         st.markdown("""
             <div style='text-align:center; padding: 40px; color: #9CA3AF; font-size: 14px; font-family: Inter, sans-serif;'>
                 No recent inks found.
             </div>
         """, unsafe_allow_html=True)

    # Process Input
    if send and intent_val and intent_val.strip():
        _process_prompt(intent_val, cfg)



# ────────────────────────────────────────────────
# STATE 2: THE STUDIO (DARK MODE REFINEMENT)
# ────────────────────────────────────────────────
def _render_studio(cfg: dict):
    st.markdown("""
    <style>
    /* Studio Dark Theme Overrides */
    .stApp { background-color: #0B0F19 !important; color: #F8F9FA !important; }
    .main .block-container { max-width: 600px !important; padding-top: 30px !important; }
    
    /* Header */
    .studio-header { margin-bottom: 30px; }
    .studio-title { font-family: 'Playfair Display', serif; font-size: 32px; color: #F8F9FA; margin-bottom: 4px; }
    .studio-sub { font-family: 'Inter', sans-serif; font-size: 14px; color: #9CA3AF; }

    /* Cards */
    .card-orig {
        background: #121826; border-radius: 16px; padding: 20px; margin-bottom: -10px;
        border: 1px solid rgba(255,255,255,0.05); z-index: 1; position: relative;
    }
    .card-refined {
        background: #0B0F19; border-radius: 16px; padding: 24px; margin-bottom: 20px;
        border: 1px solid rgba(212, 175, 55, 0.4); box-shadow: 0 0 30px rgba(212,175,55,0.08);
        z-index: 2; position: relative;
    }
    
    /* Typography inside cards */
    .card-label { display: flex; align-items: center; justify-content: space-between; font-family: 'Inter', sans-serif; font-size: 13px; color: #9CA3AF; margin-bottom: 15px; }
    .card-label-gold { color: #D4AF37; font-weight: 500; }
    .badge-gold { border: 1px solid rgba(212,175,55,0.3); background: rgba(212,175,55,0.1); padding: 4px 10px; border-radius: 999px; font-size: 11px; }
    .text-orig { font-family: 'Inter', sans-serif; font-size: 15px; color: #E5E7EB; line-height: 1.6; margin-bottom: 20px;}
    .text-refined { font-family: 'Playfair Display', serif; font-size: 18px; color: #F8F9FA; line-height: 1.7; margin-bottom: 20px;}
    .meta-row { display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 12px; font-size: 11px; color: #6B7280; font-family: 'Inter', sans-serif;}
    
    /* Connector */
    .connector { text-align: center; z-index: 3; position: relative; transform: translateY(4px); }
    .connector-icon { background: #121826; color: #6B7280; border: 1px solid rgba(255,255,255,0.05); border-radius: 999px; padding: 4px; font-size: 12px; }

    /* Action Row overrides */
    .studio-actions button {
        background: #121826 !important; border: 1px solid rgba(255,255,255,0.1) !important;
        color: #D4AF37 !important; border-radius: 12px !important; font-family: 'Inter', sans-serif !important; font-size: 13px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="studio-header">
            <div class="studio-title">Studio</div>
            <div class="studio-sub">Refine your thoughts. Ink with clarity.</div>
        </div>
    """, unsafe_allow_html=True)

    raw_input = st.session_state.get(K.LAST_INPUT, "")
    result = st.session_state.get(K.LAST_RESULT, "")

    # Original Card
    st.markdown(f"""
        <div class="card-orig">
            <div class="card-label"><span>🖊 Original Prompt</span> <span>Edit ✏️</span></div>
            <div class="text-orig">{raw_input}</div>
            <div class="meta-row"><span>{_word_count(raw_input)} words</span> <span>⎘</span></div>
        </div>
        <div class="connector"><span class="connector-icon">▼</span></div>
        <div class="card-refined">
            <div class="card-label card-label-gold"><span>✨ Refined Ink</span> <span class="badge-gold">✦ Refined</span></div>
            <div class="text-refined">{result}</div>
            <div class="meta-row" style="border-top: 1px solid rgba(212,175,55,0.2);"><span>{_word_count(result)} words</span> <span>⎘</span></div>
        </div>
    """, unsafe_allow_html=True)

    # Action Row
    st.markdown('<div class="studio-actions">', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.button("⎘ Copy", use_container_width=True)
    with c2: st.button("↗ Share", use_container_width=True)
    with c3: 
        if st.button("↺ Re-ink", use_container_width=True):
            st.session_state[K.LAST_RESULT] = None
            st.session_state["prefill_input"] = raw_input
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


# ────────────────────────────────────────────────
# ENGINE EXECUTION
# ────────────────────────────────────────────────
def _process_prompt(intent_val: str, cfg: dict):
    cleaned, violations = sanitize_input(intent_val)
    if violations:
        st.error("⚠ Blocked by security policy.")
        return

    with st.spinner("Inking..."):
        run_cfg = dict(cfg)
        payload = assemble_master_payload(cleaned, run_cfg, _get_dna_context())
        
        # We bypass the manual 7-second sleep animation for production speed
        # Real AI call:
        result, audit, _ = run_refinement_and_audit(
            payload,
            resolve_target_model(cfg.get("target_model", "auto"), cleaned)[0],
            cfg.get("framework", "RACE"),
            cfg.get("source_lang", "English"),
            cfg.get("aesthetic_choice", "Default"),
            hikmah_style=str(cfg.get("hikmah_style") or "None"),
            skip_security=False,
        )
        
        result = extract_clean_output(result)

        history = st.session_state.get(K.HISTORY, [])
        history.append({"input": cleaned, "output": result, "time": datetime.now(WAT_TZ).isoformat()})
        st.session_state[K.HISTORY] = history[-50:]
        st.session_state[K.LAST_RESULT] = result
        st.session_state[K.LAST_INPUT] = cleaned
        st.rerun()


# ────────────────────────────────────────────────
# MAIN RENDERER (THE ROUTER)
# ────────────────────────────────────────────────
def render_workspace(cfg: dict) -> None:
    # THE DUAL-STATE ROUTER
    # If a result exists in memory, we are in the Studio (Dark).
    # If memory is clear, we are at the Desk (Light).
    if st.session_state.get(K.LAST_RESULT):
        _render_studio(cfg)
    else:
        _render_desk(cfg)
