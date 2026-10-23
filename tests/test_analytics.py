from fastapi.testclient import TestClient

from app.main import app
from eso_agent.analytics import analytics_payload, seed_synthetic_month
from eso_agent.present import BEATS, TOTAL_MS
from eso_agent.store import clear_all, reset_connection


def test_synthetic_month_and_payload():
    reset_connection()
    clear_all()
    rows = seed_synthetic_month(force=True)
    assert len(rows) >= 40
    assert all(r["synthetic"] for r in rows)
    payload = analytics_payload()
    assert payload["synthetic"] is True
    assert "Sintetinis" in payload["label"]
    assert payload["assumption"] is True
    assert payload["throughput_total"] == len(rows)
    assert payload["median_stage"]["agent_s"]
    assert payload["median_stage"]["engineer_min"]
    assert payload["bottleneck"]["missing_data_h"] >= 0
    assert payload["bottleneck"]["engineer_approval_h"] >= 0
    assert set(payload["mix"]) >= {"A", "B", "C", "escalate", "waiting"}
    assert payload["mix"]["B"] >= payload["mix"]["A"]
    assert payload["hours_saved_h"] > 0
    assert payload["hours_saved_note"]
    assert payload["sla"]["at_risk"] >= 1
    assert payload["sla"]["cases"]


def test_analytics_api_and_present_beat():
    with TestClient(app) as c:
        data = c.get("/api/analytics").json()
        assert data["synthetic"] is True
        assert data["throughput"]
        pack = c.get("/api/present").json()
        assert any(b["id"] == "analytics" for b in pack["beats"])
        assert pack["analytics"]["synthetic"] is True
        assert pack["total_ms"] == TOTAL_MS
        assert 270000 <= TOTAL_MS <= 300000
        assert any(b["id"] == "analytics" for b in BEATS)
