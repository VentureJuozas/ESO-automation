from fastapi.testclient import TestClient

from app.main import app


def test_health_and_hero_via_api():
    c = TestClient(app)
    assert c.get("/api/health").json()["ok"] is True
    sc = c.get("/api/scenarios").json()
    assert {s["id"] for s in sc} >= {"hero", "solution_a", "solution_c", "fail_capacity"}
    r = c.post("/api/runs", json={"scenario_id": "hero"})
    assert r.status_code == 200
    rid = r.json()["id"]
    # poll until interrupt
    snap = None
    for _ in range(40):
        snap = c.get(f"/api/runs/{rid}").json()
        if snap["status"] in {"awaiting_approval", "escalated", "error"}:
            break
    assert snap["status"] == "awaiting_approval"
    assert snap["solution"]["id"] == "B"
    assert snap["location"]["element_id"] == "200/3"
    issued = c.post(f"/api/runs/{rid}/resume", json={"decision": "approve"}).json()
    assert issued["status"] == "issued"
    html = c.get(f"/api/runs/{rid}/ts.html")
    assert html.status_code == 200
    assert "200/3" in html.text
    assert "20 A" in html.text
