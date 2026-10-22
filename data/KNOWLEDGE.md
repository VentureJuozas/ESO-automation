# ESO Prijungimo sąlygos – knowledge base for the hackathon

Ingested from `Prijungimo_salygos_hakatonui.pptx` ("Naudingos nuorodos ir duomenys" slide) on 2026-10-22.
Raw text of each source lives in `data/sources/`. This file is the distilled version to use when solving challenges.

## 0. Challenge statement (slide 5)

Preparing grid-connection technical conditions (prijungimo sąlygos) = data assessment + applying the network
development standard + selecting technical solutions + drafting the document. These steps repeat and are manual
engineer work.

**Challenge:** use AI / automation to reduce manual work when preparing technical conditions, while making sure the
technical solutions comply with the network development standard (tinklų plėtros standartas).

**Rules:** teams pick ONE stage of the process (e.g. initial data processing, drafting conditions, or checking them)
and demonstrate it working end to end. Do that one stage fully rather than covering the whole process.

## 1. Source status

| # | Source | Status | File |
|---|--------|--------|------|
| 1 | Prijungimo sąlygų nustatymas (eso.lt/…/3111) | INGESTED (text) | `sources/02_…` |
| 2 | Technologinės plėtros standartas (eso.lt/…/4216) | PARTIAL – page index only; standard PDFs/annexes not downloaded | `sources/03_…` |
| 3 | Įtampos kokybė (eso.lt/…/4033) | INGESTED (text); map data not retrieved | `sources/04_…` |
| 4 | Prijungimo sąlygų pavyzdžiai (SharePoint folder) | NOT INGESTED – requires login | – |
| 5 | Transformatorių pastočių laisvi pajėgumai (Power BI) | NOT INGESTED – requires login | – |
| 6 | 35–10 kV linijų apkrovos (Power BI) | NOT INGESTED – requires login | – |
| 7 | Rezervuoti pajėgumai – Galios rezervacijos vartojimo (Power BI) | NOT INGESTED – requires login | – |
| 8 | TR apkrova, http://172.28.117.18:5002/ | NOT INGESTED – private IP (hackathon/ESO network only) | – |
| – | Slides 1–3 (process, decision logic) | INGESTED | `sources/01_…` |
| – | ESO reikalavimai elektros tinklo techniniams ir darbo projektams (PDF; found via search, referenced by the standard) | INGESTED (supplementary) | `sources/05_…` |

## 2. Process (6 steps)

1. Paraiška – application + required documents received
2. Patikra – completeness check (documents submitted, fee paid, documents verified). Only then does the clock start.
3. Analizė – requested power and object purpose
4. Tinklas – capacity and quality of the network
5. Sprendinys – best technical solution
6. Sąlygos – conditions prepared and issued (requirements for design)

Queue rule: applications handled in order of the moment of *proper submission* (all docs + fee + operator check),
except where an application does not affect others. If info is missing, applicant is asked to clarify.

## 3. Decision logic (4 checks at each network level)

1. **Pajėgumas** – can the network deliver/receive the requested power?
2. **Kokybė** – will voltage and other LST EN 50160 parameters remain OK?
3. **Patikimumas** – will it worsen operating modes, backup supply, N-1?
4. **Ateitis** – compatible with expansion and future load/generation growth?

Evaluate bottom-up, from the possible connection point upward. Level order:
0,4 kV network → 0,4/10 kV substation (TR) → 10 kV network → 35/10 kV substation → 35 kV network →
110/35/10 or 110/10 kV substation → transmission network elements.

- Enough capacity → choose the nearest technically suitable network element.
- Not enough → evaluate higher voltage level, determine required reconstruction/expansion.
- Generation/storage: additionally evaluate reverse power flow and ability to push energy to same/higher level.
- Final principle: safe + reliable + technically feasible + economically justified.

Per level, evaluate: existing loads; network & transformer throughput; granted and reserved capacity;
technical condition; planned development projects.

**Output of the conditions:** connection point (vieta), connection voltage level, required reconstruction works,
required expansion works, metering location (apskaita), protection & automation solutions, other technical terms.

## 4. Criteria used to assess connection feasibility

