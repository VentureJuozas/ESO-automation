"""Customer-facing application flow. Synthetic / redacted only."""
from __future__ import annotations

import time
from typing import Any

from eso_agent.adapters import get_adapters
from eso_agent.adapters.crm import REDACTED_ADDRESS, REDACTED_NAME
from eso_agent.document import REDACTED_CUSTOMER, render_ts_html
from eso_agent.engine import RUNS, create_run, run_sync_until_interrupt, snapshot, supply_data
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

TRACK = ["gauta", "tikrinama", "laukia inžinieriaus", "išduota"]


def _public(rec: dict[str, Any], snap: dict[str, Any] | None = None) -> dict[str, Any]:
    run_status = (snap or {}).get("status") or rec.get("run_status")
    status = STATUS_MAP.get(run_status, rec.get("status") or "gauta")
    missing = (snap or {}).get("missing") if status == "laukia duomenų" else None
    issued = bool((snap or {}).get("issued"))
    return {
        "id": rec["id"],
        "status": status,
        "track": TRACK,
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
        "ts_url": f"/api/portal/applications/{rec['id']}/ts.html" if issued else None,
        "pdf_url": f"/api/portal/applications/{rec['id']}/ts.pdf" if issued else None,
        "demo": True,
        "banner": "Demonstracinis maketas. Neoficialus ESO portalas. Asmens duomenų nėra.",
    }


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
    snap = run_sync_until_interrupt("intake", delay=0, text=text, form={**payload, "_queue": {"queue_id": qid}})
    rec = crm.update(rec["id"], {"run_id": snap["id"], "queue_id": qid, "status": STATUS_MAP.get(snap["status"], "tikrinama"), "run_status": snap["status"]})
    return _public(rec, snap)


def get_app(app_id: str) -> dict[str, Any]:
    rec = get_adapters().crm.get(app_id)
    if not rec:
        raise KeyError(app_id)
    snap = snapshot(RUNS[rec["run_id"]]) if rec.get("run_id") and rec["run_id"] in RUNS else None
    if snap:
        get_adapters().crm.update(app_id, {"run_status": snap["status"], "status": STATUS_MAP.get(snap["status"], rec.get("status"))})
        rec = get_adapters().crm.get(app_id) or rec
    return _public(rec, snap)


def answer(app_id: str, fields: dict[str, Any]) -> dict[str, Any]:
    rec = get_adapters().crm.get(app_id)
    if not rec or not rec.get("run_id"):
        raise KeyError(app_id)
    snap = supply_data(rec["run_id"], fields)
    get_adapters().crm.update(app_id, {"run_status": snap["status"], "status": STATUS_MAP.get(snap["status"], "tikrinama"), "lat": fields.get("lat"), "lon": fields.get("lon")})
    rec = get_adapters().crm.get(app_id) or rec
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
    snap = snapshot(RUNS[rec["run_id"]])
    issued = snap.get("issued") or {}
    doc = issued.get("document") or {}
    lines = [
        "PRIJUNGIMO SALYGOS (demonstracija)",
        f"Nr. {issued.get('ts_number') or doc.get('ts_number') or 'PROJEKTAS'}",
        f"Objektas: {doc.get('object_name') or snap.get('parsed', {}).get('object_name')}",
        f"Klientas: {REDACTED_CUSTOMER}",
        f"Adresas: {REDACTED_ADDRESS}",
        f"Galia: {snap.get('parsed', {}).get('kw')} kW  {snap.get('parsed', {}).get('phases')}F",
        f"Sprendinys: {(snap.get('solution') or {}).get('id')}  {(snap.get('breaker') or {}).get('label')}",
        "",
        (issued.get("section3") or (snap.get("draft") or {}).get("section3") or "")[:1200],
        "",
        "Neoficialus dokumentas. Asmens duomenys redaguoti.",
    ]
    return _plain_pdf(lines)


def _plain_pdf(lines: list[str]) -> bytes:
    """Minimal PDF, Latin-1 fallback. No third-party renderer."""
    def esc(s: str) -> str:
        return s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)").encode("latin-1", "replace").decode("latin-1")

    y = 800
    cmds = ["BT", "/F1 11 Tf"]
    for line in lines:
        for chunk in line.split("\n"):
            cmds.append(f"1 0 0 1 48 {y} Tm ({esc(chunk[:110])}) Tj")
            y -= 14
            if y < 48:
                break
    cmds.append("ET")
    stream = "\n".join(cmds).encode("latin-1")
    objs = []
    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objs.append(b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objs.append(b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>")
    objs.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    out = bytearray(b"%PDF-1.4\n")
    xref = [0]
    for i, obj in enumerate(objs, 1):
        xref.append(len(out))
        out += f"{i} 0 obj\n".encode() + obj + b"\nendobj\n"
    start = len(out)
    out += f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()
    for off in xref[1:]:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF".encode()
    return bytes(out)
