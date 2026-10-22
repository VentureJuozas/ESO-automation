from eso_agent.cost import estimate_cost
from eso_agent.engine import approve_sync, run_sync_until_interrupt, samples_public
from eso_agent.graph import after_capacity, mermaid
from eso_agent.llm import parse_offline
from eso_agent.models import RequestForm


def test_samples_parse_offline():
    samples = samples_public()
    assert len(samples) >= 3
    parsed = [parse_offline(s["text"], RequestForm(text=s["text"])) for s in samples]
    assert parsed[0].kw == 11
    assert parsed[0].phases == 3
    assert parsed[0].highlights
    assert parsed[2].kw == 100


def test_intake_email_runs_hero_path():
    text = samples_public()[0]["text"]
    snap = run_sync_until_interrupt("intake", delay=0, text=text, form={"text": text})
    assert snap["status"] == "awaiting_approval"
    assert snap["solution"]["id"] == "B"
    assert snap["parsed"]["kw"] == 11
    assert snap["parsed"]["highlights"]
    issued = approve_sync(snap["id"])
    assert issued["status"] == "issued"
    assert issued["issued"]["document"]["customer"]


def test_mermaid_fail_branches_at_capacity():
    chart = mermaid()
    assert "check_capacity" in chart
    assert "escalate" in chart
    assert after_capacity({"failed": True}) == "escalate"
    assert after_capacity({"failed": False}) == "check_voltage_drop"


def test_cost_lines_carry_source_tags():
    cost = estimate_cost("B", 12)
    assert cost["labour"] > 0
    assert abs(cost["gross"] - cost["net"] * 1.21) < 0.05
    assert {line["source"] for line in cost["lines"]} >= {"real", "synthetic"}
    labour = next(line for line in cost["lines"] if line["id"] == "labour")
    assert "11,78" in labour["item"] or "11.78" in labour["item"]
