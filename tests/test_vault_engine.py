"""
tests/test_vault_engine.py
===========================
Tests for vault_engine with PBKDF2 PIN hashing, legacy SHA-256 migration,
and get_vault_stats tuple return contract.
"""

from types import SimpleNamespace

import vault.vault_engine as vault_engine


# ── FAKE SUPABASE ─────────────────────────────────────────────────────────────

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

    def single(self):
        self._single = True
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

        matched = [row for row in rows if self._matches(row)]
        if self.action == "delete":
            self.store[self.table] = [r for r in rows if not self._matches(r)]
            return SimpleNamespace(data=[], count=0)
        if self.limit_value is not None:
            matched = matched[: self.limit_value]
        # single() behaviour
        if getattr(self, "_single", False):
            return SimpleNamespace(data=matched[0] if matched else None, count=len(matched))
        return SimpleNamespace(data=matched, count=len(matched))

    def _matches(self, row):
        for field, expected in self.filters:
            if isinstance(expected, tuple) and expected[0] == "ilike":
                if expected[1] not in str(row.get(field, "")).lower():
                    return False
            elif row.get(field) != expected:
                return False
        return True


class FakeSupabase:
    def __init__(self):
        self.store: dict = {"users": [], "vault": [], "personas": []}

    def table(self, name):
        return FakeQuery(name, self.store)


def _install(monkeypatch):
    fake = FakeSupabase()
    monkeypatch.setattr(vault_engine, "SUPABASE_MISSING", False)
    monkeypatch.setattr(vault_engine, "supabase", fake)
    return fake


# ── AUTH TESTS ────────────────────────────────────────────────────────────────

def test_authenticate_terminal_uses_pbkdf2_and_verifies(monkeypatch):
    fake = _install(monkeypatch)

    ok, err = vault_engine.authenticate_terminal("alice", "1234", is_new=True)
    assert ok and err is None

    stored_hash = fake.store["users"][0]["pin_hash"]
    assert stored_hash.startswith("pbkdf2_sha256$"), (
        f"Expected pbkdf2_sha256$ prefix, got: {stored_hash[:30]}"
    )
    assert "1234" not in stored_hash

    ok2, err2 = vault_engine.authenticate_terminal("alice", "1234", is_new=False)
    assert ok2 and err2 is None

    ok3, err3 = vault_engine.authenticate_terminal("alice", "9999", is_new=False)
    assert not ok3
    assert err3 == "Invalid PIN"


def test_authenticate_terminal_accepts_legacy_sha256_hash(monkeypatch):
    """
    Users with old SHA-256 hashes must still be able to log in.
    After successful login the hash is transparently upgraded to PBKDF2.
    """
    fake = _install(monkeypatch)
    legacy_hash = vault_engine._legacy_sha256_pin("1234")
    fake.store["users"].append({
        "id":              "legacy_user",
        "pin_hash":        legacy_hash,
        "salt":            "",
        "failed_attempts": 0,
        "lockout_until":   None,
    })

    ok, err = vault_engine.authenticate_terminal("legacy_user", "1234", is_new=False)
    assert ok and err is None

    updated_hash = fake.store["users"][0]["pin_hash"]
    assert updated_hash.startswith("pbkdf2_sha256$"), (
        "Successful legacy login should upgrade hash to PBKDF2"
    )


def test_legacy_sha256_pin_is_deterministic():
    """_legacy_sha256_pin must produce a consistent hex digest."""
    h1 = vault_engine._legacy_sha256_pin("password")
    h2 = vault_engine._legacy_sha256_pin("password")
    assert h1 == h2
    assert len(h1) == 64  # SHA-256 hex


# ── VAULT TESTS ───────────────────────────────────────────────────────────────

def test_save_prompt_generates_stable_id_and_clamps_score(monkeypatch):
    fake = _install(monkeypatch)

    record, error = vault_engine.save_prompt(
        "alice",
        title="Launch Plan",
        tags="Ops,AI",
        content="Deploy safely",
        score="900",
    )
    second, err2 = vault_engine.save_prompt(
        "alice",
        title="Launch Plan",
        tags="Ops,AI",
        content="Deploy safely",
        score="-1",
    )

    assert error is None and err2 is None
    assert record["score"] == 100
    assert second["score"] == 0
    assert record["tags"] == "ops,ai"


def test_get_vault_stats_returns_tuple(monkeypatch):
    """
    BUG-STATS: get_vault_stats must return (dict, Optional[str]).
    vault.py unpacks it as ``stats, err = get_vault_stats(uid)`` — bare dict
    return caused a runtime ValueError on every call.
    """
    fake = _install(monkeypatch)
    fake.store["vault"].append({
        "user_hash": "alice",
        "score": 85,
        "target": "Claude",
    })

    result = vault_engine.get_vault_stats("alice")

    assert isinstance(result, tuple) and len(result) == 2, (
        "get_vault_stats must return a 2-tuple (stats, error)"
    )
    stats, err = result
    assert err is None
    assert stats["count"] == 1
    assert stats["avg_score"] == 85
    assert stats["top_target"] == "Claude"
