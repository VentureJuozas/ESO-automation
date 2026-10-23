from eso_agent.engine import RUNS, batch_queue_sync, run_queue_case_sync
from eso_agent.queue import QUEUE, add_working_days, queue_hud, queue_public, reset_queue
from eso_agent.rules import HOUSEHOLD_DEADLINE_DAYS


def test_queue_seed_mix_and_sla():
    reset_queue()
    q = queue_public()
    assert 8 <= len(q["cases"]) <= 12
    mixes = {c["mix"] for c in q["cases"]}
    assert {"A", "B", "C", "fail", "missing"} <= mixes
    assert all(c["status"] == "new" for c in q["cases"])
    assert all(c["assignee"] for c in q["cases"])
    assert all("redaguota" in c["assignee"].lower() for c in q["cases"])
    sla = q["cases"][0]["sla"]
    assert sla["days"] == HOUSEHOLD_DEADLINE_DAYS
    assert sla["source"] == "rule"
    assert sla["deadline_at"] > sla["submitted_at"]
    late = next(c for c in q["cases"] if c["id"] == "q12")
    assert late["sla"]["overdue"] is True


def test_working_days_skip_weekend():
    from datetime import datetime

    friday = datetime(2026, 10, 16, 12, 0, 0).timestamp()
    plus_one = add_working_days(friday, 1)
    assert datetime.fromtimestamp(plus_one).weekday() == 0


def test_batch_queue_sync_updates_statuses_and_hud():
    reset_queue()
    RUNS.clear()
    snaps = batch_queue_sync()
    assert len(snaps) >= 8
    q = queue_public()
    statuses = {c["status"] for c in q["cases"]}
    assert statuses <= {"awaiting_approval", "escalated", "issued", "error", "waiting_data"}
    assert any(c["status"] == "waiting_data" for c in q["cases"])
    assert any(c["status"] == "awaiting_approval" for c in q["cases"])
    assert any(c["status"] == "escalated" and c["mix"] == "fail" for c in q["cases"])
    assert q["hud"]["processed"] >= 8
    assert q["hud"]["inbox_depth"] >= 1
    assert q["hud"]["assumption"] is True
    assert q["hud"]["saved_min_today"] > 0
    assert q["inbox"]
    hero = next(c for c in q["cases"] if c["id"] == "q01")
    assert hero["run_id"]
    assert hero["solution"] == "B"
    fail = next(c for c in q["cases"] if c["id"] == "q04")
    assert fail["status"] == "escalated"
    assert fail["brief_title"]


def test_single_queue_case_attaches_run():
    reset_queue()
    snap = run_queue_case_sync("q02")
    assert snap["queue_id"] == "q02"
    assert snap["status"] == "awaiting_approval"
    case = next(c for c in QUEUE if c["id"] == "q02")
    assert case["run_id"] == snap["id"]
    assert case["status"] == "awaiting_approval"
    hud = queue_hud()
    assert hud["processed"] >= 1
