"""Printable A4 TS HTML — official-looking demo blank, two pages, no ESO logo."""
from __future__ import annotations

from datetime import datetime, timezone
from html import escape
from typing import Any

from eso_agent.audit import build_audit
from eso_agent.fonts import GLYPHS, font_face_css
from eso_agent.gis_map import KIND_LT, render_gis_svg
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
    doc.setdefault("layout", "demo")
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
    doc = document_from_snap(snap)
    number = escape(str(doc.get("ts_number") or "PROJEKTAS"))
    issue = escape(str(doc.get("issue_date") or "—"))
    valid = escape(str(doc.get("valid_until") or "—"))
    watermark = doc.get("watermark")
    s3 = escape(doc.get("section3") or "").replace("\n", "<br>")
    s1 = escape(doc.get("section1") or "")
    kw = doc.get("kw")
    phase = escape(str(doc.get("phase_label") or "—"))
    obj = escape(str(doc.get("object_name") or "Naujas buitinis objektas"))
    customer = escape(str(doc.get("customer") or REDACTED_CUSTOMER))
    code = escape(str(doc.get("customer_code") or REDACTED_CODE))
    addr = escape(str(doc.get("address") or REDACTED_ADDRESS))
    operator = escape(str(doc.get("operator") or REDACTED_OPERATOR))
    feeder = escape(str(doc.get("feeder") or "—"))
    element = escape(str(doc.get("element") or "—"))
    kind = escape(str(doc.get("connection_kind") or "—"))
    br = escape(str(doc.get("breaker") or "—"))
    sol = escape(str(doc.get("solution_label") or doc.get("solution") or "—"))
    volt = escape(str(doc.get("voltage_level") or "0,4 kV"))
    section2 = doc.get("section2") or []
    s2 = "".join(f"<li>{escape(p)}</li>" for p in section2)
    obligations = "".join(f"<li>{escape(p)}</li>" for p in (doc.get("obligations") or []))
    sig = doc.get("signature") or {}
    cost = doc.get("cost") or {}
    cost_lines = doc.get("cost", {}).get("lines") or []
    cost_rows = "".join(
        "<tr><td>{}</td><td>{} {}</td><td>{}</td></tr>".format(
            escape(str(ln.get("item") or "")),
            escape(str(ln.get("qty") or "")),
            escape(str(ln.get("unit") or "")),
            "" if ln.get("price") is None else f"{ln.get('price'):.2f} EUR",
        )
        for ln in cost_lines[:6]
    )
    gross = cost.get("gross")
    net = cost.get("net")
    sha = escape(str(doc.get("sha256") or "—"))
    wm = f'<div class="wm">{escape(watermark)}</div>' if watermark else ""
    approved_at = escape(str(sig.get("approved_at") or "—"))
    action = escape(str(sig.get("action") or ("patvirtinta" if doc.get("issued") else "laukiama")))
    reason = escape(str(sig.get("reason") or ""))
    coords = doc.get("coords") or {}
    svg = render_gis_svg(coords.get("lat"), coords.get("lon"), doc.get("element"), doc.get("feeder"))
    banner = escape(str(doc.get("banner") or LAYOUT_BANNER))
    return f"""<!DOCTYPE html>
<html lang="lt" translate="no">
<head>
<meta charset="utf-8">
<title>Prijungimo sąlygos {number}</title>
<style>
  {font_face_css()}
  @page {{ size: A4; margin: 12mm 12mm 14mm 12mm; }}
  html, body {{ background: #e8e6e1; }}
  body {{ font-family: DejaVu, "Times New Roman", Times, Georgia, serif; color: #111; margin: 0; }}
  .sheet {{
    width: 210mm; min-height: 297mm; margin: 16px auto; background: #fff;
    padding: 12mm 14mm 16mm; box-sizing: border-box; position: relative;
    box-shadow: 0 8px 28px rgba(24,24,27,.08); page-break-after: always;
  }}
  .banner {{
    font-family: DejaVu, Inter, sans-serif; font-size: 8.5px; letter-spacing: .14em;
    text-transform: uppercase; border: 1px solid #111; padding: 4px 8px; text-align: center;
    margin-bottom: 8px; background: #f6f4ee;
  }}
  header.block {{
    display: grid; grid-template-columns: 1fr auto; gap: 12px;
    border: 2px solid #111; padding: 8px 10px; margin-bottom: 10px;
  }}
  .org {{ font-size: 10px; letter-spacing: .08em; text-transform: uppercase; color: #333; }}
  h1 {{ font-size: 15px; margin: 4px 0 0; letter-spacing: .02em; }}
  .reg {{ text-align: right; font-size: 12px; }}
  .reg b {{ font-size: 14px; }}
  h2 {{ font-size: 11.5px; margin: 10px 0 4px; border-bottom: 1px solid #111; padding-bottom: 2px;
       letter-spacing: .08em; text-transform: uppercase; }}
  table {{ width: 100%; border-collapse: collapse; margin: 4px 0 8px; font-size: 11.5px; }}
  td, th {{ padding: 3px 6px; vertical-align: top; border: 1px solid #bbb; }}
  th {{ background: #f3f1ea; font-weight: 700; text-align: left; width: 38%; }}
  .wm {{ position: absolute; inset: 34% 8%; font-size: 22px; color: rgba(180,0,0,.16); font-weight: 700;
        transform: rotate(-18deg); pointer-events: none; text-align: center; }}
  ol {{ margin: 4px 0 8px 18px; padding: 0; font-size: 11.5px; }}
  li {{ margin: 2px 0; }}
  .note {{ font-size: 9px; color: #444; margin-top: 8px; }}
  .sig {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 14px; font-size: 11px; }}
  .line {{ border-top: 1px solid #111; margin-top: 22px; padding-top: 4px; min-height: 42px; }}
  .foot {{
    position: absolute; left: 14mm; right: 14mm; bottom: 8mm;
    font-size: 8px; font-family: DejaVu, sans-serif; color: #333;
    border-top: 1px solid #111; padding-top: 4px; word-break: break-all;
  }}
  .pg {{ float: right; letter-spacing: .08em; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 10px 16px; font-size: 10.5px; margin: 8px 0; }}
  .legend i {{ display: inline-block; width: 10px; height: 10px; margin-right: 4px; vertical-align: -1px; border: 1px solid #111; }}
  .mapbox {{ border: 1px solid #111; padding: 4px; }}
  .noprint {{ margin: 12px auto; width: 210mm; }}
  .noprint button {{ border: 0; background: #1c1c1f; color: #fff; padding: 8px 14px; border-radius: 8px; font-weight: 600; }}
  @media print {{
    html, body {{ background: #fff; }}
    .sheet {{ margin: 0; box-shadow: none; width: auto; min-height: auto; padding: 0; }}
    .noprint {{ display: none; }}
    .foot {{ position: static; margin-top: 18px; }}
  }}
</style>
</head>
<body>
<div class="noprint"><button onclick="window.print()">Spausdinti / įrašyti PDF (A4, 2 psl.)</button></div>
<div class="sheet" data-page="1" data-testid="ts-page-1">
{wm}
<header class="block">
  <div>
    <div class="org">AB Energijos skirstymo operatorius</div>
    <h1>ELEKTROS VARTOTOJO PRIJUNGIMO SĄLYGOS</h1>
    <div class="org">0,4 kV buitinis prijungimas · TP 12-608</div>
  </div>
  <div class="reg">
    Registracijos Nr.<br><b>{number}</b><br>
    Išdavimo data: {issue}<br>
    Galioja iki: {valid}
  </div>
</header>
<h2>Šalys (redaguota)</h2>
<table>
<tr><th>Klientas</th><td>{customer}</td></tr>
<tr><th>Identifikatorius</th><td>{code}</td></tr>
<tr><th>Objektas</th><td>{obj}</td></tr>
<tr><th>Objekto vieta</th><td>{addr}</td></tr>
<tr><th>Operatorius</th><td>{operator}</td></tr>
</table>
<h2>Techniniai parametrai</h2>
<table>
<tr><th>Leistina naudoti galia</th><td>{kw} kW</td></tr>
<tr><th>Fazės</th><td>{phase}</td></tr>
<tr><th>Automatinis jungiklis</th><td>{br}</td></tr>
<tr><th>Prijungimo taškas</th><td>{kind} {element} · linija {feeder} · TP 12-608</td></tr>
<tr><th>Įtampos lygis</th><td>{volt}</td></tr>
<tr><th>Sprendinio tipas</th><td>{sol}</td></tr>
</table>
<h2>Sąlygos</h2>
<ol>
<li>Nuosavybės riba. {s1}</li>
{s2}
<li>Operatoriaus veiksmai (§3).<br>{s3}</li>
</ol>
<h2>Sąmata ir įsipareigojimai</h2>
<table>
<tr><th>Pozicija</th><th>Kiekis</th><th>Suma</th></tr>
{cost_rows}
<tr><th>Iš viso be PVM</th><td></td><td>{"" if net is None else f"{net:.2f} EUR"}</td></tr>
<tr><th>Iš viso su PVM</th><td></td><td>{"" if gross is None else f"{gross:.2f} EUR"}</td></tr>
</table>
<p class="note">{escape(str(cost.get("note") or "Orientyras iš 26-E-37934, ne oficiali šios paraiškos sąmata."))}</p>
<ol>{obligations}</ol>
<h2>Parašai ir tvirtinimas</h2>
<div class="sig">
  <div><div class="line">Parengė<br>{escape(str(sig.get("prepared") or "Parengė"))}</div></div>
  <div><div class="line">Tvirtino · {action}<br>{escape(str(sig.get("approved") or "Inžinierius"))}
  <br>{escape(str(sig.get("title") or ""))}<br>{approved_at}
  {f"<br>{reason}" if reason else ""}</div></div>
</div>
<div class="foot">SHA-256 {sha}<span class="pg">Puslapis 1 / 2 · TS-PAGE-1 · {GLYPHS}</span></div>
</div>
<div class="sheet" data-page="2" data-testid="ts-page-2">
<header class="block">
  <div>
    <div class="org">Priedas A · GIS schema</div>
    <h1>PRIJUNGIMO TAŠKAS, ATRAMA / SPINTA IR LINIJA</h1>
    <div class="org">TP 12-608</div>
  </div>
  <div class="reg">
    Prie Nr. <b>{number}</b><br>
    Taškas: {kind} {element}<br>
    Linija: {feeder}
  </div>
</header>
<div class="mapbox">{svg}</div>
<div class="legend">
  <span><i style="background:#111"></i>TP 12-608</span>
  <span><i style="background:#fff;border-radius:50%"></i>Atrama</span>
  <span><i style="background:#fff"></i>Spinta</span>
  <span><i style="background:#e11d48"></i>Prijungimo taškas</span>
  <span><i style="background:#111;height:2px;margin-top:4px"></i>Įvadas (punktyras)</span>
  <span>Mastelis pažymėtas žemėlapyje</span>
</div>
<p class="note">Priedas A · GIS-ANNEX.</p>
<div class="foot">SHA-256 {sha}<span class="pg">Puslapis 2 / 2 · GIS-ANNEX · {GLYPHS}</span></div>
</div>
</body></html>"""
