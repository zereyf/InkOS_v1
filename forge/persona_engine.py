"""
forge/persona_engine.py — Persona Logic Controller
====================================================
v9.3: Type-Agnostic Build.
      - Handles both dict (Session State) and str (Legacy/Direct) inputs.
      - Synchronized with Refiner v9.4.3.
"""

from typing import Optional, Any
import textwrap
# 🟢 Importing the Data from the Vault
from config.personas import AIZEN_IDENTITY, STARTER_PERSONAS

def inject_persona(persona_input: Optional[Any], target: str) -> str:
    """
    Surgical Injection Engine.
    Resolves the persona input into a formatted block for the target model.
    """
    p_data = None

    # 1. RESOLUTION PHASE: Dict vs String
    if isinstance(persona_input, dict):
        # Direct dictionary passed (Common in current Workspace)
        p_data = persona_input
    elif isinstance(persona_input, str):
        # String name passed (Common in Legacy or API calls)
        p_data = STARTER_PERSONAS.get(persona_input)
    
    # 2. FALLBACK PHASE: If no valid data found, return Master Identity
    if not p_data:
        return AIZEN_IDENTITY

    # 3. EXTRACTION PHASE
    name = p_data.get("name", "Expert")
    role = p_data.get("role", "")
    anti = p_data.get("anti_pattern", "Avoid generic responses.")
    tone = p_data.get("tone", "Professional and analytical.")

    # 4. ASSEMBLY PHASE: Target-Specific Formatting
    if target == "Claude":
        return textwrap.dedent(f"""
            {AIZEN_IDENTITY}
            <active_specialist>
              <name>{name}</name>
              <role>{role}</role>
              <constraints>
                <critical_anti_pattern>{anti}</critical_anti_pattern>
              </constraints>
              <tonal_anchor>{tone}</tonal_anchor>
            </active_specialist>
        """).strip()

    elif target == "ChatGPT":
        return textwrap.dedent(f"""
            {AIZEN_IDENTITY}
            SYSTEM OVERRIDE — ADOPT EXPERT LAYER: {name}
            - ROLE: {role}
            - AVOID: {anti}
            - TONE: {tone}
        """).strip()

    elif target == "Manus AI":
        return f"[AIZEN_CORE]\n[AGENT_PERSONA]: {role}\n[TONE]: {tone}\n[NEVER]: {anti}"

    else:
        # Default for Image Models or General Fallback
        return f"{AIZEN_IDENTITY}\nPERSONA: {role} | TONE: {tone}"

def get_persona_display_name(persona_data: Optional[dict]) -> str:
    """Helper for UI badges."""
    if not persona_data:
        return "None"
    return persona_data.get("name", "Unknown")
