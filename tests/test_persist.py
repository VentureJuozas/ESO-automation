from eso_agent.engine import create_run, run_sync_until_interrupt
from eso_agent.store import load_runs, save_run


def test_run_survives_store_reload():
    snap = run_sync_until_interrupt("hero", delay=0)
    rid = snap["id"]
    loaded = load_runs()
    assert rid in loaded
    assert loaded[rid]["status"] == "awaiting_approval"
    assert any(e.get("tool") == "parse_request" for e in loaded[rid]["events"] if e.get("type") == "tool")


def test_save_run_roundtrip_audit():
    run = create_run("hero", "", None)
    run["audit"] = [{"action": "approve", "reason": "ok", "ts": 1}]
    save_run(run)
    loaded = load_runs()
    assert loaded[run["id"]]["audit"][0]["action"] == "approve"
