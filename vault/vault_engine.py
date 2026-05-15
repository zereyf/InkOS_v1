"""
vault/vault_engine.py — Complete File
=======================================
All phases combined. This is the single source of truth.

Phase 2 security (all applied):
  - get_user_profile()       DB-driven admin flag, no username bypass
  - authenticate_terminal()  PIN auth with lockout after 5 attempts
  - _increment_failed_attempts() / _reset_failed_attempts()
  - rehydrate_session()      returns is_admin from DB

Hotfix-A (vault save):
  - save_prompt()            PGRST204-resilient: retries with safe
                             columns if intent/aesthetic missing from schema

All original functions preserved:
  - check_id_availability()
  - get_vault_items()
  - delete_prompt()
  - save_persona() / get_personas() / delete_persona()
  - get_all_users() / delete_user() / get_system_stats()
"""

from __future__ import annotations

import hashlib
import secrets
import sys
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Any

from vault.supabase_client import supabase, SUPABASE_MISSING

UTC = timezone.utc

_MAX_FAILED_ATTEMPTS = 5
_LOCKOUT_MINUTES     = 15


# ── HELPERS ───────────────────────────────────────────────────────────────────

def _hash_pin(pin: str, salt: str = "") -> str:
    return hashlib.sha256(f"{salt}{pin}".encode()).hexdigest()


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


# ── USER REGISTRATION ─────────────────────────────────────────────────────────

def check_id_availability(user_id: str) -> Tuple[bool, str]:
    """
    Check whether a user ID is available for registration.
    Returns (is_available, message).
    """
    if SUPABASE_MISSING or supabase is None:
        return False, "Database unavailable"

    if not user_id or len(user_id.strip()) < 3:
        return False, "ID must be at least 3 characters"

    uid = user_id.strip().lower()

    try:
        resp = (
            supabase.table("users")
            .select("id")
            .eq("id", uid)
            .execute()
        )
        if resp.data:
            return False, "ID already taken"
        return True, "Available"
    except Exception as exc:
        return False, f"DB error: {exc}"


def register_user(
    user_id:  str,
    pin:      str,
    ink_dna:  str = "",
    intel_dna: str = "",
    hikmah_dna: str = "",
) -> Tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    if SUPABASE_MISSING or supabase is None:
        return False, "Database unavailable"

    available, msg = check_id_availability(user_id)
    if not available:
        return False, msg

    salt     = secrets.token_hex(16)
    pin_hash = _hash_pin(pin, salt)

    record = {
        "id":          user_id.strip().lower(),
        "pin_hash":    pin_hash,
        "salt":        salt,
        "ink_dna":     ink_dna,
        "intel_dna":   intel_dna,
        "hikmah_dna":  hikmah_dna,
        "is_admin":    False,
        "failed_attempts": 0,
        "lockout_until":   None,
        "created_at":  _now_iso(),
    }

    try:
        resp = supabase.table("users").insert(record).execute()
        if resp.data:
            return True, "Registered"
        return False, "Registration failed — no data returned"
    except Exception as exc:
        return False, f"Registration error: {exc}"


# ── AUTH & LOCKOUT ─────────────────────────────────────────────────────────────

def get_user_profile(user_hash: str) -> dict:
    """Returns user profile dict including is_admin flag from DB."""
    if SUPABASE_MISSING or supabase is None:
        return {"is_admin": False}
    try:
        resp = (
            supabase.table("users")
            .select("id, is_admin, failed_attempts, lockout_until")
            .eq("id", user_hash)
            .single()
            .execute()
        )
        return resp.data or {"is_admin": False}
    except Exception:
        return {"is_admin": False}


