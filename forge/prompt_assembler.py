"""
forge/prompt_assembler.py — Neural Prompt Assembler
=====================================================
v3.0: Modular loading, pattern injection, Arabic enrichment.
"""

from __future__ import annotations

import textwrap
from typing import Optional, TypedDict

import streamlit as st

from forge.persona_engine import inject_persona
from config.prompts import (
    CIPHER_IDENTITY,
    CIPHER_CORE,
    CIPHER_TEXT_STANDARDS,
    CIPHER_VISUAL,
    CIPHER_INTENT_ANALYSIS,
    CIPHER_CONTRADICTION_GUARD,
    CIPHER_OUTPUT_CONTRACT,
)
from engine.islamic_layer import ISLAMIC_CONTEXT_LAYER
from engine.cognitive_map import detect_arabic_pattern, get_full_cipher_block

_PAYLOAD_SOFT_WARN   = 12_000
_USER_INPUT_HARD_CAP = 48_000

_VISUAL_TARGET_NAMES: frozenset = frozenset({
    "Midjourney", "FLUX", "DALL-E", "Stable Diffusion",
    "Midjourney/Flux", "midjourney", "flux", "dall-e", "stable diffusion",
})


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
        return make_dna_context(ink=raw.get("ink",""), intel=raw.get("intel",""), hikmah=raw.get("hikmah",""))
    return make_dna_context(ink=raw.get("ink_dna",""), intel=raw.get("intel_dna",""), hikmah=raw.get("hikmah_dna",""))


def _is_visual_target(target: str, user_input: str = "") -> bool:
    if not target:
        return False
    t = target.lower().strip()
    if any(v.lower() in t for v in _VISUAL_TARGET_NAMES):
        return True
    visual_signals = {"image", "photo", "draw", "illustrat", "anime", "render",
                      "visual", "portrait", "wallpaper", "concept art"}
    return any(s in user_input.lower() for s in visual_signals)


def _select_cipher_module(target: str, user_input: str) -> str:
    if not target:
        return CIPHER_IDENTITY
    if _is_visual_target(target, user_input):
        return f"{CIPHER_CORE}\n\n{CIPHER_VISUAL}"
    return f"{CIPHER_CORE}\n\n{CIPHER_TEXT_STANDARDS}"


def _get_pattern_injection(target: str) -> str:
    try:
        from state import get_best_pattern_for_target
        pattern = get_best_pattern_for_target(target)
        if not pattern or pattern.get("score", 0) < 85:
            return ""
        score     = pattern["score"]
        key_inst  = pattern.get("key_instruction", "")[:400]
        framework = pattern.get("framework", "")
        if not key_inst:
            return ""
        return textwrap.dedent(f"""
            [ HIGH_PERFORMANCE_REFERENCE | {target} | SCORE: {score} | FRAMEWORK: {framework} ]
            A previous compilation for this target scored {score}/100.
            Key instruction that drove quality:
            {key_inst}
            Use as a reference signal — adapt, don't copy.
            [ END REFERENCE ]
        """).strip()
    except Exception:
        return ""


def _get_arabic_enrichment(user_input: str) -> str:
    try:
        detected = detect_arabic_pattern(user_input)
        if not detected:
            return ""
        return get_full_cipher_block(detected)
    except Exception:
        return ""


def assemble_master_payload(
    user_input: str,
    config:     dict,
    dna:        Optional[DnaContext | dict] = None,
) -> str:

    if dna is None:
        dna_ctx = make_dna_context()
    elif isinstance(dna, dict):
        dna_ctx = _dna_from_legacy(dna)
    else:
        dna_ctx = dna

    if len(user_input) > _USER_INPUT_HARD_CAP:
        user_input = user_input[:_USER_INPUT_HARD_CAP] + (
            "\n\n[SYSTEM NOTE: Input truncated at the token budget limit.]"
        )

    target_model = str(config.get("target_model", "") or "")

    cipher_module      = _select_cipher_module(target_model, user_input)
    intelligence_block = f"{CIPHER_INTENT_ANALYSIS}\n\n{CIPHER_CONTRADICTION_GUARD}"

    system_base = inject_persona(
        persona_input = config.get("active_persona"),
        target        = target_model,
        hikmah_style  = config.get("hikmah_style", "None"),
    )

    pattern_block = _get_pattern_injection(target_model)
    arabic_block  = _get_arabic_enrichment(user_input)

    dna_block = ""
    if any([dna_ctx["ink"], dna_ctx["intel"], dna_ctx["hikmah"]]):
        dna_block = textwrap.dedent(f"""
            [ CRITICAL COMPILER DIRECTIVE: BRAND DNA INJECTION ]
            Embed the following values directly. Do NOT use placeholders:
            - VISUAL_AESTHETIC:      {dna_ctx['ink']    or 'Default Obsidian & Gold'}
            - STRATEGIC_FOCUS:       {dna_ctx['intel']  or 'Default AI & Cyber'}
            - PHILOSOPHICAL_BOUNDS:  {dna_ctx['hikmah'] or 'Default Academic Arabic'}
        """).strip()

    islamic_block = ""
    try:
        if st.session_state.get("sb_islamic", False):
            islamic_block = textwrap.dedent(f"""
                [ ACTIVE COMPLIANCE PROTOCOL: ISLAMIC ETHICAL LAYER ]
                MANDATORY for this refinement. Apply to every output decision:
                {ISLAMIC_CONTEXT_LAYER}
            """).strip()
    except Exception:
        pass

    from config.target_formats import get_format_contract
    format_contract = get_format_contract(target_model)

    parts = [cipher_module, intelligence_block, "[PERSONA_AND_POLICY_LAYER]", system_base]
    if format_contract:
        parts.append(format_contract)
    if pattern_block:
        parts.append(pattern_block)
    if arabic_block:
        parts.append(arabic_block)
    if dna_block:
        parts.append(dna_block)
    if islamic_block:
        parts.append(islamic_block)
    parts.append(f"[MISSION_PAYLOAD]\n{user_input}")

    payload = "\n\n".join(parts)

    if len(payload) > _PAYLOAD_SOFT_WARN:
        import sys
        print(f"[InkOS WARNING] Payload is {len(payload):,} chars.", file=sys.stderr)

    return payload
