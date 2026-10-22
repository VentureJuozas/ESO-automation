"""Run the LangGraph node sequence, stream tool events, interrupt for approval."""
from __future__ import annotations

import asyncio
import os
import time
import uuid
from typing import Any

from eso_agent.catalog import tool_by_id
from eso_agent.graph import (
    n_breaker,
    n_capacity,
    n_cost,
    n_draft,
    n_escalate,
    n_future,
    n_issue,
    n_locate,
    n_map,
    n_missing,
    n_parse,
    n_quality,
    n_reliability,
    n_solution,
)
from eso_agent.llm import llm_mode
from eso_agent.missing import detect_gaps
from eso_agent.rules import MANUAL_TIME_ASSUMPTION_MINUTES, MANUAL_TIME_ASSUMPTION_NOTE
from eso_agent.queue import attach_run, ensure_queue, get_case, queue_public, reset_queue, sync_case_from_run
from eso_agent.scenarios import INTAKE_SAMPLES, all_scenarios, get_scenario
from eso_agent.store import clear_all, load_runs, save_run
from eso_agent.timing import comparison_payload, replay_ms

PIPELINE_ORDER = [
    "parse_request",
    "request_missing_data",
    "locate_connection_point",
    "select_solution",
    "size_breaker",
    "check_capacity",
    "check_voltage_drop",
    "check_reliability",
    "check_future",
    "draft_ts_section3",
    "estimate_cost",
    "render_map",
    "engineer_approval",
    "issue_ts",
]

PRE_CHECK = [n_parse, n_locate, n_solution, n_breaker]
CHECKS = [n_capacity, n_quality, n_reliability, n_future]
POST = [n_draft, n_cost, n_map]
FN_TOOL = {
    n_parse: "parse_request",
    n_missing: "request_missing_data",
    n_locate: "locate_connection_point",
    n_solution: "select_solution",
    n_breaker: "size_breaker",
    n_capacity: "check_capacity",
    n_quality: "check_voltage_drop",
    n_reliability: "check_reliability",
    n_future: "check_future",
    n_draft: "draft_ts_section3",
    n_cost: "estimate_cost",
    n_map: "render_map",
    n_escalate: "escalate",
    n_issue: "issue_ts",
}

RUNS: dict[str, dict[str, Any]] = {}


def hydrate_runs() -> None:
    if RUNS:
        return
    RUNS.update(load_runs())


def _delay() -> float:
    return float(os.environ.get("ESO_STEP_DELAY", "0.11"))


def _value(events: list[dict[str, Any]], started: float, status: str) -> dict[str, Any]:
    tags: dict[str, int] = {}
    rules = 0
    elapsed_ms = 0
    for ev in events:
        if ev.get("type") != "tool":
            continue
        for t in ev.get("source_tags") or []:
            tags[t] = tags.get(t, 0) + 1
        rules += 1
        elapsed_ms += int(ev.get("elapsed_ms") or 0)
    if not any(ev.get("type") == "tool" for ev in events):
        elapsed_ms = int((time.time() - started) * 1000)
    lo, hi = MANUAL_TIME_ASSUMPTION_MINUTES
    cmp = comparison_payload(events)
    return {
        "elapsed_ms": elapsed_ms or cmp["agent_ms"],
        "status": status,
        "tools_run": rules,
        "source_counts": tags,
        "manual_minutes": {"low": lo, "high": hi},
        "manual_note": MANUAL_TIME_ASSUMPTION_NOTE,
        "llm_mode": llm_mode(),
        "assumption": True,
        "comparison": cmp,
    }


def _emit_tool(run: dict[str, Any], result: dict[str, Any], elapsed_ms: int) -> dict[str, Any]:
    event = {
        "type": "tool",
        **result,
        "elapsed_ms": elapsed_ms,
        "ts": time.time(),
    }
    if not event.get("rule_ref"):
        meta = tool_by_id(result.get("tool", ""))
        event["rule_ref"] = meta.get("rule_ref")
        event["engineer"] = meta.get("engineer")
        event["title_lt"] = meta.get("title_lt") or result.get("title")
        event["kind"] = meta.get("kind", "tool")
    run["events"].append(event)
    return event


