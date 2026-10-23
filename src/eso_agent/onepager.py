"""Printable A4 leave-behind for the jury."""
from __future__ import annotations


def render_onepager_html() -> str:
    return """<!DOCTYPE html>
<html lang="lt" translate="no">
<head>
<meta charset="utf-8"/>
<title>Prijungimo sąlygos · vieno lapo santrauka</title>
<style>
  @page { size: A4; margin: 14mm; }
  body { font-family: Georgia, serif; color: #111; margin: 0; padding: 18px 22px; }
  h1 { font-size: 20px; margin: 0 0 4px; }
  h2 { font-size: 13px; letter-spacing: .06em; text-transform: uppercase; margin: 16px 0 6px; color: #444; }
  p, li { font-size: 12px; line-height: 1.45; }
  .banner { background: #111; color: #fff; padding: 8px 10px; font-size: 11px; margin-bottom: 12px; }
  .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px 18px; }
  .box { border: 1px solid #ddd; padding: 8px 10px; }
  .tag { font-size: 10px; background: #eee; padding: 1px 6px; }
  table { width: 100%; border-collapse: collapse; font-size: 11px; }
  td, th { border-bottom: 1px solid #eee; text-align: left; padding: 3px 4px; }
  footer { margin-top: 14px; font-size: 10px; color: #666; }
</style>
</head>
<body>
<div class="banner">Demonstracija · neoficialus ESO dokumentas · asmens duomenų nėra</div>
<h1>0,4 kV prijungimo sąlygos per minutes, ne dienas</h1>
<p>Namų ūkiui prie TP <b>12-608</b> inžinierius dabar renka GIS, pajėgumą ir šabloną ranka.
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
<footer>12-608 · 400 kVA · viršūnė 227,7 kW · 80 % = 320 kW. make demo · docs/DEMO_SCRIPT.md</footer>
</body></html>
"""
