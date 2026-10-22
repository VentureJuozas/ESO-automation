"""Manager queue of today's 12-608 applications (synthetic, redacted)."""
from __future__ import annotations

import time
from datetime import datetime, timedelta
from typing import Any

from eso_agent.network import HERO_LAT, HERO_LON, element_by_id
from eso_agent.rules import HOUSEHOLD_DEADLINE_DAYS, issuing_deadline_days
from eso_agent.store import load_queue, save_queue
from eso_agent.timing import MONTHLY_CASES_ASSUMPTION, comparison_payload


def _el(eid: str) -> dict[str, Any]:
    try:
        return element_by_id(eid)
    except KeyError:
        return {"id": eid, "lat": HERO_LAT, "lon": HERO_LON}


ASSIGNEES = (
    "I. Petrauskas (redaguota)",
    "A. Kazlauskaitė (redaguota)",
    "M. Jankauskas (redaguota)",
)

QUEUE: list[dict[str, Any]] = []


def add_working_days(ts: float, days: int) -> float:
    d = datetime.fromtimestamp(ts)
    added = 0
    while added < days:
        d += timedelta(days=1)
        if d.weekday() < 5:
            added += 1
    return d.timestamp()


def sla_for(submitted_at: float, kw: float | None) -> dict[str, Any]:
    rule = issuing_deadline_days(float(kw or 11), "household")
    days = int(rule.get("days") or HOUSEHOLD_DEADLINE_DAYS)
    deadline = add_working_days(submitted_at, days)
    remain = deadline - time.time()
    return {
        "days": days,
        "unit": rule.get("unit"),
        "note": rule.get("note"),
        "source": "rule",
        "submitted_at": submitted_at,
        "deadline_at": deadline,
        "remaining_s": remain,
        "overdue": remain < 0,
        "due_today": 0 <= remain < 24 * 3600,
    }


def _form(kw, phases, lat, lon, text, name, pending=0.0) -> dict[str, Any]:
    return {
        "kw": kw,
        "phases": phases,
        "lat": lat,
        "lon": lon,
        "customer_type": "household",
        "pending_kw": pending,
        "text": text,
        "object_name": name,
    }


