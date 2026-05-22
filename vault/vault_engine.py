
"""
vault/vault_engine.py — v3.0 — Critical bug fixes
===================================================
BUG-1 FIXED: get_vault_stats() now returns (dict, Optional[str]).
             vault.py calls:  stats, err = get_vault_stats(user_hash)
             Old code returned a bare dict → ValueError: cannot unpack non-sequence dict.

BUG-2 FIXED: delete_persona(user_hash, persona_id) — args were reversed.
             Previous: delete_persona(persona_id, user_hash).
             That means the ownership check eq("user_hash", persona_id) always failed
             silently — nothing was ever deleted.

SEC-A:  PIN hashing upgraded from plain SHA256 to PBKDF2-HMAC-SHA256 (260k iterations).
        _legacy_sha256_pin() kept for backward compat (test seeding + DB migration).
        authenticate_terminal() transparently upgrades legacy rows on first successful login.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import sys
from datetime import datetime, timezone, timedelta
from typing import Optional, Tuple, Any

from vault.supabase_client import supabase, SUPABASE_MISSING

UTC = timezone.utc
_MAX_FAILED_ATTEMPTS = 5
_LOCKOUT_MINUTES     = 15
_PBKDF2_ITERATIONS   = 260_000
_PBKDF2_PREFIX       = "pbkdf2_sha256$"


# ── HASHING ───────────────────────────────────────────────────────────────────

def _pbkdf2_hash(pin: str, salt: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt.encode(), _PBKDF2_ITERATIONS)
    return f"{_PBKDF2_PREFIX}{_PBKDF2_ITERATIONS}${salt}${dk.hex()}"


def _pbkdf2_verify(pin: str, stored: str) -> bool:
    try:
        parts = stored.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False
        dk = hashlib.pbkdf2_hmac("sha256", pin.encode(), parts[2].encode(), int(parts[1]))
        return hmac.compare_digest(dk.hex(), parts[3])
    except Exception:
        return False


def _legacy_sha256_pin(pin: str, salt: str = "") -> str:
    """Legacy hash: SHA256(salt+pin). Preserved for test seeding and migration only."""
    return hashlib.sha256(f"{salt}{pin}".encode()).hexdigest()


def _legacy_verify(pin: str, stored: str, salt: str) -> bool:
    return hmac.compare_digest(_legacy_sha256_pin(pin, salt), stored)


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


# ── REGISTRATION ──────────────────────────────────────────────────────────────

def check_id_availability(user_id: str) -> Tuple[bool, str]:
    if SUPABASE_MISSING or supabase is None:
        return False, "Database unavailable"
    if not user_id or len(user_id.strip()) < 3:
        return False, "ID must be at least 3 characters"
    uid = user_id.strip().lower()
    try:
        resp = supabase.table("users").select("id").eq("id", uid).execute()
        return (False, "ID already taken") if resp.data else (True, "Available")
    except Exception as exc:
        return False, f"DB error: {exc}"


def register_user(
    user_id: str,
    pin: str,
    ink_dna: str = "",
    intel_dna: str = "",
    hikmah_dna: str = "",
) -> Tuple[bool, str]:
    if SUPABASE_MISSING or supabase is None:
        return False, "Database unavailable"
    available, msg = check_id_availability(user_id)
    if not available:
        return False, msg
    salt     = secrets.token_hex(16)
    pin_hash = _pbkdf2_hash(pin, salt)
    record   = {
        "id":              user_id.strip().lower(),
        "pin_hash":        pin_hash,
        "salt":            salt,
        "ink_dna":         ink_dna,
        "intel_dna":       intel_dna,
        "hikmah_dna":      hikmah_dna,
        "is_admin":        False,
        "failed_attempts": 0,
        "lockout_until":   None,
        "created_at":      _now_iso(),
    }
    try:
        resp = supabase.table("users").insert(record).execute()
        return (True, "Registered") if resp.data else (False, "Registration failed")
    except Exception as exc:
        return False, f"Registration error: {exc}"


# ── AUTH ──────────────────────────────────────────────────────────────────────

def get_user_profile(user_hash: str) -> dict:
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
        cur    = (resp.data or {}).get("failed_attempts", 0) or 0
        update: dict = {"failed_attempts": cur + 1}
        if cur + 1 >= _MAX_FAILED_ATTEMPTS:
            update["lockout_until"]   = (datetime.now(UTC) + timedelta(minutes=_LOCKOUT_MINUTES)).isoformat()
            update["failed_attempts"] = 0
        supabase.table("users").update(update).eq("id", user_hash).execute()
    except Exception as exc:
        print(f"[InkOS WARNING] increment_failed_attempts: {exc}", file=sys.stderr)


def _reset_failed_attempts(user_hash: str) -> None:
    if SUPABASE_MISSING or supabase is None:
        return
    try:
        supabase.table("users").update(
            {"failed_attempts": 0, "lockout_until": None}
        ).eq("id", user_hash).execute()
    except Exception as exc:
        print(f"[InkOS WARNING] reset_failed_attempts: {exc}", file=sys.stderr)


def _upgrade_legacy_hash(user_hash: str, pin: str) -> None:
    """Silent PBKDF2 upgrade on first successful legacy login."""
    if SUPABASE_MISSING or supabase is None:
        return
    try:
        new_salt = secrets.token_hex(16)
        supabase.table("users").update(
            {"pin_hash": _pbkdf2_hash(pin, new_salt), "salt": new_salt}
        ).eq("id", user_hash).execute()
    except Exception as exc:
        print(f"[InkOS WARNING] hash upgrade: {exc}", file=sys.stderr)


def authenticate_terminal(
    user_hash: str,
    pin: str,
    is_new: bool = False,
) -> Tuple[bool, str]:
    """
    Authenticate with PIN. Delegates to register_user() when is_new=True.

    Verification chain:
      1. PBKDF2 (all new accounts)
      2. Legacy SHA256 fallback (old accounts auto-upgraded on success)
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
                mins = int((lockout_dt - datetime.now(UTC)).total_seconds() / 60) + 1
                return False, f"Account locked. Try again in {mins} minute(s)."
        except (ValueError, TypeError):
            pass

    stored, salt = data.get("pin_hash", ""), data.get("salt", "")

    if stored.startswith(_PBKDF2_PREFIX):
        verified = _pbkdf2_verify(pin, stored)
    else:
        verified = _legacy_verify(pin, stored, salt)
        if verified:
            _upgrade_legacy_hash(user_hash, pin)

    if verified:
        _reset_failed_attempts(user_hash)
        return True, "Authenticated"

    _increment_failed_attempts(user_hash)
    remaining = _MAX_FAILED_ATTEMPTS - (data.get("failed_attempts", 0) or 0) - 1
    if remaining <= 0:
        return False, f"Too many failed attempts. Account locked for {_LOCKOUT_MINUTES} minutes."
    return False, "Invalid PIN"


