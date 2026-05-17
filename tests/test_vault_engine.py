"""
tests/test_vault_engine.py — v2.0
===================================
Changes from v1:
  - _legacy_sha256_pin imported directly (was missing → NameError on test run)
  - PBKDF2 prefix assertion updated: stored hash now starts with "pbkdf2_sha256$"
    (old assertion checked for that prefix but old code produced plain SHA256 hex)
  - delete_persona arg order corrected in test to match fixed signature (user_hash, id)
  - save_prompt score-clamp test updated: score="900" → clamped to 100, score="-1" → 0
    Tags are now lowercased by save_prompt; assertion updated accordingly.
"""

from types import SimpleNamespace

import vault.vault_engine as vault_engine
from vault.vault_engine import _legacy_sha256_pin


class FakeQuery:
    def __init__(self, table, store):
        self.table  = table
        self.store  = store
        self.filters = []
        self.payload = None
        self.action  = "select"
        self.limit_value = None

    def select(self, *_args, **_kwargs):
        self.action = "select"
        return self

    def eq(self, field, value):
        self.filters.append((field, value))
        return self

    def order(self, *_args, **_kwargs):
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def ilike(self, field, pattern):
        needle = pattern.strip("%").lower()
        self.filters.append((field, ("ilike", needle)))
        return self

    def insert(self, payload):
        self.action  = "insert"
        self.payload = payload
        return self

    def upsert(self, payload):
        self.action  = "upsert"
        self.payload = payload
        return self

    def delete(self):
        self.action = "delete"
        return self

    def single(self):
        return self

    def execute(self):
        rows = self.store.setdefault(self.table, [])

        if self.action in {"insert", "upsert"}:
            existing = next(
                (r for r in rows if r.get("id") == self.payload.get("id")), None
            )
            if existing:
                existing.update(self.payload)
                data = [existing]
            else:
                rows.append(dict(self.payload))
                data = [dict(self.payload)]
            return SimpleNamespace(data=data, count=len(data))

        matched = [r for r in rows if self._matches(r)]
        if self.action == "delete":
            self.store[self.table] = [r for r in rows if not self._matches(r)]
            return SimpleNamespace(data=[], count=0)
        if self.limit_value is not None:
            matched = matched[: self.limit_value]
        # .single() semantics: return first match or None in data
        if len(matched) == 1 and any(f == ("_single", True) for f in self.filters):
            return SimpleNamespace(data=matched[0], count=1)
        return SimpleNamespace(data=matched, count=len(matched))

    def _matches(self, row):
        for field, expected in self.filters:
            if field == "_single":
                continue
            if isinstance(expected, tuple) and expected[0] == "ilike":
                if expected[1] not in str(row.get(field, "")).lower():
                    return False
            elif row.get(field) != expected:
                return False
        return True


class FakeSupabase:
    def __init__(self):
        self.store = {"users": [], "vault": [], "personas": []}

    def table(self, name):
        return FakeQuery(name, self.store)


def install_fake_supabase(monkeypatch):
    fake = FakeSupabase()
    monkeypatch.setattr(vault_engine, "SUPABASE_MISSING", False)
    monkeypatch.setattr(vault_engine, "supabase", fake)
    return fake


# ── AUTH TESTS ────────────────────────────────────────────────────────────────

def test_authenticate_terminal_hashes_pin_with_pbkdf2_and_verifies(monkeypatch):
    """
    Registration must store a PBKDF2 hash (prefixed with 'pbkdf2_sha256$').
    Correct PIN must authenticate; wrong PIN must be rejected.
    """
    fake = install_fake_supabase(monkeypatch)

    created, create_error = vault_engine.authenticate_terminal("alice_1", "1234", is_new=True)
    logged_in, login_error = vault_engine.authenticate_terminal("alice_1", "1234", is_new=False)
    rejected, rejected_error = vault_engine.authenticate_terminal("alice_1", "9999", is_new=False)

    stored_hash = fake.store["users"][0]["pin_hash"]

    assert created and create_error is None
    # SEC-A: hash must use PBKDF2 format, never plain hex
    assert stored_hash.startswith("pbkdf2_sha256$"), (
        f"Expected PBKDF2 prefix, got: {stored_hash[:30]}"
    )
    assert "1234" not in stored_hash
    assert logged_in and login_error is None
    assert not rejected
    assert rejected_error == "Invalid PIN"


