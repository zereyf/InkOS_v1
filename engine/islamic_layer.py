"""
engine/islamic_layer.py — Islamic Professional Context Layer
=============================================================
Isolated as its own module because it is an independently toggleable
domain layer — not part of the core cognitive map engine.

Future extensions belong here:
  - FIQH_LAYER: Usul al-Fiqh reasoning constraints
  - ARABIC_SCHOLARLY_LAYER: Classical citation format rules
  - HALAL_FINANCE_LAYER: Specific sukuk / murabaha terminology
"""

ISLAMIC_CONTEXT_LAYER: str = """
Domain Context: Islamic Professional Standards
- Apply Sharia-compliant framing where financial or legal concepts appear.
- Use Arabic scholarly citation conventions when referencing sources (author, work, volume, page).
- Flag any output that may conflict with foundational Islamic ethical principles.
- Prefer Arabic technical terminology where it carries more precision than English equivalents.
- Acknowledge Riba (ربا) prohibition constraint by default in all economic contexts.
- Distinguish between فقه (jurisprudence) and فتوى (legal opinion) when relevant.
"""