def rehydrate_session(user_hash: str) -> dict:
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


# ── VAULT ─────────────────────────────────────────────────────────────────────

def save_prompt(
    user_hash: str,
    title: str,
    tags: str,
    content: str,
    target: str = "ChatGPT",
    framework: str = "RACE",
    score: int = 0,
    aesthetic: str = "Default",
    intent: str = "",
) -> Tuple[Optional[Any], Optional[str]]:
    if SUPABASE_MISSING or supabase is None:
        return None, "Supabase not configured"

    safe_score = max(0, min(100, int(score) if str(score).lstrip("-").isdigit() else 0))
    record = {
        "user_hash":  user_hash,
        "title":      title[:200],
        "tags":       tags[:100].lower(),
        "content":    content,
        "target":     target,
        "framework":  framework,
        "score":      safe_score,
        "aesthetic":  aesthetic,
        "intent":     intent[:500] if intent else None,
        "created_at": _now_iso(),
    }
    try:
        resp = supabase.table("vault").insert(record).execute()
        if resp.data:
            return resp.data[0], None
        return None, "Insert returned no data"
    except Exception as exc:
        err_str = str(exc)
        if "PGRST204" in err_str or (
            "column" in err_str.lower() and "schema" in err_str.lower()
        ):
            return _save_safe_columns(
                user_hash, title, tags, content, target, framework, safe_score
            )
        return None, f"Save failed: {exc}"


def _save_safe_columns(
    user_hash: str, title: str, tags: str, content: str,
    target: str, framework: str, score: int,
) -> Tuple[Optional[Any], Optional[str]]:
    record = {
        "user_hash":  user_hash,
        "title":      title[:200],
        "tags":       tags[:100].lower(),
        "content":    content,
        "target":     target,
        "framework":  framework,
        "score":      max(0, min(100, score)),
        "created_at": _now_iso(),
    }
    try:
        resp = supabase.table("vault").insert(record).execute()
        return (resp.data[0], None) if resp.data else (None, "Safe insert returned no data")
    except Exception as exc:
        return None, f"Save failed: {exc}"


def get_vault_items(
    user_hash: str, limit: int = 50, offset: int = 0,
) -> Tuple[list, Optional[str]]:
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

def save_persona(user_hash: str, persona: dict) -> Tuple[Optional[Any], Optional[str]]:
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
        return (resp.data[0], None) if resp.data else (None, "Persona save returned no data")
    except Exception as exc:
        return None, f"Save failed: {exc}"


