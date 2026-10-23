"""Customer-facing application flow. Synthetic / redacted only."""
from __future__ import annotations

import time
from typing import Any

from eso_agent.adapters import get_adapters
from eso_agent.adapters.crm import REDACTED_ADDRESS, REDACTED_NAME
from eso_agent.document import render_ts_html
from eso_agent.engine import RUNS, run_sync_until_interrupt, snapshot, supply_data
from eso_agent.pdfutil import render_official_ts_pdf
from eso_agent.queue import QUEUE, ensure_queue, sla_for

STATUS_MAP = {
    "queued": "gauta",
    "new": "gauta",
    "running": "tikrinama",
    "waiting_data": "laukia duomenų",
    "awaiting_approval": "laukia inžinieriaus",
    "issued": "išduota",
    "escalated": "perduota inžinieriui",
    "error": "klaida",
}

TRACK = ["gauta", "tikrinama", "laukia duomenų", "laukia inžinieriaus", "išduota"]


def _stamp(rec: dict[str, Any], status: str) -> None:
    tl = list(rec.get("timeline") or [])
    if not tl or tl[-1].get("status") != status:
        tl.append({"status": status, "at": time.time()})
    rec["timeline"] = tl


def _public(rec: dict[str, Any], snap: dict[str, Any] | None = None) -> dict[str, Any]:
    run_status = (snap or {}).get("status") or rec.get("run_status")
    status = STATUS_MAP.get(run_status, rec.get("status") or "gauta")
    missing = (snap or {}).get("missing") if status == "laukia duomenų" else None
    issued = bool((snap or {}).get("issued"))
    submitted = rec.get("created_at") or time.time()
    sla = sla_for(submitted, rec.get("kw"))
    return {
        "id": rec["id"],
        "status": status,
        "track": TRACK,
        "timeline": rec.get("timeline") or [{"status": "gauta", "at": submitted}],
        "kw": rec.get("kw"),
        "phases": rec.get("phases"),
        "lat": rec.get("lat"),
        "lon": rec.get("lon"),
        "object_name": rec.get("object_name"),
        "address": REDACTED_ADDRESS,
        "customer": REDACTED_NAME,
        "run_id": rec.get("run_id"),
        "missing": missing,
        "issued": issued,
        "sla": sla,
        "decision_by": sla.get("deadline_at"),
        "ts_url": f"/api/portal/applications/{rec['id']}/ts.html" if issued else None,
        "pdf_url": f"/api/portal/applications/{rec['id']}/ts.pdf" if issued else None,
        "demo": True,
        "banner": "Demonstracinis maketas. Neoficialus ESO portalas. Asmens duomenų nėra.",
    }


def _persist(rec: dict[str, Any], status: str) -> dict[str, Any]:
    _stamp(rec, status)
    rec["status"] = status
    return get_adapters().crm.update(rec["id"], rec)


def submit(form: dict[str, Any]) -> dict[str, Any]:
    crm = get_adapters().crm
    kw = float(form.get("kw") or 11)
    phases = int(form.get("phases") or 3)
    lat = form.get("lat")
    lon = form.get("lon")
    text = (
        f"Portalo paraiška: {kw} kW, {phases}F, "
        f"{'koordinatės ' + str(lat) + ', ' + str(lon) if lat and lon else 'koordinačių nėra'}."
    )
    payload = {
        "kw": kw,
        "phases": phases,
        "lat": lat,
        "lon": lon,
        "customer_type": "household",
        "text": text,
        "object_name": form.get("object_name") or "Naujas buitinis objektas",
    }
    rec = crm.create(payload)
    _stamp(rec, "gauta")
    qid = rec["id"]
    ensure_queue()
    QUEUE.append(
        {
            "id": qid,
            "title": rec["object_name"],
            "mix": "portal",
            "assignee": "I. Petrauskas (redaguota)",
            "submitted_at": time.time(),
            "data_gap": lat is None,
            "form": payload,
            "status": "new",
            "run_id": None,
            "kw": kw,
            "phases": phases,
            "sla": sla_for(time.time(), kw),
        }
    )
    rec = _persist(rec, "tikrinama")
    snap = run_sync_until_interrupt("intake", delay=0, text=text, form={**payload, "_queue": {"queue_id": qid}})
    status = STATUS_MAP.get(snap["status"], "tikrinama")
    rec = crm.update(
        rec["id"],
        {
            "run_id": snap["id"],
            "queue_id": qid,
            "status": status,
            "run_status": snap["status"],
        },
    )
    rec = crm.get(rec["id"]) or rec
    _stamp(rec, status)
    rec = crm.update(rec["id"], rec)
    return _public(rec, snap)


def get_app(app_id: str) -> dict[str, Any]:
    rec = get_adapters().crm.get(app_id)
    if not rec:
        raise KeyError(app_id)
    snap = snapshot(RUNS[rec["run_id"]]) if rec.get("run_id") and rec["run_id"] in RUNS else None
    if snap:
        status = STATUS_MAP.get(snap["status"], rec.get("status"))
        get_adapters().crm.update(app_id, {"run_status": snap["status"], "status": status})
        rec = get_adapters().crm.get(app_id) or rec
        tl = rec.get("timeline") or []
        if not tl or tl[-1].get("status") != status:
            _stamp(rec, status)
            rec = get_adapters().crm.update(app_id, rec)
    return _public(rec, snap)


def answer(app_id: str, fields: dict[str, Any]) -> dict[str, Any]:
    rec = get_adapters().crm.get(app_id)
    if not rec or not rec.get("run_id"):
        raise KeyError(app_id)
    snap = supply_data(rec["run_id"], fields)
    status = STATUS_MAP.get(snap["status"], "tikrinama")
    rec = get_adapters().crm.update(
        app_id,
        {
            "run_status": snap["status"],
            "status": status,
            "lat": fields.get("lat"),
            "lon": fields.get("lon"),
        },
    )
    rec = get_adapters().crm.get(app_id) or rec
    _stamp(rec, "tikrinama")
    _stamp(rec, status)
    rec = get_adapters().crm.update(app_id, rec)
    return _public(rec, snap)


def ts_html(app_id: str) -> str:
    rec = get_adapters().crm.get(app_id)
    if not rec or not rec.get("run_id") or rec["run_id"] not in RUNS:
        raise KeyError(app_id)
    return render_ts_html(snapshot(RUNS[rec["run_id"]]))


def ts_pdf(app_id: str) -> bytes:
    rec = get_adapters().crm.get(app_id)
    if not rec or not rec.get("run_id") or rec["run_id"] not in RUNS:
        raise KeyError(app_id)
    return render_official_ts_pdf(snapshot(RUNS[rec["run_id"]]))
