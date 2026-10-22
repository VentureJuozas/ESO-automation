"""Printable TS HTML (demo layout, redacted customer, not an official ESO form)."""
from __future__ import annotations

from html import escape
from typing import Any


def render_ts_html(snap: dict[str, Any]) -> str:
    issued = snap.get("issued") or {}
    draft = snap.get("draft") or {}
    parsed = snap.get("parsed") or {}
    doc = (draft.get("document") or {}) if not issued else {
        **(draft.get("document") or {}),
        "ts_number": issued.get("ts_number"),
        "issue_date": issued.get("issue_date"),
        "valid_until": issued.get("valid_until"),
        "watermark": None,
        "section3": issued.get("section3"),
    }
    number = escape(str(doc.get("ts_number") or "PROJEKTAS"))
    issue = escape(str(doc.get("issue_date") or "—"))
    valid = escape(str(doc.get("valid_until") or "—"))
    watermark = doc.get("watermark")
    s3 = escape(doc.get("section3") or draft.get("section3") or "").replace("\n", "<br>")
    s1 = escape(doc.get("section1") or draft.get("ownership_boundary") or "")
    kw = parsed.get("kw") or doc.get("kw")
    phases = parsed.get("phases") or doc.get("phases")
    phase = "Trifazis" if phases == 3 else "Vienfazis"
    obj = escape(str(doc.get("object_name") or "Naujas buitinis objektas"))
    wm = (
        f'<div class="wm">{escape(watermark)}</div>'
        if watermark
        else ""
    )
    return f"""<!DOCTYPE html>
<html lang="lt">
<head>
<meta charset="utf-8">
<title>Prijungimo sąlygos {number}</title>
<style>
  body {{ font-family: Georgia, "Times New Roman", serif; color: #111; margin: 32px auto; max-width: 720px; line-height: 1.45; }}
  header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #111; padding-bottom: 8px; margin-bottom: 18px; }}
  .k {{ font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: #555; }}
  h1 {{ font-size: 18px; margin: 0 0 12px; }}
  table {{ width: 100%; border-collapse: collapse; margin: 8px 0 16px; }}
  td {{ padding: 4px 0; vertical-align: top; }}
  td:first-child {{ color: #555; width: 46%; }}
  h2 {{ font-size: 14px; margin: 18px 0 8px; }}
  .wm {{ position: fixed; inset: 30% 10%; font-size: 28px; color: rgba(180,0,0,.18); font-weight: 700;
        transform: rotate(-18deg); pointer-events: none; text-align: center; }}
  .note {{ font-size: 11px; color: #666; margin-top: 24px; }}
  @media print {{ .noprint {{ display: none; }} }}
</style>
</head>
<body>
{wm}
<header>
  <div><div class="k">AB Energijos skirstymo operatorius · demonstracija</div>
  <strong>ELEKTROS VARTOTOJO PRIJUNGIMO SĄLYGOS</strong></div>
  <div style="text-align:right">Nr. {number}<br>Parengta: {issue}<br>Galioja iki: {valid}</div>
</header>
<p class="noprint"><button onclick="window.print()">Spausdinti / PDF</button></p>
<h1>Kliento prijungiamo objekto duomenys</h1>
<table>
<tr><td>Klientas</td><td>{{{{redaguota}}}}</td></tr>
<tr><td>Objekto pavadinimas</td><td>{obj}</td></tr>
<tr><td>Objekto adresas</td><td>{{{{redaguota}}}}</td></tr>
<tr><td>Nauja leistina naudoti galia</td><td>{kw} kW · {phase}</td></tr>
<tr><td>Transformatorinė</td><td>12-608</td></tr>
</table>
<h2>1. Nuosavybės riba</h2>
<p>{s1}</p>
<h2>2. Kliento veiksmai</h2>
<p>Tipiniai punktai 2.1–2.13 (fiksuotas šablonas). 2.9 generacija: ne. 2.13 pirmas prijungimas: taip.</p>
<h2>3. ESO veiksmai</h2>
<p>{s3}</p>
<p class="note">Demonstracinis dokumentas. Neoficialus ESO blankas. Asmens duomenys redaguoti.
Kainos — orientyras iš bylos 26-E-37934.</p>
</body></html>"""
