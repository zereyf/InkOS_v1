"""
forge/persona_engine.py — Composite Persona Logic
====================================================
v10.0: Zenith Edition — Rhetoric Integration.
      - ADDED: Hikmah Rhetoric Protocol support.
      - REFACTORED: Composite assembly (Aizen + Specialist + Rhetoric).
      - UPDATED: surgical injection for multi-layer instruction sets.
"""

from typing import Optional, Any
import textwrap
from config.personas import AIZEN_IDENTITY, STARTER_PERSONAS
# 🟢 Import the Rhetoric Factory
from forge.rhetoric_engine import get_hikmah_directive

def inject_persona(persona_input: Optional[Any], target: str, hikmah_style: str = "None") -> str:
    """
    Composite Injection Engine.
    Combines Core Identity, Specialist Persona, and Rhetorical Style.
    """
    p_data = None

    # 1. RESOLUTION PHASE: Persona Data
    if isinstance(persona_input, dict):
        p_data = persona_input
    elif isinstance(persona_input, str):
        p_data = STARTER_PERSONAS.get(persona_input)
    
    # Fallback to defaults if no persona is active
    if not p_data:
        p_data = {"name": "Generalist", "role": "Analytical Assistant", "anti_pattern": "Generic fluff.", "tone": "Direct."}

    # 2. RHETORIC EXTRACTION
    # Only fetches the block if style != "None"
    rhetoric_directive = get_hikmah_directive(hikmah_style)

    # 3. EXTRACTION PHASE
    name = p_data.get("name", "Expert")
    role = p_data.get("role", "")
    anti = p_data.get("anti_pattern", "")
    tone = p_data.get("tone", "")

    # 4. ASSEMBLY PHASE: Target-Specific Formatting
    if target == "Claude":
        # Anthropic responds best to XML for clear boundary separation
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
            {rhetoric_directive}
        """).strip()

    elif target == "ChatGPT":
        # OpenAI responds best to bulleted system overrides
        return textwrap.dedent(f"""
            {AIZEN_IDENTITY}
            
            [SYSTEM_OVERRIDE]: ADOPT EXPERT LAYER
            - NAME: {name}
            - ROLE: {role}
            - CONSTRAINT_AVOID: {anti}
            - TONAL_GUIDE: {tone}
            {rhetoric_directive}
        """).strip()

    elif target == "Manus AI":
        return f"[AIZEN_CORE]\n[PERSONA]: {role}\n[TONE]: {tone}\n[NEVER]: {anti}\n{rhetoric_directive}"

    else:
        # Default fallback
        return f"{AIZEN_IDENTITY}\nPERSONA: {role}\nTONE: {tone}\n{rhetoric_directive}"

def get_persona_display_name(persona_data: Optional[dict]) -> str:
    """Helper for UI badges."""
    if not persona_data:
        return "None"
    return persona_data.get("name", "Unknown")
