"""
ui/tabs/guide.py — InkOS Documentation & Intelligence Briefing
===============================================================
v12.0: Final Production Polish. Rebranded for InkOS/A.I.Z.E.N. 
       and synced with all v2026 architectural upgrades.
"""

import streamlit as st


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
    """Renders Tab 7 — InkOS Guide."""

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
              "Select your target AI model via the sidebar. InkOS supports Claude, ChatGPT, "
              "Manus AI, Midjourney, and DALL-E 3. Each selection triggers a unique structural "
              "validator to ensure syntax compliance.")

        _step("02", "Engage Tactical Persona",
              "Select an elite tactician from the Forge (e.g., KURISU, SHIKAMARU, MOTOKO). "
              "Personas act as algorithmic filters, enforcing domain-specific constraints "
              "and anti-patterns on every output.")

        _step("03", "Declare Input Language",
              "Toggle between English and Arabic. Arabic inputs engage the cognitive mapping layer, "
              "detecting classical rhetorical devices to map conceptual architecture rather "
              "than literal vocabulary.")

        _step("04", "Input Raw Intent",
              "Speak or type your raw, unstructured intent. InkOS is designed to extract "
              "high-signal requirements from low-fidelity inputs. No prompt engineering "
              "knowledge is required from the user.")

        _step("05", "Execute & Audit",
              "The A.I.Z.E.N. core compiles your prompt, run a zero-cost structural check, "
              "and then submits it to an independent adversarial evaluator for grading.")

        _step("06", "Secure to Vault",
              "Save high-performing assets to the Memory Vault. These assets are encrypted "
              "and persist across all session resets, forming your permanent tactical library.")

        st.markdown("<hr style='border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        _section("Optimal Input Strategy")

        st.markdown("""
        <div class="vc-card" style="margin-bottom:14px; background:rgba(76, 175, 154, 0.05);">
        <div style="font-family:var(--font-m);font-size:0.78rem;line-height:1.85;color:var(--text);">
        <strong style="color:#6EE7B7;">Focus on the 'What', not the 'How'.</strong><br>
        InkOS is a prompt compiler. Do not waste characters describing formatting. Describe the 
        expertise, the context, and the desired outcome. The engine will handle the structural 
        heavy lifting for you.
        </div></div>
        """, unsafe_allow_html=True)


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
            how   = "Processes input through the A.I.Z.E.N. router to select the best model, "
                    "applies logic frameworks, and audits quality via independent evaluation.",
            tip   = "Use Voice Input for rapid ideation; the Whisper engine is calibrated for "
                    "both English and Arabic tech terminology.",
            color = "var(--gold)",
        )

        _feature_card(
            icon  = "🧬",
            name  = "Identity Forge",
            tab   = "FORGE",
            what  = "Persona creation and Brand DNA management.",
            how   = "Build custom personas or latch on starter tacticians. Lock your 'Brand Identity' "
                    "to protect typography and visual motifs in image generation.",
            tip   = "The 'Muse Trigger' word allows you to instantly inject your visual avatar "
                    "descriptions into any Midjourney or DALL-E prompt.",
            color = "#7C9EBF",
        )

        _feature_card(
            icon  = "🔒",
            name  = "Memory Vault",
            tab   = "VAULT",
            what  = "Persistent asset library backed by cloud storage.",
            how   = "Stores refined prompts with metadata, scores, and tags. Prompts can be "
                    "redeployed to the Workspace with a single click.",
            tip   = "Vault assets bypass current session state, allowing you to load legacy "
                    "prompts into any new model target.",
            color = "#4CAF9A",
        )

        _feature_card(
            icon  = "🛡️",
            name  = "Threat Intel Ledger",
            tab   = "SECURITY",
            what  = "Real-time security auditing and injection blocking.",
            how   = "Monitors all inputs for adversarial patterns (jailbreaks, token overrides). "
                    "Blocks hostile payloads before they reach the engine.",
            tip   = "The ledger uses NFKC normalization, meaning visual lookalike characters "
                    "cannot bypass the firewall.",
            color = "#E53E3E",
        )

        st.markdown("<hr style='border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        _section("Operational Parameters")

        st.markdown("""
        <div class="vc-card" style="margin-bottom:14px;">
        <div style="font-family:var(--font-m);font-size:0.78rem;line-height:1.85;color:var(--text);">
        <strong style="color:var(--gold);">Independent Evaluation</strong> — InkOS uses a second, adversarial AI model to grade the primary model's output. A score of 85+ indicates production-grade quality.<br><br>
        <strong style="color:var(--gold);">Structural Validation</strong> — Deterministic Python checks enforce target-specific rules (e.g., XML tags for Claude) before the evaluator even sees the text.<br><br>
        <strong style="color:var(--gold);">Islamic Mode</strong> — Activating this protocol injects Sharia-aware constraints and academic citation requirements for Islamic research tasks.
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
            InkOS rejects literal translation. It instead utilizes <strong>Cognitive Mapping</strong> 
            to identify the rhetorical "DNA" of Arabic speech and map it to AI native instructions.<br><br>
            This system utilizes the classical sciences of 
            <strong style="color:var(--gold);">Balagha (علم البلاغة)</strong> 
            to understand user intent at a cultural and logical level.
        </div>
        """, unsafe_allow_html=True)

        _section("Rhetorical Mapping Matrix")

        _arabic_pattern_row(
            arabic   = "التدرج",
            paradigm = "Chain-of-Thought (CoT)",
            example  = "Maps gradual logic into multi-step reasoning chains for complex problem solving.",
            color    = "#90CDF4",
        )
        _arabic_pattern_row(
            arabic   = "الإيجاز",
            paradigm = "Precision Compression",
            example  = "Identifies requests for brevity and enforces maximum token efficiency without signal loss.",
            color    = "#6EE7B7",
        )
        _arabic_pattern_row(
            arabic   = "التفصيل",
            paradigm = "Hierarchical Academic Elaboration",
            example  = "Expands technical concepts into structured, high-fidelity academic frameworks.",
            color    = "#F6AD55",
        )
        _arabic_pattern_row(
            arabic   = "التصوير",
            paradigm = "Visual DNA Compilation",
            example  = "Maps descriptive imagery directly to the Visual Director prompt engine.",
            color    = "#B07C9E",
        )

        st.markdown("<hr style='border-color:rgba(255,255,255,0.05);'>", unsafe_allow_html=True)
        _section("Detection & Normalization")

        st.markdown("""
        <div class="vc-card" style="margin-bottom:14px; background:rgba(255,255,255,0.02);">
        <div style="font-family:var(--font-m);font-size:0.78rem;line-height:1.85;color:var(--text);">
        The engine identifies patterns through weighted trigger analysis. Because Arabic input 
        often varies between different digital keyboards, InkOS applies <strong>NFC Unicode 
        Normalization</strong> to every character before detection, ensuring that visually identical 
        characters always trigger the correct logical framework.
        </div></div>
        """, unsafe_allow_html=True)
