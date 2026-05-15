"""
vault/vault_engine.py — Prompt Memory Vault Engine
====================================================
"""

from __future__ import annotations

import hashlib
import hmac
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from vault.supabase_client import SUPABASE_MISSING, supabase

TABLE_VAULT    = "vault"
TABLE_USERS    = "users"
TABLE_PERSONAS = "personas"

_ID_PATTERN        = re.compile(r"^[A-Za-z0-9_.-]{3,64}$")
_PBKDF2_PREFIX     = "pbkdf2_sha256"
_PBKDF2_ITERATIONS = 210_000

# Lockout policy
_MAX_FAILED_ATTEMPTS = 5
_LOCKOUT_MINUTES     = 15


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
    salt   = os.urandom(16).hex()
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
            salt       = parts[2]
            expected   = parts[3]
            digest = hashlib.pbkdf2_hmac(
                "sha256",
                str(pin).encode("utf-8"),
                salt.encode("ascii"),
                iterations,
            ).hex()
            return hmac.compare_digest(digest, expected)
        except (TypeError, ValueError):
            return False
    return hmac.compare_digest(_legacy_sha256_pin(pin), stored_hash)


def _make_prompt_id(user_hash: str, title: str, content: str) -> str:
    seed = f"{user_hash}\0{title.strip().lower()}\0{content.strip()}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:24]


def _safe_score(value: object) -> int:
    try:
        return min(max(int(value), 0), 100)
    except (TypeError, ValueError):
        return 0


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# ── IDENTITY & AUTHENTICATION ────────────────────────────────────────────────

def check_id_availability(user_hash: str) -> Tuple[bool, str]:
    if err := _require_sb(): return False, err
    if err := _validate_user_hash(user_hash): return False, err
    clean_id = _normalize_user_hash(user_hash)
    try:
        res = supabase.table(TABLE_USERS).select("id").eq("id", clean_id).execute()
        available = len(res.data or []) == 0
        return available, f"ID '{clean_id}' is {'available' if available else 'taken'}."
    except Exception as e:
        return False, f"Check failed: {str(e)}"


def authenticate_terminal(
    user_hash: str,
    pin:       str,
    is_new:    bool,
) -> Tuple[bool, Optional[str]]:
    """
    Authenticate or register a terminal user.

    SEC-2: Lockout logic — reads `failed_attempts` and `lockout_until`
    columns from the users table. If those columns are absent (migration
    not yet applied) the function degrades silently to the previous
    unlimited-attempt behaviour and logs a warning.

    Returns (success: bool, error_message: Optional[str]).
    """
    if err := _require_sb(): return False, err

    if err := _validate_user_hash(user_hash):
        return False, err if not is_new else f"Registration Blocked: {err}"

    clean_id  = _normalize_user_hash(user_hash)
    clean_pin = str(pin or "")
    if len(clean_pin) < 4 or len(clean_pin) > 128:
        return False, "PIN must be 4–128 characters."

    try:
        res  = supabase.table(TABLE_USERS).select("*").eq("id", clean_id).execute()
        rows = res.data or []
        user_exists = len(rows) > 0

        # ── REGISTRATION ──────────────────────────────────────────────
        if is_new:
            if user_exists:
                return False, "ID exists. Switch to Login."
            supabase.table(TABLE_USERS).insert({
                "id":              clean_id,
                "pin_hash":        _hash_pin(clean_pin),
                "created_at":      _utcnow().isoformat(),
                "is_admin":        False,
                "failed_attempts": 0,
                "lockout_until":   None,
            }).execute()
            return True, None

        # ── LOGIN ─────────────────────────────────────────────────────
        if not user_exists:
            return False, "ID not found."

        row = rows[0]

        # SEC-2: Check lockout (graceful — columns may not exist yet)
        lockout_until_raw = row.get("lockout_until")
        if lockout_until_raw:
            try:
                lockout_dt = datetime.fromisoformat(
                    str(lockout_until_raw).replace("Z", "+00:00")
                )
                if _utcnow() < lockout_dt:
                    remaining = int((lockout_dt - _utcnow()).total_seconds() / 60) + 1
                    return False, (
                        f"Account locked after too many failed attempts. "
                        f"Try again in {remaining} minute(s)."
                    )
            except (ValueError, TypeError):
                pass  # malformed timestamp — ignore and proceed

        # Verify PIN
        pin_ok = _verify_pin(clean_pin, row.get("pin_hash", ""))

        if pin_ok:
            # Reset failure counter on successful login
            _reset_failed_attempts(clean_id)
            return True, None
        else:
            # Increment failure counter and possibly lock the account
            _increment_failed_attempts(clean_id, row)
            return False, "Invalid PIN."

    except Exception as e:
        return False, f"Auth Error: {str(e)}"


