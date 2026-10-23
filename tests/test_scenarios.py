from eso_agent.engine import run_sync_until_interrupt


def test_solution_a_existing_cabinet():
    snap = run_sync_until_interrupt("solution_a", delay=0)
    assert snap["solution"]["id"] == "A"
    assert snap["failed"] is False
    assert snap["status"] == "awaiting_approval"
    assert "pakeisti" in snap["draft"]["section3"].lower() or "Esamoje" in snap["draft"]["section3"]


def test_solution_c_cable_cut_in():
    snap = run_sync_until_interrupt("solution_c", delay=0)
    assert snap["solution"]["id"] == "C"
    assert snap["failed"] is False
    assert snap["reliability"]["cut_in"]["applies"] is True
    assert snap["reliability"]["cut_in"]["affected_customers"] == 59
    assert "150" in snap["draft"]["section3"]


def test_fail_capacity_escalates():
    snap = run_sync_until_interrupt("fail_capacity", delay=0)
    assert snap["failed"] is True
    assert snap["capacity"]["escalate"] is True
    assert snap["status"] == "escalated"
    assert snap["escalate"]["status"] == "needs_engineer"
    assert snap["capacity"]["transformer_bar"]["after_kw"] > 320
    tools = [e["tool"] for e in snap["events"] if e.get("type") == "tool"]
    assert "draft_ts_section3" not in tools
    assert "escalate" in tools
