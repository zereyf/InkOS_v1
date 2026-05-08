"""
ui/tabs/forge.py — Persona Forge Tab
======================================
v17.0: Hardened with Streamlit Callbacks to prevent state-race conditions.
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

# ── STREAMLIT CALLBACKS ───────────────────────────────────────────────────────
# Executes state changes before the UI locks for re-rendering

def toggle_persona_callback(persona_data: dict, is_currently_active: bool):
    if is_currently_active:
        st.session_state[K.ACTIVE_PERSONA] = None
        st.toast("🎭 System Override Deactivated.")
    else:
        st.session_state[K.ACTIVE_PERSONA] = persona_data
        st.toast(f"🎭 LATCHED: {persona_data.get('name', 'Unknown')}")

def toggle_preview_callback(pid: str):
    current = st.session_state.get(f"show_preview_{pid}", False)
    st.session_state[f"show_preview_{pid}"] = not current

# ──────────────────────────────────────────────────────────────────────────────

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

    active_label = " [● ACTIVE]" if is_active else ""
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
            # 🐛 FIX: Using on_click callback to prevent state racing 🐛
            st.button(
                btn_label, 
                key=f"activate_{pid}", 
                on_click=toggle_persona_callback,
                args=(persona, is_active),
                use_container_width=True
            )

        with a2:
            st.button(
                t("preview_injection", fallback="Preview Prompt Code"), 
                key=f"preview_{pid}", 
                on_click=toggle_preview_callback,
                args=(pid,),
                use_container_width=True
            )

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

        def _save_construct_callback():
            if not p_name.strip() or not p_role.strip():
                return
            new_persona = {
                "id":          p_name.strip().lower().replace(" ", "_"),
                "name":        p_name.strip(),
                "role":        p_role.strip(),
                "constraints": p_constraints.strip(),
                "style":       p_style.strip(),
                "target":      p_target,
                "tags":        p_tags.strip(),
            }
            if SUPABASE_MISSING:
                st.session_state[K.ACTIVE_PERSONA] = new_persona
            else:
                saved, err = save_persona(user_hash, p_name, p_role, p_constraints, p_style, p_target, p_tags)
                if not err:
                    st.session_state[K.ACTIVE_PERSONA] = saved

        if st.button("Compile & Save Construct", use_container_width=True, key="forge_save", on_click=_save_construct_callback):
            if not p_name.strip():
                st.warning("Construct requires a Designation (Name).")
            elif not p_role.strip():
                st.warning("Construct requires a Core Directive (Role).")
            elif SUPABASE_MISSING:
                st.success(f"Session memory activated: {p_name} (Cloud save unavailable)")
            else:
                st.success(f"Construct Secured: {p_name}")

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
        
        def _save_brand_callback():
            st.session_state["brand_identity"] = {
                "name": b_name, "tagline": b_tagline, "muse": b_muse,
                "trigger": b_trigger.lower(), "vibe": b_vibe
            }
            
        if st.button("💾 Lock Brand Identity DNA", use_container_width=True, on_click=_save_brand_callback):
            st.success("DNA Sequence Locked. Visual routing parameters updated.")
"""
ui/tabs/forge.py — Persona Forge Tab
======================================
v18.0: Hardened Persistence Build.
       Synchronized with Vault v18.2 (Rehydration) and Workspace v30.2.
       Integrated DNA slot mapping for users table.
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
    if is_currently_active:
        st.session_state[K.ACTIVE_PERSONA] = None
        # Remove persona from URL on deactivation
        if "p" in st.query_params:
            del st.query_params["p"]
        st.toast("🎭 Identity Matrix Reset.")
    else:
        st.session_state[K.ACTIVE_PERSONA] = persona_data
        # 🟢 PERSISTENCE: Latch persona name into URL
        st.query_params["p"] = persona_data.get("name", "Unknown")
        st.toast(f"🎭 LATCHED: {persona_data.get('name', 'Unknown')}")

# ── UI COMPONENTS ─────────────────────────────────────────────────────────────

def _render_persona_card(persona: dict, is_active: bool, user_hash: str, is_starter: bool = False) -> None:
    name, role = persona.get("name", ""), persona.get("role", "")
    constraints, style = persona.get("constraints", ""), persona.get("style", "")
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

        # Action Logic
        c1, c2, c3 = st.columns([2, 2, 1])
        with c1:
            st.button("Deactivate" if is_active else "Engage", key=f"act_{pid}", on_click=toggle_persona_callback, args=(persona, is_active), use_container_width=True)
        with c2:
            st.button("Preview Injection", key=f"pre_{pid}", on_click=toggle_preview_callback, args=(pid,), use_container_width=True)
        with c3:
            if not is_starter:
                if st.button("🗑️", key=f"del_{pid}", use_container_width=True):
                    ok, err = delete_persona(user_hash, pid)
                    if ok: st.rerun()
                    else: st.error(err)

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
            if name != "None": _render_persona_card(p, active_name == name, user_hash, is_starter=True)
        
        st.markdown("---")
        user_personas, _ = list_personas(user_hash, target_filter="All")
        if user_personas:
            for p in user_personas: _render_persona_card(p, active_name == p.get("name"), user_hash)
        else:
            st.caption("No user constructs detected in uplink.")

    # ── TAB 2: CREATE
    with tab_forge:
        st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
        f_name = st.text_input("Designation", placeholder="e.g. Shadow Auditor")
        f_target = st.selectbox("Alignment", ["All"] + list(TARGET_GUIDES.keys()))
        f_role = st.text_area("Directive", height=100)
        
        if st.button("Compile & Secure Construct", use_container_width=True):
            if f_name and f_role:
                saved, err = save_persona(user_hash, f_name, f_role, "", "", f_target, "")
                if not err:
                    st.success(f"Construct Secured: {f_name}")
                    st.rerun()

    # ── TAB 3: BRAND DNA (Synchronized with SQL slots)
    with tab_dna:
        st.markdown(textwrap.dedent("""
            <div style="margin-top:15px; margin-bottom:20px;">
                <div style="font-family:var(--font-m); font-size:0.55rem; color:var(--gold); letter-spacing:2px;">[ ATHAR PROTOCOL ]</div>
                <div style="font-family:var(--font-m); font-size:0.7rem; color:var(--text-muted);">
                    These DNA sequences are injected into the Workspace via <strong>/triggers</strong>.
                </div>
            </div>
        """), unsafe_allow_html=True)

        # 🟢 PERSISTENCE MAPPING: Link directly to K-State slots
        d_ink = st.text_area("Visual DNA (/ink)", value=st.session_state.get(K.INK_DNA, ""), height=80, help="Brand Muse and Aesthetic instructions.")
        d_intel = st.text_area("Strategic DNA (/intel)", value=st.session_state.get(K.INTEL_DNA, ""), height=80, help="Forensic logic and technical constraints.")
        d_hikmah = st.text_area("Philosophical DNA (/hikmah)", value=st.session_state.get(K.HIKMAH_DNA, ""), height=80, help="Islamic framework and ethical boundaries.")

        if st.button("💾 Lock DNA Sequences", use_container_width=True):
            # 1. Update Session State
            st.session_state[K.INK_DNA] = d_ink
            st.session_state[K.INTEL_DNA] = d_intel
            st.session_state[K.HIKMAH_DNA] = d_hikmah
            
            # 2. Persist to Database (Zero-Cost Persistence)
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
