"""
forge/prompt_assembler.py — Neural Prompt Assembler
===================================================
v1.0: Final assembly logic for 3-layer composite payloads.
"""
from forge.persona_engine import inject_persona
from forge.rhetoric_engine import get_hikmah_directive

def assemble_master_payload(user_input: str, config: dict, dna_context: dict = None) -> str:
    """
    Synthesizes Identity, Rhetoric, and DNA into a single system instruction.
    """
    # 1. Specialist Layer (Persona + Aizen Identity)
    system_base = inject_persona(
        persona_input = config.get('active_persona'),
        target        = config.get('target_model', 'ChatGPT'),
        hikmah_style  = config.get('hikmah_style', 'None')
    )
    
    # 2. DNA Layer (Brand Sovereignty)
    dna_block = ""
    if dna_context:
        dna_block = (
            f"\n[ BRAND_DNA_SEQUENCES ]\n"
            f"INK_SOUL: {dna_context.get('ink', '')}\n"
            f"INTEL_CORE: {dna_context.get('intel', '')}\n"
            f"HIKMAH_BOUNDS: {dna_context.get('hikmah', '')}\n"
        )

    # 3. Final Neural Weaving
    return f"{system_base}\n{dna_block}\n\n[ MISSION_OBJECTIVE ]\n{user_input}"
