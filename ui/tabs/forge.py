"""
ui/tabs/forge.py — Persona Forge Tab
======================================
v19.0: Zenith Edition — Behavior Locking & Rhetoric Sync.
       - UPDATED: Forge Construct now supports Hikmah Styles and Aesthetics.
       - UPDATED: save_persona call aligned with v6.0 Persistence signature.
       - UPDATED: Preview payload now renders the full composite instruction set.
       - FIXED: Synchronized rehydration of Sidebar settings on 'Engage'.
"""

import streamlit as st
import textwrap
import html
from typing import Optional
from state import K
from config.personas import STARTER_PERSONAS
from forge.persona_engine import inject_persona, get_persona_display_name
from forge.persona_store import save_persona, list_personas, delete_persona
from forge.rhetoric_engine import HIKMAH_PROFILES
from config import TARGET_GUIDES, AESTHETIC_PRESETS
from i18n.translations import t


# ── STREAMLIT CALLBACKS ───────────────────────────────────────────────────────

def toggle_persona_callback(persona_data: dict, is_currently_active: bool):
    """
    Latches identity while synchronizing Behavioral DNA.
    Forces the Sidebar to align its Rhetoric and Aesthetic to the Persona's Specs.
    """
    MASTER_KEY = "sb_persona_global_widget"

    if is_currently_active:
        st.session_state[K.ACTIVE_PERSONA] = None
        if MASTER_KEY in st.session_state: 
            st.session_state[MASTER_KEY] = "None" 
        if "p" in st.query_params: 
            del st.query_params["p"]
        st.toast("🎭 Identity Matrix Reset.")
    else:
        st.session_state[K.ACTIVE_PERSONA] = persona_data
        p_name = persona_data.get("name", "Unknown")
        st.query_params["p"] = p_name
        
        # 🟢 BEHAVIORAL REHYDRATION: Sync Sidebar widgets with Persona specs
        # This ensures the LLM receives the correct rhetoric for the chosen persona.
        if "style" in persona_data:
            st.session_state["sb_hikmah_style"] = persona_data["style"]
        if "aesthetic" in persona_data:
            st.session_state["sb_aesthetic"] = persona_data["aesthetic"]

        # Sidebar UI Label Suffixing
        is_starter = any(p_name == v.get('name') for v in STARTER_PERSONAS.values() if v)
        target_label = f"{p_name} [S]" if is_starter else f"{p_name} [C]"
        
        st.session_state[MASTER_KEY] = target_label
        st.toast(f"🎭 LATCHED: {p_name}")


def toggle_preview_callback(pid: str):
    """Toggles visibility of the XML system prompt payload."""
    key = f"show_preview_{pid}"
    st.session_state[key] = not st.session_state.get(key, False)


# ── UI COMPONENTS ─────────────────────────────────────────────────────────────

