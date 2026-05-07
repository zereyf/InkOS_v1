"""
ui/tabs/guide.py — InkOS Documentation & Intelligence Briefing
===============================================================
v1.0: Advanced Ops Integration.
       Added Technical Auditing, Muse Triggers, and Tactical Gaming.
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
        _step("06", "Secure to Vault", "Requires a verified Identity. Guest sessions remain volatile and will not persist.")

    # ══════════════════════════════════════════════════════════════════════════
    # FEATURE GUIDE
    # ══════════════════════════════════════════════════════════════════════════
    with g2:
        _section("System Modules")
        _feature_card("⚡", "Workspace", "WORKSPACE", "Primary refinement interface.", "Converts raw intent into command-grade AI instructions.", "Use Voice Input for rapid ideation.", "var(--gold)")
        _feature_card("🔒", "Memory Vault", "VAULT", "Persistent asset library.", "Requires Dual-Factor verification for decryption.", "Unlatched users see an encrypted view.", "#4CAF9A")
        _feature_card("🛡️", "Threat Intel", "SECURITY", "Real-time security auditing.", "Blocks hostile payloads before they reach the engine.", "NFKC normalization stops visually identical characters.", "#E53E3E")
        
        _section("Identity & Defense", dot_color="red")
        _card("<strong style='color:var(--danger);'>Self-Destruct Protocol</strong> — Entering an incorrect PIN 5 times will trigger a 10-minute Terminal Lockout.")

    # ══════════════════════════════════════════════════════════════════════════
    # ARABIC ENGINE
    # ══════════════════════════════════════════════════════════════════════════
    with g3:
        _section("Arabic Cognitive Mapping")
        _card("Utilizes the classical sciences of <strong>Balagha (علم البلاغة)</strong> to understand user intent.")
        st.markdown("<br>", unsafe_allow_html=True)
        from ui.tabs.guide import _arabic_pattern_row # Helper call
        _arabic_pattern_row("التدرج", "Chain-of-Thought", "Maps gradual logic into reasoning chains.", "#90CDF4")
        _arabic_pattern_row("الإيجاز", "Compression", "Enforces maximum token efficiency.", "#6EE7B7")
        _arabic_pattern_row("التفصيل", "Elaboration", "Expands concepts into academic frameworks.", "#F6AD55")

    # ══════════════════════════════════════════════════════════════════════════
    # ADVANCED OPERATIONS (NEW)
    # ══════════════════════════════════════════════════════════════════════════
    with g4:
        _section("AmeerInk Brand DNA")
        _feature_card(
            icon  = "🖌️",
            name  = "Muse Trigger",
            tab   = "FORGE",
            what  = "Instant injection of visual avatar and photography motifs.",
            how   = "Typing 'AmeerInk' in the workspace automatically injects Chiaroscuro lighting, tech-noir aesthetics, and minimalist framing.",
            tip   = "Pair with 'Chiaroscuro' aesthetic preset for maximum forensic impact.",
            color = "#C9A84C"
        )

        _section("Technical Auditing (VelvetCodex)")
        _card("The <b>VelvetCodex</b> protocol enables forensic auditing of AI code. "
              "It forces the model to explain logic errors through a security-first lens.")

        _section("Tactical Gaming & Team Rei")
        _feature_card(
            icon  = "⚔️",
            name  = "Team Rei Protocols",
            tab   = "WORKSPACE",
            what  = "MLBB Strategy and Team Anthem Generation.",
            how   = "Uses data from Ascendant, Emrys, and Aizen to generate role-specific meta strategies.",
            tip   = "Try 'Rei Anthem' as a prompt intent to generate high-motivation lyrics.",
            color = "#7C9EBF"
        )

        _section("Arabic Education Pedagogy")
        _card("For the 200-level Arabic student, InkOS acts as a <b>Linguistic Validator</b>. "
              "It breaks down syntax trees and grammar rules using the 'Hierarchical Elaboration' framework.")

"""
ui/tabs/guide.py — InkOS Documentation & Intelligence Briefing
===============================================================
v13.0: Security Integration & Production Polish. 
       Synced with Terminal Identity Latching and Lockout Protocols.
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
    """Renders Tab 7 — InkOS Guide with Security Briefing."""

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
    g1, g2, g3 = st.tabs(["⚡ Deployment Brief", "📖 Core Matrix", "🗺️ Arabic Cognitive Mapping"])

    # ══════════════════════════════════════════════════════════════════════════
    # QUICK START
    # ══════════════════════════════════════════════════════════════════════════
    with g1:
        _section("Uplink Protocol")

        _step("01", "Initialize Target Model",
              "Select your target AI model via the sidebar. Each selection triggers a unique "
              "structural validator to ensure syntax compliance.")

        _step("02", "Engage Tactical Persona",
              "Select an elite tactician from the Forge. Personas act as algorithmic filters, "
              "enforcing domain-specific constraints on every output.")

        _step("03", "Declare Input Language",
              "Toggle between English and Arabic. Arabic inputs engage the cognitive mapping layer "
              "to detect conceptual architecture.")

        _step("04", "Input Raw Intent",
              "Speak or type your unstructured intent. InkOS is designed to extract "
              "high-signal requirements from low-fidelity inputs.")

        _step("05", "Execute & Audit",
              "The A.I.Z.E.N. core compiles your prompt and submits it to an independent "
              "adversarial evaluator for grading.")

        _step("06", "Secure to Vault (Identity Latch)",
              "Save assets to the Memory Vault. Access requires a verified Terminal Identity "
              "latched with a PIN. Guest sessions remain volatile and will not persist.")

        st.markdown("<hr style='border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        _section("Optimal Input Strategy")

        _card("<strong style='color:#6EE7B7;'>Focus on the 'What', not the 'How'.</strong><br>"
              "InkOS handles structural heavy lifting. Describe expertise, context, and outcomes. "
              "Do not waste characters on formatting instructions.", accent="#4CAF9A")


    # ══════════════════════════════════════════════════════════════════════════
    # FEATURE GUIDE
    # ══════════════════════════════════════════════════════════════════════════
    with g2:
        _section("System Modules")

        _feature_card(
            icon  = "⚡",
            name  = "Intelligence Workspace",
            tab   = "WORKSPACE",
            what  = "Primary refinement interface. Converts raw intent into command-grade AI instructions.",
            how   = "Processes input through the A.I.Z.E.N. router to apply logic frameworks and audits quality.",
            tip   = "Use Voice Input for rapid ideation; the engine is calibrated for bilingual tech terminology.",
            color = "var(--gold)",
        )

        _feature_card(
            icon  = "🔒",
            name  = "Memory Vault",
            tab   = "VAULT",
            what  = "Persistent asset library backed by cloud storage. Restricted to latched identities.",
            how   = "Stores refined prompts with metadata and scores. Requires Dual-Factor verification for decryption.",
            tip   = "Unlatched (Guest) users see an encrypted view. Identity Latching is required for persistent memory.",
            color = "#4CAF9A",
        )

        _feature_card(
            icon  = "🛡️",
            name  = "Threat Intel Ledger",
            tab   = "SECURITY",
            what  = "Real-time security auditing and injection blocking.",
            how   = "Monitors inputs for adversarial patterns and hostile payloads before they reach the engine.",
            tip   = "NFKC normalization ensures visually identical 'lookalike' characters cannot bypass the firewall.",
            color = "#E53E3E",
        )

        st.markdown("<hr style='border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        _section("Identity & Forensic Defense", dot_color="red")

        st.markdown("""
        <div class="vc-card" style="margin-bottom:14px; border-color:var(--danger);">
        <div style="font-family:var(--font-m);font-size:0.78rem;line-height:1.85;color:var(--text);">
        <strong style="color:var(--danger);">Self-Destruct Protocol (Lockout)</strong> — To prevent brute-force intrusion, 
        entering an incorrect Security PIN 5 times will trigger a <strong>Terminal Lockout</strong>. 
        All operations will be frozen for 10 minutes.<br><br>
        <strong style="color:var(--gold);">Terminal Latching</strong> — Registering an identity locks your data to a 
        unique Access Key. Once secured, your identity persists via URL parameters for rapid forensic access.
        </div></div>
        """, unsafe_allow_html=True)


    # ══════════════════════════════════════════════════════════════════════════
    # ARABIC ENGINE
    # ══════════════════════════════════════════════════════════════════════════
    with g3:
        _section("Arabic Cognitive Engine")

        st.markdown("""
        <div style="font-family:var(--font-m);font-size:0.75rem;
                    color:var(--text-muted);line-height:1.85;margin-bottom:20px;">
            InkOS rejects literal translation, utilizing <strong>Cognitive Mapping</strong> 
            to identify the rhetorical "DNA" of Arabic speech through the classical sciences of 
            <strong style="color:var(--gold);">Balagha (علم البلاغة)</strong>.
        </div>
        """, unsafe_allow_html=True)

        _section("Rhetorical Mapping Matrix")

        _arabic_pattern_row(arabic="التدرج", paradigm="Chain-of-Thought (CoT)", example="Maps gradual logic into multi-step reasoning chains.", color="#90CDF4")
        _arabic_pattern_row(arabic="الإيجاز", paradigm="Precision Compression", example="Identifies requests for brevity and enforces token efficiency.", color="#6EE7B7")
        _arabic_pattern_row(arabic="التفصيل", paradigm="Academic Elaboration", example="Expands concepts into structured, academic frameworks.", color="#F6AD55")
        _arabic_pattern_row(arabic="التصوير", paradigm="Visual DNA Compilation", example="Maps descriptive imagery directly to the visual engine.", color="#B07C9E")

        st.markdown("<hr style='border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        _section("NFC Unicode Normalization")
        _card("Every character is normalized before detection, ensuring that visual variations "
              "always trigger the correct logical framework.", accent="var(--steel)")
