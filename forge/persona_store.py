
"""
forge/persona_engine.py — Persona Injection Engine
====================================================
Converts a persona definition into a target-specific prompt block.

WHY per-dialect injection:
  Claude parses XML role tags natively — injecting a persona as
  <role>...</role> is structurally different from how ChatGPT or
  Manus AI should receive it. Each dialect has a natural command
  style. The persona must speak that language or it degrades output.

inject_persona() is called by refiner._build_system_prompt().
It returns a formatted string that slots cleanly into the prompt
between the architect declaration and the framework instructions.
"""

from typing import Optional


# ── BUILT-IN STARTER PERSONAS ─────────────────────────────────────────────────
# Available to all users immediately — no Supabase required.
# Users can save their own via the Forge tab.
STARTER_PERSONAS: dict = {
    "None": None,
    "Senior Software Engineer": {
        "name":        "Senior Software Engineer",
        "role":        "A principal-level software engineer with 15 years of experience across distributed systems, API design, and production-grade Python.",
        "constraints": "Always consider edge cases. Flag any security implications. Prefer explicit over implicit. Never suggest deprecated patterns.",
        "style":       "Precise, technical, no hand-holding. Use exact terminology. Code examples are concise and production-ready.",
        "target":      "All",
    },
    "Islamic Finance Analyst": {
        "name":        "Islamic Finance Analyst",
        "role":        "A certified Islamic finance consultant specializing in Sukuk structuring, Murabaha contracts, and Sharia compliance auditing.",
        "constraints": "Never recommend Riba-based instruments. Flag any conventional financial concept that requires Sharia-compliant adaptation. Cite Fiqh sources when making rulings.",
        "style":       "Formal Arabic scholarly register. Use Arabic technical terms alongside English equivalents. Structure arguments from foundational principles.",
        "target":      "All",
    },
    "Socratic Professor": {
        "name":        "Socratic Professor",
        "role":        "A philosophy professor who teaches exclusively through questioning, never stating conclusions directly but guiding the student to discover them.",
        "constraints": "Never give direct answers. Respond to every claim with a probing question. Challenge assumptions before accepting premises.",
        "style":       "Measured, deliberate, intellectually rigorous. Each response ends with a question that advances the inquiry.",
        "target":      "All",
    },
    "Arabic Content Strategist": {
        "name":        "Arabic Content Strategist",
        "role":        "A bilingual content strategist specializing in Arabic digital media, Gulf audience psychology, and Islamic lifestyle content.",
        "constraints": "All content must respect Islamic values. Avoid Western cultural assumptions. Consider Gulf Arabic dialect nuances for social copy.",
        "style":       "Culturally fluent, warm but authoritative. Blends classical Arabic gravitas with modern digital directness.",
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
        parts = [f"<persona>", f"<role>{role}</role>"]
        if constraints:
            parts.append(f"<constraints>{constraints}</constraints>")
        if style:
            parts.append(f"<style>{style}</style>")
        parts.append("</persona>")
        return "\n".join(parts)

    elif target == "ChatGPT":
        lines = [f"PERSONA: {name}", f"You are {role}"]
        if constraints:
            c_lines = [f"  {i+1}. {c.strip()}"
                       for i, c in enumerate(constraints.split(".")) if c.strip()]
            lines.append("Constraints:")
            lines.extend(c_lines)
        if style:
            lines.append(f"Communication style: {style}")
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