def get_personas(user_hash: str) -> Tuple[list, Optional[str]]:
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


def delete_persona(user_hash: str, persona_id: str) -> Tuple[bool, str]:
    """
    BUG-2 FIX: Correct signature is (user_hash, persona_id).
    Old signature was (persona_id, user_hash) — ownership check eq("user_hash", persona_id)
    never matched anything, so deletes silently did nothing.
    """
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


# ── SEARCH & UTILITIES ────────────────────────────────────────────────────────

def search_vault(
    user_hash: str,
    query: str,
    limit: int = 50,
    tag_filter: str = "",
    target_filter: str = "",
) -> Tuple[list, Optional[str]]:
    if SUPABASE_MISSING or supabase is None:
        return [], "Supabase not configured"

    q = (query or "").strip()
    if not q:
        return get_vault_items(user_hash, limit=limit)

    def _py_filter(items: list) -> list:
        ql = q.lower()
        r  = [
            i for i in items
            if ql in str(i.get("title",   "")).lower()
            or ql in str(i.get("tags",    "")).lower()
            or ql in str(i.get("target",  "")).lower()
            or ql in str(i.get("content", "")).lower()
        ]
        if tag_filter:
            r = [i for i in r if tag_filter.lower() in str(i.get("tags", "")).lower()]
        if target_filter:
            r = [i for i in r if str(i.get("target", "")).lower() == target_filter.lower()]
        return r[:limit]

    try:
        resp    = (
            supabase.table("vault")
            .select("*")
            .eq("user_hash", user_hash)
            .or_(f"title.ilike.%{q}%,tags.ilike.%{q}%,target.ilike.%{q}%")
            .order("created_at", desc=True)
            .limit(limit)
            .execute()
        )
        results = resp.data or []
        if not results:
            all_items, err = get_vault_items(user_hash, limit=200)
            if err:
                return [], err
            return _py_filter(all_items), None
        if tag_filter:
            results = [r for r in results if tag_filter.lower() in str(r.get("tags", "")).lower()]
        if target_filter:
            results = [r for r in results if str(r.get("target", "")).lower() == target_filter.lower()]
        return results, None
    except Exception:
        all_items, err = get_vault_items(user_hash, limit=200)
        if err:
            return [], err
        return _py_filter(all_items), None


def get_prompt_by_id(item_id: str, user_hash: str) -> Tuple[Optional[dict], Optional[str]]:
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
    item_id: str, user_hash: str, updates: dict,
) -> Tuple[Optional[Any], Optional[str]]:
    if SUPABASE_MISSING or supabase is None:
        return None, "Supabase not configured"
    safe = {k: v for k, v in updates.items() if k in {"title", "tags", "content"}}
    if not safe:
        return None, "No valid fields to update"
    try:
        resp = (
            supabase.table("vault")
            .update(safe)
            .eq("id", item_id)
            .eq("user_hash", user_hash)
            .execute()
        )
        return (resp.data[0], None) if resp.data else (None, "Update returned no data")
    except Exception as exc:
        return None, f"Update failed: {exc}"


def get_vault_stats(user_hash: str) -> Tuple[dict, Optional[str]]:
    """
    BUG-1 FIX: Returns (stats_dict, Optional[error_str]).

    vault.py:
        stats, err = get_vault_stats(user_hash)   # needs a 2-tuple
    Old code returned a bare dict → ValueError: cannot unpack non-sequence dict.
    """
    empty = {"count": 0, "total": 0, "avg_score": 0, "top_score": 0, "top_target": "—"}
    if SUPABASE_MISSING or supabase is None:
        return empty, "Supabase not configured"
    try:
        resp  = (
            supabase.table("vault")
            .select("score, target")
            .eq("user_hash", user_hash)
            .execute()
        )
        items = resp.data or []
        if not items:
            return empty, None
        scores  = [int(i.get("score") or 0) for i in items]
        targets = [str(i.get("target") or "") for i in items]
        return {
            "count":      len(items),
            "total":      len(items),
            "avg_score":  round(sum(scores) / len(scores)),
            "top_score":  max(scores),
            "top_target": max(set(targets), key=targets.count) if targets else "—",
        }, None
    except Exception as exc:
        return empty, f"Stats fetch failed: {exc}"


def get_all_tags(user_hash: str) -> list:
    if SUPABASE_MISSING or supabase is None:
        return []
    try:
        resp = (
            supabase.table("vault")
            .select("tags")
            .eq("user_hash", user_hash)
            .execute()
        )
        tags = set()
        for row in resp.data or []:
            for tag in (row.get("tags") or "").split(","):
                tag = tag.strip().lower()
                if tag:
                    tags.add(tag)
        return sorted(tags)
    except Exception:
        return []
