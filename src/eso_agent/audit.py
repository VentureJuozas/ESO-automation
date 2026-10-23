"""Immutable audit snapshot for a run (JSON + readable HTML)."""
from __future__ import annotations

import hashlib
import json
from html import escape
from typing import Any


def build_audit(run: dict[str, Any] | None, snap: dict[str, Any] | None = None) -> dict[str, Any]:
    run = run or {}
    events = list(run.get("events") or (snap or {}).get("events") or [])
    tools = []
    for ev in events:
        if ev.get("type") != "tool":
            continue
        tools.append(
            {
                "ts": ev.get("ts"),
                "tool": ev.get("tool"),
                "title": ev.get("title_lt") or ev.get("title"),
                "ok": ev.get("ok"),
                "elapsed_ms": ev.get("elapsed_ms"),
                "source_tags": ev.get("source_tags") or [],
                "inputs": ev.get("inputs") or {},
                "outputs": ev.get("outputs") or {},
            }
        )
    payload = {
        "run_id": run.get("id") or (snap or {}).get("id"),
        "status": run.get("status") or (snap or {}).get("status"),
        "scenario_id": run.get("scenario_id") or (snap or {}).get("scenario_id"),
        "started": run.get("started") or (snap or {}).get("started"),
        "assignee": run.get("assignee") or (snap or {}).get("assignee"),
        "queue_id": run.get("queue_id"),
        "overridden": bool((run.get("state") or {}).get("overridden") or (snap or {}).get("overridden")),
        "engineer_actions": list(run.get("audit") or (snap or {}).get("audit") or []),
        "tools": tools,
        "disclaimer": "Snapshot užfiksuotas eksportuojant. Asmens duomenų nėra — tik redaguoti laukai.",
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    payload["sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    payload["immutable"] = True
    return payload


def render_audit_html(audit: dict[str, Any]) -> str:
    rows = "".join(
        f"<tr><td>{escape(str(t.get('ts') or ''))}</td>"
        f"<td>{escape(str(t.get('tool')))}</td>"
        f"<td>{escape(str(t.get('elapsed_ms')))} ms</td>"
        f"<td>{escape(', '.join(t.get('source_tags') or []))}</td>"
        f"<td><pre>{escape(json.dumps(t.get('inputs'), ensure_ascii=False, default=str)[:800])}</pre></td>"
        f"<td><pre>{escape(json.dumps(t.get('outputs'), ensure_ascii=False, default=str)[:1200])}</pre></td></tr>"
        for t in audit.get("tools") or []
    )
    actions = "".join(
        f"<li><b>{escape(str(a.get('action')))}</b> — {escape(str(a.get('reason') or a.get('section3') or ''))} "
        f"<small>{escape(str(a.get('ts') or ''))}</small></li>"
        for a in audit.get("engineer_actions") or []
    ) or "<li>Inžinieriaus veiksmų nėra.</li>"
    return f"""<!DOCTYPE html>
<html lang="lt"><head><meta charset="utf-8"><title>Auditas {escape(str(audit.get('run_id')))}</title>
<style>
  @page {{ size: A4; margin: 12mm; }}
  body {{ font-family: Inter, "Segoe UI", sans-serif; color: #111; margin: 20px; font-size: 12px; }}
  pre {{ white-space: pre-wrap; font-size: 10px; margin: 0; max-height: 140px; overflow: auto; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th, td {{ border-bottom: 1px solid #ddd; padding: 6px 4px; vertical-align: top; text-align: left; }}
  .hash {{ font-family: ui-monospace, monospace; font-size: 11px; word-break: break-all; }}
  .noprint button {{ border: 0; background: #1c1c1f; color: #fff; padding: 8px 14px; border-radius: 8px; }}
  @media print {{ .noprint {{ display: none; }} }}
</style></head><body>
<div class="noprint"><button onclick="window.print()">Spausdinti / PDF</button></div>
<h1>Audito įrašas, {escape(str(audit.get('run_id')))}</h1>
<p>Būsena: {escape(str(audit.get('status')))}, Scenarijus: {escape(str(audit.get('scenario_id')))},
Priskirta: {escape(str(audit.get('assignee') or '—'))}</p>
<p class="hash">SHA-256: {escape(str(audit.get('sha256')))}</p>
<h2>Inžinieriaus veiksmai</h2>
<ul>{actions}</ul>
<h2>Įrankių kvietimai</h2>
<table>
<tr><th>Laikas</th><th>Įrankis</th><th>ms</th><th>Šaltiniai</th><th>Įvestis</th><th>Išvestis</th></tr>
{rows}
</table>
<p>{escape(str(audit.get('disclaimer') or ''))}</p>
</body></html>"""