async def _broadcast(run: dict[str, Any], event: dict[str, Any]) -> None:
    for q in list(run["queues"]):
        await q.put(event)


def snapshot(run: dict[str, Any]) -> dict[str, Any]:
    st = run["state"]
    parsed = ((st.get("parsed") or {}).get("outputs") or {}).get("parsed")
    return {
        "id": run["id"],
        "status": run["status"],
        "scenario_id": run.get("scenario_id"),
        "failed": bool(st.get("failed")),
        "events": run["events"],
        "parsed": parsed,
        "location": (st.get("location") or {}).get("outputs"),
        "solution": (st.get("solution") or {}).get("outputs"),
        "breaker": (st.get("breaker") or {}).get("outputs"),
        "capacity": (st.get("capacity") or {}).get("outputs"),
        "quality": (st.get("quality") or {}).get("outputs"),
        "reliability": (st.get("reliability") or {}).get("outputs"),
        "future": (st.get("future") or {}).get("outputs"),
        "draft": (st.get("draft") or {}).get("outputs"),
        "cost": (st.get("cost") or {}).get("outputs"),
        "map": (st.get("map") or {}).get("outputs"),
        "escalate": (st.get("escalate") or {}).get("outputs"),
        "missing": (st.get("missing") or {}).get("outputs"),
        "issued": (st.get("issued") or {}).get("outputs"),
        "approval": st.get("approval"),
        "value": _value(run["events"], run["started"], run["status"]),
        "llm_mode": llm_mode(),
        "error": run.get("error"),
        "skipped": _skipped(run),
        "audit": list(run.get("audit") or []),
        "overridden": bool(st.get("overridden")),
        "queue_id": run.get("queue_id"),
        "assignee": run.get("assignee"),
        "title": run.get("title"),
        "submitted_at": run.get("submitted_at"),
    }


def _skipped(run: dict[str, Any]) -> list[str]:
    if run["state"].get("waiting_data"):
        ran = {e.get("tool") for e in run["events"] if e.get("type") == "tool"}
        return [t for t in PIPELINE_ORDER if t not in ran and t != "request_missing_data"]
    if not run["state"].get("failed") or run["state"].get("overridden"):
        return []
    ran = {e.get("tool") for e in run["events"] if e.get("type") == "tool"}
    fail_at = None
    for ev in run["events"]:
        if ev.get("type") == "tool" and (ev.get("outputs") or {}).get("escalate") and ev.get("tool") != "escalate":
            fail_at = ev.get("tool")
            break
    if not fail_at or fail_at not in PIPELINE_ORDER:
        return [t for t in ("draft_ts_section3", "estimate_cost", "render_map", "engineer_approval", "issue_ts") if t not in ran]
    idx = PIPELINE_ORDER.index(fail_at)
    return [t for t in PIPELINE_ORDER[idx + 1 :] if t not in ran]


def list_runs() -> list[dict[str, Any]]:
    out = []
    for run in sorted(RUNS.values(), key=lambda r: r["started"], reverse=True):
        parsed = ((run["state"].get("parsed") or {}).get("outputs") or {}).get("parsed") or {}
        sol = (run["state"].get("solution") or {}).get("outputs") or {}
        out.append(
            {
                "id": run["id"],
                "status": run["status"],
                "scenario_id": run.get("scenario_id"),
                "started": run["started"],
                "kw": parsed.get("kw"),
                "phases": parsed.get("phases"),
                "solution": sol.get("id"),
                "failed": bool(run["state"].get("failed")),
                "queue_id": run.get("queue_id"),
                "assignee": run.get("assignee"),
                "title": run.get("title"),
            }
        )
    return out


