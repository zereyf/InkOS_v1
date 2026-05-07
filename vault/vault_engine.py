"""
vault/vault_engine.py — Prompt Memory Vault Engine
====================================================
v17.0: Identity Integrity & Prefix Protection.
Now includes ID availability checks and reserved prefix shielding.
"""

import hashlib
from datetime import datetime
from typing import Optional, Tuple, List
from vault.supabase_client import sb, SUPABASE_MISSING

TABLE_VAULT = "vault"
TABLE_USERS = "users"


def _require_sb() -> Optional[str]:
    """Returns error string if Supabase is unavailable, None if ready."""
    if SUPABASE_MISSING or sb is None:
        return "Vault unavailable — SUPABASE_URL or SUPABASE_KEY not configured."
    return None


def _hash_pin(pin: str) -> str:
    """Standardized SHA-256 hashing for PIN security."""
    return hashlib.sha256(pin.encode()).hexdigest()


# ── IDENTITY & AUTHENTICATION ───────────────────────────────────────────────

def check_id_availability(user_hash: str) -> Tuple[bool, str]:
    """
    Checks if a Terminal ID can be registered.
    Returns (is_available, status_message).
    """
    if not user_hash.strip():
        return False, "ID cannot be empty."

    # 🛡️ PROTECT RESERVED PREFIX
    if user_hash.upper().startswith("GUEST_"):
        return False, "Reserved Prefix: ID cannot start with 'GUEST_'."

    if err := _require_sb():
        return False, err

    try:
        res = sb.table(TABLE_USERS).select("id").eq("id", user_hash.strip()).execute()
        if len(res.data) > 0:
            return False, f"ID '{user_hash}' is already taken."
        return True, f"ID '{user_hash}' is available."
    except Exception as e:
        return False, f"Check failed: {str(e)}"


def authenticate_terminal(user_hash: str, pin: str, is_new: bool) -> Tuple[bool, Optional[str]]:
    """
    The 'Real Verification' Gate with Prefix Shielding.
    """
    if err := _require_sb():
        return False, err

    clean_id = user_hash.strip()
    hashed_pin = _hash_pin(pin)

    # 🛡️ BLOCK RESERVED PREFIX DURING REGISTRATION
    if is_new and clean_id.upper().startswith("GUEST_"):
        return False, "Registration Blocked: 'GUEST_' is a reserved system prefix."

    try:
        # Check if user exists
        res = sb.table(TABLE_USERS).select("*").eq("id", clean_id).execute()
        user_exists = len(res.data) > 0

        if is_new:
            if user_exists:
                return False, "Terminal ID already exists. Switch to Login or choose a new ID."
            
            # Register new user
            sb.table(TABLE_USERS).insert({
                "id": clean_id,
                "pin_hash": hashed_pin,
                "created_at": datetime.utcnow().isoformat()
            }).execute()
            return True, None

        else:
            if not user_exists:
                return False, "Terminal ID not found. Use 'Register' to create it."
            
            # Verify PIN
            if res.data[0]["pin_hash"] == hashed_pin:
                return True, None
            else:
                return False, "Invalid Security PIN."

    except Exception as e:
        return False, f"Auth Error: {str(e)}"


# ── VAULT OPERATIONS ────────────────────────────────────────────────────────

def save_prompt(
    user_hash:  str,
    title:      str,
    tags:       str,
    content:    str,
    target:     str,
    framework:  str,
    score:      int,
    pattern:    str,
    islamic:    bool,
    aesthetic:  str,
) -> Tuple[Optional[dict], Optional[str]]:
    if err := _require_sb():
        return None, err

    record_id = hashlib.md5(f"{user_hash}{content}".encode()).hexdigest()[:16]

    record = {
        "id":         record_id,
        "user_hash":  user_hash,
        "title":      title.strip()[:120],
        "tags":       tags.strip().lower(),
        "content":    content,
        "target":     target,
        "framework":  framework,
        "score":      min(max(int(score), 0), 100),
        "pattern":    pattern or "",
        "islamic":    islamic,
        "aesthetic":  aesthetic or "",
        "created_at": datetime.utcnow().isoformat(),
    }

    try:
        res = sb.table(TABLE_VAULT).upsert(record).execute()
        return res.data[0] if res.data else record, None
    except Exception as e:
        return None, f"Save failed: {str(e)}"


def search_vault(
    user_hash:  str,
    query:      str = "",
    tag_filter: str = "",
    target_filter: str = "",
    min_score:  int = 0,
    limit:      int = 50,
) -> Tuple[List[dict], Optional[str]]:
    if err := _require_sb():
        return [], err

    try:
        q = (
            sb.table(TABLE_VAULT)
            .select("*")
            .eq("user_hash", user_hash)
            .gte("score", min_score)
            .order("created_at", desc=True)
            .limit(limit)
        )

        if tag_filter:
            q = q.ilike("tags", f"%{tag_filter.lower()}%")
        if target_filter and target_filter != "All":
            q = q.eq("target", target_filter)

        res = q.execute()
        results: List[dict] = res.data or []

        if query.strip():
            q_lower = query.strip().lower()
            results = [
                r for r in results
                if q_lower in r["title"].lower()
                or q_lower in r["tags"].lower()
                or q_lower in r["content"].lower()
            ]

        return results, None
    except Exception as e:
        return [], f"Search failed: {str(e)}"


def delete_prompt(user_hash: str, record_id: str) -> Tuple[bool, Optional[str]]:
    if err := _require_sb():
        return False, err
    try:
        sb.table(TABLE_VAULT).delete().eq("id", record_id).eq("user_hash", user_hash).execute()
        return True, None
    except Exception as e:
        return False, f"Delete failed: {str(e)}"


def get_vault_stats(user_hash: str) -> Tuple[dict, Optional[str]]:
    if err := _require_sb():
        return {"count": 0, "avg_score": 0, "top_target": "—", "top_tag": "—"}, err
    try:
        res = sb.table(TABLE_VAULT).select("score, target, tags").eq("user_hash", user_hash).execute()
        entries: List[dict] = res.data or []
        if not entries:
            return {"count": 0, "avg_score": 0, "top_target": "—", "top_tag": "—"}, None

        count = len(entries)
        avg_score = round(sum(e["score"] for e in entries) / count)

        from collections import Counter
        target_counts = Counter(e["target"] for e in entries)
        top_target = target_counts.most_common(1)[0][0] if target_counts else "—"

        all_tags = []
        for e in entries:
            all_tags.extend([t.strip() for t in e["tags"].split(",") if t.strip()])
        tag_counts = Counter(all_tags)
        top_tag = tag_counts.most_common(1)[0][0] if tag_counts else "—"

        return {"count": count, "avg_score": avg_score, "top_target": top_target, "top_tag": top_tag}, None
    except Exception as e:
        return {"count": 0, "avg_score": 0, "top_target": "—", "top_tag": "—"}, f"Stats failed: {str(e)}"


def get_all_tags(user_hash: str) -> List[str]:
    if SUPABASE_MISSING or sb is None:
        return []
    try:
        res = sb.table(TABLE_VAULT).select("tags").eq("user_hash", user_hash).execute()
        all_tags = []
        for row in (res.data or []):
            all_tags.extend([t.strip() for t in row["tags"].split(",") if t.strip()])
        return sorted(set(all_tags))
    except Exception:
        return []
