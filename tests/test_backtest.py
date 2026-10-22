from eso_agent.backtest import (
    CAT_A,
    CAT_B,
    CAT_C,
    _breaker_amps,
    all_gallery_cases,
    compare_case,
    reference_detail_cases,
    run_gallery,
)
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
    assert sol["category"] == CAT_A
    assert "Pg-452" in (sol["explain"] + (cmp.get("note") or ""))
    assert cmp["out_of_scope"] is True
    assert cmp["in_scope"] is False
    assert 0 <= cmp["score"] <= 1


def test_breaker_extractor_ignores_line_and_fuse_amps():
    assert _breaker_amps("Ant oro linijos L-206 atramos(...).") is None
    assert _breaker_amps("saugiklį į 315 A. pakeisti į 630 A") is None
    assert _breaker_amps('trifazį „C“ charakteristikos 20 A automatinį jungiklį') == 20
    assert _breaker_amps("C 40 A") == 40


def test_history_uses_total_permitted_not_increment():
    case = next(c for c in all_gallery_cases() if c["id"] == "21-62367")
    assert case["kw"] == 11
    assert case["existing_kw"] == 5
    assert case["expected_breaker_a"] == 20


def test_run_gallery_taxonomy_and_no_tool_errors():
    payload = run_gallery()
    assert payload["count"] >= 3
    assert 0 <= payload["accuracy"] <= 1
    assert 0 <= payload["in_scope_accuracy"] <= 1
    assert payload["in_scope_count"] >= 6
    assert payload["in_scope_accuracy"] >= 0.85
    assert payload["accuracy"] >= 0.75
    assert payload["before"]["accuracy"] == 0.51
    tax = payload["taxonomy"]
    assert tax["cases"][CAT_C] == 0
    assert tax["field_mismatches"][CAT_C] == 0
    assert tax["cases"][CAT_A] >= 1
    ids = {r["id"] for r in payload["results"]}
    assert "26-E-37934" in ids
    pg = next(r for r in payload["results"] if r["id"] == "26-E-37934")
    assert pg["category"] == CAT_A
    assert pg["redacted"] is True
    hero_hist = next(r for r in payload["results"] if r["id"] == "21-62367")
    assert hero_hist["agent"]["breaker_a"] == 20
    assert hero_hist["agent"]["solution"] == "A"
    missing = [r for r in payload["results"] if r["category"] == CAT_B]
    assert missing
    live = run_sync_until_interrupt("hero", delay=0)
    assert live["status"] == "awaiting_approval"
