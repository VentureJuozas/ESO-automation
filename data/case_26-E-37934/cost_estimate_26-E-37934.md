# Cost estimate for TS 26-E-37934 (from `Elektros ekspertinė skaičiuoklė 26-E-37934.xlsm`)

Sheets: `Skaičiuoklė` (input, line items with quantities), `Klientui` ("OBJEKTINĖ SĄMATA", customer-facing estimate),
`Data check`, and hidden rate tables: `Savivaldybės`, `Paslaugos`, `AVD įkainiai`, `DWH_Darbu_ikainiai` (26,968 rows),
`DWH_medziagu_ikainiai` (32,675 rows), `Medžiagos check`, `Darbai check`, `Ikainiai(dropdown)`.
Selected service on `Skaičiuoklė!J2`: "elektros įrenginių iškėlimas - 100 procentų sąmatinės vertės" (service pays 100% of
the estimate value; see the `Paslaugos` sheet for the other service types and percentages).

## Line items with non-zero quantity (this case)

| ID | Item | Unit | Qty | Price (EUR excl. VAT) |
|----|------|------|-----|-----------------------|
| 68 | Trifazio 40 A automatinio jungiklio įrengimas (3-phase 40 A breaker installation) | vnt. | 1 | 64.79 |
| 117 | KS/KAS – kirtiklių-saugiklių blokas, 1 rezervinė vieta (KS/KAS-2) | vnt. | 2 | 3,067.57 (1,533.785 each) |
| 254 | Aliuminiai 0,4 kV kabeliai (KL) 4x150 mm² | m | 90 | 4,725.38 (≈52.50 EUR/m) |
| 260 | Aliuminiai 0,4 kV kabelių galinės movos 4x150 mm² | kompl. | 4 | 755.92 (188.98 each) |
| 294 | Projektavimas iki 35 000 EUR be PVM (su topografine nuotrauka) | projekt. | 1 | 2,065.34 |

## Totals

| Row | Value (EUR) |
|-----|-------------|
| Materials and works | 10,678.99 |
| Capitalised labour (kapitalizuotas darbo užmokestis) | 1,257.99 |
| **Total excl. VAT** | **11,936.98** |
| **Total incl. VAT (21%)** | **14,443.75** |

Checks: 64.79 + 3,067.57 + 4,725.38 + 755.92 + 2,065.34 = 10,678.99 ✓; 11,936.98 × 1.21 = 14,443.75 ✓.

## Observations for the agent

- The line items map 1:1 to the TS Section 3 actions: 3.1 → items 68 + 117, 3.2/3.3 → items 254 + 260, project design →
  item 294. The TS text is the *what*, the estimate is the *how much*.
- In `Klientui` the unit price for the cable row (G259) equals the line total, so for cable/meter-length items the
  "price" column appears to carry the total for the quantity, not a per-unit rate. Verify before building a price lookup.
- Two KS/KAS (qty 2) are priced although the TS text mentions one KS and one KS/KAS: the estimate counts both cabinets.
- Breaker-only baseline costs (cheap path): trifazio 40 A įrengimas = 64.79 EUR; replacement of a breaker in an existing
  cabinet is priced as "keitimas" rows (e.g. single-phase 16–63 A: 19.47–24.92 EUR in the AVD block, higher in the
  contractor block).
- Capitalised labour is ~11.8% of materials + works here (1,257.99 / 10,678.99); the rule behind it was not extracted.
- Rates are per municipality (Savivaldybės sheet); Kauno r. sav. applies to this case.
