"""
vault/vault_engine.py — Prompt Memory Vault Engine
====================================================
Persistence and authentication helpers for Supabase-backed user vaults.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from vault.supabase_client import SUPABASE_MISSING, supabase

TABLE_VAULT = "vault"
TABLE_USERS = "users"
TABLE_PERSONAS = "personas"

_ID_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,64}$")
_PBKDF2_PREFIX = "pbkdf2_sha256"
_PBKDF2_ITERATIONS = 210_000


# ── INTERNAL UTILITIES ────────────────────────────────────────────────────────

def _require_sb() -> Optional[str]:
    if SUPABASE_MISSING or supabase is None:
        return "Vault offline: SUPABASE_URL/KEY missing."
    return None


def _normalize_user_hash(user_hash: object) -> str:
    return str(user_hash or "").strip()


def _validate_user_hash(user_hash: object) -> Optional[str]:
    clean_id = _normalize_user_hash(user_hash)
    if not clean_id:
        return "ID cannot be empty."
    if clean_id.upper().startswith("GUEST_"):
        return "Prefix Reserved."
    if not _ID_PATTERN.fullmatch(clean_id):
        return "ID must be 3-64 characters using letters, numbers, dot, dash, or underscore."
    return None


def _hash_pin(pin: str) -> str:
    """Hash a PIN with a per-record salt. Kept private to avoid exposing internals."""
    salt = os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        str(pin).encode("utf-8"),
        salt.encode("ascii"),
        _PBKDF2_ITERATIONS,
    ).hex()
    return f"{_PBKDF2_PREFIX}${_PBKDF2_ITERATIONS}${salt}${digest}"


def _legacy_sha256_pin(pin: str) -> str:
    return hashlib.sha256(str(pin).encode("utf-8")).hexdigest()


def _verify_pin(pin: str, stored_hash: str) -> bool:
    if not stored_hash:
        return False

    parts = stored_hash.split("$")
    if len(parts) == 4 and parts[0] == _PBKDF2_PREFIX:
        try:
            iterations = int(parts[1])
            salt = parts[2]
            expected = parts[3]
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                str(pin).encode("utf-8"),
                salt.encode("ascii"),
                iterations,
            ).hex()
            return hmac.compare_digest(digest, expected)
        except (TypeError, ValueError):
            return False

    # Backward-compatible verification for existing SHA-256 rows.
    return hmac.compare_digest(_legacy_sha256_pin(pin), stored_hash)


def _make_prompt_id(user_hash: str, title: str, content: str) -> str:
    seed = f"{user_hash}\0{title.strip().lower()}\0{content.strip()}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]


def _safe_score(value: object) -> int:
    try:
        return min(max(int(value), 0), 100)
    except (TypeError, ValueError):
        return 0


# ── IDENTITY & AUTHENTICATION ────────────────────────────────────────────────

def check_id_availability(user_hash: str) -> Tuple[bool, str]:
    validation_error = _validate_user_hash(user_hash)
    if validation_error:
        return False, validation_error
    if err := _require_sb():
        return False, err

    clean_id = _normalize_user_hash(user_hash)
    try:
        res = supabase.table(TABLE_USERS).select("id").eq("id", clean_id).execute()
        is_available = len(res.data or []) == 0
        return is_available, f"ID '{clean_id}' is {'available' if is_available else 'taken'}."
    except Exception as e:
        return False, f"Check failed: {str(e)}"


def authenticate_terminal(user_hash: str, pin: str, is_new: bool) -> Tuple[bool, Optional[str]]:
    if err := _require_sb():
        return False, err

    validation_error = _validate_user_hash(user_hash)
    if validation_error:
        return False, validation_error if not is_new else f"Registration Blocked: {validation_error}"

    clean_id = _normalize_user_hash(user_hash)
    clean_pin = str(pin or "")
    if len(clean_pin) < 4 or len(clean_pin) > 128:
        return False, "PIN must be 4-128 characters."

    try:
        res = supabase.table(TABLE_USERS).select("*").eq("id", clean_id).execute()
        rows = res.data or []
        user_exists = len(rows) > 0

        if is_new:
            if user_exists:
                return False, "ID exists. Switch to Login."
            supabase.table(TABLE_USERS).insert(
                {
                    "id": clean_id,
                    "pin_hash": _hash_pin(clean_pin),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
            ).execute()
            return True, None

        if not user_exists:
            return False, "ID not found."
        pin_matches = _verify_pin(clean_pin, rows[0].get("pin_hash", ""))
        return (True, None) if pin_matches else (False, "Invalid PIN")

    except Exception as e:
        return False, f"Auth Error: {str(e)}"


# ── REHYDRATION PROTOCOL (Zero-Cost Persistence) ─────────────────────────────

def rehydrate_session(user_hash: str) -> dict:
    """
    Recover terminal state from Supabase.

    Returns: {personas: [], dna: {ink, intel, hikmah}}
    """
    state = {"personas": [], "dna": {"ink": "", "intel": "", "hikmah": ""}}

    if _require_sb() or not _normalize_user_hash(user_hash):
        return state

    try:
        clean_id = _normalize_user_hash(user_hash)
        p_res = supabase.table(TABLE_PERSONAS).select("*").eq("user_hash", clean_id).execute()
        state["personas"] = p_res.data or []

        u_res = supabase.table(TABLE_USERS).select("ink_dna, intel_dna, hikmah_dna").eq("id", clean_id).execute()
        if u_res.data:
            profile = u_res.data[0]
            state["dna"] = {
                "ink": profile.get("ink_dna") or "",
                "intel": profile.get("intel_dna") or "",
                "hikmah": profile.get("hikmah_dna") or "",
            }
        return state
    except Exception:
        return state


# ── VAULT OPERATIONS ────────────────────────────────────────────────────────

def save_prompt(user_hash: str, **data) -> Tuple[Optional[dict], Optional[str]]:
    if err := _require_sb():
        return None, err
    validation_error = _validate_user_hash(user_hash)
    if validation_error:
        return None, validation_error

    title = str(data.get("title") or "Untitled").strip()[:120] or "Untitled"
    content = str(data.get("content") or "")
    clean_id = _normalize_user_hash(user_hash)
    record_id = str(data.get("id") or "").strip() or _make_prompt_id(clean_id, title, content)

    record = {
        "id": record_id,
        "user_hash": clean_id,
        "title": title,
        "tags": str(data.get("tags") or "").strip().lower()[:500],
        "content": content,
        "target": str(data.get("target") or "Claude")[:80],
        "framework": str(data.get("framework") or "Professional")[:80],
        "score": _safe_score(data.get("score", 0)),
        "pattern": str(data.get("pattern") or "")[:120],
        "style": str(data.get("style") or "None")[:80],
        "aesthetic": str(data.get("aesthetic") or "")[:120],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    try:
        res = supabase.table(TABLE_VAULT).upsert(record).execute()
        return res.data[0] if res.data else record, None
    except Exception as e:
        return None, f"Save failed: {str(e)}"


def search_vault(user_hash: str, **filters) -> Tuple[List[dict], Optional[str]]:
    if err := _require_sb():
        return [], err
    validation_error = _validate_user_hash(user_hash)
    if validation_error:
        return [], validation_error
    try:
        q = supabase.table(TABLE_VAULT).select("*").eq("user_hash", _normalize_user_hash(user_hash)).order("created_at", desc=True)
        if filters.get("tag_filter"):
            q = q.ilike("tags", f"%{str(filters['tag_filter']).lower()}%")
        if filters.get("target_filter") and filters["target_filter"] != "All":
            q = q.eq("target", filters["target_filter"])

        limit = min(max(int(filters.get("limit", 50)), 1), 200)
        res = q.limit(limit).execute()
        results = res.data or []

        query = str(filters.get("query") or "").strip().lower()
        if query:
            results = [
                r for r in results
                if query in str(r.get("title", "")).lower()
                or query in str(r.get("content", "")).lower()
            ]
        return results, None
    except Exception as e:
        return [], str(e)


def delete_prompt(user_hash: str, record_id: str) -> Tuple[bool, Optional[str]]:
    if err := _require_sb():
        return False, err
    validation_error = _validate_user_hash(user_hash)
    if validation_error:
        return False, validation_error
    if not str(record_id or "").strip():
        return False, "Record ID cannot be empty."
    try:
        supabase.table(TABLE_VAULT).delete().eq("id", str(record_id).strip()).eq("user_hash", _normalize_user_hash(user_hash)).execute()
        return True, None
    except Exception as e:
        return False, str(e)


def get_vault_stats(user_hash: str) -> Tuple[dict, Optional[str]]:
    if err := _require_sb():
        return {}, err
    validation_error = _validate_user_hash(user_hash)
    if validation_error:
        return {}, validation_error
    try:
        res = supabase.table(TABLE_VAULT).select("score, target, tags").eq("user_hash", _normalize_user_hash(user_hash)).execute()
        if not res.data:
            return {"count": 0, "avg_score": 0, "top_target": "—", "top_tag": "—"}, None

        from collections import Counter

        tags = [t.strip() for r in res.data for t in str(r.get("tags", "")).split(",") if t.strip()]
        scores = [_safe_score(r.get("score", 0)) for r in res.data]

        return {
            "count": len(res.data),
            "avg_score": round(sum(scores) / len(scores)),
            "top_target": Counter(str(r.get("target", "—")) for r in res.data).most_common(1)[0][0],
            "top_tag": Counter(tags).most_common(1)[0][0] if tags else "—",
        }, None
    except Exception as e:
        return {}, str(e)


def get_all_tags(user_hash: str) -> List[str]:
    if SUPABASE_MISSING or supabase is None or _validate_user_hash(user_hash):
        return []
    try:
        res = supabase.table(TABLE_VAULT).select("tags").eq("user_hash", _normalize_user_hash(user_hash)).execute()
        tags = [t.strip() for r in (res.data or []) for t in str(r.get("tags", "")).split(",") if t.strip()]
        return sorted(set(tags))
    except Exception:
        return []
