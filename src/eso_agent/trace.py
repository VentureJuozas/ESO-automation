"""Visible LangGraph tool-call trace: LLM vs Python vs human."""
from __future__ import annotations

from typing import Any

from eso_agent.catalog import TOOLS, tool_by_id

KIND_LT = {"llm": "LLM", "tool": "Python", "human": "Žmogus"}
KIND_HINT = {
    "llm": "Skaito paraišką arba formuluoja §3. Inžinerijos nesprendžia.",
    "tool": "Deterministinė taisyklė. Python priima sprendimą.",
    "human": "Žmogaus vartai. Be parašo TS neišduodama.",
}


def classify(tool_id: str, event: dict[str, Any] | None = None) -> str:
    meta = tool_by_id(tool_id)
    kind = (event or {}).get("kind") or meta.get("kind") or "tool"
    if kind == "llm":
        return "llm"
    if kind == "human" or (event or {}).get("type") == "interrupt" and tool_id in {"engineer_approval", "request_missing_data"}:
        return "human"
    if tool_id in {"engineer_approval", "request_missing_data"}:
        return "human"
    if tool_id in {"parse_request", "draft_ts_section3"}:
        return "llm"
    return "tool"


def _summarise(payload: Any, limit: int = 180) -> str:
    if payload is None:
        return "—"
    if isinstance(payload, str):
        text = payload.strip()
        return text if len(text) <= limit else text[: limit - 1] + "…"
    if isinstance(payload, (int, float, bool)):
        return str(payload)
    if isinstance(payload, list):
        return f"{len(payload)} įrašai"
    if isinstance(payload, dict):
        keys = ("kw", "phases", "id", "label", "feeder", "element_id", "ts_number", "pass", "escalate", "section3")
        bits = []
        for k in keys:
            if k in payload and payload[k] not in (None, "", [], {}):
                val = payload[k]
                if isinstance(val, dict):
                    continue
                bits.append(f"{k}={val}" if not isinstance(val, str) or len(val) < 40 else f"{k}={val[:36]}…")
            if len(bits) >= 4:
                break
        if not bits:
            bits = [str(k) for k in list(payload.keys())[:4]]
        return ", ".join(bits) or "—"
    return str(payload)[:limit]


def _llm_role(tool_id: str) -> str:
    if tool_id == "parse_request":
        return "skaitymas"
    if tool_id == "draft_ts_section3":
        return "formulavimas"
    return "tekstas"


def build_trace(snap: dict[str, Any] | None = None, events: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    rows = list(events if events is not None else (snap or {}).get("events") or [])
    steps: list[dict[str, Any]] = []
    n = 0
    for ev in rows:
        if ev.get("type") not in {"tool", "interrupt"}:
            continue
        tool = ev.get("tool") or ""
        if not tool:
            continue
        n += 1
        meta = tool_by_id(tool)
        kind = classify(tool, ev)
        ref = ev.get("rule_ref") or meta.get("rule_ref") or {}
        steps.append(
            {
                "step": n,
                "tool": tool,
                "title": ev.get("title_lt") or ev.get("title") or meta.get("title_lt") or tool,
                "kind": kind,
                "kind_lt": KIND_LT[kind],
                "llm_role": _llm_role(tool) if kind == "llm" else None,
                "hint": KIND_HINT[kind],
                "inputs": ev.get("inputs") or {},
                "outputs": ev.get("outputs") or {},
                "input_summary": _summarise(ev.get("inputs")),
                "output_summary": _summarise(ev.get("outputs")),
                "elapsed_ms": ev.get("elapsed_ms") or 0,
                "source_tags": ev.get("source_tags") or [],
                "rule": meta.get("rule") or "",
                "rule_ref": {
                    "label": (ref or {}).get("label") or meta.get("rule"),
                    "local": (ref or {}).get("local"),
                    "url": (ref or {}).get("url"),
                },
                "ok": ev.get("ok", True),
                "type": ev.get("type"),
            }
        )
    llm = sum(1 for s in steps if s["kind"] == "llm")
    python = sum(1 for s in steps if s["kind"] == "tool")
    human = sum(1 for s in steps if s["kind"] == "human")
    return {
        "steps": steps,
        "stats": {
            "llm": llm,
            "python": python,
            "human": human,
            "line": f"{llm} LLM kvietimai · {python} deterministiniai įrankiai · {human} žmogaus vartai",
        },
        "legend": [
            {"id": "llm", "label": "LLM", "hint": KIND_HINT["llm"]},
            {"id": "tool", "label": "Python", "hint": KIND_HINT["tool"]},
            {"id": "human", "label": "Žmogus", "hint": KIND_HINT["human"]},
        ],
        "catalog": [{"id": t["id"], "kind": t.get("kind") or "tool"} for t in TOOLS],
    }
