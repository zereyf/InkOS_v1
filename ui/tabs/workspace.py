"""
ui/tabs/workspace.py — Dual-State Workspace (Desk & Studio)
=============================================================
v5.6: The Architectural Sync.
      - Fixed DOM targeting for Brutalist button (via kind="primary").
      - Header forced to transparent to preserve native edge-to-edge UX.
      - Max history explicitly clamped to 3 items.
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

QUICK_ACTIONS = [
    ("🖊", "Refine", "Refine and improve the following prompt:\n\n"),
    ("💡", "Expand", "Expand this prompt with more detail, context, and specificity:\n\n"),
    ("🎯", "Focus", "Make this prompt more focused and precise. Remove vagueness:\n\n"),
    ("⚙️", "Adjust", "Adjust this prompt for a professional audience with clear structure:\n\n"),
]

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

def _format_history_entry(output_text: str, input_text: str):
    input_clean = input_text.strip()
    is_arabic = bool(re.search(r'[\u0600-\u06FF]', input_clean))
    title = output_text.strip().split('\n')[0][:35]
    title = re.sub(r'[*#_`]', '', title).strip()
    if not title: title = "Refined Prompt"
    
    if is_arabic:
        words = input_clean.split()
        avatar = words[0][:4] if words else "ع"
        lang_class = "ar-avatar"
        dir_class = "ar-text"
    else:
        avatar = input_clean[0].upper() if input_clean else "A"
        lang_class = "en-avatar"
        dir_class = "en-text"
        
    preview = input_clean[:60] + "..." if len(input_clean) > 60 else input_clean
    return avatar, title, preview, lang_class, dir_class


# ────────────────────────────────────────────────
# STATE 1: THE DESK (LIGHT MODE IDEATION)
# ────────────────────────────────────────────────
def _render_desk(cfg: dict):
    st.markdown("""
    <style>
    /* ── HEADER & MENU ICON OVERRIDE ── */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        box-shadow: none !important;
    }
    .stAppDeployButton { display: none !important; }
    
    /* Transform Streamlit Chevron into a Hamburger Menu */
    [data-testid="collapsedControl"] svg { display: none !important; }
    [data-testid="collapsedControl"] { color: transparent !important; background: transparent !important; }
    [data-testid="collapsedControl"]::after {
        content: "☰" !important;
        font-size: 26px !important;
        color: #111827 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-top: 5px;
        margin-left: 10px;
    }

    /* ── BASE LIGHT THEME ── */
    .stApp { background-color: #F9F9F9 !important; }
    .main .block-container { max-width: 600px !important; padding-top: 0px !important; padding-bottom: 100px !important; }
    
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    
    .desk-header { text-align: center; margin-bottom: 40px; margin-top: 10px; }
    .desk-logo { font-family: 'Playfair Display', serif; font-size: 42px; color: #111827; line-height: 1; letter-spacing: -1px; font-weight: 600; }
    .desk-logo-sub { font-family: 'Inter', sans-serif; font-size: 9px; color: #9CA3AF; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-top: 4px; }
    
    .greet-main { font-family: 'Playfair Display', serif; font-size: 34px; color: #111827 !important; margin-bottom: 5px; }
    .greet-sub { font-family: 'Inter', sans-serif; font-size: 15px; color: #6B7280 !important; margin-bottom: 25px; }

    /* ── STABLE INPUT AREA ── */
    div[data-testid="stTextArea"] > div, div[data-baseweb="textarea"], div[data-baseweb="base-input"] {
        background-color: transparent !important; background: transparent !important; border: none !important;
    }
    div[data-testid="stTextArea"] textarea {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 24px rgba(0,0,0,0.04) !important;
        color: #111827 !important;
        -webkit-text-fill-color: #111827 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 15px !important;
        padding: 16px !important;
        min-height: 120px !important;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #111827 !important; box-shadow: 0 8px 24px rgba(0,0,0,0.08) !important; outline: none !important;
    }
    div[data-testid="stTextArea"] label { display: none !important; }

    /* ── BRUTALIST PRIMARY BUTTON ── */
    button[kind="primary"] {
        background: transparent !important;
        background-color: transparent !important;
        color: #111827 !important;
        border-radius: 0px !important; /* Sharp Square */
        border: 2px solid #111827 !important; /* Thick Black Border */
        height: 54px !important;
        font-size: 14px !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        margin-top: 4px !important;
        box-shadow: none !important;
        transition: all 0.15s ease !important;
    }
    /* Hover/Active states invert the button */
    button[kind="primary"]:hover, button[kind="primary"]:active {
        background: #111827 !important;
        background-color: #111827 !important;
        color: #FFFFFF !important;
        border-color: #111827 !important;
    }

    /* ── DROPDOWN QUICK ACTIONS ── */
    div[data-testid="stSelectbox"] > div > div {
        background-color: #FFFFFF !important;
        border-radius: 16px !important;
        border: 1px solid #E5E7EB !important;
        color: #4B5563 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
    }
    
    /* ── RECENT INKS CARDS ── */
    .history-header { display: flex; justify-content: space-between; align-items: flex-end; margin-top: 30px; margin-bottom: 12px; }
    .history-title { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: 600; color: #111827; }
    .history-link { font-size: 13px; color: #6B7280; font-family: 'Inter', sans-serif; padding-top: 8px;}
    
    .history-card {
        background: #FFFFFF !important; border-radius: 16px; padding: 14px 16px; display: flex; gap: 14px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.02); margin-bottom: 12px; align-items: center;
        border: 1px solid #F3F4F6;
    }
    .history-avatar {
        width: 48px; height: 48px; border-radius: 50%; background: #F3F4F6; display: flex;
        align-items: center; justify-content: center; color: #111827; flex-shrink: 0; overflow: hidden;
    }
    .ar-avatar { font-family: 'Amiri', 'Noto Naskh Arabic', serif; font-size: 18px; font-weight: bold; }
    .en-avatar { font-family: 'Playfair Display', serif; font-size: 22px; font-weight: bold; }

    .history-content { flex-grow: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; }
    .ar-text { direction: rtl; text-align: right; }
    .en-text { direction: ltr; text-align: left; }
    
    .history-title-text { font-size: 14px; font-weight: 600; color: #111827; margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-family: 'Inter', sans-serif; }
    .history-preview { font-size: 12px; color: #9CA3AF; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; font-family: 'Inter', sans-serif; }
    
    .history-meta { display: flex; flex-direction: column; align-items: flex-end; justify-content: space-between; height: 44px; flex-shrink: 0; }
    .history-date { font-size: 11px; color: #9CA3AF; font-family: 'Inter', sans-serif; margin-top: 2px; }
    .history-dots { font-size: 16px; color: #6B7280; font-weight: bold; line-height: 1; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="desk-header">
            <div class="desk-logo">İnkOS</div>
            <div class="desk-logo-sub">PREMIUM AI PROMPT REFINER</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="greet-main">Good morning.</div>', unsafe_allow_html=True)
    st.markdown('<div class="greet-sub">Let\'s craft something exceptional.</div>', unsafe_allow_html=True)

    action_options = ["✨ Select a Quick Action..."] + [f"{icon} {label}" for icon, label, _ in QUICK_ACTIONS]
    selected_action = st.selectbox("Quick Actions", options=action_options, label_visibility="collapsed")
    
    prefill = st.session_state.pop("prefill_input", "")
    if selected_action != action_options[0]:
        for icon, label, starter in QUICK_ACTIONS:
            if f"{icon} {label}" == selected_action:
                prefill = starter
                break

    intent_val = st.text_area("Draft", value=prefill, placeholder="Draft your prompt...", key="desk_input")
    
    # ── FIXED BUTTON LOGIC (Targeting Type=Primary) ──
    send = st.button("Refine Prompt", key="desk_send", type="primary", use_container_width=True)

    st.markdown("""<div class="history-header">
        <div class="history-title">Recent Inks</div>
        <div class="history-link">View all ›</div>
    </div>""", unsafe_allow_html=True)
    
    history = st.session_state.get(K.HISTORY, [])
    if history:
        for idx, entry in enumerate(reversed(history[-3:])):
            avatar, title, preview, lang_class, dir_class = _format_history_entry(entry.get("output", ""), entry.get("input", ""))
            
            st.markdown(f"""
                <div class="history-card">
                    <div class="history-avatar {lang_class}">{avatar}</div>
                    <div class="history-content {dir_class}">
                        <div class="history-title-text">{title}</div>
                        <div class="history-preview">{preview}</div>
                    </div>
                    <div class="history-meta">
                        <div class="history-date">Just now</div>
                        <div class="history-dots">⋮</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    else:
         st.markdown("""
             <div style='text-align:center; padding: 40px; color: #9CA3AF; font-size: 14px; font-family: Inter, sans-serif;'>
                 No recent inks found.
             </div>
         """, unsafe_allow_html=True)

    if send and intent_val and intent_val.strip():
        _process_prompt(intent_val, cfg)


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
        
        try:
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
            if not result or result.strip() == "":
                result = "Engine returned an empty response. Verify AI uplink."
        except Exception as e:
            result = f"[ UPLINK FAILED ]\n\nThe A.I.Z.E.N. core encountered an error:\n{str(e)}"

        history = st.session_state.get(K.HISTORY, [])
        history.append({"input": cleaned, "output": result, "time": datetime.now(WAT_TZ).isoformat()})
        st.session_state[K.HISTORY] = history[-50:]
        
        st.session_state[K.LAST_RESULT] = result
        st.session_state[K.LAST_INPUT] = cleaned
        st.rerun()


# ────────────────────────────────────────────────
# STATE 2: THE STUDIO (DARK MODE REFINEMENT)
# ────────────────────────────────────────────────
def _render_studio(cfg: dict):
    st.markdown("""
    <style>
    /* Ensure Header is hidden in Studio too */
    header[data-testid="stHeader"] { background-color: transparent !important; box-shadow: none !important; }
    [data-testid="collapsedControl"] svg { display: none !important; }
    [data-testid="collapsedControl"]::after { content: "☰" !important; color: #F8F9FA !important; font-size: 26px !important; margin-top: 5px; margin-left: 10px; display: flex; align-items: center; justify-content: center;}
    
    .stApp { background-color: #0B0F19 !important; color: #F8F9FA !important; }
    .main .block-container { max-width: 600px !important; padding-top: 40px !important; }
    
    .studio-header { margin-bottom: 30px; }
    .studio-title { font-family: 'Playfair Display', serif; font-size: 32px; color: #F8F9FA; margin-bottom: 4px; }
    .studio-sub { font-family: 'Inter', sans-serif; font-size: 14px; color: #9CA3AF; }

    .card-orig {
        background: #121826; border-radius: 16px; padding: 20px; margin-bottom: -10px;
        border: 1px solid rgba(255,255,255,0.05); z-index: 1; position: relative;
    }
    .card-refined {
        background: #0B0F19; border-radius: 16px; padding: 24px; margin-bottom: 20px;
        border: 1px solid rgba(212, 175, 55, 0.4); box-shadow: 0 0 30px rgba(212,175,55,0.08);
        z-index: 2; position: relative;
    }
    
    .card-label { display: flex; align-items: center; justify-content: space-between; font-family: 'Inter', sans-serif; font-size: 13px; color: #9CA3AF; margin-bottom: 15px; }
    .card-label-gold { color: #D4AF37; font-weight: 500; }
    .badge-gold { border: 1px solid rgba(212,175,55,0.3); background: rgba(212,175,55,0.1); padding: 4px 10px; border-radius: 999px; font-size: 11px; }
    .text-orig { font-family: 'Inter', sans-serif; font-size: 15px; color: #E5E7EB; line-height: 1.6; margin-bottom: 20px;}
    .text-refined { font-family: 'Playfair Display', serif; font-size: 18px; color: #F8F9FA; line-height: 1.7; margin-bottom: 20px; white-space: pre-wrap;}
    .meta-row { display: flex; justify-content: space-between; border-top: 1px solid rgba(255,255,255,0.05); padding-top: 12px; font-size: 11px; color: #6B7280; font-family: 'Inter', sans-serif;}
    
    .connector { text-align: center; z-index: 3; position: relative; transform: translateY(4px); }
    .connector-icon { background: #121826; color: #6B7280; border: 1px solid rgba(255,255,255,0.05); border-radius: 999px; padding: 4px; font-size: 12px; }

    /* Override secondary buttons in Studio so they look correct */
    button[kind="secondary"] {
        background: #121826 !important; border: 1px solid rgba(255,255,255,0.1) !important;
        color: #D4AF37 !important; border-radius: 8px !important; font-family: 'Inter', sans-serif !important; font-size: 13px !important;
        text-transform: uppercase !important; letter-spacing: 1px !important; font-weight: 600 !important;
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

    c1, c2, c3 = st.columns(3)
    with c1: st.button("Copy", key="btn_copy", use_container_width=True)
    with c2: st.button("Share", key="btn_share", use_container_width=True)
    with c3: 
        if st.button("Re-ink", key="btn_reink", use_container_width=True):
            st.session_state[K.LAST_RESULT] = None
            st.session_state["prefill_input"] = raw_input
            st.rerun()

# ────────────────────────────────────────────────
# MAIN RENDERER
# ────────────────────────────────────────────────
def render_workspace(cfg: dict) -> None:
    last = st.session_state.get(K.LAST_RESULT)
    if last is not None and str(last).strip() != "":
        _render_studio(cfg)
    else:
        _render_desk(cfg)
