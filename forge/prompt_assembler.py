"""
forge/prompt_assembler.py — Neural Prompt Assembler
=====================================================
v2.0: Islamic Layer Integration Fix.

"""

from __future__ import annotations

import textwrap
from typing import Optional, TypedDict

import streamlit as st

from forge.persona_engine import inject_persona
from config.prompts import CIPHER_IDENTITY
from config.target_formats import get_format_contract
from engine.islamic_layer import ISLAMIC_CONTEXT_LAYER

_PAYLOAD_SOFT_WARN   = 12_000
_USER_INPUT_HARD_CAP = 48_000


class DnaContext(TypedDict):
    ink:    str
    intel:  str
    hikmah: str


def make_dna_context(ink: str = "", intel: str = "", hikmah: str = "") -> DnaContext:
    return DnaContext(
        ink    = str(ink    or "").strip(),
        intel  = str(intel  or "").strip(),
        hikmah = str(hikmah or "").strip(),
    )


def _dna_from_legacy(raw: dict) -> DnaContext:
    if "ink" in raw or "intel" in raw or "hikmah" in raw:
        return make_dna_context(
            ink    = raw.get("ink",    ""),
            intel  = raw.get("intel",  ""),
            hikmah = raw.get("hikmah", ""),
        )
    return make_dna_context(
        ink    = raw.get("ink_dna",    ""),
        intel  = raw.get("intel_dna",  ""),
        hikmah = raw.get("hikmah_dna", ""),
    )


def assemble_master_payload(
    user_input: str,
    config:     dict,
    dna:        Optional[DnaContext | dict] = None,
) -> str:
    """
    Synthesise Identity, Rhetoric, DNA, Islamic layer, and user intent
    into a single master compiler instruction for CIPHER.
    """

    if dna is None:
        dna_ctx = make_dna_context()
    elif isinstance(dna, dict):
        dna_ctx = _dna_from_legacy(dna)
    else:
        dna_ctx = dna

    if len(user_input) > _USER_INPUT_HARD_CAP:
        user_input = user_input[:_USER_INPUT_HARD_CAP]
        user_input += (
            "\n\n[SYSTEM NOTE: Input truncated at the token budget limit. "
            "Ask the user to shorten their input.]"
        )

    system_base = inject_persona(
        persona_input = config.get("active_persona"),
        target        = config.get("target_model", "ChatGPT"),
        hikmah_style  = config.get("hikmah_style", "None"),
    )

    dna_block = ""
    if any([dna_ctx["ink"], dna_ctx["intel"], dna_ctx["hikmah"]]):
        dna_block = textwrap.dedent(f"""
            [ CRITICAL COMPILER DIRECTIVE: BRAND DNA INJECTION ]
            Embed the following values directly. Do NOT use placeholders:

            - VISUAL_AESTHETIC:      {dna_ctx['ink']   or 'Default Obsidian & Gold'}
            - STRATEGIC_FOCUS:       {dna_ctx['intel'] or 'Default AI & Cyber'}
            - PHILOSOPHICAL_BOUNDS:  {dna_ctx['hikmah']or 'Default Academic Arabic'}
        """).strip()

    # ── BUG FIX: Islamic layer was never injected ─────────────────────────────
    # cognitive_map.py toggle sets "sb_islamic" but this was never read.
    # Now reads the flag and injects the compliance layer when active.
    islamic_block = ""
    try:
        if st.session_state.get("sb_islamic", False):
            islamic_block = textwrap.dedent(f"""
                [ ACTIVE COMPLIANCE PROTOCOL: ISLAMIC ETHICAL LAYER ]
                MANDATORY for this refinement. Apply to every output decision:

                {ISLAMIC_CONTEXT_LAYER}
            """).strip()
    except Exception:
        pass  # safe outside Streamlit context (tests)

    target_model    = config.get("target_model", "")
    format_contract = get_format_contract(str(target_model or ""))

    parts = [CIPHER_IDENTITY, "[PERSONA_AND_POLICY_LAYER]", system_base]
    if format_contract:
        parts.append(format_contract)
    if dna_block:
        parts.append(dna_block)
    if islamic_block:
        parts.append(islamic_block)
    parts.append(f"[MISSION_PAYLOAD]\n{user_input}")

    payload = "\n\n".join(parts)

    if len(payload) > _PAYLOAD_SOFT_WARN:
        import sys
        print(
            f"[InkOS WARNING] Payload is {len(payload):,} chars "
            f"(>{_PAYLOAD_SOFT_WARN:,} soft limit).",
            file=sys.stderr,
        )

    return payload
