"""
forge/intelligence.py — Canonical Routing Engine
==================================================
v3.0: Phase 1 consolidation.

  Previously two separate routing implementations existed:
    - engine/router.py          (used by sidebar / diagnostic tools)
    - forge/intelligence.py     (used by workspace pipeline)

  Both consumed TARGET_ROUTING_TABLE and produced a (target, reason) pair
  but with subtly different normalization and score-aggregation logic.
  Any routing fix had to be applied in two places.

  This file is now the single canonical router. engine/router.py is kept
  as a thin re-export shim (see engine/router.py) so existing imports don't
  break without a search-and-replace across the codebase.

  Changes:
    - Arabic normalization from engine/router.py merged in (tashkeel strip,
      alif unification, ya unification).
    - Score aggregation: highest-weight rule per target wins (same as before).
    - explain_routing() forensic helper preserved for the sidebar diagnostics.
    - resolve_target_model() now accepts AUTO_SELECT_LABEL correctly.
"""

import re
from typing import Dict, Any, Tuple
from config.targets import AUTO_SELECT_LABEL, TARGET_ROUTING_TABLE


# ── NORMALISATION ─────────────────────────────────────────────────────────────

def _normalize(text: str) -> str:
    """Strip diacritics and unify variant Arabic characters for resilient matching."""
    text = re.sub(r"[\u064B-\u0652]", "", text)   # Tashkeel
    text = re.sub(r"[أإآ]", "ا", text)              # Alif variants
    text = re.sub(r"ى", "ي", text)                  # Ya variant
    return text.strip().lower()


# ── CORE ROUTING ──────────────────────────────────────────────────────────────

def evaluate_mission_complexity(user_input: str) -> Dict[str, str]:
    """
    Scans TARGET_ROUTING_TABLE to find the highest-scoring model for user_input.
    Returns {"target": str, "reason": str}.
    """
    raw_lower  = user_input.lower()
    norm_lower = _normalize(raw_lower)

    scores:    Dict[str, int] = {}
    rationales: Dict[str, str] = {}
    best_weight: Dict[str, int] = {}

    for rule in TARGET_ROUTING_TABLE:
        target      = rule.get("target")
        if not target:
            continue

        matched = False

        # 1. English regex patterns
        for pat in rule.get("en_patterns", []):
            if re.search(pat, raw_lower):
                matched = True
                break

        # 2. Arabic substring match (normalised)
        if not matched:
            for substr in rule.get("ar_substrings", []):
                if _normalize(substr) in norm_lower:
                    matched = True
                    break

        if matched:
            weight = rule.get("score", 0)
            scores[target] = scores.get(target, 0) + weight
            # Lock rationale to the single highest-weight match per target
            if weight > best_weight.get(target, -1):
                best_weight[target]  = weight
                rationales[target]   = rule.get("rationale", "Pattern matched.")

    if not scores:
        return {
            "target": "ChatGPT",
            "reason": "NEUTRAL_ROUTING: No specific pattern detected. Defaulting to generalist.",
        }

    winner = max(scores, key=scores.get)
    return {
        "target": winner,
        "reason": f"PATTERN_MATCH: {rationales.get(winner, 'Matched.')}",
    }


def resolve_target_model(user_selection: str, user_input: str) -> Tuple[str, str]:
    """
    Returns (target, reason).

    Pass AUTO_SELECT_LABEL for automatic routing.
    Pass any explicit target string for manual override.

    FIX v3.0: The workspace was previously passing the bare string "auto",
    which never matched AUTO_SELECT_LABEL ("✦ AUTO-SELECT"), causing every
    refinement to skip routing and silently default to ChatGPT.
    """
    if user_selection != AUTO_SELECT_LABEL:
        return user_selection, "MANUAL_OVERRIDE: Target locked by user."

    result = evaluate_mission_complexity(user_input)
    return result["target"], result["reason"]


# ── FORENSIC DIAGNOSTICS (used by sidebar and cognitive map) ──────────────────

def route_to_target(user_text: str) -> Tuple[str, str]:
    """Thin wrapper matching the engine/router.py public API."""
    result = evaluate_mission_complexity(user_text)
    return result["target"], result["reason"]


def explain_routing(user_text: str) -> Dict[str, Any]:
    """Forensic breakdown showing which patterns fired and why."""
    if not user_text:
        return {"winner": "ChatGPT", "scores": {}, "signal_breakdown": []}

    raw_lower  = user_text.lower()
    norm_lower = _normalize(raw_lower)
    breakdown  = []

    for rule in TARGET_ROUTING_TABLE:
        triggers = [
            f"EN: {p}" for p in rule.get("en_patterns", [])
            if re.search(p, raw_lower)
        ]
        triggers += [
            f"AR: {s}" for s in rule.get("ar_substrings", [])
            if _normalize(s) in norm_lower
        ]
        if triggers:
            breakdown.append({
                "target":  rule.get("target"),
                "score":   rule.get("score"),
                "matched": triggers,
            })

    winner, _ = route_to_target(user_text)
    return {"winner": winner, "signal_breakdown": breakdown}
