from eso_agent.engine import RUNS, create_run, reset_demo, run_sync_until_interrupt
from eso_agent.queue import reset_queue
from eso_agent.store import load_queue, load_runs, save_run


def test_run_survives_store_reload():
    snap = run_sync_until_interrupt("hero", delay=0)
    rid = snap["id"]
    loaded = load_runs()
    assert rid in loaded
    assert loaded[rid]["status"] == "awaiting_approval"
    assert any(e.get("tool") == "parse_request" for e in loaded[rid]["events"] if e.get("type") == "tool")


def test_reset_demo_reseeds_queue_and_clears_runs():
    run_sync_until_interrupt("hero", delay=0)
    assert RUNS
    q = reset_demo()
    assert len(q["cases"]) >= 8
    assert all(c["status"] == "new" for c in q["cases"])
    assert RUNS == {}
    assert load_runs() == {}
    stored = load_queue()
    assert len(stored) >= 8


def test_save_run_roundtrip_audit():
    run = create_run("hero", "", None)
    run["audit"] = [{"action": "approve", "reason": "ok", "ts": 1}]
    save_run(run)
    loaded = load_runs()
    assert loaded[run["id"]]["audit"][0]["action"] == "approve"
    reset_queue()