def _increment_failed_attempts(user_hash: str) -> None:
    if SUPABASE_MISSING or supabase is None:
        return
    try:
        resp = (
            supabase.table("users")
            .select("failed_attempts")
            .eq("id", user_hash)
            .single()
            .execute()
        )
        current   = (resp.data or {}).get("failed_attempts", 0) or 0
        new_count = current + 1
        update: dict = {"failed_attempts": new_count}

        if new_count >= _MAX_FAILED_ATTEMPTS:
            lockout_until = (
                datetime.now(UTC) + timedelta(minutes=_LOCKOUT_MINUTES)
            ).isoformat()
            update["lockout_until"]   = lockout_until
            update["failed_attempts"] = 0

        supabase.table("users").update(update).eq("id", user_hash).execute()
    except Exception as exc:
        print(f"[InkOS WARNING] Could not increment failed attempts: {exc}",
              file=sys.stderr)


def _reset_failed_attempts(user_hash: str) -> None:
    if SUPABASE_MISSING or supabase is None:
        return
    try:
        supabase.table("users").update({
            "failed_attempts": 0,
            "lockout_until":   None,
        }).eq("id", user_hash).execute()
    except Exception as exc:
        print(f"[InkOS WARNING] Could not reset failed attempts: {exc}",
              file=sys.stderr)


def authenticate_terminal(user_hash: str, pin: str, is_new: bool = False) -> Tuple[bool, str]:
    """
    Authenticate a user by PIN with lockout enforcement.
    If is_new=True, delegates to register_user() instead.
    Returns (success, message).
    """
    if is_new:
        return register_user(user_hash, pin)

    if SUPABASE_MISSING or supabase is None:
        return False, "Database unavailable"

    try:
        resp = (
            supabase.table("users")
            .select("pin_hash, salt, lockout_until, failed_attempts")
            .eq("id", user_hash)
            .single()
            .execute()
        )
        data = resp.data
    except Exception as exc:
        return False, f"DB error: {exc}"

    if not data:
        return False, "User not found"

    lockout_str = data.get("lockout_until")
    if lockout_str:
        try:
            lockout_dt = datetime.fromisoformat(lockout_str)
            if datetime.now(UTC) < lockout_dt:
                remaining = int(
                    (lockout_dt - datetime.now(UTC)).total_seconds() / 60
                ) + 1
                return False, f"Account locked. Try again in {remaining} minute(s)."
        except (ValueError, TypeError):
            pass

    salt     = data.get("salt", "")
    pin_hash = _hash_pin(pin, salt)
    stored   = data.get("pin_hash", "")

    if secrets.compare_digest(pin_hash, stored):
        _reset_failed_attempts(user_hash)
        return True, "Authenticated"

    _increment_failed_attempts(user_hash)
    current    = data.get("failed_attempts", 0) or 0
    remaining  = _MAX_FAILED_ATTEMPTS - current - 1

    if remaining <= 0:
        return False, (
            f"Too many failed attempts. "
            f"Account locked for {_LOCKOUT_MINUTES} minutes."
        )
    return False, f"Incorrect PIN. {remaining} attempt(s) remaining."


def rehydrate_session(user_hash: str) -> dict:
    """Rehydrate DNA, personas, and admin flag for URL-param logins."""
    if SUPABASE_MISSING or supabase is None:
        return {"dna": {}, "personas": [], "is_admin": False}
    try:
        resp = (
            supabase.table("users")
            .select("ink_dna, intel_dna, hikmah_dna, personas, is_admin")
            .eq("id", user_hash)
            .single()
            .execute()
        )
        data = resp.data or {}
        return {
            "dna": {
                "ink":    data.get("ink_dna",    ""),
                "intel":  data.get("intel_dna",  ""),
                "hikmah": data.get("hikmah_dna", ""),
            },
            "personas": data.get("personas", []) or [],
            "is_admin": bool(data.get("is_admin", False)),
        }
    except Exception:
        return {"dna": {}, "personas": [], "is_admin": False}


# ── VAULT (PROMPT STORAGE) ────────────────────────────────────────────────────

