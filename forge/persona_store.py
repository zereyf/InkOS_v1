"""
forge/persona_store.py — Persona Persistence Layer
====================================================
v7.0: Consolidation patch.

Previously this module held its own Supabase query logic that duplicated
vault_engine.py. Two parallel persistence layers meant:
  - Schema changes had to be applied in both places
  - delete_persona had the reversed arg order bug from vault_engine (now fixed)
  - Any future auth or error-handling improvements only applied to one layer

Now: all DB operations delegate to vault_engine. This module is a pure
adapter — it translates between the forge UI's data shape and vault_engine's
function signatures, and provides the list_personas() query that vault_engine
doesn't expose directly.

Public API is unchanged so no callers need updating.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Optional, Tuple, List

from vault.vault_engine import (
    delete_persona,        # re-export — callers import from here
    get_personas,
    save_persona as _ve_save_persona,
)
from vault.supabase_client import supabase, SUPABASE_MISSING

TABLE = "personas"
UTC   = timezone.utc


# ── PUBLIC API ────────────────────────────────────────────────────────────────

def save_persona(
    user_hash:    str,
    name:         str,
    role:         str,
    constraints:  str,
    hikmah_style: str,
    aesthetic:    str,
    target:       str,
    tags:         str,
) -> Tuple[Optional[dict], Optional[str]]:
    """
    Save or upsert a persona. Uses a deterministic ID so the same
    (user_hash, name) pair always maps to the same row — safe to call
    multiple times (idempotent update).
    """
    if SUPABASE_MISSING or supabase is None:
        return None, "Persona store offline: Neural uplink failed."

    seed      = f"{user_hash}{name.strip().lower()}"
    record_id = hashlib.md5(seed.encode()).hexdigest()[:16]

    record = {
        "id":          record_id,
        "user_hash":   user_hash,
        "name":        name.strip()[:80],
        "role":        role.strip(),
        "constraints": constraints.strip(),
        "style":       hikmah_style,
        "aesthetic":   aesthetic,
        "target":      target,
        "tags":        tags.strip().lower(),
        "created_at":  datetime.now(UTC).isoformat(),
    }

    try:
        res = supabase.table(TABLE).upsert(record).execute()
        return (res.data[0] if res.data else record), None
    except Exception as exc:
        return None, f"Forge Persistence Fault: {exc}"


def list_personas(
    user_hash:     str,
    target_filter: str = "All",
) -> Tuple[List[dict], Optional[str]]:
    """
    Retrieve personas for a user, optionally filtered by target.
    Returns both target-specific and universal ("All") constructs.
    """
    if SUPABASE_MISSING or supabase is None:
        return [], "Persona store offline: Neural uplink failed."

    try:
        base = (
            supabase.table(TABLE)
            .select("*")
            .eq("user_hash", user_hash)
            .order("created_at", desc=True)
        )

        if target_filter and target_filter != "All":
            res_specific  = base.eq("target", target_filter).execute()
            res_universal = (
                supabase.table(TABLE)
                .select("*")
                .eq("user_hash", user_hash)
                .eq("target", "All")
                .execute()
            )
            combined = (res_specific.data or []) + (res_universal.data or [])
            seen, deduped = set(), []
            for r in combined:
                if r["id"] not in seen:
                    seen.add(r["id"])
                    deduped.append(r)
            return deduped, None

        res = base.execute()
        return res.data or [], None

    except Exception as exc:
        return [], f"Neural Registry Read Error: {exc}"


def get_persona(
    user_hash: str,
    persona_id: str,
) -> Tuple[Optional[dict], Optional[str]]:
    """Fetch a single persona with ownership check."""
    if SUPABASE_MISSING or supabase is None:
        return None, "Persona store offline: Neural uplink failed."
    try:
        res = (
            supabase.table(TABLE)
            .select("*")
            .eq("id", persona_id)
            .eq("user_hash", user_hash)
            .single()
            .execute()
        )
        return res.data, None
    except Exception as exc:
        return None, f"Uplink Fault: {exc}"


# delete_persona is re-exported from vault_engine — no local wrapper needed.
# Callers that do:  from forge.persona_store import delete_persona
# get the correctly-signed (user_hash, persona_id) function.
__all__ = ["save_persona", "list_personas", "get_persona", "delete_persona"]
