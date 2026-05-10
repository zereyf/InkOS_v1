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
"""
forge/prompt_assembler.py — Neural Prompt Assembler
===================================================
v1.2: Integrity Patch.
      - FIXED: Added missing textwrap import.
      - FIXED: Cleaned whitespace for null DNA blocks.
"""
import textwrap # 🟢 RESTORED
from forge.persona_engine import inject_persona
from state import K

def assemble_master_payload(user_input: str, config: dict, dna_context: dict = None) -> str:
    # 1. SPECIALIST LAYER
    system_base = inject_persona(
        persona_input = config.get('active_persona'),
        target        = config.get('target_model', 'ChatGPT'),
        hikmah_style  = config.get('hikmah_style', 'None')
    )
    
    # 2. DNA LAYER
    dna_block = ""
    if dna_context:
        # Check if we actually have data before dedenting
        if any(dna_context.values()):
            dna_block = textwrap.dedent(f"""
                [ BRAND_DNA_SEQUENCES ]
                INK_SOUL: {dna_context.get(K.INK_DNA, '')}
                INTEL_CORE: {dna_context.get(K.INTEL_DNA, '')}
                HIKMAH_BOUNDS: {dna_context.get(K.HIKMAH_DNA, '')}
            """).strip()

    # 3. ASSEMBLY (Surgical Whitespace Control)
    parts = [system_base]
    if dna_block:
        parts.append(dna_block)
    
    parts.append(f"[ MISSION_OBJECTIVE ]\n{user_input}")
    
    return "\n\n".join(parts)