def save_prompt(
    user_hash: str,
    title:     str,
    tags:      str,
    content:   str,
    target:    str = "ChatGPT",
    framework: str = "RACE",
    score:     int = 0,
    aesthetic: str = "Default",
    intent:    str = "",
) -> Tuple[Optional[Any], Optional[str]]:
    """
    Save a refined prompt to the vault table.

    Hotfix-A: PGRST204-resilient.
    Tries a full insert first. If Supabase returns PGRST204
    (unknown column — happens when intent/aesthetic columns
    haven't been added by the SQL migration yet), automatically
    retries with only the guaranteed safe columns.

    Run supabase_migration_vault_columns.sql to fix permanently.
    """
    if SUPABASE_MISSING or supabase is None:
        return None, "Supabase not configured"

    full_record = {
        "user_hash": user_hash,
        "title":     title[:200],
        "tags":      tags[:100],
        "content":   content,
        "target":    target,
        "framework": framework,
        "score":     max(0, min(100, int(score))),
        "aesthetic": aesthetic,
        "intent":    intent[:500] if intent else None,
        "created_at": _now_iso(),
    }

    try:
        resp = supabase.table("vault").insert(full_record).execute()
        if resp.data:
            return resp.data[0], None
        return None, "Insert returned no data"
    except Exception as exc:
        err_str = str(exc)
        if "PGRST204" in err_str or (
            "column" in err_str.lower() and "schema" in err_str.lower()
        ):
            print(
                f"[InkOS WARNING] Vault insert failed — unknown column: {exc}\n"
                "Retrying with safe columns. "
                "Run supabase_migration_vault_columns.sql to fix permanently.",
                file=sys.stderr,
            )
            return _save_safe_columns(
                user_hash, title, tags, content, target, framework, score
            )
        return None, f"Save failed: {exc}"


def _save_safe_columns(
    user_hash: str,
    title:     str,
    tags:      str,
    content:   str,
    target:    str,
    framework: str,
    score:     int,
) -> Tuple[Optional[Any], Optional[str]]:
    """Fallback insert using only columns that have always existed."""
    safe_record = {
        "user_hash": user_hash,
        "title":     title[:200],
        "tags":      tags[:100],
        "content":   content,
        "target":    target,
        "framework": framework,
        "score":     max(0, min(100, int(score))),
        "created_at": _now_iso(),
    }
    try:
        resp = supabase.table("vault").insert(safe_record).execute()
        if resp.data:
            return resp.data[0], None
        return None, "Safe insert returned no data"
    except Exception as exc:
        return None, f"Save failed: {exc}"