async def _run_fn(run: dict[str, Any], fn) -> None:
    start = {"type": "start", "tool": FN_TOOL.get(fn, fn.__name__), "ts": time.time()}
    run["events"].append(start)
    await _broadcast(run, start)
    t0 = time.perf_counter()
    run["state"] = {**run["state"], **fn(run["state"])}
    delay = run.get("delay", _delay())
    if delay:
        await asyncio.sleep(delay)
    name = FN_TOOL.get(fn, fn.__name__)
    elapsed = replay_ms(name)
    if elapsed <= 0:
        elapsed = int((time.perf_counter() - t0) * 1000)
    result = (run["state"].get("events") or [None])[-1]
    if result:
        ev = _emit_tool(run, result, elapsed)
        await _broadcast(run, ev)


def _has_gaps(state: dict[str, Any]) -> bool:
    form = state.get("form") or {}
    if form.get("ignore_missing") or form.get("supplied"):
        return False
    parsed = ((state.get("parsed") or {}).get("outputs") or {}).get("parsed") or {}
    return bool(detect_gaps(parsed, form))


async def execute(run_id: str) -> None:
    run = RUNS[run_id]
    run["status"] = "running"
    await _broadcast(run, {"type": "status", "status": "running", "id": run_id})
    try:
        for fn in PRE_CHECK:
            await _run_fn(run, fn)
            if fn is n_parse and _has_gaps(run["state"]):
                await _run_fn(run, n_missing)
                run["status"] = "waiting_data"
                interrupt = _interrupt_event(run)
                run["events"].append(interrupt)
                sync_case_from_run(run)
                save_run(run)
                await _broadcast(run, interrupt)
                await _broadcast(run, {"type": "status", "status": "waiting_data", "id": run_id, "snapshot": snapshot(run)})
                return
        for fn in CHECKS:
            await _run_fn(run, fn)
            if run["state"].get("failed"):
                await _run_fn(run, n_escalate)
                break
        if not run["state"].get("failed"):
            for fn in POST:
                await _run_fn(run, fn)
        run["status"] = "escalated" if run["state"].get("failed") else "awaiting_approval"
        interrupt = _interrupt_event(run)
        run["events"].append(interrupt)
        sync_case_from_run(run)
        await _broadcast(run, interrupt)
        await _broadcast(run, {"type": "status", "status": run["status"], "id": run_id, "snapshot": snapshot(run)})
        save_run(run)
    except Exception as exc:  # noqa: BLE001
        run["status"] = "error"
        run["error"] = str(exc)
        sync_case_from_run(run)
        save_run(run)
        await _broadcast(run, {"type": "error", "message": str(exc)})


def create_run(scenario_id: str | None, text: str, form: dict[str, Any] | None) -> dict[str, Any]:
    form = dict(form or {})
    meta = form.pop("_queue", {}) if isinstance(form.get("_queue"), dict) else {}
    if scenario_id and scenario_id not in {None, "", "intake", "queue"}:
        try:
            sc = get_scenario(scenario_id)
            form = dict(sc["form"])
            text = form.get("text") or text
        except KeyError:
            pass
    rid = uuid.uuid4().hex[:10]
    run = {
        "id": rid,
        "scenario_id": scenario_id,
        "status": "queued",
        "started": time.time(),
        "events": [],
        "queues": [],
        "delay": _delay(),
        "state": {
            "text": text or form.get("text") or "",
            "form": form or {},
            "run_id": rid,
            "events": [],
            "failed": False,
        },
        "error": None,
        "audit": [],
        "queue_id": meta.get("queue_id"),
        "assignee": meta.get("assignee"),
        "title": meta.get("title"),
        "submitted_at": meta.get("submitted_at"),
    }
    RUNS[rid] = run
    if run["queue_id"]:
        attach_run(run["queue_id"], rid)
    save_run(run)
    return run


