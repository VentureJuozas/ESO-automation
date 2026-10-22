"""SQLite persistence for queue, runs and audit. Survives process restart."""
from __future__ import annotations

import json
import os
import sqlite3
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "data" / "demo.sqlite"

_CONN: sqlite3.Connection | None = None


def db_path() -> Path:
    raw = os.environ.get("ESO_DB")
    if raw == ":memory:":
        return Path(":memory:")
    return Path(raw) if raw else DEFAULT_DB


def connect() -> sqlite3.Connection:
    global _CONN
    if _CONN is not None:
        return _CONN
    path = db_path()
    if path.name != ":memory:":
        path.parent.mkdir(parents=True, exist_ok=True)
        _CONN = sqlite3.connect(str(path), check_same_thread=False)
    else:
        _CONN = sqlite3.connect(":memory:", check_same_thread=False)
    _CONN.row_factory = sqlite3.Row
    _CONN.execute(
        "CREATE TABLE IF NOT EXISTS runs (id TEXT PRIMARY KEY, payload TEXT NOT NULL, updated_at REAL)"
    )
    _CONN.execute(
        "CREATE TABLE IF NOT EXISTS queue (id TEXT PRIMARY KEY, payload TEXT NOT NULL)"
    )
    _CONN.execute(
        "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)"
    )
    _CONN.commit()
    return _CONN


def reset_connection() -> None:
    global _CONN
    if _CONN is not None:
        try:
            _CONN.close()
        except sqlite3.Error:
            pass
        _CONN = None


def _dump_run(run: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": run.get("id"),
        "scenario_id": run.get("scenario_id"),
        "status": run.get("status"),
        "started": run.get("started"),
        "events": run.get("events") or [],
        "state": run.get("state") or {},
        "error": run.get("error"),
        "audit": run.get("audit") or [],
        "queue_id": run.get("queue_id"),
        "assignee": run.get("assignee"),
        "title": run.get("title"),
        "submitted_at": run.get("submitted_at"),
        "delay": run.get("delay"),
    }


def save_run(run: dict[str, Any]) -> None:
    if not run.get("id"):
        return
    conn = connect()
    conn.execute(
        "INSERT OR REPLACE INTO runs (id, payload, updated_at) VALUES (?, ?, ?)",
        (run["id"], json.dumps(_dump_run(run), ensure_ascii=False, default=str), time.time()),
    )
    conn.commit()


def load_runs() -> dict[str, dict[str, Any]]:
    conn = connect()
    out: dict[str, dict[str, Any]] = {}
    for row in conn.execute("SELECT id, payload FROM runs"):
        payload = json.loads(row["payload"])
        payload["queues"] = []
        out[row["id"]] = payload
    return out


def save_queue(cases: list[dict[str, Any]]) -> None:
    conn = connect()
    conn.execute("DELETE FROM queue")
    for c in cases:
        slim = {k: v for k, v in c.items()}
        conn.execute(
            "INSERT INTO queue (id, payload) VALUES (?, ?)",
            (c["id"], json.dumps(slim, ensure_ascii=False, default=str)),
        )
    conn.commit()


def load_queue() -> list[dict[str, Any]]:
    conn = connect()
    rows = list(conn.execute("SELECT payload FROM queue"))
    return [json.loads(r["payload"]) for r in rows]


def clear_all() -> None:
    conn = connect()
    conn.execute("DELETE FROM runs")
    conn.execute("DELETE FROM queue")
    conn.execute("DELETE FROM meta")
    conn.commit()
