"""Manager analytics from SQLite runs plus a labelled synthetic month."""
from __future__ import annotations

import random
import statistics
import time
from datetime import date, datetime, timedelta, timezone
from typing import Any

from eso_agent.queue import sla_for
from eso_agent.store import (
    load_runs,
    load_synthetic_history,
    save_synthetic_history,
)
from eso_agent.timing import MANUAL_MINUTES, MONTHLY_CASES_ASSUMPTION, MONTHLY_NOTE

SEED_NOTE = "Sintetinis mėnuo, ne ESO statistika, aiškiai pažymėta synthetic"
HOURS_SAVED_PER_ISSUED = round(sum(MANUAL_MINUTES.values()) / 60.0, 2)  # assumption


def _working_days(end: date, n: int = 22) -> list[date]:
    days: list[date] = []
    d = end
    while len(days) < n:
        if d.weekday() < 5:
            days.append(d)
        d -= timedelta(days=1)
    days.reverse()
    return days


def seed_synthetic_month(*, force: bool = False) -> list[dict[str, Any]]:
    existing = load_synthetic_history()
    if existing and not force and any(r.get("at_risk") for r in existing):
        return existing
    rng = random.Random(26)
    days = _working_days(date.today(), 22)
    outcomes = (
        ["B"] * 28
        + ["A"] * 8
        + ["C"] * 4
        + ["escalate"] * 6
        + ["waiting"] * 5
    )
    rng.shuffle(outcomes)
    rows: list[dict[str, Any]] = []
    i = 0
    for day in days:
        n = rng.choice([2, 2, 3, 3, 1])
        for _ in range(n):
            if i >= len(outcomes):
                break
            outcome = outcomes[i]
            i += 1
            hour = rng.randint(7, 16)
            minute = rng.choice([5, 12, 20, 35, 48])
            submitted = datetime(day.year, day.month, day.day, hour, minute, tzinfo=timezone.utc)
            agent_s = rng.uniform(5.5, 18.0)
            engineer_min = 0.0 if outcome == "waiting" else rng.uniform(14.0, 95.0)
            wait_data_h = rng.uniform(6.0, 28.0) if outcome == "waiting" or rng.random() < 0.18 else 0.0
            if outcome == "waiting":
                status = "waiting_data"
            elif outcome == "escalate":
                status = "escalated"
            else:
                status = "issued"
            sla = sla_for(submitted.timestamp(), 11.0)
            recent = (date.today() - day).days <= 8
            at_risk = (
                status != "issued"
                and recent
                and (sla["overdue"] or sla["due_today"] or sla["remaining_s"] < 48 * 3600)
            )
            rows.append(
                {
                    "id": f"syn-{day.isoformat()}-{i:02d}",
                    "day": day.isoformat(),
                    "submitted_at": submitted.timestamp(),
                    "status": status,
                    "outcome": outcome,
                    "agent_s": round(agent_s, 2),
                    "engineer_min": round(engineer_min, 1),
                    "wait_data_h": round(wait_data_h, 2),
                    "kw": rng.choice([5, 7, 10, 11, 15, 20]),
                    "phases": 3,
                    "sla_overdue": sla["overdue"],
                    "sla_due_today": sla["due_today"],
                    "at_risk": at_risk,
                    "hours_saved": HOURS_SAVED_PER_ISSUED if status == "issued" else 0.0,
                    "synthetic": True,
                    "source": "synthetic",
                }
            )
    open_rows = [r for r in rows if r["status"] in {"waiting_data", "escalated"}]
    for r in open_rows[-5:]:
        r["at_risk"] = True
        r["sla_overdue"] = r["status"] == "waiting_data"
        r["sla_due_today"] = r["status"] != "waiting_data"
    save_synthetic_history(rows)
    return rows


def _median(xs: list[float]) -> float | None:
    if not xs:
        return None
    return round(float(statistics.median(xs)), 2)