def _increment_failed_attempts(user_id: str, row: dict) -> None:
    """
    Increment failed_attempts. If it reaches the threshold, set lockout_until.
    Degrades silently if the column doesn't exist.
    """
    if _require_sb():
        return
    try:
        current  = int(row.get("failed_attempts", 0) or 0) + 1
        update   = {"failed_attempts": current}
        if current >= _MAX_FAILED_ATTEMPTS:
            lockout_until      = _utcnow() + timedelta(minutes=_LOCKOUT_MINUTES)
            update["lockout_until"]   = lockout_until.isoformat()
            update["failed_attempts"] = 0   # reset so next window starts clean
        supabase.table(TABLE_USERS).update(update).eq("id", user_id).execute()
    except Exception:
        # Column likely doesn't exist yet — warn ops, don't crash the login flow
        print(
            "[InkOS WARNING] Could not update failed_attempts. "
            "Run supabase_migration_phase2.sql to enable PIN lockout.",
            file=sys.stderr,
        )


def _reset_failed_attempts(user_id: str) -> None:
    """Reset failure counter after a successful login."""
    if _require_sb():
        return
    try:
        supabase.table(TABLE_USERS).update({
            "failed_attempts": 0,
            "lockout_until":   None,
        }).eq("id", user_id).execute()
    except Exception:
        pass  # non-critical; degrade silently


# ── USER PROFILE (SEC-1) ─────────────────────────────────────────────────────

def get_user_profile(user_hash: str) -> dict:
    """
    Returns {"is_admin": bool, ...} for the given user.

    SEC-1: Admin status is read from the `is_admin` column in the users table.
    This function is called by splash.py right after a successful login, and
    the result is stored in K.IS_ADMIN in session state.

    If the `is_admin` column doesn't exist yet (migration not run), returns
    {"is_admin": False} so the app degrades safely with no admin access.
    """
    defaults = {"is_admin": False}
    if _require_sb():
        return defaults
    if err := _validate_user_hash(user_hash):
        return defaults
    try:
        res = (
            supabase.table(TABLE_USERS)
            .select("is_admin")
            .eq("id", _normalize_user_hash(user_hash))
            .single()
            .execute()
        )
        if res.data:
            return {"is_admin": bool(res.data.get("is_admin", False))}
        return defaults
    except Exception:
        return defaults


# ── REHYDRATION PROTOCOL ──────────────────────────────────────────────────────

def rehydrate_session(user_hash: str) -> dict:
    """
    Recover terminal state from Supabase.

    SEC-1: Now includes `is_admin` flag in the returned dict so app.py can
    set K.IS_ADMIN correctly on URL-param rehydration without relying on
    username-string comparison.

    Returns: {personas: [], dna: {ink, intel, hikmah}, is_admin: bool}
    """
    state: dict = {
        "personas": [],
        "dna":      {"ink": "", "intel": "", "hikmah": ""},
        "is_admin": False,
    }
    if _require_sb() or not _normalize_user_hash(user_hash):
        return state

    try:
        clean_id = _normalize_user_hash(user_hash)

        # Personas
        p_res = (
            supabase.table(TABLE_PERSONAS)
            .select("*")
            .eq("user_hash", clean_id)
            .execute()
        )
        state["personas"] = p_res.data or []

        # User profile (DNA + admin flag)
        u_res = (
            supabase.table(TABLE_USERS)
            .select("ink_dna, intel_dna, hikmah_dna, is_admin")
            .eq("id", clean_id)
            .execute()
        )
        if u_res.data:
            profile = u_res.data[0]
            state["dna"] = {
                "ink":   profile.get("ink_dna")   or "",
                "intel": profile.get("intel_dna")  or "",
                "hikmah":profile.get("hikmah_dna") or "",
            }
            state["is_admin"] = bool(profile.get("is_admin", False))

        return state
    except Exception:
        return state


# ── VAULT OPERATIONS ─────────────────────────────────────────────────────────

