# Reference TS output: Nr. 26-E-37934 (customer data redacted)

Source: `Prijungimo sąlygos_2026-10-19_12.22.13.830.pdf` (3 pages, Kauno r. sav., 2026-10-19).
Customer name, contact details and address are intentionally NOT stored here. Use `{{placeholders}}`.
Companion files in this folder: `gis_annex_map.jpg` (Annex 4), `tr_Pg-452_load_tool_screenshot.png`
(output of the internal "TR apkrova" tool), `cost_estimate_26-E-37934.md` (priced estimate).

## Document skeleton

Every page has the same header (ESO phone numbers: customer service +370 660 01852, gas emergency 1804, electricity
fault line 1852, www.eso.lt/savitarna/) and footer (AB „Energijos skirstymo operatorius", Laisvės pr. 10, 04215
Vilnius, el. p. info@eso.lt, code 304151376, VAT LT100009860612, registry VĮ Registrų centras). **Fixed.**

```
Nr. {{ts_number}}                         e.g. 26-E-37934
Parengta: {{issue_date}}                  2026-10-19
Galioja iki: {{valid_until}}              issue date + 1 year -> 2027-10-19
ELEKTROS VARTOTOJO PRIJUNGIMO SĄLYGOS

KLIENTO PRIJUNGIAMO OBJEKTO DUOMENYS:
  Klientas:                      {{customer_name}}
  Kliento kontaktiniai duomenys: {{customer_contact}}
  Objekto pavadinimas:           {{object_name}}          e.g. "Grūdų sandėlis"
  Objekto adresas:               {{object_address}}
  Investicinio projekto Nr.:     {{investment_project_no}} e.g. E1N2619328O

KLIENTO PARAIŠKOS NR. DUOMENYS:
  Leistina naudoti galia | Atvado tipas (vienfazis, trifazis)
  Nauja leistina naudoti galia (kW): {{new_kw}}    {{phase_type}}     22  Trifazis
  Iš viso leistina naudoti galia (kW): {{total_kw}} {{phase_type}}    22  Trifazis
  Numatomas apskaitų skaičius: {{meter_count}}                         1
  Komercinės apskaitos spintos spalva: {{cabinet_colour}}              Standartinė spalva
```

### 1. Ownership boundary (fixed text)
"Nuosavybės ir turto eksploatavimo riba nustatoma: ant kabelio (įvado), pakloto iš komercinės apskaitos spintoje su
tranzitine dalimi (KS/KAS) į savininko objekto vidaus elektros tinklą, prijungimo gnybtų."

### 2. Customer actions – 13 items, almost entirely fixed
| # | Content | Variable? |
|---|---------|-----------|
| 2.1 | Read connection contract + the (new or changed) metering location in its annex, pay the fee via www.eso.lt/savitarna → "Paraiškos" | fixed |
| 2.2 | Choose a qualified contractor/electrician for the new service line (or check of the existing) up to the ownership boundary; contractor submits "Elektros energetikos įrenginių techninės būklės patikrinimo aktas" at www.eso.lt/paraiskos/rangovu-aktu-pateikimas/1 | fixed |
| 2.3 | Supply quality at the connection point follows LST EN 50160 (link to voltage fluctuation causes page) | fixed |
| 2.4 | If needs change: submit a new application; new conditions replace the previous ones | fixed |
| 2.5 | Design/approval procedures by the customer when connecting to ESO networks or relocating/reconstructing ESO assets in customer structures (per connection procedure + construction regulation) | fixed |
| 2.6 | Inform ESO (+370 660 01852) before any work that requires removing the meter seal | fixed |
| 2.7 | Backup energy source: follow the ESO recommendations page | fixed |
| 2.8 | After contractor's act is submitted, ESO installs the meter within 2–4 working days | fixed |
| 2.9 | Granting/increasing usage power is not tied to connecting generation; these conditions do not guarantee connection of a power plant | **flag:** text changes if the application includes generation |
| 2.10 | ESO will notify promptly of possible delays/new date if related projects delay the connection | fixed |
| 2.11 | Link to ESO's grid investment projects map | fixed |
| 2.12 | Contact link for questions on technical content | fixed |
| 2.13 | First-time connected customers: if no supply contract within 30 working days of service completion, monthly invoices for the power component of transmission for the whole newly connected permitted power | **flag:** only for first-time connections |

### 3. ESO actions – the only engineering section (this is what the agent must generate)
Case 26-E-37934 (22 kW, 3-phase, new connection at a transformer station Pg-452):

- **3.1** "Laisvai klientui ir Bendrovei prieinamoje vietoje įrengti komercinės apskaitos spintą su tranzitine dalimi
  (toliau - KS/KAS) su trifaziu „C" charakteristikos **{{breaker_A}} A** automatiniu jungikliu ir elektros energijos
  apskaitos skaitikliu."  → here 40 A.
- **3.2** "Laisvai Bendrovei prieinamoje vietoje, šalia **{{tp_id}}** transformatorinės, įrengti kabelinę spintą (toliau - KS).
  KS prijungti nuo transformatorinės {{tp_id}} transformatoriaus **{{trafo_id}}** 0,4kV gnybtų. Prijungimui įrengti ne
  mažesnio kaip **{{cable_mm2}} mm²** skerspjūvio kabelių liniją."  → Pg-452, T-2, 150 mm².
- **3.3** "Nuo KS iki KS/KAS įrengti žemos įtampos ne mažesnio kaip **{{cable_mm2}} mm2** skerspjūvio kabelių liniją."
- **3.4** "Elektros grandinėje atlikti trumpųjų jungimų skaičiavimus ir parinkti apsaugas pagal selektyvumą." (standard closing item)

For the simplest case (breaker change in an existing cabinet) only item 3.1-style wording is needed, replacing
"įrengti" by a change of the existing breaker (see `data/KNOWLEDGE.md` §13).

### 4. Annex "PRIEDAS PRIE PRIJUNGIMO SĄLYGŲ NR. {{ts_number}}"
Page 3 = GIS map extract titled "Paraiškos Nr.: {{ts_number}}" with the nearest TPs (Pg-452, Pg-461, Pg-462, OLS Pg-405),
pole labels (e.g. 401/26, 208/46, 404/13, 214/5), 0.4 kV lines (dark red) and 10 kV (orange),
and a green plug icon with legend "Numatoma preliminari apskaitos įrengimo vieta". See `gis_annex_map.jpg`.

## Output data model (derived)

```json
{
  "ts_number": "26-E-37934", "issue_date": "2026-10-19", "valid_until": "2027-10-19",
  "customer": {"name": "{{redacted}}", "contact": "{{redacted}}"},
  "object": {"name": "Grūdų sandėlis", "address": "{{redacted}}", "investment_project_no": "E1N2619328O"},
  "application": {"new_kw": 22, "total_kw": 22, "phase": "3F", "meters": 1, "cabinet_colour": "standard",
                  "includes_generation": false, "first_time_connection": true},
  "eso_actions": [
    {"id": "3.1", "type": "install_KS_KAS", "breaker": "3F C 40 A", "meter": true},
    {"id": "3.2", "type": "install_KS_at_TP", "tp": "Pg-452", "transformer": "T-2", "cable_min_mm2": 150},
    {"id": "3.3", "type": "lay_cable_KS_to_KSKAS", "cable_min_mm2": 150},
    {"id": "3.4", "type": "short_circuit_and_selectivity_calc"}
  ],
  "annex": {"map": "gis_annex_map.jpg"}
}
```
