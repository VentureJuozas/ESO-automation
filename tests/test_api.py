import os
import time

from fastapi.testclient import TestClient

from app.main import app

os.environ["ESO_STEP_DELAY"] = "0"


def _wait(c: TestClient, rid: str, tries: int = 80) -> dict:
    snap = None
    for _ in range(tries):
        snap = c.get(f"/api/runs/{rid}").json()
        if snap["status"] in {"awaiting_approval", "escalated", "issued", "error"}:
            return snap
        time.sleep(0.05)
    return snap


def test_health_and_hero_via_api():
    with TestClient(app) as c:
        assert c.get("/api/health").json()["ok"] is True
        sc = c.get("/api/scenarios").json()
        assert {s["id"] for s in sc} >= {"hero", "solution_a", "solution_c", "fail_capacity"}
        r = c.post("/api/runs", json={"scenario_id": "hero"})
        assert r.status_code == 200
        rid = r.json()["id"]
        snap = _wait(c, rid)
        assert snap["status"] == "awaiting_approval"
        assert snap["solution"]["id"] == "B"
        assert snap["location"]["element_id"] == "200/3"
        issued = c.post(f"/api/runs/{rid}/resume", json={"decision": "approve"}).json()
        assert issued["status"] == "issued"
        html = c.get(f"/api/runs/{rid}/ts.html")
        assert html.status_code == 200
        assert "200/3" in html.text
        assert "20 A" in html.text
        assert "11" in html.text
        assert "redaguota" in html.text.lower()
        samples = c.get("/api/samples").json()
        assert len(samples) >= 3


def test_fail_override_requires_reason_via_api():
    with TestClient(app) as c:
        r = c.post("/api/runs", json={"scenario_id": "fail_capacity"})
        rid = r.json()["id"]
        snap = _wait(c, rid)
        assert snap["status"] == "escalated"
        assert "check_voltage_drop" in snap["skipped"]
        denied = c.post(f"/api/runs/{rid}/resume", json={"decision": "approve"})
        assert denied.status_code == 400
        short = c.post(f"/api/runs/{rid}/resume", json={"decision": "override", "override_reason": "short"})
        assert short.status_code == 400
        ok = c.post(
            f"/api/runs/{rid}/resume",
            json={"decision": "override", "override_reason": "Planuojamas TR keitimas 2027 Q1."},
        )
        assert ok.status_code == 200
        assert ok.json()["overridden"] is True
        assert ok.json()["status"] == "awaiting_approval"
        assert ok.json()["audit"][0]["action"] == "engineer_override"
        brief = c.get(f"/api/runs/{rid}/brief.html")
        assert brief.status_code == 200
        assert "630" in brief.text
        audit = c.get(f"/api/runs/{rid}/audit.json").json()
        assert audit["sha256"]
        assert audit["tools"]
        html = c.get(f"/api/runs/{rid}/audit.html")
        assert html.status_code == 200
        assert audit["sha256"] in html.text


def test_queue_and_gallery_via_api():
    with TestClient(app) as c:
        reset = c.post("/api/queue/reset")
        assert reset.status_code == 200
        q = c.get("/api/queue").json()
        assert len(q["cases"]) >= 8
        started = c.post("/api/queue/q01/start")
        assert started.status_code == 200
        snap = _wait(c, started.json()["id"])
        assert snap["queue_id"] == "q01"
        assert snap["status"] in {"awaiting_approval", "escalated"}
        q2 = c.get("/api/queue").json()
        row = next(x for x in q2["cases"] if x["id"] == "q01")
        assert row["run_id"] == snap["id"]
        gal = c.get("/api/gallery").json()
        ids = {x["id"] for x in gal["cases"]}
        assert "26-E-37934" in ids
        ran = c.post("/api/gallery/run").json()
        assert 0 <= ran["accuracy"] <= 1
        assert ran["taxonomy"]["cases"]["tool_error"] == 0
        assert "in_scope_accuracy" in ran
        wiped = c.post("/api/demo/reset").json()
        assert wiped["hud"]["new"] >= 8
        assert all(x["status"] == "new" for x in wiped["cases"])
        assert ran["count"] >= 3
