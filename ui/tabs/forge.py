"""
ui/tabs/forge.py — Persona Forge Tab
======================================
v18.1: Hardened Persistence & Callback Sync.
       - Restored toggle_preview_callback (Fixes NameError).
       - Synchronized with Workspace v30.8 HUD logic.
       - URL-Synced Identity Engagement.
"""

import streamlit as st
import textwrap
from typing import Optional
from state import K
from forge.persona_engine import STARTER_PERSONAS, inject_persona, get_persona_display_name
from forge.persona_store import save_persona, list_personas, delete_persona
from vault.supabase_client import SUPABASE_MISSING
from config import TARGET_GUIDES
from i18n.translations import t

# ── STREAMLIT CALLBACKS ───────────────────────────────────────────────────────

def toggle_persona_callback(persona_data: dict, is_currently_active: bool):
    """Latches or unlatches a persona while syncing with URL parameters."""
    if is_currently_active:
        st.session_state[K.ACTIVE_PERSONA] = None
        if "p" in st.query_params:
            del st.query_params["p"]
        st.toast("🎭 Identity Matrix Reset.")
    else:
        st.session_state[K.ACTIVE_PERSONA] = persona_data
        # Latch name into URL parameter for refresh survival
        st.query_params["p"] = persona_data.get("name", "Unknown")
        st.toast(f"🎭 LATCHED: {persona_data.get('name', 'Unknown')}")

def toggle_preview_callback(pid: str):
    """Toggles the prompt code injection preview window."""
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

        # Action logic
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
                t("preview_injection", fallback="Preview Injection"), 
                key=f"pre_{pid}", 
                on_click=toggle_preview_callback, 
                args=(pid,), 
                use_container_width=True
            )
        with c3:
            if not is_starter:
                # Two-stage Delete Confirmation Gate
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
            st.code(inject_persona(persona, "Claude"), language="text")

# ── MAIN RENDERER ─────────────────────────────────────────────────────────────

def render_forge() -> None:
    st.markdown('<div class="vc-header"><span class="status-dot"></span>Identity Forge</div>', unsafe_allow_html=True)
    
    user_hash = st.session_state.get(K.USER_HASH, "")
    active_persona = st.session_state.get(K.ACTIVE_PERSONA)
    active_name = get_persona_display_name(active_persona)

    tab_browse, tab_forge, tab_dna = st.tabs(["Neural Matrix", "Forge Construct", "Visual DNA 🧬"])

    # ── TAB 1: BROWSE
    with tab_browse:
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        for name, p in STARTER_PERSONAS.items():
            if name != "None": 
                _render_persona_card(p, active_name == name, user_hash, is_starter=True)
        
        st.markdown("---")
        user_personas, _ = list_personas(user_hash, target_filter="All")
        if user_personas:
            for p in user_personas: 
                _render_persona_card(p, active_name == p.get("name"), user_hash)
        else:
            st.caption("No custom constructs detected in uplink.")

    # ── TAB 2: CREATE
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

    # ── TAB 3: BRAND DNA
    with tab_dna:
        st.markdown(textwrap.dedent("""
            <div style="margin-top:15px; margin-bottom:20px;">
                <div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:2px;">[ ATHAR PROTOCOL ]</div>
                <div style="font-family:var(--font-m); font-size:0.7rem; color:var(--text-muted);">
                    These DNA sequences are injected into the Workspace via <strong>/triggers</strong>.
                </div>
            </div>
        """), unsafe_allow_html=True)

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
                st.toast("DNA Locked in Permanent Memory.")
            except Exception as e:
                st.error(f"Persistence Fault: {e}")
