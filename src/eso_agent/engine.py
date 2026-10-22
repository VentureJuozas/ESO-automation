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
    n_parse,
    n_quality,
    n_reliability,
    n_solution,
)
from eso_agent.llm import llm_mode
from eso_agent.rules import MANUAL_TIME_ASSUMPTION_MINUTES, MANUAL_TIME_ASSUMPTION_NOTE
from eso_agent.scenarios import all_scenarios, get_scenario

PRE_CHECK = [n_parse, n_locate, n_solution, n_breaker]
CHECKS = [n_capacity, n_quality, n_reliability, n_future]
POST = [n_draft, n_cost, n_map]
FN_TOOL = {
    n_parse: "parse_request",
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
    if elapsed_ms == 0:
        elapsed_ms = int((time.time() - started) * 1000)
    lo, hi = MANUAL_TIME_ASSUMPTION_MINUTES
    return {
        "elapsed_ms": elapsed_ms,
        "status": status,
        "tools_run": rules,
        "source_counts": tags,
        "manual_minutes": {"low": lo, "high": hi},
        "manual_note": MANUAL_TIME_ASSUMPTION_NOTE,
        "llm_mode": llm_mode(),
        "assumption": True,
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
        "issued": (st.get("issued") or {}).get("outputs"),
        "approval": st.get("approval"),
        "value": _value(run["events"], run["started"], run["status"]),
        "llm_mode": llm_mode(),
        "error": run.get("error"),
    }


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
            }
        )
    return out


async def _run_fn(run: dict[str, Any], fn) -> None:
    await _broadcast(run, {"type": "start", "tool": FN_TOOL.get(fn, fn.__name__), "ts": time.time()})
    t0 = time.perf_counter()
    run["state"] = {**run["state"], **fn(run["state"])}
    elapsed = int((time.perf_counter() - t0) * 1000)
    result = (run["state"].get("events") or [None])[-1]
    if result:
        ev = _emit_tool(run, result, elapsed)
        await _broadcast(run, ev)
    delay = run.get("delay", _delay())
    if delay:
        await asyncio.sleep(delay)


async def execute(run_id: str) -> None:
    run = RUNS[run_id]
    run["status"] = "running"
    await _broadcast(run, {"type": "status", "status": "running", "id": run_id})
    try:
        for fn in PRE_CHECK + CHECKS:
            await _run_fn(run, fn)
        if run["state"].get("failed"):
            await _run_fn(run, n_escalate)
        await _run_fn(run, n_draft)
        await _run_fn(run, n_cost)
        await _run_fn(run, n_map)
        run["status"] = "escalated" if run["state"].get("failed") else "awaiting_approval"
        interrupt = {
            "type": "interrupt",
            "tool": "engineer_approval",
            "title": "Inžinieriaus patvirtinimas",
            "title_lt": "Inžinieriaus patvirtinimas",
            "kind": "human",
            "failed": bool(run["state"].get("failed")),
            "status": run["status"],
            **tool_by_id("engineer_approval"),
        }
        # tool_by_id returns extra keys; keep event lean
        interrupt = {
            "type": "interrupt",
            "tool": "engineer_approval",
            "title": "Inžinieriaus patvirtinimas",
            "title_lt": "Inžinieriaus patvirtinimas",
            "kind": "human",
            "failed": bool(run["state"].get("failed")),
            "status": run["status"],
            "rule_ref": tool_by_id("engineer_approval").get("rule_ref"),
            "engineer": tool_by_id("engineer_approval").get("engineer"),
            "inputs": {"draft": True, "failed": bool(run["state"].get("failed"))},
            "outputs": {"waiting": True},
            "source_tags": ["rule"],
            "ok": True,
            "elapsed_ms": 0,
            "ts": time.time(),
        }
        run["events"].append(interrupt)
        await _broadcast(run, interrupt)
        await _broadcast(run, {"type": "status", "status": run["status"], "id": run_id, "snapshot": snapshot(run)})
    except Exception as exc:  # noqa: BLE001
        run["status"] = "error"
        run["error"] = str(exc)
        await _broadcast(run, {"type": "error", "message": str(exc)})


def create_run(scenario_id: str | None, text: str, form: dict[str, Any] | None) -> dict[str, Any]:
    if scenario_id:
        sc = get_scenario(scenario_id)
        form = dict(sc["form"])
        text = form.get("text") or text
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
            "text": text or "",
            "form": form or {},
            "run_id": rid,
            "events": [],
            "failed": False,
        },
        "error": None,
    }
    RUNS[rid] = run
    return run


