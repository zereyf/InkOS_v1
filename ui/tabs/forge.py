"""
ui/tabs/forge.py — Persona Forge Tab
======================================
v16.0: Upgraded for InkOS. Advanced Tech-Noir UI, active state anchoring,
       and unified Brand Identity payloads.
Tab 6: Create, browse, and manage AI personas and Visual DNA.
"""

import streamlit as st
from typing import Optional
from state import K
from forge.persona_engine import STARTER_PERSONAS, inject_persona, get_persona_display_name
from forge.persona_store import save_persona, list_personas, delete_persona
from vault.supabase_client import SUPABASE_MISSING
from config import TARGET_GUIDES
from i18n.translations import t


def _render_persona_card(
    persona:   dict,
    is_active: bool,
    user_hash: str,
    is_starter: bool = False,
) -> None:
    """Renders a single persona card with activate/preview/delete actions."""
    name        = persona.get("name", "")
    role        = persona.get("role", "")
    constraints = persona.get("constraints", "")
    style       = persona.get("style", "")
    target      = persona.get("target", "All")
    pid         = persona.get("id", name)

    border_color = "var(--gold)" if is_active else "rgba(201,168,76,0.14)"
    active_label = ' <span style="color:#4CAF9A;font-size:0.7rem;margin-left:8px;">● ACTIVE</span>' if is_active else ""
    indicator    = "🟢" if is_active else "✦"

    with st.expander(f"{indicator} {name}  ·  {target}{active_label}"):

        # Role preview
        st.markdown(f"""
        <div style="
            background:rgba(201,168,76,0.02);
            border:1px solid rgba(201,168,76,0.1);
            border-radius:4px; padding:12px 14px;
            margin-bottom:12px;
        ">
            <div style="font-family:var(--font-m);font-size:0.6rem;
                        color:var(--text-muted);letter-spacing:0.1em;
                        text-transform:uppercase;margin-bottom:6px;">DIRECTIVE / ROLE</div>
            <div style="font-family:var(--font-m);font-size:0.78rem;
                        line-height:1.7;color:var(--text);">{role}</div>
        </div>
        """, unsafe_allow_html=True)

        if constraints:
            st.markdown(f"""
            <div style="font-family:var(--font-m);font-size:0.7rem;
                        color:var(--text-muted);line-height:1.6;
                        border-left:2px solid #E53E3E;
                        padding-left:12px;margin-bottom:8px;">
                <strong style="color:#FC8181;font-size:0.65rem;letter-spacing:0.05em;text-transform:uppercase;">Anti-Patterns & Constraints:</strong><br>
                {constraints}
            </div>
            """, unsafe_allow_html=True)

        if style:
            st.markdown(f"""
            <div style="font-family:var(--font-m);font-size:0.7rem;
                        color:var(--text-muted);line-height:1.6;
                        border-left:2px solid #7C9EBF;
                        padding-left:12px;margin-bottom:14px;">
                <strong style="color:#90CDF4;font-size:0.65rem;letter-spacing:0.05em;text-transform:uppercase;">Tonal Anchor:</strong><br>
                {style}
            </div>
            """, unsafe_allow_html=True)

        # Action buttons
        a1, a2, a3 = st.columns([2, 2, 1])

        with a1:
            btn_label = "Deactivate Persona" if is_active else "Engage Persona"
            if st.button(btn_label, key=f"activate_{pid}", use_container_width=True):
                st.session_state[K.ACTIVE_PERSONA] = None if is_active else persona
                st.rerun()

        with a2:
            preview_target = st.session_state.get("sb_target", "Claude")
            if st.button(t("preview_injection", fallback="Preview Prompt Code"), key=f"preview_{pid}", use_container_width=True):
                st.session_state[f"show_preview_{pid}"] = not st.session_state.get(f"show_preview_{pid}", False)
                st.rerun()

        with a3:
            if not is_starter:
                confirm_key = f"confirm_del_persona_{pid}"
                if st.session_state.get(confirm_key):
                    if st.button(t("confirm_delete", fallback="Confirm"), key=f"confirm_persona_btn_{pid}", use_container_width=True):
                        ok, err = delete_persona(user_hash, pid)
                        if ok:
                            if st.session_state.get(K.ACTIVE_PERSONA, {}).get("id") == pid:
                                st.session_state[K.ACTIVE_PERSONA] = None
                            st.session_state[confirm_key] = False
                            st.rerun()
                        else:
                            st.error(err)
                else:
                    if st.button("Delete", key=f"del_persona_{pid}", use_container_width=True):
                        st.session_state[confirm_key] = True
                        st.rerun()

        if st.session_state.get(f"show_preview_{pid}"):
            preview_target = st.session_state.get("sb_target", "Claude")
            injected = inject_persona(persona, preview_target)
            st.markdown(
                f'<div style="font-family:var(--font-m);font-size:0.6rem;'
                f'color:var(--text-muted);letter-spacing:0.1em;'
                f'text-transform:uppercase;margin-top:14px;margin-bottom:4px;">'
                f'INJECTION PREVIEW FOR: <span style="color:var(--gold);">{preview_target}</span></div>',
                unsafe_allow_html=True,
            )
            st.code(injected, language="text")


