"""Customer portal / CRM. Mock = SQLite redacted apps. Stub = official savitarna."""
from __future__ import annotations

import json
import time
import uuid
from typing import Any, Protocol

from eso_agent.store import connect

REDACTED_ADDRESS = "Adresas redaguotas, objektas prie TP 12-608 (koordinatės, be gatvės)"
REDACTED_NAME = "Buitinis vartotojas (redaguota)"


def _ensure() -> None:
    connect().execute(
        "CREATE TABLE IF NOT EXISTS portal_apps (id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at REAL)"
    )
    connect().commit()


class CrmPort(Protocol):
    mode: str

    def create(self, payload: dict[str, Any]) -> dict[str, Any]: ...
    def get(self, app_id: str) -> dict[str, Any] | None: ...
    def list(self) -> list[dict[str, Any]]: ...
    def update(self, app_id: str, patch: dict[str, Any]) -> dict[str, Any]: ...


class MockCrm:
    mode = "mock"

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        _ensure()
        app_id = payload.get("id") or f"p{uuid.uuid4().hex[:8]}"
        rec = {
            "id": app_id,
            "created_at": time.time(),
            "status": "gauta",
            "run_id": payload.get("run_id"),
            "queue_id": payload.get("queue_id"),
            "kw": payload.get("kw") or 11,
            "phases": payload.get("phases") or 3,
            "lat": payload.get("lat"),
            "lon": payload.get("lon"),
            "object_name": payload.get("object_name") or "Naujas buitinis objektas",
            "address": REDACTED_ADDRESS,
            "customer": REDACTED_NAME,
            "note": "Demonstracinis maketas. Asmens duomenų nėra.",
        }
        connect().execute(
            "INSERT OR REPLACE INTO portal_apps (id, payload, updated_at) VALUES (?, ?, ?)",
            (app_id, json.dumps(rec, ensure_ascii=False, default=str), time.time()),
        )
        connect().commit()
        return rec

    def get(self, app_id: str) -> dict[str, Any] | None:
        _ensure()
        row = connect().execute("SELECT payload FROM portal_apps WHERE id = ?", (app_id,)).fetchone()
        return json.loads(row["payload"]) if row else None

    def list(self) -> list[dict[str, Any]]:
        _ensure()
        rows = connect().execute("SELECT payload FROM portal_apps").fetchall()
        return [json.loads(r["payload"]) for r in rows]

    def update(self, app_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        rec = self.get(app_id)
        if not rec:
            raise KeyError(app_id)
        rec.update(patch)
        rec["address"] = REDACTED_ADDRESS
        rec["customer"] = REDACTED_NAME
        connect().execute(
            "INSERT OR REPLACE INTO portal_apps (id, payload, updated_at) VALUES (?, ?, ?)",
            (app_id, json.dumps(rec, ensure_ascii=False, default=str), time.time()),
        )
        connect().commit()
        return rec


class StubCrm:
    mode = "stub"
    target = "ESO savitarna / CRM queue"

    def create(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(f"Connect {self.target}")

    def get(self, app_id: str) -> dict[str, Any] | None:
        raise NotImplementedError(f"Connect {self.target}")

    def list(self) -> list[dict[str, Any]]:
        raise NotImplementedError(f"Connect {self.target}")

    def update(self, app_id: str, patch: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError(f"Connect {self.target}")
