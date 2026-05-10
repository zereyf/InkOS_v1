from types import SimpleNamespace

import vault.vault_engine as vault_engine


class FakeQuery:
    def __init__(self, table, store):
        self.table = table
        self.store = store
        self.filters = []
        self.payload = None
        self.action = "select"
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
        self.action = "insert"
        self.payload = payload
        return self

    def upsert(self, payload):
        self.action = "upsert"
        self.payload = payload
        return self

    def delete(self):
        self.action = "delete"
        return self

    def execute(self):
        rows = self.store.setdefault(self.table, [])
        if self.action in {"insert", "upsert"}:
            existing = next((row for row in rows if row.get("id") == self.payload.get("id")), None)
            if existing:
                existing.update(self.payload)
                data = [existing]
            else:
                rows.append(dict(self.payload))
                data = [dict(self.payload)]
            return SimpleNamespace(data=data)

        matched = [row for row in rows if self._matches(row)]
        if self.action == "delete":
            self.store[self.table] = [row for row in rows if not self._matches(row)]
            return SimpleNamespace(data=[])
        if self.limit_value is not None:
            matched = matched[: self.limit_value]
        return SimpleNamespace(data=matched)

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
        self.store = {"users": [], "vault": [], "personas": []}

    def table(self, name):
        return FakeQuery(name, self.store)


def install_fake_supabase(monkeypatch):
    fake = FakeSupabase()
    monkeypatch.setattr(vault_engine, "SUPABASE_MISSING", False)
    monkeypatch.setattr(vault_engine, "supabase", fake)
    return fake


def test_authenticate_terminal_hashes_pin_with_salt_and_verifies(monkeypatch):
    fake = install_fake_supabase(monkeypatch)

    created, create_error = vault_engine.authenticate_terminal("alice_1", "1234", is_new=True)
    logged_in, login_error = vault_engine.authenticate_terminal("alice_1", "1234", is_new=False)
    rejected, rejected_error = vault_engine.authenticate_terminal("alice_1", "9999", is_new=False)

    stored_hash = fake.store["users"][0]["pin_hash"]
    assert created and create_error is None
    assert stored_hash.startswith("pbkdf2_sha256$")
    assert "1234" not in stored_hash
    assert logged_in and login_error is None
    assert not rejected and rejected_error == "Invalid PIN"


def test_authenticate_terminal_accepts_legacy_sha256_hash(monkeypatch):
    fake = install_fake_supabase(monkeypatch)
    fake.store["users"].append({"id": "legacy", "pin_hash": vault_engine._legacy_sha256_pin("1234")})

    logged_in, error = vault_engine.authenticate_terminal("legacy", "1234", is_new=False)

    assert logged_in and error is None


def test_save_prompt_generates_stable_id_and_clamps_score(monkeypatch):
    fake = install_fake_supabase(monkeypatch)

    record, error = vault_engine.save_prompt(
        "alice_1",
        title=" Launch Plan ",
        tags="Ops,AI",
        content="Deploy safely",
        score="900",
    )
    second_record, second_error = vault_engine.save_prompt(
        "alice_1",
        title=" Launch Plan ",
        tags="Ops,AI",
        content="Deploy safely",
        score="-1",
    )

    assert error is None and second_error is None
    assert record["id"] == second_record["id"]
    assert record["score"] == 100
    assert second_record["score"] == 0
    assert fake.store["vault"][0]["tags"] == "ops,ai"
