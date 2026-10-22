# Network context for TS 26-E-37934 (TP Pg-452, transformer T-2)

Sources: `Pg-452 Vartotojai.xlsx` (customer list from TEVIS, redacted below), screenshot of the internal TR load tool,
GIS annex map (`gis_annex_map.jpg`). The folder also had `Pg-452.dwg` and `Pg-461.dwg` (not parsed).

## Customers on Pg-452 (TEVIS export)
One object (obj. no. 71214647, "GAMYBINIAI PASTATAI", commercial, 0.4 kV, 3-phase), rows duplicated for two
metering points. Name, contact person and phone are redacted on purpose.

| Field | Value |
|-------|-------|
| Division | Kauno tinklas |
| 35–110 kV TP | Vandžiogala |
| 10 kV line | L-200 Pagynė (busbar section S210) |
| TP / transformer | Pg-452 / T-2 |
| Permitted power (leistinoji, LNG) | 22 kW; installed active 22 kW |
| Permit no. / date | 23-KA0250816 / 2023-07-01 |
| Breaker type and rated current | "Saugiklis" (fuse); 250 A on one row, 300 A on the other |
| Meter voltage | 57/400 V |
| Metering location | inside the transformer station |
| Outage duration, reliability category | 336 (units not stated), category 6 |
| Connected since | 1994-05-03 |

## TR load tool (internal "TR apkrova" page, screenshot)
- TR op. pav.: Pg-452, TR id 340359
- Objects 1, meters 2; SMART meters 2 (100%), SMART LNG 44.0 kW; non-SMART 0
- **Max load 9 kW, reached 2026-01-29 10:15 (+02:00)**; SMART data collection 100%
- 3-phase total P: 11 kW; max current 17 A
- Note shown: "TR turi tik vieną traf'ą" (TR has only one transformer)

## Observations
- Existing load on T-2 is tiny: 9 kW measured peak vs 44 kW SMART permitted power. The new 22 kW is easily absorbed
  at transformer level, so the engineering decision here was about *physical* connection (new KS at the TP + 150 mm²
  cable), not capacity.
- The tool says the TR has one transformer while the TS says "transformatoriaus T-2" and TEVIS lists T-2. A naming
  mismatch (T-2 as the only transformer) – worth validating in the data model.
- The TS picks a new cabinet next to the TP with ≥150 mm² cable, then a ≥150 mm² cable to the customer's KS/KAS. The
  GIS map shows the preliminary metering spot (green plug) ~90 m east of Pg-452, consistent with the 90 m of 4x150 cable
  in the estimate.
