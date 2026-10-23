"""Reinforcement brief when the 0.4 kV / 400 kVA check fails (rung 5)."""
from __future__ import annotations

from html import escape
from typing import Any

from eso_agent.fonts import GLYPHS, font_face_css
from eso_agent.pdfutil import render_brief_pdf


def build_reinforcement_brief(
    numbers: dict[str, Any],
    *,
    pending_kw: float = 0.0,
    pending_cases: int = 0,
) -> dict[str, Any]:
    after = numbers.get("after_kw")
    limit = numbers.get("limit_80_kw") or 320
    over = numbers.get("over_kw")
    if over is None and after is not None:
        over = round(float(after) - float(limit), 1)
    options = [
        {
            "id": "tr_630",
            "rung": 5,
            "title": "Transformatoriaus keitimas 400 → 630 kVA",
            "why": "80 % riba 320 kW viršyta. 630 kVA (~504 kW @ 80 %) grąžina atsargą šiai ir gretimoms paraiškoms.",
            "cost_lo": 18000,
            "cost_hi": 32000,
            "currency": "EUR",
            "tag": "inferred",
            "owner": "Tinklų plėtros inžinierius · TP 12-608",
            "next_step": "Parengti 5 pakopos užduotį: TR užsakymas, 0,4 kV įvado 630 A ir 10 kV 50 A saugikliai.",
            "recommended": True,
        },
        {
            "id": "feeder_split",
            "rung": 4,
            "title": "Linijos skaidymas / stiprinimas",
            "why": "Jei perkrova lokalizuota vienoje 0,4 kV šakoje, skaidymas mažina Isk, bet nepadidina TR 80 % ribos.",
            "cost_lo": 12000,
            "cost_hi": 40000,
            "currency": "EUR",
            "tag": "inferred",
            "owner": "0,4 kV tinklo inžinierius",
            "next_step": "Patikrinti L linijos Isk ir saugiklį. Jei TR vis tiek virš 80 % — šis kelias nepakanka.",
            "recommended": False,
        },
        {
            "id": "new_tp",
            "rung": 6,
            "title": "Nauja TP / 10 kV darbai",
            "why": "Už šio demo SCOPE. Reikia, jei 630 kVA vis tiek netilptų arba teritorija auga.",
            "cost_lo": 80000,
            "cost_hi": 180000,
            "currency": "EUR",
            "tag": "inferred",
            "owner": "Technologinė plėtra",
            "next_step": "Nepradėti šiame demo. Perduoti plėtros planui.",
            "recommended": False,
        },
    ]
    return {
        "title": "Stiprinimo paketas · 5 pakopa",
        "numbers": {**numbers, "over_kw": over},
        "options": options,
        "recommended": "tr_630",
        "pending_impact": {
            "pending_kw": pending_kw,
            "pending_cases": pending_cases,
            "note": (
                f"Dar {pending_cases} eilės paraiškų dalijasi tą patį 400 kVA. "
                f"Rezervuota papildomai {pending_kw:.0f} kW (sintetinis / eilės suma)."
            ),
            "source": "inferred",
        },
        "disclaimer": "Kainų rėžiai — inžinerinė prielaida, ne ESO įkainis ir ne 26-E-37934 eilutė.",
        "safety": "Sąlygos neišduodamos be override su priežastimi. Šis paketas — kitas procesas, ne „išduoti vis tiek“.",
    }


def render_brief_html(snap: dict[str, Any]) -> str:
    esc = (snap.get("escalate") or {})
    brief = esc.get("brief") or {}
    nums = brief.get("numbers") or esc.get("numbers") or {}
    options = brief.get("options") or []
    impact = brief.get("pending_impact") or {}
    rows = "".join(
        f"<tr class='{'rec' if o.get('recommended') else ''}'>"
        f"<td>{escape(str(o.get('rung')))}</td>"
        f"<td><b>{escape(str(o.get('title')))}</b><br><small>{escape(str(o.get('why')))}</small></td>"
        f"<td>{o.get('cost_lo')}–{o.get('cost_hi')} € <span class='tag'>{escape(str(o.get('tag')))}</span></td>"
        f"<td>{escape(str(o.get('owner')))}</td>"
        f"<td>{escape(str(o.get('next_step')))}</td>"
        f"</tr>"
        for o in options
    )
    return f"""<!DOCTYPE html>
<html lang="lt" translate="no"><head><meta charset="utf-8"><title>Stiprinimo paketas</title>
<style>
  {font_face_css()}
  @page {{ size: A4; margin: 16mm; }}
  body {{ font-family: DejaVu, Inter, "Segoe UI", sans-serif; color: #111; margin: 24px; }}
  h1 {{ font-size: 18px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  th, td {{ border-bottom: 1px solid #ddd; padding: 8px 6px; vertical-align: top; text-align: left; }}
  tr.rec {{ background: #f1fbf6; }}
  .tag {{ font-size: 11px; color: #9a3412; }}
  .note {{ color: #555; font-size: 12px; margin-top: 16px; }}
  .noprint button, .noprint a {{ border: 0; background: #1c1c1f; color: #fff; padding: 8px 14px; border-radius: 8px; text-decoration: none; }}
  @media print {{ .noprint {{ display: none; }} }}
</style></head><body>
<div class="noprint"><button onclick="window.print()">Spausdinti</button>
<a href="/api/runs/{escape(str(snap.get('id') or ''))}/brief.pdf">Atsisiųsti PDF</a></div>
<h1>Stiprinimo paketas · TP 12-608</h1>
<p class="note">Lietuviškos raidės: {GLYPHS}</p>
<p>Po prijungimo <b>{nums.get('after_kw')}</b> kW vs 80 % riba <b>{nums.get('limit_80_kw')}</b> kW
(viršijimas {nums.get('over_kw')} kW). Sąlygos neišduotos.</p>
<table>
<tr><th>Pakopa</th><th>Variantas</th><th>Kaina</th><th>Savininkas</th><th>Kitas žingsnis</th></tr>
{rows}
</table>
<p>{escape(str(impact.get('note') or ''))}</p>
<p class="note">{escape(str(brief.get('disclaimer') or ''))} {escape(str(brief.get('safety') or ''))}</p>
</body></html>"""


def brief_pdf_bytes(snap: dict[str, Any]) -> bytes:
    esc = (snap.get("escalate") or {})
    brief = esc.get("brief") or {}
    nums = brief.get("numbers") or esc.get("numbers") or {}
    lines = [
        f"Po prijungimo {nums.get('after_kw')} kW vs 80 % riba {nums.get('limit_80_kw')} kW (viršijimas {nums.get('over_kw')} kW).",
        "Sąlygos neišduotos.",
    ]
    for o in brief.get("options") or []:
        lines.append(f"Pakopa {o.get('rung')}: {o.get('title')} — {o.get('why')}")
    lines.append(str((brief.get("pending_impact") or {}).get("note") or ""))
    lines.append(str(brief.get("disclaimer") or ""))
    lines.append(str(brief.get("safety") or ""))
    return render_brief_pdf("Stiprinimo paketas · TP 12-608", lines)
