"""LangGraph definition. Nodes call deterministic tools; two nodes may use the LLM."""
from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from eso_agent import tools as T


class AgentState(TypedDict, total=False):
    text: str
    form: dict[str, Any]
    run_id: str
    parsed: dict[str, Any]
    location: dict[str, Any]
    solution: dict[str, Any]
    breaker: dict[str, Any]
    capacity: dict[str, Any]
    quality: dict[str, Any]
    reliability: dict[str, Any]
    future: dict[str, Any]
    draft: dict[str, Any]
    cost: dict[str, Any]
    map: dict[str, Any]
    escalate: dict[str, Any]
    approval: dict[str, Any]
    issued: dict[str, Any]
    failed: bool
    events: list[dict[str, Any]]


def _trace(state: AgentState, result: dict[str, Any]) -> AgentState:
    events = list(state.get("events") or [])
    events.append(result)
    return {"events": events}


def n_parse(state: AgentState) -> AgentState:
    r = T.parse_request(state.get("text") or "", state.get("form"))
    return {**_trace(state, r), "parsed": r}


def n_locate(state: AgentState) -> AgentState:
    r = T.locate_connection_point(state["parsed"]["outputs"]["parsed"])
    return {**_trace(state, r), "location": r}


def n_solution(state: AgentState) -> AgentState:
    r = T.select_solution_tool(state["location"])
    return {**_trace(state, r), "solution": r}


def n_breaker(state: AgentState) -> AgentState:
    r = T.size_breaker(state["parsed"]["outputs"]["parsed"])
    return {**_trace(state, r), "breaker": r}


def n_capacity(state: AgentState) -> AgentState:
    r = T.check_capacity(state["parsed"]["outputs"]["parsed"], state["location"], state["breaker"])
    return {**_trace(state, r), "capacity": r, "failed": bool(r["outputs"]["escalate"] or state.get("failed"))}


def n_quality(state: AgentState) -> AgentState:
    r = T.check_voltage_drop(state["parsed"]["outputs"]["parsed"], state["location"], state["solution"])
    return {**_trace(state, r), "quality": r, "failed": bool(r["outputs"]["escalate"] or state.get("failed"))}


def n_reliability(state: AgentState) -> AgentState:
    r = T.check_reliability(state["location"], state["solution"])
    return {**_trace(state, r), "reliability": r}


def n_future(state: AgentState) -> AgentState:
    r = T.check_future(state["parsed"]["outputs"]["parsed"], state["capacity"])
    return {**_trace(state, r), "future": r, "failed": bool(r["outputs"]["escalate"] or state.get("failed"))}


def n_draft(state: AgentState) -> AgentState:
    r = T.draft_ts_section3(
        state["parsed"]["outputs"]["parsed"],
        state["location"],
        state["solution"],
        state["breaker"],
        (state.get("approval") or {}).get("section3"),
    )
    return {**_trace(state, r), "draft": r}


def n_cost(state: AgentState) -> AgentState:
    r = T.estimate_cost_tool(state["solution"], state["location"])
    return {**_trace(state, r), "cost": r}


def n_map(state: AgentState) -> AgentState:
    r = T.render_map(state["parsed"]["outputs"]["parsed"], state["location"], state["solution"])
    return {**_trace(state, r), "map": r}


def n_escalate(state: AgentState) -> AgentState:
    checks = [state["capacity"], state["quality"], state["reliability"], state["future"]]
    r = T.escalate_package(checks)
    return {**_trace(state, r), "escalate": r}


def n_issue(state: AgentState) -> AgentState:
    r = T.issue_ts(
        state["parsed"]["outputs"]["parsed"],
        state["location"],
        state["solution"],
        state["breaker"],
        state["draft"],
        state.get("approval") or {"section3": state["draft"]["outputs"]["section3"]},
        state.get("run_id") or "xxxxxx",
    )
    return {**_trace(state, r), "issued": r}


def after_checks(state: AgentState) -> str:
    return "escalate" if state.get("failed") else "draft_ts_section3"


def after_approval(state: AgentState) -> str:
    decision = (state.get("approval") or {}).get("decision")
    if decision == "approve" and not state.get("failed"):
        return "issue_ts"
    return END


def build_graph():
    g = StateGraph(AgentState)
    g.add_node("parse_request", n_parse)
    g.add_node("locate_connection_point", n_locate)
    g.add_node("select_solution", n_solution)
    g.add_node("size_breaker", n_breaker)
    g.add_node("check_capacity", n_capacity)
    g.add_node("check_voltage_drop", n_quality)
    g.add_node("check_reliability", n_reliability)
    g.add_node("check_future", n_future)
    g.add_node("draft_ts_section3", n_draft)
    g.add_node("estimate_cost", n_cost)
    g.add_node("render_map", n_map)
    g.add_node("escalate", n_escalate)
    g.add_node("issue_ts", n_issue)

    g.add_edge(START, "parse_request")
    g.add_edge("parse_request", "locate_connection_point")
    g.add_edge("locate_connection_point", "select_solution")
    g.add_edge("select_solution", "size_breaker")
    g.add_edge("size_breaker", "check_capacity")
    g.add_edge("check_capacity", "check_voltage_drop")
    g.add_edge("check_voltage_drop", "check_reliability")
    g.add_edge("check_reliability", "check_future")
    g.add_conditional_edges(
        "check_future",
        after_checks,
        {"escalate": "escalate", "draft_ts_section3": "draft_ts_section3"},
    )
    g.add_edge("draft_ts_section3", "estimate_cost")
    g.add_edge("estimate_cost", "render_map")
    g.add_edge("escalate", "estimate_cost")
    # Approval is a human interrupt implemented in the engine, then issue_ts.
    g.add_edge("render_map", END)
    g.add_edge("issue_ts", END)
    return g.compile()


COMPILED = None


def compiled_graph():
    global COMPILED
    if COMPILED is None:
        COMPILED = build_graph()
    return COMPILED


def mermaid() -> str:
    try:
        return compiled_graph().get_graph().draw_mermaid()
    except Exception:  # noqa: BLE001
        return (
            "flowchart TD\n"
            "  parse_request --> locate_connection_point --> select_solution --> size_breaker\n"
            "  size_breaker --> check_capacity --> check_voltage_drop --> check_reliability --> check_future\n"
            "  check_future -->|pass| draft_ts_section3 --> estimate_cost --> render_map --> engineer_approval --> issue_ts\n"
            "  check_future -->|fail| escalate --> estimate_cost\n"
        )


BEFORE_APPROVAL = [
    n_parse,
    n_locate,
    n_solution,
    n_breaker,
    n_capacity,
    n_quality,
    n_reliability,
    n_future,
    n_draft,
    n_cost,
    n_map,
]

BEFORE_APPROVAL_FAIL = [
    n_parse,
    n_locate,
    n_solution,
    n_breaker,
    n_capacity,
    n_quality,
    n_reliability,
    n_future,
    n_escalate,
    n_cost,
    n_map,
]