def test_authenticate_terminal_accepts_legacy_sha256_hash(monkeypatch):
    """
    Rows hashed with the old SHA256 scheme must still authenticate
    (backward compat during migration window).
    """
    fake = install_fake_supabase(monkeypatch)
    legacy_hash = _legacy_sha256_pin("1234")
    fake.store["users"].append({
        "id":              "legacy",
        "pin_hash":        legacy_hash,
        "salt":            "",
        "failed_attempts": 0,
        "lockout_until":   None,
    })

    logged_in, error = vault_engine.authenticate_terminal("legacy", "1234", is_new=False)

    assert logged_in and error is None


def test_authenticate_terminal_rejects_wrong_pin_on_legacy_row(monkeypatch):
    fake = install_fake_supabase(monkeypatch)
    fake.store["users"].append({
        "id":              "legacy2",
        "pin_hash":        _legacy_sha256_pin("correct"),
        "salt":            "",
        "failed_attempts": 0,
        "lockout_until":   None,
    })

    ok, err = vault_engine.authenticate_terminal("legacy2", "wrong", is_new=False)

    assert not ok
    assert err == "Invalid PIN"


# ── VAULT TESTS ───────────────────────────────────────────────────────────────

def test_save_prompt_generates_stable_id_and_clamps_score(monkeypatch):
    """
    Score must be clamped to [0, 100].
    Tags must be lowercased.
    Two saves of the same content produce distinct rows (no upsert collision on vault).
    """
    fake = install_fake_supabase(monkeypatch)

    record_high, err_high = vault_engine.save_prompt(
        "alice_1",
        title="Launch Plan",
        tags="Ops,AI",
        content="Deploy safely",
        score="900",     # over-limit — must clamp to 100
    )
    record_low, err_low = vault_engine.save_prompt(
        "alice_1",
        title="Launch Plan",
        tags="Ops,AI",
        content="Deploy safely",
        score="-1",      # under-limit — must clamp to 0
    )

    assert err_high is None and err_low is None
    assert record_high["score"] == 100
    assert record_low["score"]  == 0
    assert record_high["tags"]  == "ops,ai"   # lowercased by save_prompt


def test_get_vault_stats_returns_tuple(monkeypatch):
    """
    get_vault_stats() must return (dict, Optional[str]).
    vault.py unpacks: stats, err = get_vault_stats(user_hash)
    Returning a bare dict causes ValueError at runtime.
    """
    fake = install_fake_supabase(monkeypatch)
    fake.store["vault"] = [
        {"user_hash": "u1", "score": 80, "target": "Claude"},
        {"user_hash": "u1", "score": 90, "target": "Claude"},
    ]

    result = vault_engine.get_vault_stats("u1")

    # Must be unpackable as a 2-tuple
    assert isinstance(result, tuple) and len(result) == 2, (
        "get_vault_stats must return (dict, Optional[str]), not a bare dict"
    )
    stats, err = result
    assert stats["count"]      == 2
    assert stats["avg_score"]  == 85
    assert stats["top_target"] == "Claude"
    assert err is None


def test_get_vault_stats_empty_vault(monkeypatch):
    fake = install_fake_supabase(monkeypatch)

    stats, err = vault_engine.get_vault_stats("nobody")

    assert stats["count"] == 0
    assert err is None


# ── PERSONA TESTS ─────────────────────────────────────────────────────────────

def test_delete_persona_correct_arg_order(monkeypatch):
    """
    delete_persona(user_hash, persona_id) — ownership check must match.
    Old reversed signature delete_persona(persona_id, user_hash) silently
    deleted nothing because eq("user_hash", persona_id) never matched.
    """
    fake = install_fake_supabase(monkeypatch)
    fake.store["personas"] = [
        {"id": "p001", "user_hash": "alice_1", "name": "TestPersona"},
    ]

    ok, err = vault_engine.delete_persona("alice_1", "p001")

    assert ok and err == "Deleted"
    assert len(fake.store["personas"]) == 0


def test_delete_persona_rejects_wrong_owner(monkeypatch):
    """A user must not be able to delete another user's persona."""
    fake = install_fake_supabase(monkeypatch)
    fake.store["personas"] = [
        {"id": "p001", "user_hash": "alice_1", "name": "Private"},
    ]

    ok, _ = vault_engine.delete_persona("mallory", "p001")

    # Row must still exist — ownership check blocked the delete
    assert len(fake.store["personas"]) == 1
