"""
ui/tabs/forge.py — Persona Forge Tab
======================================
Tab 6: Create, browse, and manage AI personas.

Features:
  - Four built-in starter personas available immediately
  - Create custom personas with role, constraints, style, target
  - Save to Supabase — persists across sessions
  - Activate directly from this tab (sets K.ACTIVE_PERSONA)
  - Delete with confirmation
  - Preview shows exactly how the persona injects per target dialect
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
    active_label = ' <span style="color:var(--gold);font-size:0.6rem;">● ACTIVE</span>' if is_active else ""

    with st.expander(f"{name}  ·  {target}{active_label}"):

        # Role preview
        st.markdown(f"""
        <div class="vc-card" style="margin-bottom:10px;">
            <div style="font-family:var(--font-m);font-size:0.6rem;
                        color:var(--text-muted);letter-spacing:0.1em;
                        text-transform:uppercase;margin-bottom:6px;">Role</div>
            <div style="font-family:var(--font-m);font-size:0.78rem;
                        line-height:1.7;color:var(--text);">{role}</div>
        </div>
        """, unsafe_allow_html=True)

        if constraints:
            st.markdown(f"""
            <div style="font-family:var(--font-m);font-size:0.7rem;
                        color:var(--text-muted);line-height:1.6;
                        border-left:2px solid var(--gold-border);
                        padding-left:10px;margin-bottom:8px;">
                <strong style="color:var(--steel);">Constraints:</strong> {constraints}
            </div>
            """, unsafe_allow_html=True)

        if style:
            st.markdown(f"""
            <div style="font-family:var(--font-m);font-size:0.7rem;
                        color:var(--text-muted);line-height:1.6;
                        border-left:2px solid rgba(124,158,191,0.4);
                        padding-left:10px;margin-bottom:10px;">
                <strong style="color:var(--steel);">Style:</strong> {style}
            </div>
            """, unsafe_allow_html=True)

        # Action buttons
        a1, a2, a3 = st.columns([2, 2, 1])

        with a1:
            btn_label = t("active_btn") if is_active else t("activate_btn")
            if st.button(btn_label, key=f"activate_{pid}", use_container_width=True):
                st.session_state[K.ACTIVE_PERSONA] = None if is_active else persona
                st.rerun()

        with a2:
            # Injection preview — shows exactly what gets added to the prompt
            preview_target = st.session_state.get("sb_target", "Claude")
            if st.button(t("preview_injection"), key=f"preview_{pid}", use_container_width=True):
                st.session_state[f"show_preview_{pid}"] = not st.session_state.get(f"show_preview_{pid}", False)
                st.rerun()

        with a3:
            if not is_starter:
                confirm_key = f"confirm_del_persona_{pid}"
                if st.session_state.get(confirm_key):
                    if st.button(t("confirm_delete"), key=f"confirm_persona_btn_{pid}", use_container_width=True):
                        ok, err = delete_persona(user_hash, pid)
                        if ok:
                            if st.session_state.get(K.ACTIVE_PERSONA, {}).get("id") == pid:
                                st.session_state[K.ACTIVE_PERSONA] = None
                            st.session_state[confirm_key] = False
                            st.rerun()
                        else:
                            st.error(err)
                else:
                    if st.button(t("delete_btn"), key=f"del_persona_{pid}", use_container_width=True):
                        st.session_state[confirm_key] = True
                        st.rerun()

        # Injection preview panel
        if st.session_state.get(f"show_preview_{pid}"):
            preview_target = st.session_state.get("sb_target", "Claude")
            injected = inject_persona(persona, preview_target)
            st.markdown(
                f'<div style="font-family:var(--font-m);font-size:0.6rem;'
                f'color:var(--text-muted);letter-spacing:0.1em;'
                f'text-transform:uppercase;margin-top:10px;">'
                f'Injection preview for {preview_target}</div>',
                unsafe_allow_html=True,
            )
            st.code(injected, language="text")


def render_forge() -> None:
    """Renders Tab 6 — Persona Forge."""

    st.markdown(
        f'<div class="vc-header"><span class="status-dot"></span>{t("forge_header")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-family:var(--font-m);font-size:0.72rem;color:var(--text-muted);'
        'line-height:1.8;margin-bottom:20px;">'
        'Build reusable AI personas. Activate one from the sidebar and it injects '
        'into every refinement automatically.</p>',
        unsafe_allow_html=True,
    )

    user_hash     = st.session_state.get(K.USER_HASH, "")
    active_persona = st.session_state.get(K.ACTIVE_PERSONA)
    active_name    = get_persona_display_name(active_persona)

    # ── CURRENT ACTIVE ─────────────────────────────────────────────────────────
    if active_persona:
        st.markdown(f"""
        <div style="
            background:rgba(201,168,76,0.07);
            border:1px solid var(--gold-border);
            border-radius:3px;padding:10px 16px;
            font-family:var(--font-m);font-size:0.7rem;
            color:var(--gold);margin-bottom:16px;
        ">
            <span class="status-dot"></span>
            Active: <strong>{active_name}</strong>
            &nbsp;—&nbsp;
            <span style="color:var(--text-muted);">injecting into all refinements</span>
        </div>
        """, unsafe_allow_html=True)

    # ── TABS: BROWSE | CREATE ──────────────────────────────────────────────────
    forge_tab1, forge_tab2 = st.tabs([t("browse_personas"), t("create_new")])

    # ── BROWSE ─────────────────────────────────────────────────────────────────
    with forge_tab1:

        # Starter personas
        st.markdown(
            f'<div class="vc-header" style="font-size:0.62rem;margin-top:8px;">{t("builtin_starters")}</div>',
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

        # User-saved personas
        if not SUPABASE_MISSING:
            st.markdown(
                f'<div class="vc-header" style="font-size:0.62rem;margin-top:16px;">{t("your_personas")}</div>',
                unsafe_allow_html=True,
            )
            user_personas, err = list_personas(user_hash, target_filter="All")

            if err:
                st.error(f"Could not load personas: {err}")
            elif not user_personas:
                st.markdown(
                    '<p style="font-family:var(--font-m);font-size:0.72rem;'
                    'color:var(--text-muted);">No saved personas yet. Create one below.</p>',
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
                '<p style="font-family:var(--font-m);font-size:0.72rem;color:var(--text-muted);">'
                f'{t("supabase_hint")}</p>',
                unsafe_allow_html=True,
            )

    # ── CREATE ─────────────────────────────────────────────────────────────────
    with forge_tab2:
        st.markdown(
            f'<div class="vc-header" style="font-size:0.62rem;margin-top:8px;">{t("create_new")}</div>',
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns([2, 1])
        with c1:
            p_name = st.text_input(
                "Persona Name",
                placeholder="e.g. Islamic Finance Consultant",
                key="forge_name",
            )
        with c2:
            p_target = st.selectbox(
                "Optimised For",
                ["All"] + list(TARGET_GUIDES.keys()),
                key="forge_target",
                help="'All' works across every AI. Pick a specific AI for dialect-aware injection.",
            )

        p_role = st.text_area(
            "Role Definition",
            height=90,
            placeholder="Describe who this persona is and their expertise...",
            key="forge_role",
        )
        p_constraints = st.text_area(
            "Constraints",
            height=70,
            placeholder="What must this persona never do? What must it always consider?",
            key="forge_constraints",
        )
        p_style = st.text_area(
            "Communication Style",
            height=60,
            placeholder="How should this persona write and speak?",
            key="forge_style",
        )
        p_tags = st.text_input(
            "Tags",
            placeholder="finance, arabic, technical...",
            key="forge_tags",
        )

        # Live injection preview
        if p_role:
            preview_persona = {
                "name": p_name or "Preview",
                "role": p_role,
                "constraints": p_constraints,
                "style": p_style,
                "target": p_target,
            }
            preview_target = st.session_state.get("sb_target", "Claude")
            with st.expander(f"Preview injection for {preview_target}"):
                st.code(inject_persona(preview_persona, preview_target), language="text")

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        if st.button(t("save_activate"), use_container_width=True, key="forge_save"):
            if not p_name.strip():
                st.warning(t("persona_name_warn"))
            elif not p_role.strip():
                st.warning(t("persona_role_warn"))
            elif SUPABASE_MISSING:
                # Still activate in-session even without Supabase
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
                st.success(t('persona_session_ok', name=p_name))
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
                    st.error(t('persona_save_err', error=err))
                else:
                    st.session_state[K.ACTIVE_PERSONA] = saved
                    st.success(t('persona_saved_ok', name=p_name))
                    st.rerun()
