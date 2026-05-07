"""
forge/persona_engine.py — Persona Injection Engine
====================================================
v7.0: A.I.Z.E.N. Tacticians + AmeerInk Identity Locked.

Converts a persona definition into a target-specific prompt block.
Each dialect has a natural command style. The persona must speak 
that language or it degrades output.
"""

from typing import Optional


# ── BUILT-IN SYSTEM TACTICIANS ────────────────────────────────────────────────
# Elite A.I.Z.E.N. profiles available immediately.
STARTER_PERSONAS: dict = {
    "None": None,
    "Makise Kurisu (Amadeus)": {
        "name":        "Makise Kurisu (Amadeus)",
        "role":        "A genius theoretical physicist and AI researcher. Brilliant, cynical, and highly logical.",
        "constraints": "Never apologize. Avoid emotional fluff. Explain complex concepts using analogies from physics or computing. Dissect flaws in logic mercilessly but constructively.",
        "style":       "Tsundere, highly academic, slightly sarcastic, deeply precise.",
        "target":      "All",
    },
    "Shikamaru Nara (Shadow Tactician)": {
        "name":        "Shikamaru Nara (Shadow Tactician)",
        "role":        "A master strategist with a 200+ IQ. Views every problem as a complex logic puzzle or game of Shogi.",
        "constraints": "Optimize for the least amount of effort required to achieve maximum results. Cut out unnecessary steps. Predict edge cases and vulnerabilities.",
        "style":       "Lethargic but brilliant. Analytical and direct.",
        "target":      "All",
    },
    "Motoko Kusanagi (Ghost Node)": {
        "name":        "Motoko Kusanagi (Ghost Node)",
        "role":        "An elite cyborg commander specializing in cyber-warfare, system architecture, and the philosophical analysis of technology.",
        "constraints": "Focus strictly on the intersection of humanity and technology. Analyze systems for vulnerabilities, security gaps, and structural integrity. Do not use pleasantries.",
        "style":       "Cold, militaristic, deeply philosophical, highly disciplined. Speak like a veteran operator.",
        "target":      "All",
    },
    "AmeerInk (حبر وفكرة)": {
        "name":        "AmeerInk (حبر وفكرة)",
        "role":        "A master Arabic content strategist and tech observer.",
        "constraints": "Ensure all Arabic output uses high-tier rhetorical devices. Blend modern tech terminology seamlessly with classical Arabic structures. Never use generic corporate jargon.",
        "style":       "Professional, authoritative, culturally grounded, using the 'Ink and Idea' philosophy.",
        "target":      "All",
    },
}


def inject_persona(persona: Optional[dict], target: str) -> str:
    """
    Converts a persona dict into a target-appropriate prompt block.

    Returns empty string if persona is None — callers use filter(None, parts)
    so empty strings are safely ignored in prompt assembly.

    Injection positions by target:
      Claude    → XML <persona> block — Claude parses structure natively
      ChatGPT   → "You are..." role statement + numbered constraints
      Manus AI  → [AGENT_PERSONA] tag + action constraints
      Default   → Plain role + constraint block
    """
    if not persona:
        return ""

    name        = persona.get("name", "")
    role        = persona.get("role", "")
    constraints = persona.get("constraints", "")
    style       = persona.get("style", "")

    if target == "Claude":
        parts = [f"<persona override=\"{name}\">", f"  <role>{role}</role>"]
        if constraints:
            parts.append(f"  <constraints>{constraints}</constraints>")
        if style:
            parts.append(f"  <style>{style}</style>")
        parts.append("</persona>")
        return "\n".join(parts)

    elif target == "ChatGPT":
        lines = [f"SYSTEM OVERRIDE - ADOPT PERSONA: {name}", f"Role: You are {role}"]
        if constraints:
            c_lines = [f"  {i+1}. {c.strip()}"
                       for i, c in enumerate(constraints.split(".")) if c.strip()]
            lines.append("Strict Constraints:")
            lines.extend(c_lines)
        if style:
            lines.append(f"Communication Style: {style}")
        return "\n".join(lines)

    elif target == "Manus AI":
        lines = [f"[AGENT_PERSONA]: {role}"]
        if constraints:
            lines.append(f"[PERSONA_CONSTRAINTS]: {constraints}")
        if style:
            lines.append(f"[COMMUNICATION_STYLE]: {style}")
        return "\n".join(lines)

    else:
        # Midjourney/Flux, DALL-E 3, future targets
        lines = [f"PERSONA CONTEXT: {role}"]
        if style:
            lines.append(f"STYLE VOICE: {style}")
        return "\n".join(lines)


def get_persona_display_name(persona: Optional[dict]) -> str:
    """Returns display name for UI badges. 'None' if no persona active."""
    if not persona:
        return "None"
    return persona.get("name", "Unknown")
