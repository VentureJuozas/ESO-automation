import os
import time

from fastapi.testclient import TestClient

from app.main import app

os.environ["ESO_STEP_DELAY"] = "0"


def _wait(c: TestClient, rid: str, tries: int = 80) -> dict:
    snap = None
    for _ in range(tries):
        snap = c.get(f"/api/runs/{rid}").json()
        if snap["status"] in {"awaiting_approval", "escalated", "issued", "error", "waiting_data"}:
            return snap
        time.sleep(0.05)
    return snap


def test_health_and_hero_via_api():
    with TestClient(app) as c:
        assert c.get("/api/health").json()["ok"] is True
        r = c.post("/api/runs", json={"scenario_id": "hero"})
        assert r.status_code == 200
        rid = r.json()["id"]
        snap = _wait(c, rid)
        assert snap["status"] == "awaiting_approval"
        assert snap["solution"]["id"] == "B"
        assert snap["location"]["element_id"] == "200/3"
        assert snap["capacity"]["load_loss"]["ampacity_a"] == 160
        assert snap["quality"]["load_loss"]["to_customer"][-1]["id"] == "200/3"
        issued = c.post(f"/api/runs/{rid}/resume", json={"decision": "approve"}).json()
        assert issued["status"] == "issued"
        html = c.get(f"/api/runs/{rid}/ts.html")
        assert html.status_code == 200
        assert "200/3" in html.text
        assert "20 A" in html.text
        assert "11" in html.text
        assert "DEMONSTRACINIS" not in html.text
        assert "n8n" not in html.text.lower()
        audit = c.get(f"/api/runs/{rid}/audit.html")
        assert audit.status_code == 200


def test_fail_override_requires_reason_via_api():
    with TestClient(app) as c:
        r = c.post("/api/runs", json={"scenario_id": "fail_capacity"})
        rid = r.json()["id"]
        snap = _wait(c, rid)
        assert snap["status"] == "escalated"
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
        audit = c.get(f"/api/runs/{rid}/audit.json").json()
        assert audit["sha256"]
        assert audit["tools"]
