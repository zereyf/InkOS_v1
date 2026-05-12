"""
ui/tabs/workspace.py — Dual-State Workspace (Desk & Studio)
=============================================================
v8.0: The Perfection Patch.
      - Stealth "Edit" button wired for instant Desk return.
      - "Ghost" Model Picker injected for seamless UX.
      - Custom Ink styling applied to the execution spinner.
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

# ── QUICK ACTIONS & MODELS ──
QUICK_ACTIONS = [
    ("🖊", "Refine", "Refine and improve the following prompt:\n\n"),
    ("💡", "Expand", "Expand this prompt with more detail, context, and specificity:\n\n"),
    ("🎯", "Focus", "Make this prompt more focused and precise. Remove vagueness:\n\n"),
    ("⚙️", "Adjust", "Adjust this prompt for a professional audience with clear structure:\n\n"),
]
AVAILABLE_MODELS = ["A.I.Z.E.N. Core", "Claude 3.5 Sonnet", "Gemini 1.5 Pro"]

def _get_dna_context() -> dict:
    return {
        K.INK_DNA:    str(st.session_state.get(K.INK_DNA)    or ""),
        K.INTEL_DNA:  str(st.session_state.get(K.INTEL_DNA)  or ""),
        K.HIKMAH_DNA: str(st.session_state.get(K.HIKMAH_DNA) or ""),
    }

def extract_clean_output(raw: str) -> str:
    t = str(raw or "")
    t = re.sub(r"Claude Target Specific Output\s*", "", t, flags=re.I)
    t = re.sub(r"JSON Audit Object[\s\S]*", "", t, flags=re.I) 
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
# STATE 1: THE DESK (IDEATION PHASE)
# ────────────────────────────────────────────────
def _render_desk(cfg: dict):
    theme = st.session_state.get("desk_theme", "light")
    
    st.markdown("""
    <style>
    header[data-testid="stHeader"] { background-color: transparent !important; box-shadow: none !important; }
    .stAppDeployButton { display: none !important; }
    .stAppToolbar > div:not(:first-child) { display: none !important; }
    
    [data-testid="collapsedControl"] { color: var(--text-1) !important; }
    [data-testid="collapsedControl"] svg { display: none !important; }
    [data-testid="collapsedControl"]::before { content: "☰" !important; font-size: 28px !important; color: var(--text-1) !important; display: block !important; line-height: 1; margin-top: 4px; margin-left: 8px; }

    .desk-header { display: flex; flex-direction: column; align-items: center; margin-bottom: 40px; margin-top: -30px; }
    .desk-logo { font-family: var(--font-serif); font-size: 46px; color: var(--text-1); line-height: 1; letter-spacing: -1px; font-weight: 600; }
    .desk-logo-sub { font-family: var(--font-sans); font-size: 9px; color: var(--text-3); letter-spacing: 2.5px; text-transform: uppercase; font-weight: 600; margin-top: 6px; }
    
    .greet-main { font-family: var(--font-serif); font-size: 34px; color: var(--text-1) !important; margin-bottom: 5px; }
    .greet-sub { font-family: var(--font-sans); font-size: 15px; color: var(--text-2) !important; margin-bottom: 25px; }

    div.theme-toggle-btn div[data-testid="stButton"] button {
        background: transparent !important; border: 1px solid var(--border) !important; border-radius: 50% !important;
        width: 44px !important; height: 44px !important; display: flex !important; align-items: center !important; justify-content: center !important;
        color: var(--text-1) !important; font-size: 18px !important; box-shadow: none !important; margin-left: auto !important;
    }

    button[kind="primary"] {
        background: transparent !important; color: var(--text-1) !important; border-radius: 0px !important; 
        border: 2px solid var(--text-1) !important; height: 54px !important; font-family: var(--font-sans) !important; 
        font-size: 14px !important; font-weight: 700 !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; 
        margin-top: 4px !important; box-shadow: none !important; transition: all 0.2s ease !important;
    }
    button[kind="primary"]:hover, button[kind="primary"]:active {
        background: var(--text-1) !important; color: var(--bg) !important; border-color: var(--text-1) !important;
    }

    /* ── Ghost Model Picker ── */
    .model-picker-container div[data-testid="stSelectbox"] > div > div {
        background: transparent !important; border: none !important; box-shadow: none !important; color: var(--text-3) !important; font-size: 12px !important; font-family: var(--font-sans) !important; padding: 0 !important; min-height: 20px !important; margin-bottom: -10px !important;
    }
    .model-picker-container div[data-testid="stSelectbox"] svg { fill: var(--text-3) !important; width: 12px !important;}

    /* ── Quick Actions ── */
    .qa-container div[data-testid="stSelectbox"] > div > div {
        background-color: var(--surface-card) !important; border-radius: 16px !important; border: 1px solid var(--border) !important;
        color: var(--text-1) !important; font-family: var(--font-sans) !important; font-size: 14px !important; box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
    }

    /* ── Input Area ── */
    div[data-testid="stTextArea"] > div, div[data-baseweb="textarea"], div[data-baseweb="base-input"] { background: transparent !important; border: none !important; }
    div[data-testid="stTextArea"] textarea {
        background-color: var(--surface-card) !important; border: 1px solid var(--border) !important; border-radius: 16px !important;
        box-shadow: var(--shadow-sm) !important; color: var(--text-1) !important; -webkit-text-fill-color: var(--text-1) !important;
        font-family: var(--font-sans) !important; font-size: 15px !important; padding: 16px !important; min-height: 120px !important;
    }
    div[data-testid="stTextArea"] textarea:focus { border-color: var(--text-1) !important; box-shadow: var(--shadow-md) !important; outline: none !important; }
    div[data-testid="stTextArea"] label { display: none !important; }

    /* ── Custom Spinner ── */
    [data-testid="stSpinner"] > div > div { border-color: var(--text-1) transparent var(--text-1) transparent !important; }
    [data-testid="stSpinner"] > div > div:nth-child(2) { color: var(--text-1) !important; font-family: var(--font-serif) !important; font-style: italic !important; font-size: 16px !important;}

    .history-header { display: flex; justify-content: space-between; align-items: flex-end; margin-top: 30px; margin-bottom: 12px; }
    .history-title { font-family: var(--font-serif); font-size: 22px; font-weight: 600; color: var(--text-1); }
    .history-link { font-size: 13px; color: var(--text-2); font-family: var(--font-sans); padding-top: 8px;}
    .history-card { background: var(--surface-card) !important; border-radius: 16px; padding: 14px 16px; display: flex; gap: 14px; box-shadow: var(--shadow-sm); margin-bottom: 12px; align-items: center; border: 1px solid var(--border); }
    .history-avatar { width: 48px; height: 48px; border-radius: 50%; background: var(--surface-up); display: flex; align-items: center; justify-content: center; color: var(--text-1); flex-shrink: 0; border: 1px solid var(--border); }
    .ar-avatar { font-family: var(--font-ar-serif); font-size: 18px; font-weight: bold; }
    .en-avatar { font-family: var(--font-serif); font-size: 22px; font-weight: bold; }
    .history-content { flex-grow: 1; min-width: 0; display: flex; flex-direction: column; justify-content: center; }
    .ar-text { direction: rtl; text-align: right; }
    .en-text { direction: ltr; text-align: left; }
    .history-title-text { font-size: 14px; font-weight: 600; color: var(--text-1); margin-bottom: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-family: var(--font-sans); }
    .history-preview { font-size: 12px; color: var(--text-2); line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; font-family: var(--font-sans); }
    .history-meta { display: flex; flex-direction: column; align-items: flex-end; justify-content: space-between; height: 44px; flex-shrink: 0; }
    .history-date { font-size: 11px; color: var(--text-3); font-family: var(--font-sans); margin-top: 2px; }
    .history-dots { font-size: 16px; color: var(--text-3); font-weight: bold; line-height: 1; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="theme-toggle-btn">', unsafe_allow_html=True)
    col_space, col_t = st.columns([8, 1.5])
    with col_t:
        toggle_icon = "🌙" if theme == "light" else "☀️"
        if st.button(toggle_icon, key="btn_theme_toggle"):
            st.session_state["desk_theme"] = "dark" if theme == "light" else "light"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
        <div class="desk-header">
            <div class="desk-logo">İnkOS</div>
            <div class="desk-logo-sub">PREMIUM AI PROMPT REFINER</div>
        </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="greet-main">Good morning.</div>', unsafe_allow_html=True)
    st.markdown('<div class="greet-sub">Let\'s craft something exceptional.</div>', unsafe_allow_html=True)

    # Ghost Model Picker & Quick Actions
    st.markdown('<div class="model-picker-container">', unsafe_allow_html=True)
    selected_model = st.selectbox("Target Model", options=AVAILABLE_MODELS, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="qa-container">', unsafe_allow_html=True)
    action_options = ["✨ Select a Quick Action..."] + [f"{icon} {label}" for icon, label, _ in QUICK_ACTIONS]
    selected_action = st.selectbox("Quick Actions", options=action_options, label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    
    prefill = st.session_state.pop("prefill_input", "")
    if selected_action != action_options[0]:
        for icon, label, starter in QUICK_ACTIONS:
            if f"{icon} {label}" == selected_action: prefill = starter; break

    intent_val = st.text_area("Draft", value=prefill, placeholder="Draft your prompt...", key="desk_input")
    send = st.button("REFINE PROMPT", key="desk_send", type="primary", use_container_width=True)

    st.markdown("""<div class="history-header"><div class="history-title">Recent Inks</div><div class="history-link">View all ›</div></div>""", unsafe_allow_html=True)
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
                    <div class="history-meta"><div class="history-date">Just now</div><div class="history-dots">⋮</div></div>
                </div>
            """, unsafe_allow_html=True)
    else:
         st.markdown(f"<div style='text-align:center; padding: 40px; color: var(--text-3); font-size: 14px; font-family: var(--font-sans);'>No recent inks found.</div>", unsafe_allow_html=True)

    if send and intent_val and intent_val.strip(): _process_prompt(intent_val, selected_model, cfg)


# ────────────────────────────────────────────────
# ENGINE EXECUTION
# ────────────────────────────────────────────────
def _process_prompt(intent_val: str, model_selection: str, cfg: dict):
    cleaned, violations = sanitize_input(intent_val)
    if violations: st.error("⚠ Blocked by security policy."); return

    # Custom Ink Spinner
    with st.spinner("Distilling ink..."):
        run_cfg = dict(cfg)
        payload = assemble_master_payload(cleaned, run_cfg, _get_dna_context())
        
        # Map frontend model string to backend target
        target_map = {"A.I.Z.E.N. Core": "auto", "Claude 3.5 Sonnet": "claude", "Gemini 1.5 Pro": "gemini"}
        actual_target = target_map.get(model_selection, "auto")

        try:
            result, audit, _ = run_refinement_and_audit(
                payload, resolve_target_model(actual_target, cleaned)[0],
                cfg.get("framework", "RACE"), cfg.get("source_lang", "English"),
                cfg.get("aesthetic_choice", "Default"), hikmah_style=str(cfg.get("hikmah_style") or "None"), skip_security=False,
            )
            result = extract_clean_output(result)
            if not result or result.strip() == "": result = "Engine returned an empty response. Verify AI uplink."
        except Exception as e:
            result = f"[ UPLINK FAILED ]\n\nThe A.I.Z.E.N. core encountered an error:\n{str(e)}"

        history = st.session_state.get(K.HISTORY, [])
        history.append({"input": cleaned, "output": result, "time": datetime.now(WAT_TZ).isoformat()})
        st.session_state[K.HISTORY] = history[-50:]
        
        st.session_state[K.LAST_RESULT] = str(result)
        st.session_state[K.LAST_INPUT] = str(cleaned)
        st.session_state["in_studio"] = True
        st.session_state["desk_theme"] = "dark"
        st.rerun()


# ────────────────────────────────────────────────
# STATE 2: THE STUDIO (DARK MODE REFINEMENT)
# ────────────────────────────────────────────────
def _render_studio(cfg: dict):
    st.markdown("""
    <style>
    header[data-testid="stHeader"] { background-color: transparent !important; box-shadow: none !important; }
    .stAppDeployButton { display: none !important; }
    .stAppToolbar > div:not(:first-child) { display: none !important; }
    
    [data-testid="collapsedControl"] { color: var(--text-1) !important; }
    [data-testid="collapsedControl"] svg { display: none !important; }
    [data-testid="collapsedControl"]::before { content: "☰" !important; font-size: 28px !important; color: var(--text-1) !important; display: block !important; line-height: 1; margin-top: 4px; margin-left: 8px;}
    
    .studio-header { margin-bottom: 30px; margin-top: 20px;}
    .studio-title { font-family: var(--font-serif); font-size: 32px; color: var(--text-1); margin-bottom: 4px; }
    .studio-sub { font-family: var(--font-sans); font-size: 14px; color: var(--text-2); }

    .card-orig { background: var(--surface-card); border-radius: 16px; padding: 20px 20px 30px 20px; margin-bottom: -10px; border: 1px solid var(--border); z-index: 1; position: relative; }
    .card-refined { background: var(--surface); border-radius: 16px; padding: 24px; margin-bottom: 20px; border: 1px solid var(--border-gold); box-shadow: 0 0 30px var(--gold-dim); z-index: 2; position: relative; }
    
    .card-label { display: flex; align-items: center; justify-content: space-between; font-family: var(--font-sans); font-size: 13px; color: var(--text-2); margin-bottom: 15px; }
    .card-label-gold { color: var(--gold); font-weight: 500; }
    .badge-gold { border: 1px solid var(--gold-border); background: var(--gold-dim); padding: 4px 10px; border-radius: 999px; font-size: 11px; color: var(--gold); }
    .text-orig { font-family: var(--font-sans); font-size: 15px; color: var(--text-1); line-height: 1.6; margin-bottom: 20px;}
    .text-refined { font-family: var(--font-serif); font-size: 18px; color: var(--text-1); line-height: 1.7; margin-bottom: 20px; white-space: pre-wrap;}
    .meta-row { display: flex; justify-content: space-between; border-top: 1px solid var(--border); padding-top: 12px; font-size: 11px; color: var(--text-3); font-family: var(--font-sans);}
    
    .connector { text-align: center; z-index: 3; position: relative; transform: translateY(4px); }
    .connector-icon { background: var(--surface-card); color: var(--text-3); border: 1px solid var(--border); border-radius: 999px; padding: 4px; font-size: 12px; }

    /* ── STEALTH EDIT BUTTON ── */
    /* Hijack the Streamlit button to look exactly like the "Edit ✏️" text label */
    .stealth-edit button { background: transparent !important; border: none !important; box-shadow: none !important; color: var(--text-2) !important; font-size: 13px !important; font-family: var(--font-sans) !important; padding: 0 !important; height: auto !important; min-height: 0 !important; }
    .stealth-edit button:hover { color: var(--text-1) !important; }

    div[data-testid="stHorizontalBlock"]:has(.studio-btn-marker) { display: flex !important; flex-direction: row !important; flex-wrap: nowrap !important; gap: 10px !important; }
    div[data-testid="stHorizontalBlock"]:has(.studio-btn-marker) > div[data-testid="column"] { width: 33.33% !important; flex: 1 1 0px !important; }
    div[data-testid="stHorizontalBlock"]:has(.studio-btn-marker) button { width: 100% !important; padding: 12px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="studio-header"><div class="studio-title">Studio</div><div class="studio-sub">Refine your thoughts. Ink with clarity.</div></div>', unsafe_allow_html=True)

    raw_input = st.session_state.get(K.LAST_INPUT, "")
    result = st.session_state.get(K.LAST_RESULT, "")

    # We use columns here so the Streamlit "Edit" button sits exactly opposite the label
    st.markdown('<div class="card-orig">', unsafe_allow_html=True)
    c_lbl, c_edit = st.columns([5, 1])
    with c_lbl:
        st.markdown('<div class="card-label"><span>🖊 Original Prompt</span></div>', unsafe_allow_html=True)
    with c_edit:
        st.markdown('<div class="stealth-edit">', unsafe_allow_html=True)
        if st.button("Edit ✏️", key="btn_edit_orig"):
            st.session_state["in_studio"] = False
            st.session_state[K.LAST_RESULT] = None
            st.session_state["desk_theme"] = "light" # Snap back to light mode
            st.session_state["prefill_input"] = raw_input
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""
            <div class="text-orig">{raw_input}</div>
            <div class="meta-row"><span>{_word_count(raw_input)} words</span> <span>⎘</span></div>
        </div>
        <div class="connector"><span class="connector-icon">▼</span></div>
        <div class="card-refined">
            <div class="card-label card-label-gold"><span>✨ Refined Ink</span> <span class="badge-gold">✦ Refined</span></div>
            <div class="text-refined">{result}</div>
            <div class="meta-row" style="border-top: 1px solid var(--border-gold);"><span>{_word_count(result)} words</span> <span>⎘</span></div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div class='studio-btn-marker'></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.button("Copy", key="btn_copy", use_container_width=True)
    with c2: st.button("Share", key="btn_share", use_container_width=True)
    with c3: 
        if st.button("Re-ink", key="btn_reink", use_container_width=True):
            st.session_state["in_studio"] = False
            st.session_state[K.LAST_RESULT] = None
            st.session_state["prefill_input"] = raw_input
            st.rerun()

def render_workspace(cfg: dict) -> None:
    if st.session_state.get("in_studio", False): _render_studio(cfg)
    else: _render_desk(cfg)