def _interrupt_event(run: dict[str, Any]) -> dict[str, Any]:
    if run["state"].get("waiting_data"):
        meta = tool_by_id("request_missing_data")
        return {
            "type": "interrupt",
            "tool": "request_missing_data",
            "title": meta.get("title_lt") or "Trūkstami duomenys",
            "title_lt": meta.get("title_lt"),
            "kind": "human",
            "failed": False,
            "status": "waiting_data",
            "rule_ref": meta.get("rule_ref"),
            "engineer": meta.get("engineer"),
            "inputs": {"waiting": True},
            "outputs": (run["state"].get("missing") or {}).get("outputs") or {"waiting": True},
            "source_tags": ["rule"],
            "ok": True,
            "elapsed_ms": 0,
            "ts": time.time(),
        }
    failed = bool(run["state"].get("failed"))
    tool = "escalate" if failed else "engineer_approval"
    meta = tool_by_id(tool)
    return {
        "type": "interrupt",
        "tool": tool,
        "title": meta.get("title_lt") or ("Perdavimas inžinieriui" if failed else "Inžinieriaus patvirtinimas"),
        "title_lt": meta.get("title_lt"),
        "kind": "human" if not failed else "tool",
        "failed": failed,
        "status": run["status"],
        "rule_ref": meta.get("rule_ref"),
        "engineer": meta.get("engineer"),
        "inputs": {"failed": failed, "draft": not failed},
        "outputs": (run["state"].get("escalate") or {}).get("outputs") if failed else {"waiting": True},
        "source_tags": ["rule"],
        "ok": True,
        "elapsed_ms": 0,
        "ts": time.time(),
    }


async def start_run(scenario_id: str | None, text: str, form: dict[str, Any] | None) -> dict[str, Any]:
    run = create_run(scenario_id, text, form)
    asyncio.create_task(execute(run["id"]))
    return snapshot(run)


async def resume(
    run_id: str,
    decision: str,
    section3: str | None = None,
    force: bool = False,
    override_reason: str | None = None,
) -> dict[str, Any]:
    run = RUNS[run_id]
    run["state"]["approval"] = {
        "decision": decision,
        "section3": section3,
        "force": False,
        "override_reason": override_reason,
    }
    if decision == "override":
        reason = (override_reason or "").strip()
        if len(reason) < 8:
            raise ValueError("Override reikalauja priežasties (mažiausiai 8 simboliai).")
        run.setdefault("audit", []).append(
            {
                "ts": time.time(),
                "action": "engineer_override",
                "reason": reason,
                "actor": "engineer",
                "failed_at": (run["state"].get("escalate") or {}).get("outputs", {}).get("failed_at"),
            }
        )
        run["state"]["overridden"] = True
        run["state"]["override_reason"] = reason
        run["state"]["failed"] = False
        ran = {e.get("tool") for e in run["events"] if e.get("type") == "tool"}
        for fn in POST:
            if FN_TOOL[fn] in ran:
                continue
            await _run_fn(run, fn)
        run["status"] = "awaiting_approval"
        interrupt = _interrupt_event(run)
        run["events"].append(interrupt)
        sync_case_from_run(run)
        await _broadcast(run, interrupt)
        await _broadcast(run, {"type": "status", "status": run["status"], "id": run_id, "snapshot": snapshot(run)})
        save_run(run)
        return snapshot(run)
    if decision == "edit" and section3:
        if run["state"].get("failed") and not run["state"].get("overridden"):
            raise ValueError("Eskaluotos eigos negalima taisyti be override.")
        run.setdefault("audit", []).append(
            {"ts": time.time(), "action": "edit_section3", "reason": "§3 pataisa", "actor": "engineer"}
        )
        await _run_fn(run, n_draft)
        run["status"] = "awaiting_approval"
        sync_case_from_run(run)
        await _broadcast(run, {"type": "status", "status": run["status"], "id": run_id, "snapshot": snapshot(run)})
        save_run(run)
        return snapshot(run)
    if decision == "approve":
        if run["state"].get("failed") and not run["state"].get("overridden"):
            raise ValueError("Sąlygos neišduodamos eskalacijos metu. Reikalingas inžinieriaus override su priežastimi.")
        run.setdefault("audit", []).append(
            {"ts": time.time(), "action": "approve", "reason": "Patvirtinta ir išduota", "actor": "engineer"}
        )
        await _run_fn(run, n_issue)
        run["status"] = "issued"
        sync_case_from_run(run)
        done = {"type": "done", "status": "issued", "id": run_id, "snapshot": snapshot(run)}
        await _broadcast(run, done)
        save_run(run)
        return snapshot(run)
    run["status"] = "escalated"
    await _broadcast(run, {"type": "done", "status": "escalated", "id": run_id, "snapshot": snapshot(run)})
    save_run(run)
    return snapshot(run)


