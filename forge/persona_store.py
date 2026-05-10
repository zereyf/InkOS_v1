"""
forge/persona_store.py — Persona Persistence Layer
====================================================
v6.0: Zenith Edition — Rhetoric Alignment.
      - REFACTORED: save_persona signature to include hikmah_style and aesthetic.
      - UPDATED: Record mapping to match v15.0 Sidebar config.
      - RETAINED: Deterministic MD5 hashing and User Hash isolation.
"""

import hashlib
from datetime import datetime, timezone
from typing import Optional, Tuple, List
from vault.supabase_client import supabase, SUPABASE_MISSING

TABLE = "personas"

# ── INTERNAL UTILITIES ────────────────────────────────────────────────────────

def _require_sb() -> Optional[str]:
    """Check if the neural uplink to Supabase is active."""
    if SUPABASE_MISSING or supabase is None:
        return "Persona store offline: Neural uplink failed."
    return None

# ── PERSISTENCE OPERATIONS ───────────────────────────────────────────────────

def save_persona(
    user_hash:    str,
    name:         str,
    role:         str,
    constraints:  str,
    hikmah_style: str,  # 🟢 NEW: Rhetorical Profile (mapped to 'style')
    aesthetic:    str,  # 🟢 NEW: Visual Identity
    target:       str,
    tags:         str,
) -> Tuple[Optional[dict], Optional[str]]:
    """🟢 v6.0: Saves/Updates a tactical construct with full Rhetorical DNA."""
    if err := _require_sb():
        return None, err

    # 🛡️ DETERMINISTIC ID: user_hash + name ensures unique records per user
    seed = f"{user_hash}{name.strip().lower()}"
    record_id = hashlib.md5(seed.encode()).hexdigest()[:16]

    record = {
        "id":           record_id,
        "user_hash":    user_hash,
        "name":         name.strip()[:80],
        "role":         role.strip(),
        "constraints":  constraints.strip(),
        "style":        hikmah_style, # 🟢 Behavioral Logic
        "aesthetic":    aesthetic,    # 🟢 Visual Identity
        "target":       target,
        "tags":         tags.strip().lower(),
        "created_at":   datetime.now(timezone.utc).isoformat(),
    }

    try:
        # Perform Upsert: Insert if new, Update if ID exists
        res = supabase.table(TABLE).upsert(record).execute()
        return res.data[0] if res.data else record, None
    except Exception as e:
        return None, f"Forge Persistence Fault: {str(e)}"


def list_personas(
    user_hash:     str,
    target_filter: str = "All",
) -> Tuple[List[dict], Optional[str]]:
    """Retrieves constructs isolated by user_hash and filtered by target."""
    if err := _require_sb():
        return [], err

    try:
        # Base query: Order by newest first
        q = supabase.table(TABLE).select("*").eq("user_hash", user_hash).order("created_at", desc=True)
        
        if target_filter and target_filter != "All":
            # Fetch target-specific AND universal constructs
            res_specific = q.eq("target", target_filter).execute()
            res_universal = (
                supabase.table(TABLE)
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


def get_persona(user_hash: str, persona_id: str) -> Tuple[Optional[dict], Optional[str]]:
    """Fetch a single construct from the vault."""
    if err := _require_sb():
        return None, err
    try:
        res = supabase.table(TABLE).select("*").eq("id", persona_id).eq("user_hash", user_hash).single().execute()
        return res.data, None
    except Exception as e:
        return None, f"Uplink Fault: {str(e)}"


def delete_persona(user_hash: str, persona_id: str) -> Tuple[bool, Optional[str]]:
    """Erase a construct from the permanent armory."""
    if err := _require_sb():
        return False, err
    try:
        supabase.table(TABLE).delete().eq("id", persona_id).eq("user_hash", user_hash).execute()
        return True, None
    except Exception as e:
        return False, f"De-initialization Error: {str(e)}"