def render_forge() -> None:
    """Renders Tab 6 — Persona Forge."""

    st.markdown(
        f'<div class="vc-header"><span class="status-dot" style="background:#7C9EBF;box-shadow:0 0 8px #7C9EBF;"></span>Identity Forge</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-family:var(--font-m);font-size:0.72rem;color:var(--text-muted);'
        'line-height:1.8;margin-bottom:20px;">'
        'Build reusable AI tactical personas and lock your Visual Brand DNA. Active profiles '
        'are injected into the refinement layer automatically.</p>',
        unsafe_allow_html=True,
    )

    user_hash     = st.session_state.get(K.USER_HASH, "")
    active_persona = st.session_state.get(K.ACTIVE_PERSONA)
    active_name    = get_persona_display_name(active_persona)

    # ── CURRENT ACTIVE ─────────────────────────────────────────────────────────
    if active_persona:
        st.markdown(f"""
        <div style="
            background:rgba(76, 175, 154, 0.08);
            border:1px solid rgba(76, 175, 154, 0.3);
            border-radius:3px;padding:12px 16px;
            font-family:var(--font-m);font-size:0.7rem;
            color:#4CAF9A;margin-bottom:20px;
            display:flex;align-items:center;gap:10px;
        ">
            <span class="status-dot green"></span>
            <div>
                <span style="letter-spacing:0.05em;text-transform:uppercase;">System Override Active:</span> 
                <strong style="color:#6EE7B7;font-size:0.8rem;margin-left:4px;">{active_name}</strong>
                <div style="font-size:0.6rem;color:var(--text-muted);margin-top:2px;">
                    This persona is currently dominating all refinement outputs.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── TABS: BROWSE | CREATE | BRAND IDENTITY ─────────────────────────────────
    forge_tab1, forge_tab2, forge_tab3 = st.tabs(["Browse Matrix", "Forge Persona", "Brand Identity 🧬"])

    # ── BROWSE ─────────────────────────────────────────────────────────────────
    with forge_tab1:
        st.markdown(
            f'<div style="font-size:0.65rem;color:var(--text-muted);font-family:var(--font-m);margin-top:12px;margin-bottom:8px;">'
            f'SYSTEM STARTERS</div>',
            unsafe_allow_html=True,
        )
        for name, persona in STARTER_PERSONAS.items():
            if name == "None" or persona is None:
                continue
            _render_persona_card(
                persona    = persona,
                is_active  = (active_name == name),
                user_hash  = user_hash,
                is_starter = True,
            )

        if not SUPABASE_MISSING:
            st.markdown(
                f'<div style="font-size:0.65rem;color:var(--text-muted);font-family:var(--font-m);margin-top:24px;margin-bottom:8px;">'
                f'USER CONSTRUCTS</div>',
                unsafe_allow_html=True,
            )
            user_personas, err = list_personas(user_hash, target_filter="All")

            if err:
                st.error(f"Could not load personas: {err}")
            elif not user_personas:
                st.markdown(
                    '<div style="background:rgba(255,255,255,0.02);border:1px dashed rgba(255,255,255,0.1);padding:20px;text-align:center;border-radius:4px;">'
                    '<p style="font-family:var(--font-m);font-size:0.72rem;color:var(--text-muted);margin:0;">'
                    'No custom constructs detected in the Vault. Forge one in the next tab.</p></div>',
                    unsafe_allow_html=True,
                )
            else:
                for persona in user_personas:
                    _render_persona_card(
                        persona    = persona,
                        is_active  = (active_name == persona.get("name")),
                        user_hash  = user_hash,
                        is_starter = False,
                    )
        else:
            st.markdown(
                '<p style="font-family:var(--font-m);font-size:0.72rem;color:var(--text-muted);margin-top:20px;">'
                f'Supabase integration required to save custom constructs.</p>',
                unsafe_allow_html=True,
            )

    # ── CREATE ─────────────────────────────────────────────────────────────────
    with forge_tab2:
        st.markdown(
            f'<div style="font-size:0.65rem;color:var(--gold);font-family:var(--font-m);margin-top:12px;margin-bottom:12px;">'
            f'✦ INITIALIZE NEW CONSTRUCT</div>',
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns([2, 1])
        with c1:
            p_name = st.text_input("Codename / Designation", placeholder="e.g. Shadow Editor", key="forge_name")
        with c2:
            p_target = st.selectbox(
                "Native Target Alignment",
                ["All"] + list(TARGET_GUIDES.keys()),
                key="forge_target",
                help="'All' makes this a universal persona. Select a specific AI if this persona uses syntax exclusive to that model.",
            )

        p_role = st.text_area("Core Directive (Role)", height=90, placeholder="You are an elite copywriter specializing in...", key="forge_role")
        p_constraints = st.text_area("Anti-Patterns & Constraints", height=70, placeholder="Never use emojis. Never apologize. Always format as...", key="forge_constraints")
        p_style = st.text_area("Tonal Anchor", height=60, placeholder="Speak like a cynical veteran engineer...", key="forge_style")
        p_tags = st.text_input("Taxonomy Tags", placeholder="writing, code, visual...", key="forge_tags")

        if p_role:
            preview_persona = {
                "name": p_name or "Preview Construct",
                "role": p_role,
                "constraints": p_constraints,
                "style": p_style,
                "target": p_target,
            }
            preview_target = st.session_state.get("sb_target", "Claude")
            with st.expander(f"Compile Preview for {preview_target}"):
                st.code(inject_persona(preview_persona, preview_target), language="text")

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        if st.button("Compile & Save Construct", use_container_width=True, key="forge_save"):
            if not p_name.strip():
                st.warning("Construct requires a Designation (Name).")
            elif not p_role.strip():
                st.warning("Construct requires a Core Directive (Role).")
            elif SUPABASE_MISSING:
                new_persona = {
                    "id":          p_name.strip().lower().replace(" ", "_"),
                    "name":        p_name.strip(),
                    "role":        p_role.strip(),
                    "constraints": p_constraints.strip(),
                    "style":       p_style.strip(),
                    "target":      p_target,
                    "tags":        p_tags.strip(),
                }
                st.session_state[K.ACTIVE_PERSONA] = new_persona
                st.success(f"Session memory activated: {p_name} (Cloud save unavailable)")
            else:
                saved, err = save_persona(
                    user_hash   = user_hash,
                    name        = p_name,
                    role        = p_role,
                    constraints = p_constraints,
                    style       = p_style,
                    target      = p_target,
                    tags        = p_tags,
                )
                if err:
                    st.error(f"Save failed: {err}")
                else:
                    st.session_state[K.ACTIVE_PERSONA] = saved
                    st.success(f"Construct Secured: {p_name}")
                    st.rerun()

    # ── BRAND IDENTITY (DYNAMIC ENGINE) ────────────────────────────────────────
    with forge_tab3:
        st.markdown(
            f'<div style="font-size:0.65rem;color:var(--gold);font-family:var(--font-m);margin-top:12px;margin-bottom:4px;">'
            f'✦ VISUAL BRAND DNA MATRIX</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p style="font-family:var(--font-m);font-size:0.7rem;color:var(--text-muted);">'
            'Establish the persistent typography, aesthetics, and motifs that A.I.Z.E.N. will automatically '
            'protect and inject during any visual generation task.</p>',
            unsafe_allow_html=True,
        )
        
        # Load existing config or deploy personalized default baseline
        current_id = st.session_state.get("brand_identity", {
            "name": "AmeerInk",
            "tagline": "حبر وفكرة",
            "muse": "Dark, cinematic, high-contrast cyber-tactical aesthetic with Shikamaru-like posture and intelligence",
            "trigger": "shikamaru",
            "vibe": "Tech-noir, obsidian UI elements, terminal green accents, cybersecurity motifs"
        })
        
        st.markdown('<div style="margin-top:15px;margin-bottom:5px;font-size:0.65rem;color:var(--steel);font-family:var(--font-m);">TYPOGRAPHY LATCH</div>', unsafe_allow_html=True)
        t1, t2 = st.columns(2)
        with t1:
            b_name = st.text_input("Brand Name", value=current_id.get("name"), help="Exact spelling protected during image+text generation.")
        with t2:
            b_tagline = st.text_input("Brand Tagline", value=current_id.get("tagline"), help="Secondary text element injected into banners.")

        st.markdown('<div style="margin-top:10px;margin-bottom:5px;font-size:0.65rem;color:var(--steel);font-family:var(--font-m);">AESTHETIC INJECTION</div>', unsafe_allow_html=True)
        b_trigger = st.text_input("Muse Trigger Word", value=current_id.get("trigger"), help="The specific word in your input that activates this DNA block.")
        b_muse = st.text_input("Muse Rendering Instructions", value=current_id.get("muse"), help="The detailed visual description applied when the trigger is fired.")
        b_vibe = st.text_area("Core Vibe / Environment FX", value=current_id.get("vibe"), height=70, help="Environmental elements universally applied to your generated assets.")
        
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        
        if st.button("💾 Lock Brand Identity DNA", use_container_width=True):
            st.session_state["brand_identity"] = {
                "name": b_name,
                "tagline": b_tagline,
                "muse": b_muse,
                "trigger": b_trigger.lower(),
                "vibe": b_vibe
            }
            st.success("DNA Sequence Locked. Visual routing parameters updated.")
            st.rerun()
