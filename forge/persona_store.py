"""
forge/persona_store.py — Persona Persistence Layer
====================================================
"""

import hashlib
from datetime import datetime
from typing import Optional, Tuple, List
from vault.supabase_client import sb, SUPABASE_MISSING

TABLE = "personas"


def _require_sb() -> Optional[str]:
    """Check if Supabase is connected."""
    if SUPABASE_MISSING or sb is None:
        return "Persona store unavailable — Supabase not configured."
    return None


def save_persona(
    user_hash:   str,
    name:        str,
    role:        str,
    constraints: str,
    style:       str,
    target:      str,
    tags:        str,
) -> Tuple[Optional[dict], Optional[str]]:
    """Save or update a persona."""
    if err := _require_sb():
        return None, err

    record_id = hashlib.md5(f"{user_hash}{name.strip().lower()}".encode()).hexdigest()[:16]

    record = {
        "id":          record_id,
        "user_hash":   user_hash,
        "name":        name.strip()[:80],
        "role":        role.strip(),
        "constraints": constraints.strip(),
        "style":       style.strip(),
        "target":      target,
        "tags":        tags.strip().lower(),
        "created_at":  datetime.utcnow().isoformat(),
    }

    try:
        res = sb.table(TABLE).upsert(record).execute()
        return res.data[0] if res.data else record, None
    except Exception as e:
        return None, f"Save failed: {str(e)}"


def list_personas(
    user_hash:     str,
    target_filter: str = "All",
) -> Tuple[List[dict], Optional[str]]:
    """List all personas for a user."""
    if err := _require_sb():
        return [], err

    try:
        q = (
            sb.table(TABLE)
            .select("*")
            .eq("user_hash", user_hash)
            .order("created_at", desc=True)
        )
        if target_filter and target_filter != "All":
            res_specific = q.eq("target", target_filter).execute()
            res_universal = (
                sb.table(TABLE)
                .select("*")
                .eq("user_hash", user_hash)
                .eq("target", "All")
                .execute()
            )
            combined = (res_specific.data or []) + (res_universal.data or [])
            seen = set()
            results = []
            for r in combined:
                if r["id"] not in seen:
                    seen.add(r["id"])
                    results.append(r)
            return results, None

        res = q.execute()
        return res.data or [], None

    except Exception as e:
        return [], f"List failed: {str(e)}"


def get_persona(
    user_hash:  str,
    persona_id: str,
) -> Tuple[Optional[dict], Optional[str]]:
    """Fetch a single persona."""
    if err := _require_sb():
        return None, err
    try:
        res = (
            sb.table(TABLE)
            .select("*")
            .eq("id", persona_id)
            .eq("user_hash", user_hash)
            .single()
            .execute()
        )
        return res.data, None
    except Exception as e:
        return None, f"Fetch failed: {str(e)}"


def delete_persona(
    user_hash:  str,
    persona_id: str,
) -> Tuple[bool, Optional[str]]:
    """Delete a persona."""
    if err := _require_sb():
        return False, err
    try:
        sb.table(TABLE)\
            .delete()\
            .eq("id", persona_id)\
            .eq("user_hash", user_hash)\
            .execute()
        return True, None
    except Exception as e:
        return False, f"Delete failed: {str(e)}"
