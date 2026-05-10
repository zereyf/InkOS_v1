"""
forge/prompt_assembler.py — Neural Prompt Assembler
===================================================
v1.3: Zenith Data-Binding Patch.
      - FIXED: Variable Reference Leak (Context Collapse).
      - HARDENED: Explicit Compiler Directives for DNA injection.
      - ISOLATED: Mission objective boundary to prevent execution hallucination.
"""
import textwrap
from forge.persona_engine import inject_persona
from state import K

def assemble_master_payload(user_input: str, config: dict, dna_context: dict = None) -> str:
    """
    Synthesizes Identity, Rhetoric, and DNA into a single master compiler instruction.
    """
    # 1. SPECIALIST LAYER (Identity + Rhetoric)
    system_base = inject_persona(
        persona_input = config.get('active_persona'),
        target        = config.get('target_model', 'ChatGPT'),
        hikmah_style  = config.get('hikmah_style', 'None')
    )
    
    # 2. DNA LAYER (Hardened Compiler Directive)
    dna_block = ""
    if dna_context and any(dna_context.values()):
        # 🟢 FIX: We instruct the Refiner explicitly to unpack the literal strings.
        dna_block = textwrap.dedent(f"""
            [ ⚠️ CRITICAL COMPILER DIRECTIVE: BRAND DNA INJECTION ]
            You must embed the exact text values below directly into the generated prompt. 
            DO NOT use abstract placeholders or variable names (like 'INK_SOUL'). 
            Expand these definitions fully into the final output:
            
            - VISUAL_AESTHETIC: {dna_context.get(K.INK_DNA, 'Default Obsidian & Gold')}
            - STRATEGIC_FOCUS: {dna_context.get(K.INTEL_DNA, 'Default AI & Cyber')}
            - PHILOSOPHICAL_BOUNDS: {dna_context.get(K.HIKMAH_DNA, 'Default Academic Arabic')}
        """).strip()

    # 3. ASSEMBLY (Surgical Whitespace Control)
    parts = [system_base]
    if dna_block:
        parts.append(dna_block)
    
    # 🟢 FIX: Renamed the header to explicitly remind the Refiner of its job
    parts.append(f"[ MISSION TO BE PROMPT-ENGINEERED ]\n{user_input}")
    
    return "\n\n".join(parts)
