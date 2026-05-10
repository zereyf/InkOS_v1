"""
forge/rhetoric_engine.py — The Hikmah Factory
=============================================
v1.0: Translates Arabic rhetoric (Balaghah) into machine directives.
"""
import textwrap

HIKMAH_PROFILES = {
    "None": "",
    "Academic (Tahqiq)": "Prioritize precision, citation-ready structure, and formal objectivity. Use high-level academic vocabulary (Nahw/Sarf alignment).",
    "Classical Adab (Badi')": "Utilize elevated vocabulary, balanced sentence structures, and subtle Saj' (rhymed prose). Maintain a sophisticated literary 'soul'.",
    "Concise Wisdom (I'jaz)": "Focus on extreme brevity. Maximum meaning with minimum tokens. Every word must be weight-bearing and essential.",
    "Technical (Bayan)": "Focus on descriptive clarity. Translate modern tech concepts into formal Arabic without losing functional or technical accuracy."
}

def get_hikmah_directive(style_key: str) -> str:
    """Returns the formatted system directive for a given profile."""
    directive = HIKMAH_PROFILES.get(style_key, "")
    if directive:
        return textwrap.dedent(f"""
            [ RHETORIC_PROTOCOL: {style_key.upper()} ]
            - INSTRUCTION: {directive}
            - CONSTRAINT: Ensure technical terminology remains accurate during stylistic shifts.
            - OUTPUT_LANGUAGE: Must adhere to formal Modern Standard Arabic (Fusha) standards.
        """).strip()
    return ""