async def rerun_from(run_id: str, from_tool: str, overrides: dict[str, Any] | None = None) -> dict[str, Any]:
    """Re-apply overrides and re-execute from a named tool through approval."""
    run = RUNS[run_id]
    overrides = overrides or {}
    form = dict(run["state"].get("form") or {})
    form.update({k: v for k, v in overrides.items() if k in {"kw", "phases", "lat", "lon", "pending_kw", "text"}})
    run["state"]["form"] = form
    if "pending_kw" in overrides:
        form["pending_kw"] = overrides["pending_kw"]
    order = {
        "parse_request": 0,
        "locate_connection_point": 1,
        "select_solution": 2,
        "size_breaker": 3,
        "check_capacity": 4,
        "check_voltage_drop": 5,
        "check_reliability": 6,
        "check_future": 7,
        "draft_ts_section3": 8,
        "estimate_cost": 9,
        "render_map": 10,
    }
    start = order.get(from_tool, 0)
    # Drop events from that tool onward
    kept = []
    for ev in run["events"]:
        if ev.get("type") == "tool" and order.get(ev.get("tool"), 99) >= start:
            break
        if ev.get("type") == "interrupt":
            break
        kept.append(ev)
    run["events"] = kept
    run["state"]["events"] = [e for e in kept if e.get("type") == "tool"]
    run["state"]["failed"] = False
    run["state"]["issued"] = None
    run["status"] = "running"
    run["state"]["overridden"] = False
    fns = PRE_CHECK + CHECKS
    if start < 8:
        for fn in fns[start:]:
            await _run_fn(run, fn)
            if run["state"].get("failed") and fn in CHECKS:
                await _run_fn(run, n_escalate)
                break
        if not run["state"].get("failed"):
            for fn in POST:
                await _run_fn(run, fn)
    else:
        rest = POST[start - 8 :]
        for fn in rest:
            await _run_fn(run, fn)
    run["status"] = "escalated" if run["state"].get("failed") else "awaiting_approval"
    interrupt = _interrupt_event(run)
    run["events"].append(interrupt)
    sync_case_from_run(run)
    save_run(run)
    await _broadcast(run, interrupt)
    await _broadcast(run, {"type": "status", "status": run["status"], "id": run_id, "snapshot": snapshot(run)})
    return snapshot(run)


async def subscribe(run_id: str):
    run = RUNS[run_id]
    q: asyncio.Queue = asyncio.Queue()
    run["queues"].append(q)
    try:
        for ev in run["events"]:
            yield ev
        while True:
            ev = await q.get()
            yield ev
            if ev.get("type") in {"done", "error"}:
                break
    finally:
        if q in run["queues"]:
            run["queues"].remove(q)


