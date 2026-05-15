"""
vault/vault_engine.py  
"""

from __future__ import annotations

import hashlib
import secrets
import sys
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Any

from vault.supabase_client import supabase, SUPABASE_MISSING

UTC = timezone.utc

# PIN lockout constants (Phase 2)
_MAX_FAILED_ATTEMPTS = 5
_LOCKOUT_MINUTES     = 15

# Columns guaranteed to exist in every vault deployment
_SAFE_VAULT_COLUMNS = {
    "user_hash", "title", "tags", "content", "target", "framework", "score"
}


# ── SAVE PROMPT (patched) ─────────────────────────────────────────────────────

def save_prompt(
    user_hash: str,
    title:     str,
    tags:      str,
    content:   str,
    target:    str    = "ChatGPT",
    framework: str    = "RACE",
    score:     int    = 0,
    aesthetic: str    = "Default",
    intent:    str    = "",
) -> Tuple[Optional[Any], Optional[str]]:
    """
    Save a refined prompt to the vault table.

    Tries a full insert first (all columns).
    On PGRST204 (unknown column), retries with safe columns only
    so saves work before the SQL migration is applied.
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
        "created_at": datetime.now(UTC).isoformat(),
    }

    # ── Primary attempt: all columns ─────────────────────────────────────
    try:
        resp = supabase.table("vault").insert(full_record).execute()
        data = resp.data
        if data:
            return data[0], None
        return None, "Insert returned no data"
    except Exception as exc:
        err_str = str(exc)

        # PGRST204 = column doesn't exist in schema cache
        if "PGRST204" in err_str or "column" in err_str.lower():
            print(
                f"[InkOS WARNING] Vault insert failed with schema error: {exc}\n"
                "Retrying with safe columns only. "
                "Run supabase_migration_vault_columns.sql to fix permanently.",
                file=sys.stderr,
            )
            return _save_safe_columns(user_hash, title, tags, content,
                                      target, framework, score)

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
    """
    Fallback insert using only columns guaranteed to exist.
    Used when the full insert fails due to missing schema columns.
    """
    safe_record = {
        "user_hash": user_hash,
        "title":     title[:200],
        "tags":      tags[:100],
        "content":   content,
        "target":    target,
        "framework": framework,
        "score":     max(0, min(100, int(score))),
        "created_at": datetime.now(UTC).isoformat(),
    }
    try:
        resp = supabase.table("vault").insert(safe_record).execute()
        data = resp.data
        if data:
            return data[0], None
        return None, "Safe insert returned no data"
    except Exception as exc:
        return None, f"Save failed: {exc}"


# ── AUTH & LOCKOUT (Phase 2 — unchanged) ─────────────────────────────────────

def _hash_pin(pin: str, salt: str = "") -> str:
    return hashlib.sha256(f"{salt}{pin}".encode()).hexdigest()


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
        current = (resp.data or {}).get("failed_attempts", 0) or 0
        new_count = current + 1
        update: dict = {"failed_attempts": new_count}
        if new_count >= _MAX_FAILED_ATTEMPTS:
            lockout_until = (
                datetime.now(UTC) + timedelta(minutes=_LOCKOUT_MINUTES)
            ).isoformat()
            update["lockout_until"]  = lockout_until
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


def authenticate_terminal(user_hash: str, pin: str) -> Tuple[bool, str]:
    """
    Authenticate a user by PIN with lockout enforcement.
    Returns (success, message).
    """
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

    # Check lockout
    lockout_str = data.get("lockout_until")
    if lockout_str:
        try:
            lockout_dt = datetime.fromisoformat(lockout_str)
            if datetime.now(UTC) < lockout_dt:
                remaining = int((lockout_dt - datetime.now(UTC)).total_seconds() / 60) + 1
                return False, f"Account locked. Try again in {remaining} minute(s)."
        except (ValueError, TypeError):
            pass

    # Verify PIN
    salt      = data.get("salt", "")
    pin_hash  = _hash_pin(pin, salt)
    stored    = data.get("pin_hash", "")

    if secrets.compare_digest(pin_hash, stored):
        _reset_failed_attempts(user_hash)
        return True, "Authenticated"

    _increment_failed_attempts(user_hash)
    remaining_attempts = _MAX_FAILED_ATTEMPTS - (data.get("failed_attempts", 0) or 0) - 1
    if remaining_attempts <= 0:
        return False, f"Too many failed attempts. Account locked for {_LOCKOUT_MINUTES} minutes."
    return False, f"Incorrect PIN. {remaining_attempts} attempt(s) remaining."


def rehydrate_session(user_hash: str) -> dict:
    """Rehydrate session data from Supabase for URL-param logins."""
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
