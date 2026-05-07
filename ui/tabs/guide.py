"""
ui/tabs/guide.py — InkOS Documentation & Intelligence Briefing
===============================================================
v22.0: The Trifecta Blueprint.
       Documenting the new /INK, /INTEL, and /HIKMAH Macro Injectors.
"""

import streamlit as st
from i18n.translations import t


def _section(title: str, dot_color: str = "") -> None:
    dot = f'<span class="status-dot{" " + dot_color if dot_color else ""}"></span>' 
    st.markdown(
        f'<div class="vc-header">{dot}{title}</div>',
        unsafe_allow_html=True,
    )


def _card(content: str, accent: str = "var(--gold-border)") -> None:
    st.markdown(f"""
    <div class="vc-card" style="border-color:{accent};margin-bottom:14px;">
        <div style="font-family:var(--font-m);font-size:0.78rem;
                    line-height:1.85;color:var(--text);">
            {content}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _step(number: str, title: str, body: str) -> None:
    st.markdown(f"""
    <div style="display:flex;gap:16px;margin-bottom:16px;align-items:flex-start;">
        <div style="
            font-family:var(--font-d);font-size:1.4rem;color:var(--gold);
            min-width:36px;line-height:1;padding-top:2px;
        ">{number}</div>
        <div>
            <div style="font-family:var(--font-m);font-size:0.75rem;
                        font-weight:600;color:var(--text);letter-spacing:0.06em;
                        text-transform:uppercase;margin-bottom:4px;">{title}</div>
            <div style="font-family:var(--font-m);font-size:0.75rem;
                        color:var(--text-muted);line-height:1.75;">{body}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _feature_card(
    icon:     str,
    name:     str,
    tab:      str,
    what:     str,
    how:      str,
    tip:      str,
    color:    str = "var(--gold)",
) -> None:
    st.markdown(f"""
    <div class="vc-card" style="margin-bottom:14px;">
        <div style="display:flex;justify-content:space-between;
                    align-items:center;margin-bottom:10px;">
            <div style="font-family:var(--font-d);font-size:1rem;color:{color};">
                {icon} {name}
            </div>
            <span style="font-family:var(--font-m);font-size:0.6rem;
                         color:var(--text-muted);letter-spacing:0.1em;
                         background:rgba(255,255,255,0.05);padding:2px 10px;
                         border-radius:2px;text-transform:uppercase;">
                Tab: {tab}
            </span>
        </div>
        <div style="font-family:var(--font-m);font-size:0.73rem;
                    color:var(--text-muted);line-height:1.75;margin-bottom:8px;">
            <strong style="color:var(--text);">Function:</strong> {what}
        </div>
        <div style="font-family:var(--font-m);font-size:0.73rem;
                    color:var(--text-muted);line-height:1.75;margin-bottom:8px;">
            <strong style="color:var(--text);">Operation:</strong> {how}
        </div>
        <div style="font-family:var(--font-m);font-size:0.68rem;
                    color:var(--gold);border-left:2px solid var(--gold-border);
                    padding-left:10px;line-height:1.6;font-style:italic;">
            💡 {tip}
        </div>
    </div>
    """, unsafe_allow_html=True)


