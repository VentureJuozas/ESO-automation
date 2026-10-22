"""Recorded agent timings and assumed manual baselines for the value panel.

Agent milliseconds are replay recordings (offline demo). Manual minutes are
an engineering assumption, not ESO statistics.
"""
from __future__ import annotations

from typing import Any

# Recorded replay durations for the live canvas (offline / no API key).
REPLAY_MS: dict[str, int] = {
    "parse_request": 480,
    "locate_connection_point": 720,
    "select_solution": 390,
    "size_breaker": 210,
    "check_capacity": 940,
    "check_voltage_drop": 1100,
    "check_reliability": 360,
    "check_future": 340,
    "draft_ts_section3": 680,
    "estimate_cost": 430,
    "render_map": 510,
    "escalate": 280,
    "engineer_approval": 0,
    "issue_ts": 320,
}

# Assumed manual desk time per step. Tag: inferred / assumption.
MANUAL_MINUTES: dict[str, float] = {
    "parse_request": 8,
    "locate_connection_point": 25,
    "select_solution": 20,
    "size_breaker": 8,
    "check_capacity": 25,
    "check_voltage_drop": 30,
    "check_reliability": 15,
    "check_future": 15,
    "draft_ts_section3": 35,
    "estimate_cost": 20,
    "render_map": 15,
    "escalate": 20,
    "engineer_approval": 15,
    "issue_ts": 10,
}

MONTHLY_CASES_ASSUMPTION = 40
MONTHLY_NOTE = (
    "Prielaida: 40 buitinių 0,4 kV paraiškų per mėnesį vienam inžinieriui. "
    "Tai nėra ESO statistika."
)


def replay_ms(tool: str) -> int:
    return int(REPLAY_MS.get(tool, 400))


def comparison_payload(events: list[dict[str, Any]]) -> dict[str, Any]:
    tools = [e for e in events if e.get("type") == "tool"]
    rows = []
    agent_ms = 0
    manual_min = 0.0
    for ev in tools:
        tool = ev.get("tool") or ""
        ms = int(ev.get("elapsed_ms") or replay_ms(tool))
        mins = float(MANUAL_MINUTES.get(tool, 10))
        agent_ms += ms
        manual_min += mins
        rows.append(
            {
                "tool": tool,
                "title": ev.get("title_lt") or ev.get("title") or tool,
                "agent_ms": ms,
                "manual_min": mins,
                "tag": "inferred",
            }
        )
    saved_min = max(0.0, manual_min - agent_ms / 60000.0)
    monthly_hours = round(saved_min / 60.0 * MONTHLY_CASES_ASSUMPTION, 1)
    return {
        "rows": rows,
        "agent_ms": agent_ms,
        "manual_min": round(manual_min, 1),
        "saved_min": round(saved_min, 1),
        "monthly_cases": MONTHLY_CASES_ASSUMPTION,
        "monthly_hours": monthly_hours,
        "assumption": True,
        "manual_tag": "inferred",
        "note": MONTHLY_NOTE,
    }
