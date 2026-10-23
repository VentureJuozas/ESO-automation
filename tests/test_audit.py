from eso_agent.audit import build_audit, render_audit_html
from eso_agent.brief import build_reinforcement_brief, render_brief_html
from eso_agent.engine import RUNS, override_sync, run_sync_until_interrupt


def test_audit_json_has_tools_hash_and_override():
    snap = run_sync_until_interrupt("fail_capacity", delay=0)
    override_sync(snap["id"], "Planuojamas TR keitimas 400 į 630 kVA.")
    run = RUNS[snap["id"]]
    audit = build_audit(run, snap)
    assert audit["run_id"] == snap["id"]
    assert audit["immutable"] is True
    assert len(audit["sha256"]) == 64
    assert int(audit["sha256"], 16) >= 0
    tools = {t["tool"] for t in audit["tools"]}
    assert "parse_request" in tools
    assert "check_capacity" in tools
    assert "escalate" in tools
    assert any(t.get("inputs") is not None and t.get("outputs") is not None for t in audit["tools"])
    assert any(a["action"] == "engineer_override" for a in audit["engineer_actions"])
    html = render_audit_html(audit)
    assert audit["sha256"] in html
    assert "Įrankių kvietimai" in html
    assert "override" in html.lower() or "engineer_override" in html


def test_reinforcement_brief_options_and_html():
    snap = run_sync_until_interrupt("fail_capacity", delay=0)
    brief = (snap.get("escalate") or {}).get("brief")
    assert brief
    ids = {o["id"] for o in brief["options"]}
    assert {"tr_630", "feeder_split", "new_tp"} <= ids
    rec = next(o for o in brief["options"] if o["recommended"])
    assert rec["id"] == "tr_630"
    assert rec["cost_lo"] < rec["cost_hi"]
    assert rec["tag"] == "inferred"
    assert rec["owner"]
    assert rec["next_step"]
    html = render_brief_html(snap)
    assert "630" in html
    assert "inferred" in html or "prielaida" in html.lower()
    assert "ąčęėįšųūž" in html
    from eso_agent.brief import brief_pdf_bytes

    pdf = brief_pdf_bytes(snap)
    assert pdf[:4] == b"%PDF"
    assert b"DejaVu" in pdf
    built = build_reinforcement_brief({"after_kw": 327.7, "limit_80_kw": 320, "over_kw": 7.7}, pending_kw=25, pending_cases=3)
    assert built["pending_impact"]["pending_cases"] == 3
