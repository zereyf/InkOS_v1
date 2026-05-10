"""
forge/prompt_assembler.py — Neural Prompt Assembler
===================================================
v1.0: Final assembly logic for multi-layer payloads.
"""

from forge.persona_engine import inject_persona
from forge.rhetoric_engine import get_hikmah_directive

def assemble_master_payload(
    user_input: str,
    config: dict,  # This is the SidebarConfig from sidebar.py
    dna_context: dict = None
) -> str:
    """
    Synthesizes the 3-layer system prompt:
    1. Identity (Persona + Aizen Core)
    2. Rhetoric (Hikmah Profile)
    3. DNA (Athar Sequences)
    """
    
    # 1. Specialist Layer
    system_base = inject_persona(
        persona_input = config.get('active_persona'),
        target        = config.get('target_model', 'ChatGPT'),
        hikmah_style  = config.get('hikmah_style', 'None')
    )
    
    # 2. DNA Layer (If available)
    dna_block = ""
    if dna_context:
        dna_block = f"\n[ DNA_SEQUENCES ]\nINK: {dna_context.get('ink', '')}\nINTEL: {dna_context.get('intel', '')}\nHIKMAH: {dna_context.get('hikmah', '')}\n"

    # 3. Final Synthesis
    # Note: The actual prompt sent to the LLM
    final_payload = f"{system_base}\n{dna_block}\n\n[ USER_OBJECTIVE ]\n{user_input}"
    
    return final_payload
