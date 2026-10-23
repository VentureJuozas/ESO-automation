# Back-test before / after

Recorded for the jury. History CSV was **not** edited to raise the score.

## Before (Round 3)

- Overall accuracy: **51 %** (16 cases, mean of per-case field scores)
- In-scope figure: not reported (apples mixed with oranges)
- Visible pain: increment kW sized the breaker (6 kW → 13 A vs issued 20 A on an 11 kW total)

| id | What looked like a miss | Real cause |
|---|---|---|
| 26-E-37934 | solution + cost | (a) other TP Pg-452 |
| 26-E-37536 | — (100 %) | (a) other TP Rg-202, analog on L-300 |
| 21-62367, 25-78962, 23-31728, 22-35508, 22-77660, 22-83797, 21-64496 | breaker | (c) `LG nauja` increment used instead of `Leist. Galia suma` |
| 20-80254 | breaker 206 A | (c) regex ate `L-206 atramos` as 206 A |
| 23-93436, 20-67807 | A vs B | (b) KS-13154 / KS-13160 not in the 12-608 fixture |
| 22-26356, 21-26840 | escalate | (c) single 205 V event on L-KS13058 treated as a hard fail |
| 24-88201 | escalate + 32 A vs 25 A | (c) synthetic 250 A fuse blocked; (d) table 18 kW = 32 A |
| 23-44040 | C vs B | (b) no coordinates; (c) `L-KS14330` parsed as cabinet |

## Fixes in deterministic tools (category c only)

1. **Breaker input** — size on total permitted kW; `existing_kw` so capacity/voltage add only the increment (`added_demand_kw`).
2. **Voltage baseline** — a measured min already below 207 V is an unfiltered event (same as L-200). Use 230 V and do not auto-escalate.
3. **Synthetic fuse** — Isk above a `fuse_source=synthetic` default is a note, not a block. Real fuses (L-KS14330 315 A) still block.
4. **Comparator** — household C-characteristic only; do not treat L-206 / 315 / 630 as the customer breaker; do not treat `L-KSxxxxx` as a plot cabinet.

## After (Round 4)

- Overall: **84 %**
- In-scope (12-608 and the cabinet/pole exists in the fixture): **95 %** (7 cases)
- Tool-error cases: **0**
- Taxonomy (cases): out of scope 2 · missing input 7 · tool error 0 · engineer judgment 1 · match 6

Remaining honest misses:

- **(a)** 26-E-37934 Pg-452 (and 26-E-37536 Rg-202, analog only)
- **(b)** L-KS13154 cabinets, pole 206/2, pole 100/14, pole 205/6, and 23-44040 (new C, no point)
- **(d)** 24-88201 issued C 25 A at 18 kW; §15 table is C 32 A

In-scope 95 % is six full matches plus one judgment score (32 A vs 25 A). It is not 100 %, and it should not be.
