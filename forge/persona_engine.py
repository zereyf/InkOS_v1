"""
forge/persona_engine.py — Persona Logic Controller
====================================================
v9.2: Logic/Data Separation Build.
      - Transforms static assets from config/personas.py.
      - Handles operational target-specific injection.
"""

from typing import Optional
import textwrap
# 🟢 Importing the Data from the Vault we just sync'd
from config.personas import AIZEN_IDENTITY, STARTER_PERSONAS

def inject_persona(persona_name: Optional[str], target: str) -> str:
    """
    The main engine for prompt transformation.
    Takes a selection and converts it into a high-pressure instruction block.
    """
    # 1. Fallback to AIZEN Core if no persona is selected
    if not persona_name or persona_name not in STARTER_PERSONAS:
        return AIZEN_IDENTITY

    p_data = STARTER_PERSONAS[persona_name]
    if p_data is None: 
        return AIZEN_IDENTITY
    
    # 2. Extract specific expert traits
    name = p_data.get("name", "Expert")
    role = p_data.get("role", "")
    anti = p_data.get("anti_pattern", "Avoid generic responses.")
    tone = p_data.get("tone", "Professional and analytical.")

    # 3. Target-Specific Assembly Matrix
    if target == "Claude":
        # Claude responds best to nested XML for instruction weighting
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
        # GPT-4o prefers direct "SYSTEM OVERRIDE" and bulleted lists
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
        # Default fallback for Image Models (Midjourney/Flux)
        return f"{AIZEN_IDENTITY}\nPERSONA: {role} | TONE: {tone}"

def get_persona_display_name(persona_data: Optional[dict]) -> str:
    """
    Helper for UI badges. 
    Note: This expects a dict because it's often called on session_state[K.ACTIVE_PERSONA]
    """
    if not persona_data:
        return "None"
    return persona_data.get("name", "Unknown")
