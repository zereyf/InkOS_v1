"""
forge/rhetoric_engine.py — The Hikmah Factory
=============================================
Translates cultural and academic profiles into machine directives.
"""

HIKMAH_PROFILES = {
    "None": "",
    "Academic (Tahqiq)": "Prioritize precision, citation-ready structure, and formal objectivity. Use high-level academic vocabulary.",
    "Classical Adab (Badi')": "Utilize elevated vocabulary, balanced sentence structures, and subtle Saj' (rhymed prose) where appropriate. Maintain a sophisticated literary 'soul'.",
    "Concise Wisdom (I'jaz)": "Focus on extreme brevity. Maximum meaning with minimum tokens. Every word must be weight-bearing.",
    "Technical (Bayan)": "Focus on descriptive clarity. Translate modern tech concepts into formal Arabic without losing functional accuracy."
}

def get_hikmah_directive(style_key: str) -> str:
    """Returns the formatted system directive for a given profile."""
    directive = HIKMAH_PROFILES.get(style_key, "")
    if directive:
        return textwrap.dedent(f"""
            [ RHETORIC_PROTOCOL: {style_key.upper()} ]
            - INSTRUCTION: {directive}
            - CONSTRAINT: Ensure technical terminology remains accurate during stylistic shifts.
        """).strip()
    return ""

import textwrap