Inputs: requested permitted usage power (LNG), requested permitted generation power (LGG), max capacity (Pmax),
storage power, current network loads, reserved and already granted capacity, possible connection point,
technical condition of existing network, planned/ongoing development or reconstruction projects, free throughput
for priorities in Electricity Law art. 39 par. 21.

Quality check (LST EN 50160): voltage levels, voltage fluctuations, load distribution, voltage rise during
generation, other PQ indicators.

Reliability check: network operating modes, backup supply options, N-1, impact of emergencies.

Also consider: territorial development plans, planned new connections, expected regional consumption/generation growth.

## 5. Deadlines for issuing conditions

Counted from the date of *proper* submission (all docs + fee paid + operator check). Matches the official ESO text
(re-confirmed by the user's verbatim paste, 2026-10-22).

| Pt. | Case | Deadline |
|-----|------|----------|
| 1 | Consumers (vartotojai), permitted usage power (LNG) ≤ 250 kW | 3 working days |
| 1 | Consumers, LNG > 250 kW | 5 working days |
| 1 | Consumers, needs changes in transmission network, or new/reconstructed 330/110/35 kV lines (OL/cable), 330/110/10, 110/35/10(6), 110/10(6), 35/10 kV substations or distribution points | 15 working days |
| 2 | Producing consumers with Pmax ≤ 100 kW; renewable generation ≤ 100 kW with LGG > 0 (not parks); active consumers ≤ 100 kW – no network-part project | 5 working days |
| 2 | same group – network-part project is being prepared | 10 working days |
| 2 | same group – objectively not possible within the above | 20 working days |
| 3 | Producing consumers with Pmax > 100 kW | 30 calendar days |
| 4 | Generation Pmax ≤ 100 kW + consumption installations / power increase together | point-2 terms, unless consumption term (pt. 1) is longer |
| 5 | Generation Pmax > 100 kW + consumption installations / power increase together | point-3 term (30 calendar days) |
| 6 | Network users with a protocol of intent (ketinimų protokolas) | ≤ 1 month from request |
| 7 | Other network users | 1 month, unless law sets otherwise |

Note: working days (darbo dienos) in pts. 1, 2; calendar days in pt. 3; months in pts. 6, 7.

Typical conditions (section 8) are published at "Tipinės sąlygos | ESO" on eso.lt (link not recovered).
Information on that page is reviewed within 30 working days of changes in law, processes or technical standards,
and at least once a year.

## 6. Required documents (depends on service)

Ownership documents; owner/co-owner consent; documents proving right to use the object; design/technical
documents; other documents required by law. Missing info → user is asked to clarify.
Principles apply to all users: consumers, producers, producing consumers, storage operators, others.

## 7. Legal framework

1. Elektros energetikos įstatymas
2. Atsinaujinančių išteklių energetikos įstatymas
3. Energetikos įstatymas (relocation/reconstruction cost principles)
4. Elektros energijos gamintojų ir vartotojų elektros įrenginių prijungimo prie elektros tinklų tvarkos aprašas
5. Elektros energijos įrenginių prijungimo prie elektros tinklų įkainių nustatymo metodika
6. Elektros įrenginių įrengimo bendrosios taisyklės
7. Pasinaudojimo elektros skirstomaisiais tinklais tvarkos aprašas
8. Pasinaudojimo elektros perdavimo tinklais tvarkos aprašas
9. Skaičiuojamųjų elektros apkrovų nustatymo metodika

## 8. Typical (pre-defined) conditions

Published for storage and producing consumers from 1 kW to 100 kW (inclusive) Pmax with 1 kW permitted generation
into the distribution network. (Example documents are in the SharePoint folder – not ingested.)

## 9. Voltage quality (LST EN 50160)

ESO publishes a map of power-quality parameters for 110/35/10, 110/10, 110/6 kV substations that have PQ analyzers
(on MV busbars). Mitigation device types: UPS / storage with power electronics (battery or capacitor), flywheel
storage, generators, hybrid systems; also voltage regulators/stabilizers.

## 10. Standard facts found (technologinės plėtros standartas – partial, from search snippets)

The standard is split into annexes (priedai), e.g. "12 priedas. 0,4 kV elektros linijos". Snippets seen:

- New 0,4 kV KL: no longer than 600 m (exception: level-4 sparse areas for single consumers).
- "Single-radial" cable scheme for new consumers when no backup supply is required; must not exceed 80 kW.
- When ≥2 0,4 kV cable lines run in parallel and one is ≥ 500 m → build a ring with the other line.
- Cable runs up to 450 m laid without joints; at most 2 joint sleeves per 1 km.
- Trunk KL cross-sections 120/240 mm² Al; branch KL 35/70 mm²; trunk OL 70/120 (OKL), branch OL 25–70; service
  connections from 16 mm².
- Rebuilding single-phase OL / new KL and OKL lines → three-phase.
- Area "levels" I–IV drive whether to cable (kabeliavimas) or switch to OKL.

These are NOT authoritative – obtain the actual annex PDFs before relying on them for rule checks.

## 11. Useful reference lists (from the Techniniai reikalavimai page)

Page lists ESO typical-project albums (0,4–10 kV), typical scheme DWG templates (updated 2026-10-19),
equipment/material requirement lists (transformers, cells, cables, joints, protection etc.), and memos
(atmintinės). Relevant to checking a solution against standards. Contact: technologijos@eso.lt;
materials: medziagos.irenginiai@eso.lt. Full index in `sources/03_…`.

## 12. Open gaps to fill (need user/organizer access)

1. SharePoint "Techninės sąlygos" examples folder – gives the target format of the generated document.
2. Power BI reports (free TR capacity, 35–10 kV line loads, reserved capacities) – exports/CSV needed.
3. Internal TR load tool at 172.28.117.18:5002 – reachable only inside the hackathon/ESO network.
4. The actual standard annex PDFs (eso.lt blocks scripted access; needs manual download in the browser).

## 13. Team approach (from the planning chat, `ESO_TS_hackathon_chat.md`)

Scope = **level 1: breaker change in the customer's existing metering cabinet (KAS)**, shown as step 1 of an
"upgrade ladder": 2 fuse change, 3 new KAS / cut-in cable, 4 feeder reinforcement, 5 transformer swap, 6 new TP / 10 kV.
Flow: request (object/meter, new kW, 1F/3F) -> validate -> resolve chain (meter -> KAS -> cabinet/pole -> 0.4 kV
feeder -> TP) -> breaker from kW table (e.g. 3F 22 kW -> 40 A) -> upstream checks (cabinet fuse >= breaker, feeder load
vs rating, transformer loading vs 0.8 / 1.0, voltage >= 207 V) -> pass: draft TS Section 3 + cost; fail: escalate with
reason + suggested next level -> engineer approves/edits. Deterministic Python decides; LangGraph orchestrates; the LLM
only parses the request and phrases text. Every number carries a source tag (real / inferred / synthetic).
Historical TS cases are NOT used as a reference.

## 14. Reference output (TS 26-E-37934) – see `data/case_26-E-37934/`

| File | What it is |
|------|-----------|
| `ts_output_template.md` | Structure of the issued TS: header, application data, fixed §1–§2, engineering §3, GIS annex; placeholders + JSON model |
| `cost_estimate_26-E-37934.md` | Priced estimate from the expert calculator: items, quantities, totals (11,936.98 EUR excl. VAT, 14,443.75 incl.) |
| `network_context_Pg-452.md` | TP/transformer/customer context and measured load (9 kW peak) |
| `gis_annex_map.jpg` | The GIS map extract used as Annex 4 |
| `tr_Pg-452_load_tool_screenshot.png` | Output of the internal TR load tool |

Key takeaways for the generator:
- Only TS §3 (ESO actions) and two flags in §2 (2.9 generation, 2.13 first-time connection) need decisions; the rest is a
  fixed template filled from application data. Validity = issue date + 1 year.
- §3 is built from a closed set of action blocks (install KS/KAS with breaker X A; install KS at TP connected to
  transformer terminals with cable >= Y mm²; cable KS -> KS/KAS; short-circuit/selectivity calc), and each block maps to
  rate lines in the price workbook.
- Customer personal data is redacted in these files; keep it out of demos and prompts.
- Not parsed: `Pg-452.dwg`, `Pg-461.dwg` (CAD drawings of the stations).

## 15. Reference output #2 (TS 26-E-37536, breaker-in-KAS on overhead line) – see `data/case_26-E-37536/`

Closest example to the level-1 scope: new 11 kW 3F on overhead line L-300 at pole 300/1 (5 m from TP Rg-202, 63 kVA).
Whole engineering content of the TS = install KAS with 3F C 20 A breaker on the pole + 16 mm² cable to the line.
Files: `case_summary.md` (TS content, draft vs issued, correction e-mail, calculator inputs/results, template variants), `gis_annex_map.jpg`.

Key takeaways:
- The combined calculator (`Apjungta elektros tinklų skaičiuoklė`) has: line check (two coefficient sets, "nuo 2018" = new, "iki 2018" = old),
  transformer load check (T-1/T-2), SMART-load transformer check, and a kW -> breaker / current-transformer table.
- Line check = chain of segments (conductor, length, houses, kW) -> diversity (nesutapimo) coefficient by cumulative house count ->
  Psk, Imax, Isk per segment -> short-circuit current and voltage loss per point -> RESULTS (line length, permitted power, Psk, Isk,
  total voltage loss %, voltage before/after). For a connection at the head of the line the change is ~0.004 pp.
- Diversity coefficients, "nuo 2018" (n houses -> k): 25: 0.464, 14: 0.632, 13: 0.657, 12: 0.681, 5: 0.947, 4: 0.973, 3 or fewer: 1.
  Old set: 26: 0.306, 25: 0.311, 14: 0.377, 13: 0.385, 12: 0.394, 5: 0.717, 4: 0.859, <=3: 1. (Full tables are in hidden sheet `Kofai`, not yet extracted.)
- The TS has several template variants (§1 wording, §2 count and order); draft state has a "PROJEKTAS. SUTARTIS NEPATVIRTINTA" watermark and no issue date.
- Engineers can request a TS correction (e-mail notice) -> re-issue; model this as the edit/approval gate.

### Breaker table (sheet `Srovės transf. įvertinimas`): connection power -> automatic breaker
Values are the upper bound of the power range (60 kW -> 100 A, 61 kW -> 125 A).
| 3F power, kW (up to) | 5 | 7 | 9 | 11 | 14 | 18 | 22 | 28 | 35 | 45 | 60 | 61–97 | 98–152 | 153–195 | 196–243 | 244–304 | 305–365 | 366–487 | 488+ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Breaker, A | 10 | 13 | 16 | 20 | 25 | 32 | 40 | 50 | 63 | 80 | 100 | 125–160 | 200–250 | 300–320 | 400 | 500 | 600 | 800 | 1000 |
Raw rows (3F kW -> A / CT): 61->125/150:5, 76->125/150:5, 77->160/200:5, 97->160/200:5, 98->200/200:5, 121->200/200:5, 122->250/300:5,
152->250/300:5, 153->300/300:5, 182->300/300:5, 183->320/400:5, 195->320/400:5, 196->400/400:5, 243->400/400:5, 244->500/500:5,
304->500/500:5, 305->600/600:5, 365->600/600:5, 366->800/800:5, 487->800/800:5, 488->1000/1000:5, 600->1000/1000:5 (CT needed above 60 kW).
1F kW -> A: 1->6, 2->10, 3->16, 4->20, 5->25, 6->32, 7->40.

## 16. Working dataset: substation 12-608 – see `data/substation_12-608/README.md`

The real data for the demo substation (400 kW single transformer, 6 feeders, 221 accounting points, 14 days of 15-min load, per-meter load and
min voltage, 14 past TS cases). Peak 227.7 kW (57% of nominal; 80% limit = 320 kW). 9 of 14 historical TS are pure breaker changes; the
kW -> breaker table matches 13 of 14. Raw files are in `raw/` (git-ignored); `ts_history_redacted.csv` is committed. Data-quality flags
(one outage-like event on 2026-02-04, 0 V meters, L1-only voltage, missing line impedances/fuses) are listed in that README.

## 17. Demo scope – see `data/SCOPE.md`
New customer on substation 12-608; solution = connect to an existing cabinet (A), new KAS on a pole (B) or new KS/KAS cut into a cable line (C); four checks on 0.4 kV and the 0.4/10 kV station only. Transformer swap, new station and above are out of scope.
