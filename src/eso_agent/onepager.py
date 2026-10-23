"""Leave-behind: full-screen layout plus a separate A4 print stylesheet."""
from __future__ import annotations

from eso_agent.fonts import GLYPHS, font_face_css


def render_onepager_html() -> str:
    return f"""<!DOCTYPE html>
<html lang="lt" translate="no">
<head>
<meta charset="utf-8"/>
<title>Prijungimo sąlygos · vieno lapo santrauka</title>
<style>
  {font_face_css()}
  * {{ box-sizing: border-box; }}
  html, body {{ min-height: 100%; }}
  body {{
    font-family: DejaVu, Georgia, serif; color: #111; margin: 0;
    background: #f3f3f5;
  }}
  .screen {{
    max-width: 1100px; margin: 0 auto; padding: 28px 28px 48px;
  }}
  .banner {{ background: #111; color: #fff; padding: 10px 14px; font-size: 12px; border-radius: 10px; }}
  h1 {{ font-size: 32px; line-height: 1.2; margin: 16px 0 10px; font-weight: 700; }}
  .lead {{ font-size: 16px; line-height: 1.5; max-width: 70ch; }}
  .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px; }}
  .box {{
    background: #fff; border-radius: 14px; padding: 18px 20px;
    box-shadow: 0 10px 30px rgba(24,24,27,.06); min-height: 210px;
  }}
  h2 {{ font-size: 13px; letter-spacing: .08em; text-transform: uppercase; margin: 0 0 10px; color: #555; }}
  p, li {{ font-size: 14px; line-height: 1.5; }}
  .tag {{ font-size: 11px; background: #eee; padding: 2px 7px; border-radius: 99px; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
  td, th {{ border-bottom: 1px solid #eee; text-align: left; padding: 5px 4px; }}
  footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
  .noprint {{ margin: 14px 0; display: flex; gap: 8px; }}
  .noprint a, .noprint button {{
    border: 0; background: #1c1c1f; color: #fff; padding: 8px 14px;
    border-radius: 8px; font: inherit; text-decoration: none;
  }}
  @media print {{
    @page {{ size: A4; margin: 14mm; }}
    html, body {{ background: #fff; min-height: 0; }}
    .screen {{ max-width: none; margin: 0; padding: 0; }}
    .banner {{ border-radius: 0; }}
    h1 {{ font-size: 20px; margin: 10px 0 6px; }}
    .lead {{ font-size: 12px; }}
    .grid {{ gap: 10px 14px; margin-top: 10px; }}
    .box {{ box-shadow: none; border: 1px solid #ddd; border-radius: 0; min-height: 0; padding: 8px 10px; }}
    p, li {{ font-size: 12px; }}
    .noprint {{ display: none; }}
    footer {{ font-size: 10px; }}
  }}
</style>
</head>
<body>
<div class="screen">
<div class="banner">Demonstracija · neoficialus ESO dokumentas · asmens duomenų nėra · {GLYPHS}</div>
<div class="noprint">
  <button onclick="window.print()">Spausdinti A4</button>
  <a href="/api/onepager.pdf">Atsisiųsti PDF</a>
</div>
<h1>0,4 kV prijungimo sąlygos per minutes, ne dienas</h1>
<p class="lead">Namų ūkiui prie TP <b>12-608</b> inžinierius dabar renka GIS, pajėgumą ir šabloną ranka.
Agentas paruošia tą patį paketą: A/B/C, jungiklį, keturias patikras, §3 ir sąmatą.
Sąlygas visada pasirašo žmogus.</p>
<div class="grid">
  <div class="box">
    <h2>Kaip veikia</h2>
    <ol>
      <li>Klientų maketas pateikia paraišką (redaguota).</li>
      <li>LangGraph eina n8n drobe: parse → locate → A/B/C → patikros.</li>
      <li>Python priima sprendimus. LLM tik skaito tekstą.</li>
      <li>Trūksta duomenų — laiško peržiūra, eiga laukia.</li>
      <li>Inžinierius tvirtina. Auditas + SHA-256.</li>
    </ol>
  </div>
  <div class="box">
    <h2>Laikas <span class="tag">prielaida</span></h2>
    <p>Rankinis stalas: 2–4 val. paraiškai. Replay: sekundės.
    40 bylų / mėn. — <b>ne ESO statistika</b>.</p>
    <h2>Back-test</h2>
    <table>
      <tr><th></th><th>Visų 16</th><th>In-scope</th><th>Įrankio klaidų</th></tr>
      <tr><td>R3</td><td>51 %</td><td>—</td><td>paslėpta</td></tr>
      <tr><td>R4+</td><td>84 %</td><td>95 %</td><td>0</td></tr>
    </table>
    <p>Taksonomija: (a) kita TP · (b) trūksta įvesties · (c) įrankis · (d) inžinieriaus sprendimas.
    What-if užpildymas: 6 / 7 trūkstamų bylų.</p>
  </div>
  <div class="box">
    <h2>Sauga</h2>
    <ul>
      <li>Žmogaus vartai: be patvirtinimo nėra TS.</li>
      <li>Override ≥ 8 simboliai, rašoma į auditą.</li>
      <li>Provenance: real / rule / inferred / synthetic.</li>
      <li>SHA-256 kanoninis paketas. SQLite persikrauna.</li>
      <li>Be vardų, adresų, skaitiklių.</li>
    </ul>
  </div>
  <div class="box">
    <h2>Toliau — adapteriai</h2>
    <ul>
      <li>GIS / topologija → ESO GIS</li>
      <li>Pajėgumas → Power BI / SCADA</li>
      <li>CRM → savitarna</li>
      <li>Kainos → įkainių metodika</li>
      <li>TS registras → SharePoint</li>
    </ul>
    <p>Šiandien visos penkios — <b>mock</b>. Stubai aprašyti, neprijungti.</p>
  </div>
</div>
<footer>12-608 · 400 kVA · viršūnė 227,7 kW · 80 % = 320 kW. make demo · docs/DEMO_SCRIPT.md · {GLYPHS}</footer>
</div>
</body></html>
"""
