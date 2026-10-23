from eso_agent.backtest import run_gallery_whatif
from eso_agent.engine import run_sync_until_interrupt, supply_data, whatif
from eso_agent.present import frozen_pack


def test_missing_coords_waits_and_resumes():
    snap = run_sync_until_interrupt(
        "intake",
        delay=0,
        form={"text": "Sveiki, 11 kW, trys fazės. Adreso nerašau.", "object_name": "Sodyba"},
    )
    assert snap["status"] == "waiting_data"
    assert snap["missing"]["letter"]["sent"] is False
    assert snap["missing"]["gaps"]
    assert snap["missing"]["letter"]["to"]
    assert "neišsiųstas" in snap["missing"]["letter"]["body"]
    assert snap["missing"]["provisional"]["sensitivity"]
    resumed = supply_data(snap["id"], {"lat": 54.55929, "lon": 25.27955, "kw": 11, "phases": 3})
    assert resumed["status"] == "awaiting_approval"
    assert resumed["solution"]["id"] == "B"


def test_whatif_11_to_100_escalates():
    ok = whatif({"kw": 11, "phases": 3, "distance_m": 66, "pending_kw": 0})
    assert ok["status"] == "awaiting_approval"
    assert ok["solution"]["id"] in {"A", "B", "C"}
    assert ok["capacity"]["pass"] is True
    fail = whatif({"kw": 100, "phases": 3, "distance_m": 66, "pending_kw": 0})
    assert fail["failed"] is True
    assert fail["status"] == "escalated"
    assert fail["capacity"]["escalate"] is True


def test_gallery_whatif_fill_resolves_some():
    payload = run_gallery_whatif()
    assert payload["mode"] == "whatif"
    assert payload["missing_count"] == 7
    assert payload["resolved_matches"] >= 6
    assert all(r.get("whatif") for r in payload["results"])


def test_present_pack_frozen_beats():
    pack = frozen_pack()
    assert pack["frozen"] is True
    assert len(pack["beats"]) >= 8
    assert pack["hero"]["solution"]["id"] == "B"
    assert pack["fail"]["failed"] is True
    assert pack["beats"][0]["en"]["title"]
    assert pack["audit"]["sha256"]
    assert 270000 <= pack["total_ms"] <= 315000
    assert any(b["id"] == "analytics" for b in pack["beats"])
    assert pack.get("analytics", {}).get("synthetic") is True
    assert all(b.get("dwell_ms") for b in pack["beats"])
    assert pack["beats"][-1]["dwell_ms"] == 30000