def _seed_specs() -> list[dict[str, Any]]:
    cab = _el("KS-39685")
    ks36 = _el("KS-14336")
    ks32 = _el("KS-14332")
    ks_c = _el("KS-14336")
    pole204 = _el("204/4")
    pole300 = _el("300/2")
    now = time.time()
    return [
        {
            "id": "q01",
            "title": "Sodyba prie L-200",
            "mix": "B",
            "assignee": ASSIGNEES[0],
            "submitted_at": now - 2 * 3600,
            "data_gap": False,
            "form": _form(11, 3, HERO_LAT, HERO_LON, "Naujas buitinis, 11 kW, trys fazės, 54,55929, 25,27955, TP 12-608.", "Sodyba (eilė)"),
        },
        {
            "id": "q02",
            "title": "Sklypas prie KS-39685",
            "mix": "A",
            "assignee": ASSIGNEES[1],
            "submitted_at": now - 5 * 3600,
            "data_gap": False,
            "form": _form(11, 3, cab["lat"], cab["lon"], f"Naujas buitinis 11 kW 3F, sklype KS-39685, {cab['lat']}, {cab['lon']}.", "Sklypas prie KS"),
        },
        {
            "id": "q03",
            "title": "Įsipjovimas L-KS14330",
            "mix": "C",
            "assignee": ASSIGNEES[2],
            "submitted_at": now - 8 * 3600,
            "data_gap": False,
            "form": _form(14, 3, ks_c["lat"] + 0.00036, ks_c["lon"] + 0.00012, "Naujas buitinis 14 kW 3 fazės prie kabelių linijos.", "Sklypas prie kabelio"),
        },
        {
            "id": "q04",
            "title": "100 kW cechas",
            "mix": "fail",
            "assignee": ASSIGNEES[0],
            "submitted_at": now - 26 * 3600,
            "data_gap": False,
            "form": _form(100, 3, HERO_LAT, HERO_LON, "100 kW trifazis, koordinatės 54,55929, 25,27955.", "Cechas (demonstracija)"),
        },
        {
            "id": "q05",
            "title": "Laiškas be koordinačių",
            "mix": "missing",
            "assignee": ASSIGNEES[1],
            "submitted_at": now - 3 * 3600,
            "data_gap": True,
            "form": {"text": "Sveiki, prašome prijungimo sąlygų sodybai, 11 kW, trys fazės. Adreso nerašau.", "object_name": "Sodyba (koordinatės trūksta)", "customer_type": "household"},
        },
        {
            "id": "q06",
            "title": "14 kW L-204",
            "mix": "B",
            "assignee": ASSIGNEES[2],
            "submitted_at": now - 1 * 3600,
            "data_gap": False,
            "form": _form(14, 3, pole204["lat"] + 0.00005, pole204["lon"] - 0.00004, "14 kW 3F prie L-204.", "Namas L-204"),
        },
        {
            "id": "q07",
            "title": "KS-14336 didinimas",
            "mix": "A",
            "assignee": ASSIGNEES[0],
            "submitted_at": now - 10 * 3600,
            "data_gap": False,
            "form": _form(11, 3, ks36["lat"], ks36["lon"], f"11 kW 3F, sklype KS-14336, {ks36['lat']}, {ks36['lon']}.", "Sklypas KS-14336"),
        },
        {
            "id": "q08",
            "title": "80 kW sandėlis",
            "mix": "fail",
            "assignee": ASSIGNEES[1],
            "submitted_at": now - 72 * 3600,
            "data_gap": False,
            "form": _form(80, 3, HERO_LAT, HERO_LON, "Sandėliui reikia 80 kW, 3 fazės, 54,55929, 25,27955.", "Sandėlis"),
        },
        {
            "id": "q09",
            "title": "Neaiški paraiška",
            "mix": "missing",
            "assignee": ASSIGNEES[2],
            "submitted_at": now - 4 * 3600,
            "data_gap": True,
            "form": {"text": "Prašome sąlygų.", "object_name": "Objektas nenurodytas", "customer_type": "household"},
        },
        {
            "id": "q10",
            "title": "11 kW L-300",
            "mix": "B",
            "assignee": ASSIGNEES[0],
            "submitted_at": now - 6 * 3600,
            "data_gap": False,
            "form": _form(11, 3, pole300["lat"] + 0.00004, pole300["lon"], "11 kW trifazis prie L-300.", "Sodyba L-300"),
        },
        {
            "id": "q11",
            "title": "KS-14332",
            "mix": "A",
            "assignee": ASSIGNEES[1],
            "submitted_at": now - 12 * 3600,
            "data_gap": False,
            "form": _form(22, 3, ks32["lat"], ks32["lon"], f"22 kW 3F, esama KS-14332, {ks32['lat']}, {ks32['lon']}.", "Sklypas KS-14332"),
        },
        {
            "id": "q12",
            "title": "18 kW nauja KAS",
            "mix": "B",
            "assignee": ASSIGNEES[2],
            "submitted_at": now - 90 * 3600,
            "data_gap": False,
            "form": _form(18, 3, HERO_LAT + 0.0002, HERO_LON - 0.0001, "18 kW, 3 fazės, naujas buitinis prie 12-608.", "Nauja KAS"),
        },
    ]


def reset_queue() -> list[dict[str, Any]]:
    QUEUE.clear()
    for spec in _seed_specs():
        kw = (spec.get("form") or {}).get("kw")
        QUEUE.append(
            {
                **spec,
                "status": "new",
                "run_id": None,
                "solution": None,
                "kw": kw,
                "phases": (spec.get("form") or {}).get("phases"),
                "sla": sla_for(spec["submitted_at"], kw),
            }
        )
    save_queue(QUEUE)
    return QUEUE