def _live_cases() -> list[dict[str, Any]]:
    out = []
    for run in load_runs().values():
        if (run.get("state") or {}).get("synthetic_month"):
            continue
        events = [e for e in (run.get("events") or []) if e.get("type") == "tool"]
        started = float(run.get("started") or run.get("submitted_at") or time.time())
        day = datetime.fromtimestamp(started, tz=timezone.utc).date().isoformat()
        agent_s = sum(float(e.get("elapsed_ms") or 0) for e in events) / 1000.0
        approve = next((a for a in (run.get("audit") or []) if a.get("action") == "approve"), None)
        engineer_min = 0.0
        if approve and approve.get("ts"):
            engineer_min = max(0.0, (float(approve["ts"]) - started) / 60.0)
        status = run.get("status") or "new"
        sol = ((run.get("state") or {}).get("solution") or {}).get("outputs") or {}
        if status == "issued":
            outcome = sol.get("id") or "B"
        elif status == "escalated":
            outcome = "escalate"
        elif status == "waiting_data":
            outcome = "waiting"
        elif status == "awaiting_approval":
            outcome = sol.get("id") or "waiting"
        else:
            outcome = status
        parsed = ((run.get("state") or {}).get("parsed") or {}).get("outputs") or {}
        parsed = parsed.get("parsed") or parsed
        sla = sla_for(started, parsed.get("kw"))
        wait_data_h = 0.0
        if status == "waiting_data":
            wait_data_h = max(0.0, (time.time() - started) / 3600.0)
        out.append(
            {
                "id": run.get("id"),
                "day": day,
                "submitted_at": started,
                "status": status,
                "outcome": outcome,
                "agent_s": round(agent_s, 2),
                "engineer_min": round(engineer_min, 1),
                "wait_data_h": round(wait_data_h, 2),
                "kw": parsed.get("kw"),
                "sla_overdue": sla["overdue"],
                "sla_due_today": sla["due_today"],
                "at_risk": status not in {"issued", "escalated"} and (sla["overdue"] or sla["due_today"]),
                "hours_saved": HOURS_SAVED_PER_ISSUED if status == "issued" else 0.0,
                "synthetic": False,
                "source": "live",
            }
        )
    return out


def analytics_payload() -> dict[str, Any]:
    hist = seed_synthetic_month()
    live = _live_cases()
    cases = list(hist) + live
    by_day: dict[str, int] = {}
    for c in hist:
        by_day[c["day"]] = by_day.get(c["day"], 0) + 1
    throughput = [{"day": d, "n": by_day[d]} for d in sorted(by_day)]
    mix_keys = ["A", "B", "C", "escalate", "waiting"]
    mix = {k: sum(1 for c in hist if c["outcome"] == k) for k in mix_keys}
    agent_med = _median([c["agent_s"] for c in hist if c["agent_s"]])
    eng_med = _median([c["engineer_min"] for c in hist if c["engineer_min"]])
    wait_med = _median([c["wait_data_h"] for c in hist if c["wait_data_h"]])
    wait_hours = round(sum(c["wait_data_h"] for c in hist), 1)
    approval_hours = round(sum(c["engineer_min"] for c in hist) / 60.0, 1)
    at_risk = [c for c in cases if c.get("at_risk")]
    hours_saved = round(sum(c["hours_saved"] for c in hist), 1)
    return {
        "synthetic": True,
        "label": SEED_NOTE,
        "assumption": True,
        "hours_saved_note": MONTHLY_NOTE,
        "hours_saved_per_issued_h": HOURS_SAVED_PER_ISSUED,
        "monthly_cases_assumption": MONTHLY_CASES_ASSUMPTION,
        "throughput": throughput,
        "throughput_total": sum(by_day.values()),
        "median_stage": {
            "agent_s": agent_med,
            "engineer_min": eng_med,
            "wait_data_h": wait_med,
            "note": "Agentas — replay sekundės. Inžinieriaus peržiūra — sintetinis laukimas.",
        },
        "bottleneck": {
            "missing_data_h": wait_hours,
            "engineer_approval_h": approval_hours,
            "note": "Kur bylos laukia: trūkstami duomenys vs inžinieriaus tvirtinimas.",
        },
        "sla": {
            "at_risk": len(at_risk),
            "overdue": sum(1 for c in cases if c.get("sla_overdue")),
            "cases": [
                {
                    "id": c["id"],
                    "day": c.get("day"),
                    "status": c.get("status"),
                    "outcome": c.get("outcome"),
                    "overdue": c.get("sla_overdue"),
                    "source": c.get("source"),
                }
                for c in at_risk[:12]
            ],
            "rule": "Buitinis 0,4 kV — 3 darbo dienos.",
        },
        "mix": mix,
        "hours_saved_h": hours_saved,
        "live_n": len(live),
        "synthetic_n": len(hist),
        "days": len(throughput),
    }