def run_sync_until_interrupt(
    scenario_id: str = "hero",
    delay: float = 0,
    text: str = "",
    form: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Deterministic helper for tests (no asyncio loop required beyond running)."""
    os.environ["ESO_STEP_DELAY"] = str(delay)
    run = create_run(scenario_id, text, form)
    run["delay"] = delay
    state = run["state"]
    def _step(fn):
        nonlocal state
        name = FN_TOOL.get(fn, fn.__name__)
        state = {**state, **fn(state)}
        result = (state.get("events") or [None])[-1]
        if result:
            _emit_tool(run, result, replay_ms(name))
        run["state"] = state

    for fn in PRE_CHECK:
        _step(fn)
        if fn is n_parse and _has_gaps(state):
            _step(n_missing)
            run["status"] = "waiting_data"
            run["state"] = state
            run["events"].append(_interrupt_event(run))
            sync_case_from_run(run)
            save_run(run)
            return snapshot(run)
    for fn in CHECKS:
        _step(fn)
        if state.get("failed"):
            _step(n_escalate)
            break
    if not state.get("failed"):
        for fn in POST:
            _step(fn)
    run["status"] = "escalated" if state.get("failed") else "awaiting_approval"
    run["state"] = state
    run["events"].append(_interrupt_event(run))
    sync_case_from_run(run)
    save_run(run)
    return snapshot(run)


def approve_sync(run_id: str, section3: str | None = None) -> dict[str, Any]:
    run = RUNS[run_id]
    if run["state"].get("failed") and not run["state"].get("overridden"):
        raise ValueError("Sąlygos neišduodamos eskalacijos metu.")
    run["state"]["approval"] = {"decision": "approve", "section3": section3}
    if section3:
        run["state"] = {**run["state"], **n_draft(run["state"])}
        _emit_tool(run, run["state"]["events"][-1], replay_ms("draft_ts_section3"))
    run["state"] = {**run["state"], **n_issue(run["state"])}
    _emit_tool(run, run["state"]["events"][-1], replay_ms("issue_ts"))
    run["status"] = "issued"
    sync_case_from_run(run)
    save_run(run)
    return snapshot(run)


def override_sync(run_id: str, reason: str) -> dict[str, Any]:
    run = RUNS[run_id]
    reason = (reason or "").strip()
    if len(reason) < 8:
        raise ValueError("Override reikalauja priežasties.")
    run.setdefault("audit", []).append(
        {"ts": time.time(), "action": "engineer_override", "reason": reason, "actor": "engineer"}
    )
    run["state"]["overridden"] = True
    run["state"]["failed"] = False
    ran = {e.get("tool") for e in run["events"] if e.get("type") == "tool"}

    def _step(fn):
        name = FN_TOOL.get(fn, fn.__name__)
        run["state"] = {**run["state"], **fn(run["state"])}
        result = (run["state"].get("events") or [None])[-1]
        if result:
            _emit_tool(run, result, replay_ms(name))

    for fn in POST:
        if FN_TOOL[fn] in ran:
            continue
        _step(fn)
    run["status"] = "awaiting_approval"
    run["events"].append(_interrupt_event(run))
    sync_case_from_run(run)
    save_run(run)
    return snapshot(run)


_BATCH = {"running": False}


def _queue_form(case: dict[str, Any]) -> dict[str, Any]:
    form = dict(case.get("form") or {})
    form["_queue"] = {
        "queue_id": case["id"],
        "assignee": case.get("assignee"),
        "title": case.get("title"),
        "submitted_at": case.get("submitted_at"),
    }
    return form


async def start_queue_case(cid: str, wait: bool = False) -> dict[str, Any]:
    case = get_case(cid)
    form = _queue_form(case)
    run = create_run("queue", form.get("text") or "", form)
    if wait:
        await execute(run["id"])
        return snapshot(run)
    asyncio.create_task(execute(run["id"]))
    return snapshot(run)


async def _run_batch() -> None:
    try:
        for case in list(ensure_queue()):
            if case.get("status") != "new":
                continue
            try:
                await start_queue_case(case["id"], wait=True)
            except Exception as exc:  # noqa: BLE001
                case["status"] = "error"
                case["error"] = str(exc)
                sync_case_from_run({"id": None, "queue_id": case["id"], "status": "error", "state": {}})
    finally:
        _BATCH["running"] = False


async def batch_queue() -> dict[str, Any]:
    ensure_queue()
    if _BATCH.get("running"):
        return {"ok": True, "already": True, "batching": True, **queue_public()}
    _BATCH["running"] = True
    asyncio.create_task(_run_batch())
    return {"ok": True, "already": False, "batching": True, **queue_public()}


def run_queue_case_sync(cid: str) -> dict[str, Any]:
    case = get_case(cid)
    form = _queue_form(case)
    return run_sync_until_interrupt("queue", delay=0, text=form.get("text") or "", form=form)


def batch_queue_sync() -> list[dict[str, Any]]:
    ensure_queue()
    return [run_queue_case_sync(c["id"]) for c in list(ensure_queue()) if c.get("status") == "new"]


def batching() -> bool:
    return bool(_BATCH.get("running"))


def _continue_pipeline(run: dict[str, Any]) -> dict[str, Any]:
    state = run["state"]

    def _step(fn):
        nonlocal state
        name = FN_TOOL.get(fn, fn.__name__)
        state = {**state, **fn(state)}
        result = (state.get("events") or [None])[-1]
        if result:
            _emit_tool(run, result, replay_ms(name))
        run["state"] = state

    _step(n_parse)
    if _has_gaps(state):
        _step(n_missing)
        run["status"] = "waiting_data"
        run["events"].append(_interrupt_event(run))
        sync_case_from_run(run)
        save_run(run)
        return snapshot(run)
    for fn in PRE_CHECK[1:]:
        _step(fn)
    for fn in CHECKS:
        _step(fn)
        if state.get("failed"):
            _step(n_escalate)
            break
    if not state.get("failed"):
        for fn in POST:
            _step(fn)
    run["status"] = "escalated" if state.get("failed") else "awaiting_approval"
    run["events"].append(_interrupt_event(run))
    sync_case_from_run(run)
    save_run(run)
    return snapshot(run)


def supply_data(run_id: str, fields: dict[str, Any]) -> dict[str, Any]:
    """Resume a waiting_data run after the engineer fills gaps."""
    run = RUNS[run_id]
    form = dict(run["state"].get("form") or {})
    for key, val in (fields or {}).items():
        if val is not None and val != "":
            form[key] = val
    form["supplied"] = True
    form["ignore_missing"] = True
    run["state"]["form"] = form
    if fields.get("text"):
        run["state"]["text"] = fields["text"]
    run["state"]["waiting_data"] = False
    run["state"]["failed"] = False
    run["status"] = "running"
    run["audit"] = list(run.get("audit") or []) + [
        {"ts": time.time(), "action": "supply_data", "fields": sorted(form.keys()), "actor": "engineer"}
    ]
    return _continue_pipeline(run)


def whatif(form: dict[str, Any]) -> dict[str, Any]:
    """Deterministic live recompute. Not attached to the manager queue."""
    from eso_agent.network import STATION, destination

    payload = dict(form or {})
    dist = payload.pop("distance_m", None)
    if dist not in (None, ""):
        lat, lon = destination(STATION["lat"], STATION["lon"], 18.0, float(dist))
        payload["lat"] = lat
        payload["lon"] = lon
    payload["ignore_missing"] = True
    payload.setdefault("text", f"What-if {payload.get('kw')} kW {payload.get('phases')}F.")
    return run_sync_until_interrupt("intake", delay=0, text=payload.get("text") or "", form=payload)


def reset_demo() -> dict[str, Any]:
    """Wipe SQLite + memory and reseed the synthetic queue."""
    RUNS.clear()
    from eso_agent.queue import QUEUE

    QUEUE.clear()
    clear_all()
    reset_queue()
    return queue_public()


def scenarios_public() -> list[dict[str, Any]]:
    return [
        {
            "id": s["id"],
            "code": s["code"],
            "title": s["title"],
            "subtitle": s["subtitle"],
            "pitch": s["pitch"],
            "expected_solution": s["expected_solution"],
            "expected_escalate": s["expected_escalate"],
            "form": s["form"],
            "notes": s["notes"],
        }
        for s in all_scenarios()
    ]


def samples_public() -> list[dict[str, Any]]:
    return list(INTAKE_SAMPLES)
