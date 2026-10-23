"""Printable A4 TS HTML. Redacted / synthetic customer fields only — no real PII."""
from __future__ import annotations

from html import escape
from typing import Any

from eso_agent.fonts import font_face_css
from eso_agent.ts_text import issue_dates, ownership_boundary, section3_blocks

REDACTED_CUSTOMER = "Buitinis vartotojas (redaguota)"
REDACTED_CODE = "ASMENS KODAS / EIC REDAGUOTAS"
REDACTED_ADDRESS = "Adresas redaguotas · objektas prie TP 12-608 (koordinatės, be gatvės)"


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
    kw = parsed.get("kw")
    phases = parsed.get("phases")
    obj = parsed.get("object_name") or "Naujas buitinis objektas"
    section2 = [
        "2.1. Įrengti objekto vidaus elektros tinklą iki nuosavybės ribos.",
        "2.2. Užtikrinti laisvą prieigą prie komercinės apskaitos spintos.",
        "2.3. Atlikti reikalingus žemės darbus savo sklype pagal ESO nurodymus.",
        "2.9. Generacija / kaupimas: neprašoma.",
        "2.13. Pirmas prijungimas: taip.",
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
        "kw": kw,
        "phases": phases,
        "phase_label": "Trifazis" if phases == 3 else "Vienfazis",
        "tp": "12-608",
        "feeder": feeder,
        "element": element,
        "solution": sol.get("id"),
        "breaker": br.get("label"),
        "section1": ownership_boundary(sol.get("id") or "B"),
        "section2": section2,
        "section3": section3,
        "blocks": section3_blocks(sol, br, loc) if not section3 else [],
        "coords": {"lat": parsed.get("lat"), "lon": parsed.get("lon"), "source": "synthetic"},
        "signature": {
            "prepared": "Demonstracinis agentas (deterministiniai Python įrankiai)",
            "approved": "Inžinierius (žmogaus vartai)",
            "title": "Prijungimo sąlygų inžinierius",
        },
        "disclaimer": "Demonstracinis dokumentas. Neoficialus ESO blankas. Asmens duomenys redaguoti.",
        "run_id": run_id,
        "issued": issued,
    }