def _arabic_pattern_row(arabic: str, paradigm: str, example: str, color: str) -> None:
    st.markdown(f"""
    <div style="display:flex;gap:12px;align-items:flex-start;
                margin-bottom:10px;padding:12px 14px;
                background:rgba(255,255,255,0.02);border-radius:3px;
                border-left:2px solid {color};">
        <div style="font-family:var(--font-a);font-size:1.25rem;
                    color:{color};direction:rtl;min-width:120px;
                    text-align:right;">{arabic}</div>
        <div>
            <div style="font-family:var(--font-m);font-size:0.68rem;
                        color:{color};letter-spacing:0.08em;
                        text-transform:uppercase;margin-bottom:3px;">
                → {paradigm}
            </div>
            <div style="font-family:var(--font-m);font-size:0.68rem;
                        color:var(--text-muted);line-height:1.6;">
                {example}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_guide() -> None:
    """Renders Tab 7 — InkOS Guide with Advanced Operations."""

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div style="text-align:center;padding:32px 0 24px 0;">
        <div style="font-family:var(--font-d);font-size:2.2rem;
                    color:var(--gold);letter-spacing:0.2em;
                    text-transform:uppercase;margin-bottom:8px;">
            ⚡ InkOS
        </div>
        <div style="font-family:var(--font-m);font-size:0.75rem;
                    color:var(--text-muted);letter-spacing:0.15em;
                    text-transform:uppercase;margin-bottom:8px;">
            Cognitive Intelligence for Prompt Heuristics & Engineering
        </div>
        <div style="font-family:var(--font-a);font-size:1.1rem;
                    color:var(--gold);direction:rtl;">
            حبر وفكرة · Intelligence Redefined
        </div>
    </div>
    <hr style="border-color:rgba(255,255,255,0.1);">
    """, unsafe_allow_html=True)

    # ── GUIDE TABS ─────────────────────────────────────────────────────────────
    g1, g2, g3, g4 = st.tabs([
        "⚡ Deployment Brief", 
        "📖 Core Matrix", 
        "🗺️ Arabic Engine", 
        "🛠️ Advanced Ops"
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # QUICK START
    # ══════════════════════════════════════════════════════════════════════════
    with g1:
        _section("Uplink Protocol")
        _step("01", "Initialize Target Model", "Select your target model. Each selection triggers structural validation.")
        _step("02", "Engage Tactical Persona", "Personas act as algorithmic filters, enforcing domain constraints.")
        _step("03", "Declare Language", "Arabic inputs engage the cognitive mapping layer to detect conceptual architecture.")
        _step("04", "Input Raw Intent", "Speak or type. InkOS extracts high-signal requirements from low-fidelity input.")
        _step("05", "Execute & Audit", "The A.I.Z.E.N. core compiles your prompt and runs an adversarial audit.")
        _step("06", "Secure to Vault (Identity Latch)", "Requires a verified Terminal Identity latched with a PIN. Guest sessions remain volatile.")

    # ══════════════════════════════════════════════════════════════════════════
    # FEATURE GUIDE
    # ══════════════════════════════════════════════════════════════════════════
    with g2:
        _section("System Modules")
        _feature_card("⚡", "Workspace", "WORKSPACE", "Primary refinement interface.", "Converts raw intent into command-grade AI instructions.", "Use Voice Input for rapid ideation.", "var(--gold)")
        _feature_card("🔒", "Memory Vault", "VAULT", "Persistent asset library.", "Requires Dual-Factor verification for decryption.", "Unlatched users see an encrypted view.", "#4CAF9A")
        _feature_card("🛡️", "Threat Intel", "SECURITY", "Real-time security auditing.", "Blocks hostile payloads before they reach the engine.", "NFKC normalization stops visually identical characters.", "#E53E3E")
        
        _section("Identity & Defense", dot_color="red")
        _card("<strong style='color:var(--danger);'>Self-Destruct Protocol</strong> — Entering an incorrect PIN 5 times will trigger a 10-minute Terminal Lockout to prevent brute-force intrusion.")

    # ══════════════════════════════════════════════════════════════════════════
    # ARABIC ENGINE
    # ══════════════════════════════════════════════════════════════════════════
    with g3:
        _section("Arabic Cognitive Mapping")
        _card("Utilizes the classical sciences of <strong>Balagha (علم البلاغة)</strong> to understand user intent. "
              "InkOS rejects literal translation, mapping rhetorical DNA directly to AI architecture.")
        st.markdown("<br>", unsafe_allow_html=True)
        from ui.tabs.guide import _arabic_pattern_row # Helper call
        _arabic_pattern_row("التدرج", "Chain-of-Thought", "Maps gradual logic into reasoning chains.", "#90CDF4")
        _arabic_pattern_row("الإيجاز", "Compression", "Enforces maximum token efficiency.", "#6EE7B7")
        _arabic_pattern_row("التفصيل", "Elaboration", "Expands concepts into academic frameworks.", "#F6AD55")

    # ══════════════════════════════════════════════════════════════════════════
    # ADVANCED OPERATIONS (THE TRIFECTA MACROS)
    # ══════════════════════════════════════════════════════════════════════════
    with g4:
        _section("Command Macros (The DNA Trifecta)")
        _card("InkOS utilizes a proprietary <b>Slash Command</b> architecture to instantly inject "
              "complex cognitive frameworks into your prompts. Click the macro buttons in the Workspace "
              "to append these DNA markers without misfires.")

        _feature_card(
            icon  = "⚡",
            name  = "/INK DNA",
            tab   = "WORKSPACE",
            what  = "Creative Direction & Brand Identity.",
            how   = "Injects AmeerInk tech-noir aesthetics, chiaroscuro lighting, and minimalist framing.",
            tip   = "Use this for all visual generation and design-focused prompts.",
            color = "var(--gold)"
        )

        _feature_card(
            icon  = "👁️",
            name  = "/INTEL DNA",
            tab   = "WORKSPACE",
            what  = "Tech Observer & Forensic Analysis.",
            how   = "Shifts the engine to an authoritative, critical tone for AI trends and cybersecurity.",
            tip   = "Perfect for drafting tech blog posts or analyzing software architectures.",
            color = "#7C9EBF"
        )

        _feature_card(
            icon  = "⚖️",
            name  = "/HIKMAH DNA",
            tab   = "WORKSPACE",
            what  = "Scholarly Research & Linguistics.",
            how   = "Applies pedagogical clarity, Balagha logic, and ethical/Sharia-compliant frameworks.",
            tip   = "Use this for university-level Arabic Education tasks and Islamic research.",
            color = "#4CAF9A"
        )
