"""
engine/router.py — Compatibility shim
=======================================
v5.0: Phase 1 consolidation.

All routing logic now lives in forge/intelligence.py (the canonical router).
This module re-exports the public API so existing imports in the codebase
(sidebar.py, cognitive_map.py, diagnostic tools) continue to work without
a search-and-replace.

Do not add logic here. Edit forge/intelligence.py instead.
"""

from forge.intelligence import (   # noqa: F401  (re-export)
    evaluate_mission_complexity,
    resolve_target_model,
    route_to_target,
    explain_routing,
)
