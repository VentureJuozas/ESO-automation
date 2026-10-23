import pytest

from eso_agent.engine import RUNS, approve_sync, override_sync, run_sync_until_interrupt
from eso_agent.llm import parse_offline
from eso_agent.models import RequestForm


def test_fail_branches_at_capacity_and_skips_downstream():
    snap = run_sync_until_interrupt("fail_capacity", delay=0)
    tools = [e["tool"] for e in snap["events"] if e.get("type") == "tool"]
    assert snap["failed"] is True
    assert snap["status"] == "escalated"
    assert snap["capacity"]["escalate"] is True
    assert snap["capacity"]["transformer_bar"]["after_kw"] == pytest.approx(327.7)
    assert "escalate" in tools
    for skipped in (
        "check_voltage_drop",
        "check_reliability",
        "check_future",
        "draft_ts_section3",
        "estimate_cost",
        "render_map",
        "issue_ts",
    ):
        assert skipped not in tools
        assert skipped in snap["skipped"]
    pkg = snap["escalate"]
    assert pkg["numbers"]["after_kw"] == pytest.approx(327.7)
    assert pkg["numbers"]["limit_80_kw"] == 320
    assert pkg["failed_at"] == "check_capacity"
    with pytest.raises(ValueError):
        approve_sync(snap["id"])


def test_override_requires_reason_and_is_audited():
    snap = run_sync_until_interrupt("fail_capacity", delay=0)
    with pytest.raises(ValueError):
        override_sync(snap["id"], "short")
    out = override_sync(snap["id"], "TR 80 % riba viršyta, keisti transformatorių planuojama 2027 Q1.")
    assert out["overridden"] is True
    assert out["audit"]
    assert out["audit"][0]["action"] == "engineer_override"
    assert "transformatorių" in out["audit"][0]["reason"]
    tools = [e["tool"] for e in out["events"] if e.get("type") == "tool"]
    assert "draft_ts_section3" in tools
    assert out["status"] == "awaiting_approval"
    issued = approve_sync(out["id"])
    assert issued["status"] == "issued"


def test_hero_still_runs_full_path():
    snap = run_sync_until_interrupt("hero", delay=0)
    assert snap["skipped"] == []
    assert snap["status"] == "awaiting_approval"
    assert snap["draft"]["document"]["kw"] == 11
    assert snap["draft"]["document"]["customer"]
    assert "redaguota" in snap["draft"]["document"]["customer"].lower()


def test_parse_highlights_lithuanian_email():
    text = (
        "Prašome sąlygų sodybai. Reikia 11 kW, trys fazės, "
        "koordinatės 54,55929, 25,27955."
    )
    parsed = parse_offline(text, RequestForm(text=text))
    assert parsed.kw == 11
    assert parsed.phases == 3
    assert abs(parsed.lat - 54.55929) < 1e-5
    assert parsed.highlights
    fields = {h["field"] for h in parsed.highlights}
    assert "kw" in fields
    assert "coords" in fields
    assert parsed.extraction["kw"]["confidence"] >= 0.9


def test_replay_timings_are_nonzero():
    snap = run_sync_until_interrupt("hero", delay=0)
    times = [e["elapsed_ms"] for e in snap["events"] if e.get("type") == "tool"]
    assert all(t > 0 for t in times)
    assert snap["value"]["elapsed_ms"] == sum(times)
    assert snap["value"]["comparison"]["manual_min"] > 60
    assert snap["value"]["comparison"]["assumption"] is True