async def start_run(scenario_id: str | None, text: str, form: dict[str, Any] | None) -> dict[str, Any]:
    run = create_run(scenario_id, text, form)
    asyncio.create_task(execute(run["id"]))
    return snapshot(run)


async def resume(run_id: str, decision: str, section3: str | None = None, force: bool = False) -> dict[str, Any]:
    run = RUNS[run_id]
    run["state"]["approval"] = {"decision": decision, "section3": section3, "force": force}
    if decision == "edit" and section3:
        await _run_fn(run, n_draft)
        run["status"] = "escalated" if run["state"].get("failed") else "awaiting_approval"
        await _broadcast(run, {"type": "status", "status": run["status"], "id": run_id, "snapshot": snapshot(run)})
        return snapshot(run)
    if decision == "approve" and (not run["state"].get("failed") or force):
        await _run_fn(run, n_issue)
        run["status"] = "issued"
        done = {"type": "done", "status": "issued", "id": run_id, "snapshot": snapshot(run)}
        await _broadcast(run, done)
        return snapshot(run)
    run["status"] = "escalated"
    await _broadcast(run, {"type": "done", "status": "escalated", "id": run_id, "snapshot": snapshot(run)})
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
    seq = PRE_CHECK + CHECKS + POST
    # Map fn to tool name via running from index
    fns = PRE_CHECK + CHECKS
    if start < 8:
        for fn in fns[start:]:
            await _run_fn(run, fn)
        if run["state"].get("failed"):
            await _run_fn(run, n_escalate)
        await _run_fn(run, n_draft)
        await _run_fn(run, n_cost)
        await _run_fn(run, n_map)
    else:
        rest = POST[start - 8 :]
        for fn in rest:
            await _run_fn(run, fn)
    run["status"] = "escalated" if run["state"].get("failed") else "awaiting_approval"
    interrupt = {
        "type": "interrupt",
        "tool": "engineer_approval",
        "title": "Inžinieriaus patvirtinimas",
        "title_lt": "Inžinieriaus patvirtinimas",
        "kind": "human",
        "failed": bool(run["state"].get("failed")),
        "status": run["status"],
        "ok": True,
        "elapsed_ms": 0,
        "ts": time.time(),
        "source_tags": ["rule"],
    }
    run["events"].append(interrupt)
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


def run_sync_until_interrupt(scenario_id: str = "hero", delay: float = 0) -> dict[str, Any]:
    """Deterministic helper for tests (no asyncio loop required beyond running)."""
    os.environ["ESO_STEP_DELAY"] = str(delay)
    run = create_run(scenario_id, "", None)
    run["delay"] = delay
    state = run["state"]
    for fn in PRE_CHECK + CHECKS:
        t0 = time.perf_counter()
        state = {**state, **fn(state)}
        result = (state.get("events") or [None])[-1]
        if result:
            _emit_tool(run, result, int((time.perf_counter() - t0) * 1000))
        run["state"] = state
    if state.get("failed"):
        t0 = time.perf_counter()
        state = {**state, **n_escalate(state)}
        _emit_tool(run, state["events"][-1], int((time.perf_counter() - t0) * 1000))
    for fn in POST:
        t0 = time.perf_counter()
        state = {**state, **fn(state)}
        _emit_tool(run, state["events"][-1], int((time.perf_counter() - t0) * 1000))
        run["state"] = state
    run["status"] = "escalated" if state.get("failed") else "awaiting_approval"
    run["state"] = state
    run["events"].append(
        {
            "type": "interrupt",
            "tool": "engineer_approval",
            "title": "Inžinieriaus patvirtinimas",
            "title_lt": "Inžinieriaus patvirtinimas",
            "kind": "human",
            "failed": bool(state.get("failed")),
            "status": run["status"],
            "ok": True,
            "elapsed_ms": 0,
            "ts": time.time(),
            "source_tags": ["rule"],
            "outputs": {"waiting": True},
        }
    )
    return snapshot(run)


def approve_sync(run_id: str, section3: str | None = None) -> dict[str, Any]:
    run = RUNS[run_id]
    run["state"]["approval"] = {"decision": "approve", "section3": section3}
    if section3:
        run["state"] = {**run["state"], **n_draft(run["state"])}
        _emit_tool(run, run["state"]["events"][-1], 0)
    run["state"] = {**run["state"], **n_issue(run["state"])}
    _emit_tool(run, run["state"]["events"][-1], 0)
    run["status"] = "issued"
    return snapshot(run)


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
