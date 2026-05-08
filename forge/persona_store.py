"""
forge/persona_store.py — Persona Persistence Layer
====================================================
v5.0: Master Sync — SQL Slot Alignment.
      Synchronized with v18.2 Rehydration and v30.3 Workspace.
      Armored with User Hash isolation for multi-tenant security.
"""

import hashlib
from datetime import datetime, timezone
from typing import Optional, Tuple, List
from vault.supabase_client import sb, SUPABASE_MISSING

TABLE = "personas"

# ── INTERNAL UTILITIES ────────────────────────────────────────────────────────

def _require_sb() -> Optional[str]:
    """Check if the neural uplink to Supabase is active."""
    if SUPABASE_MISSING or sb is None:
        return "Persona store offline: Neural uplink failed."
    return None

# ── PERSISTENCE OPERATIONS ───────────────────────────────────────────────────

def save_persona(
    user_hash:   str,
    name:        str,
    role:        str,
    constraints: str,
    style:       str,
    target:      str,
    tags:        str,
) -> Tuple[Optional[dict], Optional[str]]:
    """🟢 UPDATED: Saves or updates a tactical construct in the SQL armory."""
    if err := _require_sb():
        return None, err

    # 🛡️ DETERMINISTIC ID: Prevents name collisions within the same user space
    seed = f"{user_hash}{name.strip().lower()}"
    record_id = hashlib.md5(seed.encode()).hexdigest()[:16]

    record = {
        "id":          record_id,
        "user_hash":   user_hash,
        "name":        name.strip()[:80],
        "role":        role.strip(),
        "constraints": constraints.strip(),
        "style":       style.strip(),
        "target":      target,
        "tags":        tags.strip().lower(),
        "created_at":  datetime.now(timezone.utc).isoformat(),
    }

    try:
        res = sb.table(TABLE).upsert(record).execute()
        return res.data[0] if res.data else record, None
    except Exception as e:
        return None, f"Forge Persistence Fault: {str(e)}"


def list_personas(
    user_hash:     str,
    target_filter: str = "All",
) -> Tuple[List[dict], Optional[str]]:
    """🟢 UPDATED: Retrieves constructs from the user's specific registry."""
    if err := _require_sb():
        return [], err

    try:
        # 🛰️ BASE QUERY: Isolate by identity first
        q = sb.table(TABLE).select("*").eq("user_hash", user_hash).order("created_at", desc=True)
        
        # 🔗 LOGICAL UNION: Fetch specific target + universal "All" constructs
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
            
            # Deduplicate by ID
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
        return [], f"Neural Registry Read Error: {str(e)}"


def get_persona(
    user_hash:  str,
    persona_id: str,
) -> Tuple[Optional[dict], Optional[str]]:
    """Fetch a single construct from the vault."""
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
        return None, f"Uplink Fault: {str(e)}"


def delete_persona(
    user_hash:  str,
    persona_id: str,
) -> Tuple[bool, Optional[str]]:
    """Erase a construct from the permanent armory."""
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
        return False, f"De-initialization Error: {str(e)}"
