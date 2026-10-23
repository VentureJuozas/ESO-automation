"""Issued prijungimo sąlygos, rendered from the TSL2 Word template."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from eso_agent.audit import build_audit
from eso_agent.gis_map import KIND_LT
from eso_agent.ts_text import issue_dates, ownership_boundary, section3_blocks

REDACTED_CUSTOMER = "Buitinis vartotojas (redaguota)"
REDACTED_CODE = "ASMENS KODAS / EIC REDAGUOTAS"
REDACTED_ADDRESS = "Adresas redaguotas · objektas prie TP 12-608 (koordinatės, be gatvės)"
REDACTED_OPERATOR = "AB Energijos skirstymo operatorius"
SOLUTION_LT = {
    "A": "A · esama KAS, jungiklio keitimas",
    "B": "B · nauja KAS ant atramos",
    "C": "C · nauja KS/KAS sklypo riboje",
}
LAYOUT_BANNER = ""


def _phase_label(phases: Any) -> str:
    return "Trifazis" if phases == 3 else "Vienfazis"


def build_ts_document(
    parsed: dict[str, Any],
    location: dict[str, Any],
    solution: dict[str, Any],
    breaker: dict[str, Any],
    section3: str,
    *,
    issued: bool = False,
    ts_number: str = "PROJEKTAS",
    issue_date: str | None = None,
    valid_until: str | None = None,
    run_id: str = "",
) -> dict[str, Any]:
    loc = location.get("outputs") or location
    sol = solution.get("outputs") or solution
    br = breaker.get("outputs") or breaker
    today, plus_year = issue_dates()
    if issued:
        issue_date = issue_date or today
        valid_until = valid_until or plus_year
        watermark = None
    else:
        watermark = "PROJEKTAS. SUTARTIS NEPATVIRTINTA"
        valid_until = valid_until or plus_year
    feeder = loc.get("feeder") if isinstance(loc.get("feeder"), str) else (loc.get("feeder_record") or {}).get("name")
    element = loc.get("element_id") or (loc.get("element") or {}).get("id")
    kind = (loc.get("element") or {}).get("kind") or "pole"
    kw = parsed.get("kw")
    phases = parsed.get("phases")
    obj = parsed.get("object_name") or "Naujas buitinis objektas"
    section2 = [
        "2.1. Įrengti objekto vidaus elektros tinklą iki nuosavybės ribos.",
        "2.2. Užtikrinti laisvą prieigą prie komercinės apskaitos spintos.",
        "2.3. Atlikti reikalingus žemės darbus savo sklype pagal operatoriaus nurodymus.",
        "2.9. Generacija / kaupimas: neprašoma.",
        "2.13. Pirmas prijungimas: taip.",
    ]
    obligations = [
        "5.1. Sąlygos galioja vienerius metus nuo parengimo datos.",
        "5.2. Klientas apmoka prijungimo įmoką pagal galiojančią metodiką (čia — orientyras).",
        "5.3. Darbus tinkle atlieka operatorius arba jo rangovas po sutarties.",
        "5.4. Sąlygas tvirtina inžinierius. Be parašo dokumentas negalioja.",
    ]
    return {
        "ts_number": ts_number if issued else "PROJEKTAS",
        "issue_date": issue_date,
        "valid_until": valid_until,
        "watermark": watermark,
        "object_name": obj,
        "customer": REDACTED_CUSTOMER,
        "customer_code": REDACTED_CODE,
        "address": REDACTED_ADDRESS,
        "operator": REDACTED_OPERATOR,
        "kw": kw,
        "phases": phases,
        "phase_label": _phase_label(phases),
        "voltage_level": "0,4 kV",
        "tp": "12-608",
        "feeder": feeder,
        "element": element,
        "connection_kind": KIND_LT.get(kind, "Elementas"),
        "solution": sol.get("id"),
        "solution_label": SOLUTION_LT.get(sol.get("id") or "", sol.get("id") or "—"),
        "breaker": br.get("label"),
        "section1": ownership_boundary(sol.get("id") or "B"),
        "section2": section2,
        "section3": section3,
        "blocks": section3_blocks(sol, br, loc) if not section3 else [],
        "obligations": obligations,
        "coords": {"lat": parsed.get("lat"), "lon": parsed.get("lon"), "source": "synthetic"},
        "signature": {
            "prepared": "Parengė automatizuoti tinklo įrankiai",
            "approved": "Inžinierius",
            "title": "Prijungimo sąlygų inžinierius",
            "action": None,
            "approved_at": None,
            "reason": "",
        },
        "disclaimer": "Asmens duomenys redaguoti.",
        "layout": "demo",
        "banner": LAYOUT_BANNER,
        "run_id": run_id,
        "issued": issued,
    }


def _fmt_ts(ts: Any) -> str | None:
    if ts is None:
        return None
    try:
        return datetime.fromtimestamp(float(ts), tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    except (TypeError, ValueError, OSError):
        return str(ts)


def document_from_snap(snap: dict[str, Any]) -> dict[str, Any]:
    issued = snap.get("issued") or {}
    draft = snap.get("draft") or {}
    parsed = snap.get("parsed") or {}
    loc = snap.get("location") or {}
    sol = snap.get("solution") or {}
    br = snap.get("breaker") or {}
    doc = dict(issued.get("document") or draft.get("document") or {})
    if not doc:
        doc = build_ts_document(
            parsed,
            loc,
            {"outputs": sol} if "id" in (sol or {}) else sol or {},
            {"outputs": br} if "label" in (br or {}) else br or {},
            issued.get("section3") or draft.get("section3") or "",
            issued=bool(issued),
            ts_number=issued.get("ts_number") or "PROJEKTAS",
            issue_date=issued.get("issue_date"),
            valid_until=issued.get("valid_until"),
            run_id=str(snap.get("id") or ""),
        )
    if issued:
        doc["ts_number"] = issued.get("ts_number") or doc.get("ts_number")
        doc["issue_date"] = issued.get("issue_date") or doc.get("issue_date")
        doc["valid_until"] = issued.get("valid_until") or doc.get("valid_until")
        doc["watermark"] = None
        doc["section3"] = issued.get("section3") or doc.get("section3")
        doc["issued"] = True
    doc.setdefault("kw", parsed.get("kw"))
    doc.setdefault("phases", parsed.get("phases"))
    doc.setdefault("phase_label", _phase_label(doc.get("phases")))
    doc.setdefault("voltage_level", "0,4 kV")
    doc.setdefault("tp", "12-608")
    doc.setdefault("feeder", loc.get("feeder"))
    doc.setdefault("element", loc.get("element_id") or (loc.get("element") or {}).get("id"))
    kind = (loc.get("element") or {}).get("kind") or "pole"
    doc.setdefault("connection_kind", KIND_LT.get(kind, "Elementas"))
    doc.setdefault("solution", sol.get("id"))
    doc.setdefault("solution_label", SOLUTION_LT.get(sol.get("id") or "", sol.get("id") or "—"))
    doc.setdefault("breaker", br.get("label"))
    doc.setdefault("customer", REDACTED_CUSTOMER)
    doc.setdefault("customer_code", REDACTED_CODE)
    doc.setdefault("address", REDACTED_ADDRESS)
    doc.setdefault("operator", REDACTED_OPERATOR)
    doc.setdefault("object_name", parsed.get("object_name") or "Naujas buitinis objektas")
    doc.setdefault("banner", LAYOUT_BANNER)
    doc.setdefault("layout", "TSL2_K1")
    doc["run_id"] = str(snap.get("id") or doc.get("run_id") or "")
    cost = snap.get("cost") or {}
    doc["cost"] = {
        "net": cost.get("net"),
        "gross": cost.get("gross"),
        "vat_rate": cost.get("vat_rate"),
        "currency": cost.get("currency") or "EUR",
        "note": cost.get("note") or "Orientyras, ne oficiali sąmata.",
        "lines": cost.get("lines") or [],
    }
    actions = list(snap.get("audit") or [])
    approve = next((a for a in reversed(actions) if a.get("action") in {"approve", "engineer_override"}), None)
    sig = dict(doc.get("signature") or {})
    sig["prepared"] = sig.get("prepared") or "Parengė automatizuoti tinklo įrankiai"
    sig["approved"] = snap.get("assignee") or sig.get("approved") or "I. Petrauskas (redaguota)"
    sig["title"] = sig.get("title") or "Prijungimo sąlygų inžinierius"
    if approve:
        sig["action"] = approve.get("action")
        sig["approved_at"] = _fmt_ts(approve.get("ts"))
        sig["reason"] = approve.get("reason") or ""
    doc["signature"] = sig
    try:
        from eso_agent.engine import RUNS

        run = RUNS.get(snap.get("id") or "")
    except Exception:  # noqa: BLE001
        run = None
    audit = build_audit(run, snap)
    doc["sha256"] = audit.get("sha256") or ""
    doc["coords"] = doc.get("coords") or {
        "lat": parsed.get("lat"),
        "lon": parsed.get("lon"),
        "source": "synthetic",
    }
    if not doc.get("obligations"):
        doc["obligations"] = [
            "5.1. Sąlygos galioja vienerius metus nuo parengimo datos.",
            "5.2. Klientas apmoka prijungimo įmoką pagal galiojančią metodiką (čia — orientyras).",
            "5.3. Darbus tinkle atlieka operatorius arba jo rangovas po sutarties.",
            "5.4. Sąlygas tvirtina inžinierius. Be parašo dokumentas negalioja.",
        ]
    return doc


def render_ts_html(snap: dict[str, Any]) -> str:
    from eso_agent.ts_template import fill_ts_docx, render_docx_html

    doc = document_from_snap(snap)
    return render_docx_html(fill_ts_docx(doc), run_id=str(doc.get('run_id') or ''))
