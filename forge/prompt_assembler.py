"""
forge/prompt_assembler.py — Neural Prompt Assembler
=====================================================
Phase 3 Architecture Upgrade:

  ARC-2: DnaContext TypedDict introduced.
         Previously the assembler received a raw dict keyed by internal
         K-class string constants (e.g. K.INK_DNA = "ink_dna"), which
         coupled the assembler directly to the session-state layer.
         Now callers pass a typed DnaContext object. The workspace
         constructs it explicitly, keeping the boundary clean.

         Backward-compatible: if a plain dict is passed it is coerced
         via DnaContext.from_dict() so existing callers don't break.

  ARC-3: Token budget guard.
         The assembled payload is now measured before it reaches the LLM.
         Groq context window for llama-3.3-70b is 128k tokens. We use a
         conservative 12 000-char (~3 000 token) soft warning threshold
         and a hard 48 000-char (~12 000 token) truncation limit on the
         user input portion only — the system layers are never truncated.
"""

from __future__ import annotations

import textwrap
from typing import Optional, TypedDict

from forge.persona_engine import inject_persona
from config.prompts import CIPHER_IDENTITY
from config.target_formats import get_format_contract

# ── SOFT / HARD LIMITS ────────────────────────────────────────────────────────
# These are character counts, not token counts.
# llama-3.3-70b context: ~128k tokens ≈ 512 000 chars.
# We set conservative limits to keep room for the full system layers.
_PAYLOAD_SOFT_WARN  = 12_000   # chars — emit a warning to logs
_USER_INPUT_HARD_CAP = 48_000  # chars — truncate user input if exceeded


# ── TYPED DNA INTERFACE ───────────────────────────────────────────────────────

class DnaContext(TypedDict):
    """
    Typed interface for Brand DNA passed into the prompt assembler.
    Replaces the raw dict keyed by K-class string constants.
    """
    ink:    str   # Visual aesthetic DNA
    intel:  str   # Strategic / analytical DNA
    hikmah: str   # Philosophical / rhetorical DNA


def make_dna_context(
    ink:    str = "",
    intel:  str = "",
    hikmah: str = "",
) -> DnaContext:
    """Convenience constructor with safe string coercion."""
    return DnaContext(
        ink    = str(ink    or "").strip(),
        intel  = str(intel  or "").strip(),
        hikmah = str(hikmah or "").strip(),
    )


def _dna_from_legacy(raw: dict) -> DnaContext:
    """
    Coerce the old K-keyed dict format to DnaContext.
    Handles both the old format {K.INK_DNA: ...} and the new {ink: ...}.
    """
    # Try new-style keys first
    if "ink" in raw or "intel" in raw or "hikmah" in raw:
        return make_dna_context(
            ink    = raw.get("ink",    ""),
            intel  = raw.get("intel",  ""),
            hikmah = raw.get("hikmah", ""),
        )
    # Legacy K-key style: {"ink_dna": ..., "intel_dna": ..., "hikmah_dna": ...}
    return make_dna_context(
        ink    = raw.get("ink_dna",    ""),
        intel  = raw.get("intel_dna",  ""),
        hikmah = raw.get("hikmah_dna", ""),
    )


# ── ASSEMBLY ──────────────────────────────────────────────────────────────────

def assemble_master_payload(
    user_input: str,
    config:     dict,
    dna:        Optional[DnaContext | dict] = None,
) -> str:
    """
    Synthesise Identity, Rhetoric, DNA, and user intent into a single
    master compiler instruction for the CIPHER refiner.

    Args:
        user_input: Raw user prompt + control block.
        config:     SidebarConfig dict (target_model, hikmah_style, etc.).
        dna:        DnaContext (preferred) or legacy K-keyed dict (coerced).
    """

    # ── ARC-2: normalise DNA input ────────────────────────────────────────
    if dna is None:
        dna_ctx = make_dna_context()
    elif isinstance(dna, dict):
        dna_ctx = _dna_from_legacy(dna)
    else:
        dna_ctx = dna   # already a DnaContext

    # ── ARC-3: token budget guard on user input ───────────────────────────
    user_input_len = len(user_input)
    if user_input_len > _USER_INPUT_HARD_CAP:
        # Truncate only the user portion — system layers are never cut
        user_input = user_input[:_USER_INPUT_HARD_CAP]
        user_input += (
            "\n\n[SYSTEM NOTE: Input truncated at the token budget limit. "
            "The most recent content may be missing. Ask the user to shorten their input.]"
        )

    # ── Specialist layer (Identity + Rhetoric) ────────────────────────────
    system_base = inject_persona(
        persona_input = config.get("active_persona"),
        target        = config.get("target_model", "ChatGPT"),
        hikmah_style  = config.get("hikmah_style", "None"),
    )

    # ── DNA layer ─────────────────────────────────────────────────────────
    dna_block = ""
    has_dna   = any([dna_ctx["ink"], dna_ctx["intel"], dna_ctx["hikmah"]])

    if has_dna:
        dna_block = textwrap.dedent(f"""
            [ ⚠ CRITICAL COMPILER DIRECTIVE: BRAND DNA INJECTION ]
            Embed the following values directly into the generated prompt.
            Do NOT use abstract placeholders. Expand them fully:

            - VISUAL_AESTHETIC:      {dna_ctx['ink']   or 'Default Obsidian & Gold'}
            - STRATEGIC_FOCUS:       {dna_ctx['intel'] or 'Default AI & Cyber'}
            - PHILOSOPHICAL_BOUNDS:  {dna_ctx['hikmah']or 'Default Academic Arabic'}
        """).strip()

    # ── Target format contract ───────────────────────────────────────────
    # Injected before generation so CIPHER knows the correct structure
    # for the specific target model — fixes "You are..." for non-ChatGPT.
    target_model    = config.get("target_model", "")
    format_contract = get_format_contract(str(target_model or ""))

    # ── Assemble ──────────────────────────────────────────────────────────
    parts = [CIPHER_IDENTITY, "[PERSONA_AND_POLICY_LAYER]", system_base]
    if format_contract:
        parts.append(format_contract)
    if dna_block:
        parts.append(dna_block)
    parts.append(f"[MISSION_PAYLOAD]\n{user_input}")

    payload = "\n\n".join(parts)

    # ARC-3: soft-warn if the full assembled payload is very large
    if len(payload) > _PAYLOAD_SOFT_WARN:
        import sys
        print(
            f"[InkOS WARNING] Assembled payload is {len(payload):,} chars "
            f"(>{_PAYLOAD_SOFT_WARN:,} soft limit). "
            "Consider trimming DNA sequences or user input.",
            file=sys.stderr,
        )

    return payload