def render_ts_html(snap: dict[str, Any]) -> str:
    issued = snap.get("issued") or {}
    draft = snap.get("draft") or {}
    parsed = snap.get("parsed") or {}
    doc = issued.get("document") or draft.get("document") or {}
    if issued and not doc.get("issued"):
        doc = {
            **doc,
            "ts_number": issued.get("ts_number") or doc.get("ts_number"),
            "issue_date": issued.get("issue_date") or doc.get("issue_date"),
            "valid_until": issued.get("valid_until") or doc.get("valid_until"),
            "watermark": None,
            "section3": issued.get("section3") or doc.get("section3"),
            "issued": True,
        }
    number = escape(str(doc.get("ts_number") or "PROJEKTAS"))
    issue = escape(str(doc.get("issue_date") or "—"))
    valid = escape(str(doc.get("valid_until") or "—"))
    watermark = doc.get("watermark")
    s3 = escape(doc.get("section3") or draft.get("section3") or "").replace("\n", "<br>")
    s1 = escape(doc.get("section1") or draft.get("ownership_boundary") or "")
    kw = doc.get("kw") or parsed.get("kw")
    phases = doc.get("phases") or parsed.get("phases")
    phase = escape(str(doc.get("phase_label") or ("Trifazis" if phases == 3 else "Vienfazis")))
    obj = escape(str(doc.get("object_name") or parsed.get("object_name") or "Naujas buitinis objektas"))
    customer = escape(str(doc.get("customer") or REDACTED_CUSTOMER))
    code = escape(str(doc.get("customer_code") or REDACTED_CODE))
    addr = escape(str(doc.get("address") or REDACTED_ADDRESS))
    feeder = escape(str(doc.get("feeder") or "—"))
    element = escape(str(doc.get("element") or "—"))
    br = escape(str(doc.get("breaker") or "—"))
    sol = escape(str(doc.get("solution") or "—"))
    section2 = doc.get("section2") or []
    s2 = "".join(f"<p>{escape(p)}</p>" for p in section2)
    sig = doc.get("signature") or {}
    wm = f'<div class="wm">{escape(watermark)}</div>' if watermark else ""
    return f"""<!DOCTYPE html>
<html lang="lt" translate="no">
<head>
<meta charset="utf-8">
<title>Prijungimo sąlygos {number}</title>
<style>
  {font_face_css()}
  @page {{ size: A4; margin: 16mm 16mm 18mm 16mm; }}
  html, body {{ background: #ececec; }}
  body {{ font-family: DejaVu, "Times New Roman", Times, Georgia, serif; color: #111; margin: 0; }}
  .sheet {{
    width: 210mm; min-height: 297mm; margin: 16px auto; background: #fff;
    padding: 18mm 16mm 16mm; box-sizing: border-box; position: relative;
  }}
  header {{ display: flex; justify-content: space-between; gap: 16px;
    border-bottom: 2.5px solid #111; padding-bottom: 10px; margin-bottom: 14px; }}
  .k {{ font-size: 10px; letter-spacing: .12em; text-transform: uppercase; color: #444; }}
  h1 {{ font-size: 16px; margin: 4px 0 0; }}
  h2 {{ font-size: 13px; margin: 16px 0 6px; border-bottom: 1px solid #bbb; padding-bottom: 3px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 6px 0 12px; font-size: 13px; }}
  td {{ padding: 3px 0; vertical-align: top; }}
  td:first-child {{ color: #444; width: 42%; }}
  .wm {{ position: absolute; inset: 34% 8%; font-size: 26px; color: rgba(180,0,0,.16); font-weight: 700;
        transform: rotate(-18deg); pointer-events: none; text-align: center; }}
  .note {{ font-size: 10px; color: #555; margin-top: 18px; }}
  .sig {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-top: 28px; font-size: 12px; }}
  .line {{ border-top: 1px solid #111; margin-top: 28px; padding-top: 4px; }}
  .noprint {{ margin: 12px auto; width: 210mm; }}
  .noprint button {{ border: 0; background: #1c1c1f; color: #fff; padding: 8px 14px; border-radius: 8px; font-weight: 600; }}
  @media print {{
    html, body {{ background: #fff; }}
    .sheet {{ margin: 0; box-shadow: none; width: auto; min-height: auto; padding: 0; }}
    .noprint {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="noprint"><button onclick="window.print()">Spausdinti / įrašyti PDF (A4)</button></div>
<div class="sheet">
{wm}
<header>
  <div>
    <div class="k">AB Energijos skirstymo operatorius · demonstracija</div>
    <h1>ELEKTROS VARTOTOJO PRIJUNGIMO SĄLYGOS</h1>
  </div>
  <div style="text-align:right; font-size:13px">
    Nr. <b>{number}</b><br>Parengta: {issue}<br>Galioja iki: {valid}
  </div>
</header>
<h2>Kliento prijungiamo objekto duomenys</h2>
<table>
<tr><td>Klientas</td><td>{customer}</td></tr>
<tr><td>Identifikatorius</td><td>{code}</td></tr>
<tr><td>Objekto pavadinimas</td><td>{obj}</td></tr>
<tr><td>Objekto vieta</td><td>{addr}</td></tr>
<tr><td>Nauja leistina naudoti galia</td><td>{kw} kW · {phase}</td></tr>
<tr><td>Transformatorinė</td><td>12-608</td></tr>
<tr><td>Linija / elementas</td><td>{feeder} · {element}</td></tr>
<tr><td>Sprendinys / jungiklis</td><td>{sol} · {br}</td></tr>
</table>
<h2>1. Nuosavybės riba</h2>
<p>{s1}</p>
<h2>2. Kliento veiksmai</h2>
{s2}
<h2>3. ESO veiksmai</h2>
<p>{s3}</p>
<h2>4. Galiojimas ir parašas</h2>
<p>Sąlygos galioja vienerius metus nuo parengimo datos ({issue} → {valid}).</p>
<div class="sig">
  <div><div class="line">{escape(str(sig.get("prepared") or "Parengė"))}</div></div>
  <div><div class="line">{escape(str(sig.get("approved") or "Tvirtino"))}<br>{escape(str(sig.get("title") or ""))}</div></div>
</div>
<p class="note">{escape(str(doc.get("disclaimer") or "Demonstracinis dokumentas. Neoficialus ESO blankas. Asmens duomenys redaguoti."))}</p>
</div>
</body></html>"""
