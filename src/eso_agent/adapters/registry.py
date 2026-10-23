"""Issued TS registry. Mock = SQLite. Stub = SharePoint / document store."""
from __future__ import annotations

from typing import Any, Protocol

from eso_agent.store import connect


class RegistryPort(Protocol):
    mode: str

    def register(self, record: dict[str, Any]) -> dict[str, Any]: ...
    def get(self, ts_number: str) -> dict[str, Any] | None: ...


class MockRegistry:
    mode = "mock"

    def register(self, record: dict[str, Any]) -> dict[str, Any]:
        conn = connect()
        conn.execute(
            "CREATE TABLE IF NOT EXISTS ts_registry (number TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )
        import json

        conn.execute(
            "INSERT OR REPLACE INTO ts_registry (number, payload) VALUES (?, ?)",
            (record.get("ts_number") or record.get("id"), json.dumps(record, ensure_ascii=False, default=str)),
        )
        conn.commit()
        return {**record, "stored": True, "mode": "mock"}

    def get(self, ts_number: str) -> dict[str, Any] | None:
        import json

        conn = connect()
        conn.execute(
            "CREATE TABLE IF NOT EXISTS ts_registry (number TEXT PRIMARY KEY, payload TEXT NOT NULL)"
        )
        row = conn.execute("SELECT payload FROM ts_registry WHERE number = ?", (ts_number,)).fetchone()
        return json.loads(row["payload"]) if row else None


class StubRegistry:
    mode = "stub"
    target = "SharePoint issued-TS library"

    def register(self, record: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(f"Connect {self.target}")

    def get(self, ts_number: str) -> dict[str, Any] | None:
        raise NotImplementedError(f"Connect {self.target}")
