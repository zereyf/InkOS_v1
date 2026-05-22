"""
ui/tabs/guide.py — InkOS Documentation & Intelligence Briefing
===============================================================
v22.1: The Premium Branding Sync.
       - INTEGRATED: Terminal SVG Logo & Neon Wordmark.
       - REFINED: Chiaroscuro Documentation Header.
"""

import streamlit as st
import textwrap
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

    # ── 🟢 PREMIUM HERO SYNC ──────────────────────────────────────────────────
    brand_html = textwrap.dedent(f"""
        <div style="text-align:center; margin-bottom: 40px; padding-top: 20px;">
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 12px;">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" style="width: 50px; height: 50px; fill: var(--gold); filter: drop-shadow(0px 0px 8px rgba(201, 168, 76, 0.4));">
                    <path d="M73.4 182.6C60.9 170.1 60.9 149.8 73.4 137.3C85.9 124.8 106.2 124.8 118.7 137.3L278.7 297.3C291.2 309.8 291.2 330.1 278.7 342.6L118.7 502.6C106.2 515.1 85.9 515.1 73.4 502.6C60.9 490.1 60.9 469.8 73.4 457.3L210.7 320L73.4 182.6zM288 448L544 448C561.7 448 576 462.3 576 480C576 497.7 561.7 512 544 512L288 512C270.3 512 256 497.7 256 480C256 462.3 270.3 448 288 448z"/>
                </svg>
                <span style="font-family: var(--font-m); font-size: 2.2rem; color: var(--text); letter-spacing: 8px; margin-left: 20px; font-weight: bold; text-transform: uppercase;">
                    INK<span style="color: var(--gold);">OS</span> // GUIDE
                </span>
            </div>
            <div style="font-family:var(--font-m); font-size:0.7rem; color:var(--text-muted); letter-spacing:0.15em; text-transform:uppercase; margin-bottom:8px;">
                Cognitive Intelligence Briefing // حبر وفكرة
            </div>
            <hr style="border-color:rgba(255,255,255,0.05); width: 30%; margin: 20px auto;">
        </div>
    """)
    st.markdown(brand_html, unsafe_allow_html=True)

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

_feature_card(
    icon  = "◈",
    name  = "Visual Director",
    tab   = "VISUAL DIRECTOR",
    what  = "10-layer structured image prompt compiler for all major image models.",
    how   = (
        "Walks through Subject, 3-zone Environment, Lighting (Kelvin temps), "
        "Lens, Composition, Per-region Style (face/clothing/hands separately), "
        "Palette (hex codes), Glitch effects, Exclusions, and Narrative Logic. "
        "Compiles into model-specific syntax: Midjourney :: separators, "
        "DALL-E prose paragraphs, Stable Diffusion keyword tags + Negative prompt."
    ),
    tip   = (
        "Layer 10 (Narrative Logic) is the most important. "
        "Explain WHY elements work, not just what they look like. "
        "The model uses this reasoning to handle every unspecified detail correctly."
    ),
    color = "var(--steel)",
)

    # ══════════════════════════════════════════════════════════════════════════
    # ARABIC ENGINE
    # ══════════════════════════════════════════════════════════════════════════
    with g3:
        _section("Arabic Cognitive Mapping")
        _card("Utilizes the classical sciences of <strong>Balagha (علم البلاغة)</strong> to understand user intent. "
              "InkOS rejects literal translation, mapping rhetorical DNA directly to AI architecture.")
        st.markdown("<br>", unsafe_allow_html=True)
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
            icon  = "♦️",
            name  = "/INTEL DNA",
            tab   = "WORKSPACE",
            what  = "Tech Observer & Forensic Analysis.",
            how   = "Shifts the engine to an authoritative, critical tone for AI trends and cybersecurity.",
            tip   = "Perfect for drafting tech blog posts or analyzing software architectures.",
            color = "#7C9EBF"
        )

        _feature_card(
            icon  = "🔶️",
            name  = "/HIKMAH DNA",
            tab   = "WORKSPACE",
            what  = "Scholarly Research & Linguistics.",
            how   = "Applies pedagogical clarity, Balagha logic, and ethical/Sharia-compliant frameworks.",
            tip   = "Use this for university-level Arabic Education tasks and Islamic research.",
            color = "#4CAF9A"
        )

    # ── 🟢 FOOTER SIGNATURE ──────────────────────────────────────────────────
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(f"""
        <div style="text-align:center; color:var(--text-dim); font-family:var(--font-m); font-size:0.6rem; letter-spacing:2px;">
            [ END OF INTELLIGENCE BRIEFING // INKOS v2026.4 ]
        </div>
    """, unsafe_allow_html=True)
