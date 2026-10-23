from fastapi.testclient import TestClient

from app.main import app
from eso_agent.engine import run_sync_until_interrupt
from eso_agent.trace import build_trace


def test_hero_trace_kinds_and_stats():
    snap = run_sync_until_interrupt("hero", delay=0)
    trace = build_trace(snap)
    kinds = {s["tool"]: s["kind"] for s in trace["steps"]}
    assert kinds["parse_request"] == "llm"
    assert kinds["draft_ts_section3"] == "llm"
    assert kinds["select_solution"] == "tool"
    assert kinds["check_capacity"] == "tool"
    assert kinds["engineer_approval"] == "human"
    assert trace["stats"]["llm"] == 2
    assert trace["stats"]["python"] >= 8
    assert trace["stats"]["human"] == 1
    assert "LLM" in trace["stats"]["line"]
    assert "Python" in trace["stats"]["line"]
    assert "Human" in trace["stats"]["line"]
    parse = next(s for s in trace["steps"] if s["tool"] == "parse_request")
    assert parse["rule_ref"]["local"]
    assert parse["llm_role"] == "parse"


def test_trace_api():
    with TestClient(app) as c:
        r = c.post("/api/runs", json={"scenario_id": "hero"})
        rid = r.json()["id"]
        for _ in range(80):
            snap = c.get(f"/api/runs/{rid}").json()
            if snap["status"] in {"awaiting_approval", "issued"}:
                break
        tr = c.get(f"/api/runs/{rid}/trace").json()
        assert tr["stats"]["llm"] >= 1
        assert tr["stats"]["human"] >= 1
        assert "Human" in tr["stats"]["line"]
