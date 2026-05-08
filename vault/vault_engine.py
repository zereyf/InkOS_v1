"""
vault/vault_engine.py — Prompt Memory Vault Engine
====================================================
v18.2: Master Sync — Identity Rehydration Edition.
       Integrated rehydrate_session to support persistent 
       identity across page refreshes (Zero-Cost Persistence).
"""

import hashlib
from datetime import datetime, timezone
from typing import Optional, Tuple, List
from vault.supabase_client import sb, SUPABASE_MISSING

TABLE_VAULT = "vault"
TABLE_USERS = "users"
TABLE_PERSONAS = "personas" # 🟢 Standardized table name

# ── INTERNAL UTILITIES ────────────────────────────────────────────────────────

def _require_sb() -> Optional[str]:
    if SUPABASE_MISSING or sb is None:
        return "Vault offline: SUPABASE_URL/KEY missing."
    return None

def _hash_pin(pin: str) -> str:
    return hashlib.sha256(pin.encode()).hexdigest()

# ── IDENTITY & AUTHENTICATION ────────────────────────────────────────────────

def check_id_availability(user_hash: str) -> Tuple[bool, str]:
    if not user_hash.strip(): return False, "ID cannot be empty."
    if user_hash.upper().startswith("GUEST_"): return False, "Prefix Reserved."
    if err := _require_sb(): return False, err

    try:
        res = sb.table(TABLE_USERS).select("id").eq("id", user_hash.strip()).execute()
        return (len(res.data) == 0, f"ID '{user_hash}' is {'available' if len(res.data)==0 else 'taken'}.")
    except Exception as e:
        return False, f"Check failed: {str(e)}"

def authenticate_terminal(user_hash: str, pin: str, is_new: bool) -> Tuple[bool, Optional[str]]:
    if err := _require_sb(): return False, err
    clean_id, hashed_pin = user_hash.strip(), _hash_pin(pin)

    if is_new and clean_id.upper().startswith("GUEST_"):
        return False, "Registration Blocked: Reserved Prefix."

    try:
        res = sb.table(TABLE_USERS).select("*").eq("id", clean_id).execute()
        user_exists = len(res.data) > 0

        if is_new:
            if user_exists: return False, "ID exists. Switch to Login."
            sb.table(TABLE_USERS).insert({
                "id": clean_id, 
                "pin_hash": hashed_pin, 
                "created_at": datetime.now(timezone.utc).isoformat()
            }).execute()
            return True, None
        
        if not user_exists: return False, "ID not found."
        return (res.data[0]["pin_hash"] == hashed_pin, "Invalid PIN" if res.data[0]["pin_hash"] != hashed_pin else None)

    except Exception as e:
        return False, f"Auth Error: {str(e)}"

# ── REHYDRATION PROTOCOL (Zero-Cost Persistence) ─────────────────────────────

def rehydrate_session(user_hash: str) -> dict:
    """
    🟢 NEW: Recovers the entire terminal state from Supabase to survive refreshes.
    Returns: {personas: [], dna: {ink, intel, hikmah}}
    """
    state = {
        "personas": [],
        "dna": {"ink": "", "intel": "", "hikmah": ""}
    }
    
    if err := _require_sb() or not user_hash: return state

    try:
        # 1. Recover Personas
        p_res = sb.table(TABLE_PERSONAS).select("*").eq("user_hash", user_hash).execute()
        state["personas"] = p_res.data or []
        
        # 2. Recover DNA Strings from User Profile
        u_res = sb.table(TABLE_USERS).select("ink_dna, intel_dna, hikmah_dna").eq("id", user_hash).execute()
        if u_res.data:
            profile = u_res.data[0]
            state["dna"] = {
                "ink": profile.get("ink_dna", ""),
                "intel": profile.get("intel_dna", ""),
                "hikmah": profile.get("hikmah_dna", "")
            }
        return state
    except Exception:
        return state

# ── VAULT OPERATIONS ────────────────────────────────────────────────────────

def save_prompt(user_hash: str, **data) -> Tuple[Optional[dict], Optional[str]]:
    if err := _require_sb(): return None, err

    seed = f"{user_hash}{data.get('content')}{data.get('title')}{data.get('target')}"
    record_id = hashlib.md5(seed.encode()).hexdigest()[:16]

    record = {
        "id": record_id,
        "user_hash": user_hash,
        "title": str(data.get("title", "Untitled")).strip()[:120],
        "tags": str(data.get("tags", "")).strip().lower(),
        "content": data.get("content", ""),
        "target": data.get("target", "Claude"),
        "framework": data.get("framework", "Professional"),
        "score": min(max(int(data.get("score", 0)), 0), 100),
        "pattern": data.get("pattern", ""),
        "islamic": data.get("islamic", False),
        "aesthetic": data.get("aesthetic", ""),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        res = sb.table(TABLE_VAULT).upsert(record).execute()
        return res.data[0] if res.data else record, None
    except Exception as e:
        return None, f"Save failed: {str(e)}"

def search_vault(user_hash: str, **filters) -> Tuple[List[dict], Optional[str]]:
    if err := _require_sb(): return [], err
    try:
        q = sb.table(TABLE_VAULT).select("*").eq("user_hash", user_hash).order("created_at", desc=True)
        if filters.get("tag_filter"): q = q.ilike("tags", f"%{filters['tag_filter'].lower()}%")
        if filters.get("target_filter") and filters["target_filter"] != "All":
            q = q.eq("target", filters["target_filter"])
        
        res = q.limit(filters.get("limit", 50)).execute()
        results = res.data or []

        if query := filters.get("query", "").strip().lower():
            results = [r for r in results if query in r["title"].lower() or query in r["content"].lower()]
        return results, None
    except Exception as e:
        return [], str(e)

def delete_prompt(user_hash: str, record_id: str) -> Tuple[bool, Optional[str]]:
    if err := _require_sb(): return False, err
    try:
        sb.table(TABLE_VAULT).delete().eq("id", record_id).eq("user_hash", user_hash).execute()
        return True, None
    except Exception as e:
        return False, str(e)

def get_vault_stats(user_hash: str) -> Tuple[dict, Optional[str]]:
    if err := _require_sb(): return {}, err
    try:
        res = sb.table(TABLE_VAULT).select("score, target, tags").eq("user_hash", user_hash).execute()
        if not res.data: return {"count": 0, "avg_score": 0, "top_target": "—", "top_tag": "—"}, None

        from collections import Counter
        tags = [t.strip() for r in res.data for t in r["tags"].split(",") if t.strip()]
        
        return {
            "count": len(res.data),
            "avg_score": round(sum(r["score"] for r in res.data) / len(res.data)),
            "top_target": Counter(r["target"] for r in res.data).most_common(1)[0][0],
            "top_tag": Counter(tags).most_common(1)[0][0] if tags else "—"
        }, None
    except Exception as e:
        return {}, str(e)

def get_all_tags(user_hash: str) -> List[str]:
    if SUPABASE_MISSING or sb is None: return []
    try:
        res = sb.table(TABLE_VAULT).select("tags").eq("user_hash", user_hash).execute()
        tags = [t.strip() for r in (res.data or []) for t in r["tags"].split(",") if t.strip()]
        return sorted(set(tags))
    except Exception:
        return []