def _render_persona_card(persona: dict, is_active: bool, user_hash: str, is_starter: bool = False) -> None:
    name = persona.get("name", "Unknown")
    target = persona.get("target", "All")
    pid = persona.get("id", name)
    
    # Extract Behavioral DNA (with legacy fallbacks)
    h_style = persona.get("style", "None")
    a_style = persona.get("aesthetic", "Default")

    active_style = "border: 1px solid var(--gold); background:rgba(201,168,76,0.05);" if is_active else "border: 1px solid rgba(255,255,255,0.05);"
    indicator = "🟢" if is_active else "✦"

    with st.expander(f"{indicator} {name.upper()}  ·  {target}"):
        st.markdown(f"""
            <div style="background:rgba(255,255,255,0.02); padding:15px; border-radius:2px; {active_style}">
                <div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:2px; margin-bottom:8px;">[ CORE_DIRECTIVE ]</div>
                <div style="font-family:var(--font-m); font-size:0.75rem; color:var(--text); line-height:1.6; margin-bottom:12px;">{persona.get('role','')}</div>
                <div style="display:flex; gap:8px;">
                    <span style="background:rgba(201,168,76,0.1); color:var(--gold); padding:2px 6px; border-radius:2px; font-size:0.5rem; font-family:var(--font-m);">{h_style.upper()}</span>
                    <span style="background:rgba(255,255,255,0.05); color:var(--text-dim); padding:2px 6px; border-radius:2px; font-size:0.5rem; font-family:var(--font-m);">{a_style.upper()}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.button("Deactivate" if is_active else "Engage", key=f"act_{pid}", on_click=toggle_persona_callback, args=(persona, is_active), use_container_width=True)
        with c2:
            st.button(t("preview_injection", fallback="Preview Payload"), key=f"pre_{pid}", on_click=toggle_preview_callback, args=(pid,), use_container_width=True)
        with c3:
            if not is_starter:
                if st.session_state.get(f"confirm_del_{pid}"):
                    if st.button("CONFIRM", key=f"real_del_{pid}", type="primary", use_container_width=True):
                        ok, _ = delete_persona(user_hash, pid)
                        if ok: st.rerun()
                elif st.button("🗑️", key=f"del_{pid}", use_container_width=True):
                    st.session_state[f"confirm_del_{pid}"] = True
                    st.rerun()

        if st.session_state.get(f"show_preview_{pid}"):
            st.markdown('<div style="font-family:var(--font-m); font-size:0.5rem; color:var(--steel); letter-spacing:2px; margin-top:15px; margin-bottom:5px;">[ COMPOSITE_NEURAL_PAYLOAD ]</div>', unsafe_allow_html=True)
            # 🟢 UPDATED: Preview now reflects the persona's specifically locked rhetoric style
            st.code(inject_persona(persona, "Claude", hikmah_style=h_style), language="xml")


# ── MAIN RENDERER ─────────────────────────────────────────────────────────────

def render_forge() -> None:
    st.markdown('<div class="vc-header"><span class="status-dot"></span>IDENTITY_FORGE</div>', unsafe_allow_html=True)
    
    user_hash = st.session_state.get(K.USER_HASH, "")
    active_persona = st.session_state.get(K.ACTIVE_PERSONA)
    active_short_name = get_persona_display_name(active_persona)

    tab_browse, tab_forge, tab_dna = st.tabs(["NEURAL_MATRIX", "FORGE_CONSTRUCT", "VISUAL_DNA"])

    with tab_browse:
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        # Starter constructs (Immutable)
        for label, p in STARTER_PERSONAS.items():
            if label != "None" and p: 
                _render_persona_card(p, (active_short_name == p.get("name")), user_hash, is_starter=True)
        
        st.markdown("---")
        # Custom constructs (Database driven)
        user_personas, _ = list_personas(user_hash, target_filter="All")
        for p in user_personas: 
            _render_persona_card(p, (active_short_name == p.get("name")), user_hash)

    with tab_forge:
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        
        f_name = st.text_input("Designation", placeholder="e.g. Shadow Auditor", key="f_p_name")
        f_target = st.selectbox("Alignment", ["All"] + list(TARGET_GUIDES.keys()), key="f_p_target")
        
        c1, c2 = st.columns(2)
        with c1:
            f_hikmah = st.selectbox("Hikmah Style (Rhetoric)", options=list(HIKMAH_PROFILES.keys()), key="f_p_hikmah")
        with c2:
            f_aest = st.selectbox("Aesthetic Preset (Visual)", options=list(AESTHETIC_PRESETS.keys()), key="f_p_aest")
            
        f_role = st.text_area("Core Directive", height=120, key="f_p_role", help="Define the expert's behavior and knowledge boundaries.")
        
        if st.button("COMPILE & SECURE CONSTRUCT", use_container_width=True):
            if f_name and f_role:
                # 🟢 v6.0 ALIGNMENT: user, name, role, constraints, hikmah_style, aesthetic, target, tags
                saved, err = save_persona(user_hash, f_name, f_role, "", f_hikmah, f_aest, f_target, "")
                if not err:
                    st.success(f"Construct Secured: {f_name}")
                    st.rerun()
                else: 
                    st.error(f"Persistence Fault: {err}")

    with tab_dna:
        st.markdown('<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:2px; margin-bottom:15px;">[ ATHAR_DNA_SEQUENCING ]</div>', unsafe_allow_html=True)
        
        d_ink = st.text_area("Visual DNA (/ink)", value=st.session_state.get(K.INK_DNA, ""), height=80, placeholder="Define the visual aesthetic soul...")
        d_intel = st.text_area("Strategic DNA (/intel)", value=st.session_state.get(K.INTEL_DNA, ""), height=80, placeholder="Define the strategic operational parameters...")
        d_hikmah = st.text_area("Philosophical DNA (/hikmah)", value=st.session_state.get(K.HIKMAH_DNA, ""), height=80, placeholder="Define the ethical and linguistic boundaries...")

        if st.button("💾 LOCK DNA SEQUENCES", use_container_width=True):
            st.session_state[K.INK_DNA] = d_ink
            st.session_state[K.INTEL_DNA] = d_intel
            st.session_state[K.HIKMAH_DNA] = d_hikmah
            
            from vault.supabase_client import supabase
            try:
                supabase.table("users").update({
                    "ink_dna": d_ink,
                    "intel_dna": d_intel,
                    "hikmah_dna": d_hikmah
                }).eq("id", user_hash).execute()
                st.toast("DNA Locked.")
            except Exception as e:
                st.error(f"Persistence Fault: {e}")