def get_vault_items(
    user_hash: str,
    limit:     int = 50,
    offset:    int = 0,
) -> Tuple[list, Optional[str]]:
    """Fetch vault items for a user, newest first."""
    if SUPABASE_MISSING or supabase is None:
        return [], "Supabase not configured"
    try:
        resp = (
            supabase.table("vault")
            .select("*")
            .eq("user_hash", user_hash)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        return resp.data or [], None
    except Exception as exc:
        return [], f"Fetch failed: {exc}"


def delete_prompt(user_hash: str, item_id: str) -> Tuple[bool, str]:
    """Delete a vault item. Requires ownership check."""
    if SUPABASE_MISSING or supabase is None:
        return False, "Supabase not configured"
    try:
        supabase.table("vault").delete().eq("id", item_id).eq(
            "user_hash", user_hash
        ).execute()
        return True, "Deleted"
    except Exception as exc:
        return False, f"Delete failed: {exc}"


# ── PERSONAS ──────────────────────────────────────────────────────────────────

def save_persona(
    user_hash: str,
    persona:   dict,
) -> Tuple[Optional[Any], Optional[str]]:
    """Save or update a custom persona for a user."""
    if SUPABASE_MISSING or supabase is None:
        return None, "Supabase not configured"

    record = {
        "user_hash":  user_hash,
        "name":       str(persona.get("name", "Unnamed"))[:100],
        "ink_dna":    persona.get("ink_dna",    ""),
        "intel_dna":  persona.get("intel_dna",  ""),
        "hikmah_dna": persona.get("hikmah_dna", ""),
        "target":     persona.get("target",     "ChatGPT"),
        "created_at": _now_iso(),
    }

    try:
        resp = supabase.table("personas").insert(record).execute()
        if resp.data:
            return resp.data[0], None
        return None, "Persona save returned no data"
    except Exception as exc:
        return None, f"Save failed: {exc}"


def get_personas(user_hash: str) -> Tuple[list, Optional[str]]:
    """Fetch all custom personas for a user."""
    if SUPABASE_MISSING or supabase is None:
        return [], "Supabase not configured"
    try:
        resp = (
            supabase.table("personas")
            .select("*")
            .eq("user_hash", user_hash)
            .order("created_at", desc=True)
            .execute()
        )
        return resp.data or [], None
    except Exception as exc:
        return [], f"Fetch failed: {exc}"


def delete_persona(persona_id: str, user_hash: str) -> Tuple[bool, str]:
    """Delete a custom persona. Requires ownership check."""
    if SUPABASE_MISSING or supabase is None:
        return False, "Supabase not configured"
    try:
        supabase.table("personas").delete().eq("id", persona_id).eq(
            "user_hash", user_hash
        ).execute()
        return True, "Deleted"
    except Exception as exc:
        return False, f"Delete failed: {exc}"


# ── ADMIN ─────────────────────────────────────────────────────────────────────

def get_all_users(limit: int = 100) -> Tuple[list, Optional[str]]:
    """Admin only: fetch all users."""
    if SUPABASE_MISSING or supabase is None:
        return [], "Supabase not configured"
    try:
        resp = (
            supabase.table("users")
            .select("id, is_admin, created_at, failed_attempts, lockout_until")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        return resp.data or [], None
    except Exception as exc:
        return [], f"Fetch failed: {exc}"


def delete_user(user_id: str) -> Tuple[bool, str]:
    """Admin only: delete a user and their vault items."""
    if SUPABASE_MISSING or supabase is None:
        return False, "Supabase not configured"
    try:
        supabase.table("vault").delete().eq("user_hash", user_id).execute()
        supabase.table("personas").delete().eq("user_hash", user_id).execute()
        supabase.table("users").delete().eq("id", user_id).execute()
        return True, f"User {user_id} deleted"
    except Exception as exc:
        return False, f"Delete failed: {exc}"


def get_system_stats() -> dict:
    """Admin only: basic system stats."""
    if SUPABASE_MISSING or supabase is None:
        return {"error": "Supabase not configured"}
    try:
        users    = supabase.table("users").select("id", count="exact").execute()
        prompts  = supabase.table("vault").select("id", count="exact").execute()
        personas = supabase.table("personas").select("id", count="exact").execute()
        return {
            "total_users":    users.count    or 0,
            "total_prompts":  prompts.count  or 0,
            "total_personas": personas.count or 0,
            "db_status":      "online",
        }
    except Exception as exc:
        return {"error": str(exc), "db_status": "error"}


# ── VAULT SEARCH & UTILITIES ──────────────────────────────────────────────────

def search_vault(
    user_hash:     str,
    query:         str,
    limit:         int = 50,
    tag_filter:    str = "",
    target_filter: str = "",
) -> Tuple[list, Optional[str]]:
    """
    Search vault items by title, tags, target, or content keywords.
    Falls back to get_vault_items() filtered in Python if the DB
    doesn't support full-text search.
    """
    if SUPABASE_MISSING or supabase is None:
        return [], "Supabase not configured"

    q = (query or "").strip()
    if not q:
        return get_vault_items(user_hash, limit=limit)

    try:
        # Try Supabase ilike search on title and tags first
        resp = (
            supabase.table("vault")
            .select("*")
            .eq("user_hash", user_hash)
            .or_(f"title.ilike.%{q}%,tags.ilike.%{q}%,target.ilike.%{q}%")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        results = resp.data or []

        # If DB search returned nothing, fall back to Python-side filter
        if not results:
            all_items, err = get_vault_items(user_hash, limit=200)
            if err:
                return [], err
            q_lower = q.lower()
            results = [
                item for item in all_items
                if q_lower in str(item.get("title",   "")).lower()
                or q_lower in str(item.get("tags",    "")).lower()
                or q_lower in str(item.get("target",  "")).lower()
                or q_lower in str(item.get("content", "")).lower()
            ][:limit]

        # Apply tag / target filters in Python
        if tag_filter:
            tl = tag_filter.lower()
            results = [r for r in results if tl in str(r.get("tags", "")).lower()]
        if target_filter:
            results = [r for r in results if str(r.get("target", "")).lower() == target_filter.lower()]

        return results, None
    except Exception as exc:
        # If the DB query itself fails, fall back to Python-side filter
        try:
            all_items, err = get_vault_items(user_hash, limit=200)
            if err:
                return [], err
            q_lower = q.lower()
            results = [
                item for item in all_items
                if q_lower in str(item.get("title",   "")).lower()
                or q_lower in str(item.get("tags",    "")).lower()
                or q_lower in str(item.get("target",  "")).lower()
                or q_lower in str(item.get("content", "")).lower()
            ][:limit]
            return results, None
        except Exception as exc2:
            return [], f"Search failed: {exc2}"


def get_prompt_by_id(
    item_id:   str,
    user_hash: str,
) -> Tuple[Optional[dict], Optional[str]]:
    """Fetch a single vault item by ID. Ownership check enforced."""
    if SUPABASE_MISSING or supabase is None:
        return None, "Supabase not configured"
    try:
        resp = (
            supabase.table("vault")
            .select("*")
            .eq("id", item_id)
            .eq("user_hash", user_hash)
            .single()
            .execute()
        )
        return resp.data, None
    except Exception as exc:
        return None, f"Fetch failed: {exc}"


def update_prompt(
    item_id:   str,
    user_hash: str,
    updates:   dict,
) -> Tuple[Optional[Any], Optional[str]]:
    """
    Update editable fields on a vault item.
    Allowed fields: title, tags, content.
    Ownership check enforced — user_hash must match.
    """
    if SUPABASE_MISSING or supabase is None:
        return None, "Supabase not configured"

    allowed = {"title", "tags", "content"}
    safe_updates = {k: v for k, v in updates.items() if k in allowed}

    if not safe_updates:
        return None, "No valid fields to update"

    try:
        resp = (
            supabase.table("vault")
            .update(safe_updates)
            .eq("id", item_id)
            .eq("user_hash", user_hash)
            .execute()
        )
        data = resp.data
        if data:
            return data[0], None
        return None, "Update returned no data — item may not exist or wrong user"
    except Exception as exc:
        return None, f"Update failed: {exc}"


def get_vault_stats(user_hash: str) -> dict:
    """
    Returns summary stats for the vault header display:
    total items, average score, highest score, most used target.
    """
    if SUPABASE_MISSING or supabase is None:
        return {"total": 0, "avg_score": 0, "top_score": 0, "top_target": "—"}

    try:
        resp = (
            supabase.table("vault")
            .select("score, target")
            .eq("user_hash", user_hash)
            .execute()
        )
        items = resp.data or []

        if not items:
            return {"count": 0, "total": 0, "avg_score": 0, "top_score": 0, "top_target": "—"}

        scores     = [int(i.get("score") or 0) for i in items]
        targets    = [str(i.get("target") or "") for i in items]
        top_target = max(set(targets), key=targets.count) if targets else "—"

        return {
            "count":      len(items),
            "total":      len(items),  # alias
            "avg_score":  round(sum(scores) / len(scores)),
            "top_score":  max(scores),
            "top_target": top_target,
        }
    except Exception:
        return {"total": 0, "avg_score": 0, "top_score": 0, "top_target": "—"}


def get_all_tags(user_hash: str) -> list:
    """
    Return a sorted list of unique tags for a user's vault items.
    Used by vault.py to populate the tag filter dropdown.
    """
    if SUPABASE_MISSING or supabase is None:
        return []
    try:
        resp = (
            supabase.table("vault")
            .select("tags")
            .eq("user_hash", user_hash)
            .execute()
        )
        raw   = resp.data or []
        tags  = set()
        for row in raw:
            val = row.get("tags") or ""
            for tag in val.split(","):
                tag = tag.strip().lower()
                if tag:
                    tags.add(tag)
        return sorted(tags)
    except Exception:
        return []