def save_prompt(user_hash: str, **data) -> Tuple[Optional[dict], Optional[str]]:
    if err := _require_sb(): return None, err
    if err := _validate_user_hash(user_hash): return None, err

    title   = str(data.get("title") or "Untitled").strip()[:120] or "Untitled"
    content = str(data.get("content") or "")
    clean_id = _normalize_user_hash(user_hash)
    record_id = str(data.get("id") or "").strip() or _make_prompt_id(clean_id, title, content)

    record = {
        "id":         record_id,
        "user_hash":  clean_id,
        "title":      title,
        "tags":       str(data.get("tags") or "").strip().lower()[:500],
        "content":    content,
        "target":     str(data.get("target")    or "Claude")[:80],
        "framework":  str(data.get("framework") or "Professional")[:80],
        "score":      _safe_score(data.get("score", 0)),
        "pattern":    str(data.get("pattern")   or "")[:120],
        "style":      str(data.get("style")     or "None")[:80],
        "aesthetic":  str(data.get("aesthetic") or "")[:120],
        "intent":     str(data.get("intent")    or "")[:500],
        "created_at": _utcnow().isoformat(),
    }

    try:
        res = supabase.table(TABLE_VAULT).upsert(record).execute()
        return res.data[0] if res.data else record, None
    except Exception as e:
        return None, f"Save failed: {str(e)}"


def search_vault(user_hash: str, **filters) -> Tuple[List[dict], Optional[str]]:
    if err := _require_sb(): return [], err
    if err := _validate_user_hash(user_hash): return [], err
    try:
        q = (
            supabase.table(TABLE_VAULT)
            .select("*")
            .eq("user_hash", _normalize_user_hash(user_hash))
            .order("created_at", desc=True)
        )
        if filters.get("tag_filter"):
            q = q.ilike("tags", f"%{str(filters['tag_filter']).lower()}%")
        if filters.get("target_filter") and filters["target_filter"] != "All":
            q = q.eq("target", filters["target_filter"])

        limit = min(max(int(filters.get("limit", 50)), 1), 200)
        res     = q.limit(limit).execute()
        results = res.data or []

        query = str(filters.get("query") or "").strip().lower()
        if query:
            results = [
                r for r in results
                if query in str(r.get("title",   "")).lower()
                or query in str(r.get("content", "")).lower()
            ]
        return results, None
    except Exception as e:
        return [], str(e)


def delete_prompt(user_hash: str, record_id: str) -> Tuple[bool, Optional[str]]:
    if err := _require_sb(): return False, err
    if err := _validate_user_hash(user_hash): return False, err
    if not str(record_id or "").strip(): return False, "Record ID cannot be empty."
    try:
        supabase.table(TABLE_VAULT).delete() \
            .eq("id", str(record_id).strip()) \
            .eq("user_hash", _normalize_user_hash(user_hash)) \
            .execute()
        return True, None
    except Exception as e:
        return False, str(e)


def get_vault_stats(user_hash: str) -> Tuple[dict, Optional[str]]:
    if err := _require_sb(): return {}, err
    if err := _validate_user_hash(user_hash): return {}, err
    try:
        res = (
            supabase.table(TABLE_VAULT)
            .select("score, target, tags")
            .eq("user_hash", _normalize_user_hash(user_hash))
            .execute()
        )
        if not res.data:
            return {"count": 0, "avg_score": 0, "top_target": "—", "top_tag": "—"}, None

        from collections import Counter
        tags   = [t.strip() for r in res.data for t in str(r.get("tags","")).split(",") if t.strip()]
        scores = [_safe_score(r.get("score", 0)) for r in res.data]

        return {
            "count":      len(res.data),
            "avg_score":  round(sum(scores) / len(scores)),
            "top_target": Counter(str(r.get("target","—")) for r in res.data).most_common(1)[0][0],
            "top_tag":    Counter(tags).most_common(1)[0][0] if tags else "—",
        }, None
    except Exception as e:
        return {}, str(e)


def get_all_tags(user_hash: str) -> List[str]:
    if SUPABASE_MISSING or supabase is None or _validate_user_hash(user_hash):
        return []
    try:
        res = (
            supabase.table(TABLE_VAULT)
            .select("tags")
            .eq("user_hash", _normalize_user_hash(user_hash))
            .execute()
        )
        tags = [
            t.strip()
            for r in (res.data or [])
            for t in str(r.get("tags","")).split(",")
            if t.strip()
        ]
        return sorted(set(tags))
    except Exception:
        return []