def ensure_queue() -> list[dict[str, Any]]:
    if QUEUE:
        return QUEUE
    stored = load_queue()
    if stored:
        QUEUE.extend(stored)
        return QUEUE
    reset_queue()
    return QUEUE


def get_case(cid: str) -> dict[str, Any]:
    for c in ensure_queue():
        if c["id"] == cid:
            return c
    raise KeyError(cid)


def attach_run(cid: str, run_id: str) -> None:
    case = get_case(cid)
    case["run_id"] = run_id
    case["status"] = "running"


def sync_case_from_run(run: dict[str, Any]) -> None:
    qid = run.get("queue_id")
    if not qid:
        return
    try:
        case = get_case(qid)
    except KeyError:
        return
    case["status"] = run.get("status") or case["status"]
    case["run_id"] = run.get("id")
    parsed = ((run.get("state") or {}).get("parsed") or {}).get("outputs") or {}
    inner = parsed.get("parsed") or {}
    if inner.get("kw") is not None:
        case["kw"] = inner.get("kw")
    sol = ((run.get("state") or {}).get("solution") or {}).get("outputs") or {}
    if sol.get("id"):
        case["solution"] = sol.get("id")
    draft = ((run.get("state") or {}).get("draft") or {}).get("outputs") or {}
    if draft.get("section3"):
        case["section3"] = draft.get("section3")
    esc = ((run.get("state") or {}).get("escalate") or {}).get("outputs") or {}
    if esc:
        case["failed_at"] = esc.get("failed_at")
        case["brief_title"] = (esc.get("brief") or {}).get("title")
    case["sla"] = sla_for(case["submitted_at"], case.get("kw"))
    case["failed"] = bool((run.get("state") or {}).get("failed"))
    case["overridden"] = bool((run.get("state") or {}).get("overridden"))
    save_queue(QUEUE)


def queue_public() -> dict[str, Any]:
    cases = []
    for c in ensure_queue():
        item = {k: v for k, v in c.items() if k != "form"}
        item["sla"] = sla_for(c["submitted_at"], c.get("kw"))
        item["form"] = c.get("form")
        cases.append(item)
    return {"cases": cases, "hud": queue_hud(), "inbox": [c for c in cases if c["status"] in {"awaiting_approval", "escalated"}]}


def queue_hud(runs: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    from eso_agent.engine import RUNS

    runs = runs if runs is not None else RUNS
    cases = ensure_queue()
    processed = [c for c in cases if c["status"] in {"awaiting_approval", "issued", "escalated"}]
    issued = [c for c in cases if c["status"] == "issued"]
    inbox = [c for c in cases if c["status"] in {"awaiting_approval", "escalated"}]
    saved = 0.0
    for c in processed:
        rid = c.get("run_id")
        run = runs.get(rid) if rid else None
        if not run:
            continue
        cmp = comparison_payload(run.get("events") or [])
        saved += float(cmp.get("saved_min") or 0)
    monthly = round(saved / 60.0 * MONTHLY_CASES_ASSUMPTION / max(1, len(processed) or 1) * max(1, len(processed)), 1)
    if processed:
        monthly = round((saved / len(processed)) / 60.0 * MONTHLY_CASES_ASSUMPTION, 1)
    return {
        "total": len(cases),
        "new": sum(1 for c in cases if c["status"] == "new"),
        "running": sum(1 for c in cases if c["status"] == "running"),
        "processed": len(processed),
        "issued": len(issued),
        "inbox_depth": len(inbox),
        "saved_min_today": round(saved, 1),
        "monthly_hours": monthly,
        "assumption": True,
        "monthly_cases": MONTHLY_CASES_ASSUMPTION,
        "note": "Minutės ir 40 bylų / mėn. — prielaida, ne ESO statistika.",
    }


def pending_queue_load() -> tuple[float, int]:
    cases = ensure_queue()
    open_cases = [c for c in cases if c["status"] in {"new", "running", "awaiting_approval"}]
    kw = sum(float(c.get("kw") or 0) for c in open_cases)
    return kw, len(open_cases)
