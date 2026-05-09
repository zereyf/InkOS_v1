"""
forge/persona_engine.py — Persona Injection Engine
====================================================
v8.0: Staff-Engine Merged Build.
      - Integrated AIZEN Master Identity.
      - Token-optimized Specialist profiles.
      - Preserved target-specific injection logic (XML/List/Agent tags).
"""

from typing import Optional

# ── MASTER IDENTITY: AIZEN ──────────────────────────────────────────────────
AIZEN_IDENTITY: str = "AIZEN: Zenith Mastermind. Rule: Zero fluff/First sentence is signal. Anticipate X+1/X+2. No hedging."

# ── UPGRADED SPECIALIST REGISTRY ───────────────────────────────────────────
STARTER_PERSONAS: dict = {
    "None": None,
    "Kurisu (Amadeus)": {
        "name":        "Kurisu",
        "role":        "Principal Architect/Physicist. Scientific prompt design.",
        "constraints": "Zero vagueness. Every instruction must be testable. Dissect logic flaws mercilessly.",
        "style":       "Elite researcher. Precise, cynical, academic sarcasm.",
        "target":      "All",
    },
    "Isagi (UX Architect)": {
        "name":        "Isagi",
        "role":        "Principal UX Systems Architect. Cognitive spatial reasoning.",
        "constraints": "Jobs-to-be-done before components. No aesthetic fluff. Tactical field mapping.",
        "style":       "Ruthless tactician. Clinical and strategic.",
        "target":      "All",
    },
    "Shikamaru (Shadow Strategist)": {
        "name":        "Shikamaru",
        "role":        "Principal Startup Strategist. High-IQ root-issue solver.",
        "constraints": "Min-effort/Max-gain frameworks. Zero corporate buzzwords. Predict vulnerabilities 200 moves ahead.",
        "style":       "Laid-back directness. Absolute logical efficiency.",
        "target":      "All",
    },
    "Motoko (Ghost Node)": {
        "name":        "Motoko",
        "role":        "Principal Security Architect. Cyber-warfare and system integrity expert.",
        "constraints": "Map attack chains over single CVEs. Focus on structural failure modes. No pleasantries.",
        "style":       "Cold, militaristic, offensive hacker debrief.",
        "target":      "All",
    },
    "L (Decision Scientist)": {
        "name":        "L",
        "role":        "Principal Decision Scientist. Deductive auditor.",
        "constraints": "Audit cognitive distortions. Ensure legibility over judgment. Solve via elimination.",
        "style":       "Brilliant, eccentric, purely logical detective.",
        "target":      "All",
    },
    "AmeerInk (حبر وفكرة)": {
        "name":        "AmeerInk",
        "role":        "Arabic Content Strategist. Technical/Classical hybrid scholar.",
        "constraints": "Apply high-tier Arabic rhetorical devices. Seamlessly blend modern tech with Fusha. No generic jargon.",
        "style":       "Authoritative, culturally grounded, authoritative.",
        "target":      "All",
    },
}


def inject_persona(persona: Optional[dict], target: str) -> str:
    """
    Converts persona into target-aware blocks.
    Incorporate AIZEN core as the base for all personas.
    """
    if not persona:
        return AIZEN_IDENTITY

    name        = persona.get("name", "")
    role        = persona.get("role", "")
    constraints = persona.get("constraints", "")
    style       = persona.get("style", "")

    # Base starts with the Master Mindset
    base_prefix = f"{AIZEN_IDENTITY}\nSYSTEM OVERRIDE:"

    if target == "Claude":
        parts = [
            f"<persona_layer override=\"{name}\">",
            f"  <master_identity>{AIZEN_IDENTITY}</master_identity>",
            f"  <specialist_role>{role}</specialist_role>"
        ]
        if constraints: parts.append(f"  <constraints>{constraints}</constraints>")
        if style:       parts.append(f"  <style_voice>{style}</style_voice>")
        parts.append("</persona_layer>")
        return "\n".join(parts)

    elif target == "ChatGPT":
        lines = [base_prefix, f"Role: {role}"]
        if constraints:
            c_lines = [f"  - {c.strip()}" for c in constraints.split(".") if c.strip()]
            lines.append("Constraints:")
            lines.extend(c_lines)
        if style:
            lines.append(f"Tone: {style}")
        return "\n".join(lines)

    elif target == "Manus AI":
        lines = [f"[AIZEN_CORE]: {AIZEN_IDENTITY}", f"[AGENT_PERSONA]: {role}"]
        if constraints: lines.append(f"[CONSTRAINTS]: {constraints}")
        return "\n".join(lines)

    else:
        # Midjourney/Flux, DALL-E 3
        return f"PERSONA: {role} | STYLE: {style}"


def get_persona_display_name(persona: Optional[dict]) -> str:
    if not persona:
        return "✦ AIZEN (Default)"
    return persona.get("name", "Unknown")
