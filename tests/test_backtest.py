from eso_agent.backtest import all_gallery_cases, compare_case, reference_detail_cases, run_gallery
from eso_agent.engine import run_sync_until_interrupt


def test_gallery_includes_reference_and_history():
    cases = all_gallery_cases()
    ids = {c["id"] for c in cases}
    assert "26-E-37934" in ids
    assert "26-E-37536" in ids
    assert any(c["source"] == "ts_history_redacted" for c in cases)
    for c in cases:
        blob = " ".join(str(v) for v in c.values())
        assert "asmens kodas" not in blob.lower()
        assert "@" not in blob


def test_compare_case_is_honest_about_pg452():
    ref = next(c for c in reference_detail_cases() if c["id"] == "26-E-37934")
    snap = {
        "failed": False,
        "solution": {"id": "B"},
        "breaker": {"amps": 40},
        "cost": {"net": 2100},
        "draft": {"section3": "KAS ant atramos, C 40 A"},
        "status": "awaiting_approval",
        "id": "dummy",
    }
    cmp = compare_case(ref, snap)
    sol = next(f for f in cmp["fields"] if f["field"] == "solution")
    assert sol["match"] is False
    assert "Pg-452" in sol["explain"]
    cost = next(f for f in cmp["fields"] if f["field"] == "cost")
    assert cost["match"] is False
    assert 0 <= cmp["score"] <= 1


def test_run_gallery_scores_between_zero_and_one():
    payload = run_gallery()
    assert payload["count"] >= 3
    assert 0 <= payload["accuracy"] <= 1
    ids = {r["id"] for r in payload["results"]}
    assert "26-E-37934" in ids
    assert "26-E-37536" in ids
    pg = next(r for r in payload["results"] if r["id"] == "26-E-37934")
    assert any(f["match"] is False and f["explain"] for f in pg["fields"])
    assert pg["redacted"] is True
    live = run_sync_until_interrupt("hero", delay=0)
    assert live["status"] == "awaiting_approval"
