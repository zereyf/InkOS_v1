"""
ui/tabs/forge.py — Persona Forge Tab
======================================
v18.5: Structural Sync Build.
       - FIXED: Moved STARTER_PERSONAS import to config.personas.
       - Synchronized with Sidebar v13.4 Master Latch.
       - Integrated Type-Agnostic Engine v9.3.
"""

import streamlit as st
import textwrap
from typing import Optional
from state import K
# 🟢 FIXED: Import the data from the Vault (config), not the Engine (forge)
from config.personas import STARTER_PERSONAS
from forge.persona_engine import inject_persona, get_persona_display_name
from forge.persona_store import save_persona, list_personas, delete_persona
from vault.supabase_client import SUPABASE_MISSING
from config import TARGET_GUIDES
from i18n.translations import t


# ── STREAMLIT CALLBACKS ───────────────────────────────────────────────────────

def toggle_persona_callback(persona_data: dict, is_currently_active: bool):
    """Latches identity while forcing the Master Sidebar widget to sync."""
    
    # 🟢 MASTER KEY SYNC: Must match sidebar v13.4 exactly
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
        p_short_name = persona_data.get("name", "Unknown")
        
        # 1. Update URL (The absolute Source of Truth for refreshes)
        st.query_params["p"] = p_short_name
        
        # 2. Reconstruct the Sidebar's UI Label (Suffix-Aware)
        # We need the exact string the Sidebar selectbox is using as a key.
        is_starter = any(p_short_name == v.get('name') for k, v in STARTER_PERSONAS.items() if v)
        
        if is_starter:
            # Find the original legacy key (e.g., "Makise Kurisu (Amadeus)")
            legacy_key = next((k for k, v in STARTER_PERSONAS.items() if v and v.get('name') == p_short_name), p_short_name)
            target_label = f"{legacy_key} [S]"
        else:
            target_label = f"{p_short_name} [C]"

        # 3. Force the Sidebar widget to move immediately
        st.session_state[MASTER_KEY] = target_label
        st.toast(f"🎭 LATCHED: {p_short_name}")


def toggle_preview_callback(pid: str):
    """Toggles the XML prompt payload window."""
    key = f"show_preview_{pid}"
    st.session_state[key] = not st.session_state.get(key, False)

# ── UI COMPONENTS ─────────────────────────────────────────────────────────────

def _render_persona_card(persona: dict, is_active: bool, user_hash: str, is_starter: bool = False) -> None:
    name, role = persona.get("name", ""), persona.get("role", "")
    target, pid = persona.get("target", "All"), persona.get("id", name)

    active_style = "border-color:var(--gold); background:rgba(201,168,76,0.05);" if is_active else ""
    indicator = "🟢" if is_active else "✦"

    with st.expander(f"{indicator} {name}  ·  {target}"):
        st.markdown(textwrap.dedent(f"""
            <div style="background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.05); padding:15px; border-radius:3px; {active_style}">
                <div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:2px; text-transform:uppercase; margin-bottom:8px;">[ CORE DIRECTIVE ]</div>
                <div style="font-family:var(--font-m); font-size:0.8rem; line-height:1.6; color:var(--text);">{role}</div>
            </div>
        """), unsafe_allow_html=True)

        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.button(
                "Deactivate" if is_active else "Engage", 
                key=f"act_{pid}", 
                on_click=toggle_persona_callback, 
                args=(persona, is_active), 
                use_container_width=True
            )
        with c2:
            st.button(
                t("preview_injection", fallback="Preview XML Payload"), 
                key=f"pre_{pid}", 
                on_click=toggle_preview_callback, 
                args=(pid,), 
                use_container_width=True
            )
        with c3:
            if not is_starter:
                confirm_key = f"confirm_del_{pid}"
                if st.session_state.get(confirm_key):
                    if st.button("CONFIRM", key=f"real_del_{pid}", type="primary", use_container_width=True):
                        ok, err = delete_persona(user_hash, pid)
                        if ok:
                            st.session_state[confirm_key] = False
                            st.rerun()
                        else:
                            st.error(err)
                else:
                    if st.button("🗑️", key=f"del_{pid}", use_container_width=True):
                        st.session_state[confirm_key] = True
                        st.rerun()

        if st.session_state.get(f"show_preview_{pid}"):
            st.markdown('<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--steel); letter-spacing:1px; margin-top:10px; margin-bottom:4px; text-transform:uppercase;">[ XML NEURAL PAYLOAD ]</div>', unsafe_allow_html=True)
            st.code(inject_persona(persona, "Claude"), language="xml")

# ── MAIN RENDERER ─────────────────────────────────────────────────────────────

def render_forge() -> None:
    st.markdown('<div class="vc-header"><span class="status-dot"></span>Identity Forge</div>', unsafe_allow_html=True)
    
    user_hash = st.session_state.get(K.USER_HASH, "")
    active_persona = st.session_state.get(K.ACTIVE_PERSONA)
    active_short_name = get_persona_display_name(active_persona)

    tab_browse, tab_forge, tab_dna = st.tabs(["Neural Matrix", "Forge Construct", "Visual DNA 🧬"])

    with tab_browse:
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        # 🟢 Match against STARTER_PERSONAS from config
        for label, p in STARTER_PERSONAS.items():
            if label != "None" and p: 
                is_active = (active_short_name == p.get("name"))
                _render_persona_card(p, is_active, user_hash, is_starter=True)
        
        st.markdown("---")
        user_personas, _ = list_personas(user_hash, target_filter="All")
        if user_personas:
            for p in user_personas: 
                is_active = (active_short_name == p.get("name"))
                _render_persona_card(p, is_active, user_hash)
        else:
            st.caption("No custom constructs detected.")

    with tab_forge:
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        f_name = st.text_input("Designation", placeholder="e.g. Shadow Auditor", key="f_p_name")
        f_target = st.selectbox("Alignment", ["All"] + list(TARGET_GUIDES.keys()), key="f_p_target")
        f_role = st.text_area("Directive", height=100, key="f_p_role")
        
        if st.button("Compile & Secure Construct", use_container_width=True):
            if f_name and f_role:
                saved, err = save_persona(user_hash, f_name, f_role, "", "", f_target, "")
                if not err:
                    st.success(f"Construct Secured: {f_name}")
                    st.rerun()

    with tab_dna:
        st.markdown('<div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:2px;">[ ATHAR PROTOCOL ]</div>', unsafe_allow_html=True)
        d_ink = st.text_area("Visual DNA (/ink)", value=st.session_state.get(K.INK_DNA, ""), height=80)
        d_intel = st.text_area("Strategic DNA (/intel)", value=st.session_state.get(K.INTEL_DNA, ""), height=80)
        d_hikmah = st.text_area("Philosophical DNA (/hikmah)", value=st.session_state.get(K.HIKMAH_DNA, ""), height=80)

        if st.button("💾 Lock DNA Sequences", use_container_width=True):
            st.session_state[K.INK_DNA] = d_ink
            st.session_state[K.INTEL_DNA] = d_intel
            st.session_state[K.HIKMAH_DNA] = d_hikmah
            
            from vault.supabase_client import sb
            try:
                sb.table("users").update({
                    "ink_dna": d_ink,
                    "intel_dna": d_intel,
                    "hikmah_dna": d_hikmah
                }).eq("id", user_hash).execute()
                st.toast("DNA Locked.")
            except Exception as e:
                st.error(f"Persistence Fault: {e}")
