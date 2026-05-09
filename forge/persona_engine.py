"""
forge/persona_engine.py — Persona Injection Engine
==================================================
v9.1: Logic Layer.
      - Imports from config/personas.py.
      - Handles target-specific prompt assembly.
"""

from typing import Optional
import textwrap
# 🟢 Importing Data from the Vault
from config.personas import AIZEN_IDENTITY, STARTER_PERSONAS

def inject_persona(persona_name: Optional[str], target: str) -> str:
    """
    Transforms a persona selection into a formatted system block.
    """
    if not persona_name or persona_name not in STARTER_PERSONAS:
        return AIZEN_IDENTITY

    p = STARTER_PERSONAS[persona_name]
    if p is None: return AIZEN_IDENTITY
    
    name, role, anti, tone = p["name"], p["role"], p["anti_pattern"], p["tone"]

    # ── TARGET-SPECIFIC ASSEMBLY ──────────────────────────────────────────
    if target == "Claude":
        return textwrap.dedent(f"""
            {AIZEN_IDENTITY}
            <active_specialist>
              <name>{name}</name>
              <role>{role}</role>
              <constraints>
                <anti_pattern_avoid>{anti}</anti_pattern_avoid>
              </constraints>
              <tonal_anchor>{tone}</tonal_anchor>
            </active_specialist>
        """).strip()

    elif target == "ChatGPT":
        return textwrap.dedent(f"""
            {AIZEN_IDENTITY}
            SYSTEM OVERRIDE — ADOPT EXPERT: {name}
            - ROLE: {role}
            - AVOID: {anti}
            - TONE: {tone}
        """).strip()

    elif target == "Manus AI":
        return f"[AIZEN_CORE]: {AIZEN_IDENTITY}\n[AGENT_PERSONA]: {role}\n[ANTI_PATTERN]: {anti}"

    else:
        # Default for Image Models or fallback
        return f"{AIZEN_IDENTITY}\nPersona Context: {role} | Tone: {tone}"

def get_persona_display_name(persona_name: Optional[str]) -> str:
    """Helper for UI badges."""
    return persona_name if persona_name else "✦ AIZEN (Mastermind)"
