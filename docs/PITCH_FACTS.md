# Pitch facts — ESO helper

Every number a slide can quote. Each row has a **source** and a **tag**. Tags are for this document only — they are not shown in the UI.

| Tag | Meaning |
|---|---|
| `real` | Taken from issued 12-608 files or Substations_info / cost sheets in the repo |
| `rule` | Written in a published table or standard used by the tools |
| `inferred` | Calculated from real or rule inputs |
| `assumption` | Hypothesis, **not** ESO statistics |
| `synthetic` | Generated fixture (geometry, conductor, baseline) |

## Problem

A household 0.4 kV connection on TP **12-608** still takes an engineer through GIS, capacity, voltage, a solution letter and a signed TS. The SLA is **three working days**. ESO helper reads the request, runs deterministic Python for every engineering decision, writes Lithuanian §3, and stops for a human signature. The LLM only parses text and may phrase §3. It does not pick the breaker, the feeder or the cost.

## Hero case — 11 kW, 3F, TP 12-608

| Fact | Value | Source | Tag |
|---|---|---|---|
| Request | **11 kW**, **3 phases** | `scenarios.hero` | `synthetic` (canonical case) |
| Coordinates | **54.55929, 25.27955** | same | `synthetic` (plot near 12-608) |
| Substation | **TP 12-608** | `network.SUBSTATION` | `real` |
| Transformer nameplate | **400 kVA** | Substations_info via `network.py` | `real` |
| Recorded peak | **227.7 kW** | `network.SUBSTATION["peak_kw"]` | `real` |
| 80 % limit | **320 kW** | 400 kVA × 0.80 | `rule` |
| 90 % limit | **360 kW** | 400 kVA × 0.90 | `rule` |
| After this 11 kW | **238.7 kW** | 227.7 + 11 | `inferred` |
| Connection point | pole **200/3** on **L-200** | locate tool | `inferred` |
| Solution | **B** (new KAS on pole + 16 mm²) | `select_solution` | `rule` |
| Breaker | **3F C 20 A** | §15 table, 11 kW 3F | `rule` |
| Voltage after (tool) | **224.0 V** | `quality.voltage_after_v` | `inferred` |
| Voltage at 200/3 after | **224.0 V** | `quality.profile` and load/loss span TP → 200/3 | `inferred` |
| L-200 meter peak | **79.3 kW** | `network.FEEDERS["L-200"]["meter_max_kw"]` | `real` |
| Feeder current after | **144.7 A** | (79.3 + 11) / 0.624 | `inferred` |
| Line loading after | **90.4 %** of 160 A | 144.7 / 160 | `inferred` |
| Limit | **207 V** (230 − 10 %) | LST EN 50160 | `rule` |
| Cost net / gross | **1 786.89 / 2 162.14 €** | `estimate_cost` | `inferred` |
| SLA | **3 working days** | household deadline ≤ 250 kW | `rule` |

## Load and loss estimator

From `src/eso_agent/load_loss.py` using `src/line_load.py` (2018 calculator).

| Fact | Formula | Tag |
|---|---|---|
| Feeder peak (thermal) | L-200 `meter_max_kw`, not the TP 227.7 kW total | `real` |
| Feeder current | `I = P_feeder / 0.624` | `rule` |
| Voltage drop | `ΔU = L_km × Psk × kU` with `Psk = ΣP_perm × k(n)` | `rule` |
| Feeder loss | `3 × I² × R`, `R = r_Ω/km × L_km` on TP → customer | `rule` |
| Transformer loss | `P0 + Pk × (S/Sn)²` · P0 0.93 kW, Pk 4.60 kW, Sn 400 kVA | `rule` |
| Annual energy | `P_peak × 8760 × (0.3 LF + 0.7 LF²)` | `rule` |
| Line loading | Pass only if every segment ≤ 100 % of ampacity | `rule` |
| 4A-50 ampacity | **160 A** | `rule` |
| Hero feeder loss | **2.738 → 3.570 kW** · **2 808 kWh/year** on TP → 200/3 | `inferred` |
| Hero transformer loss | **2.421 → 2.568 kW** | `inferred` |

## LLM / Python / human

From `build_trace(hero)` / `/api/runs/{id}/trace`.

| State | LLM | Deterministic Python | Human |
|---|---|---|---|
| Awaiting engineer | **2** | **9** | **1** |
| After issue | **2** | **10** | **1** |

LLM: `parse_request`, `draft_ts_section3`. Human: `engineer_approval`.

## What is fixture versus measured

**Real (in the repo, used by tools)**

- TP 12-608 identity, 400 kVA, recorded peak 227.7 kW
- Breaker table, 80/90 % shares, 207 V limit, 3-day SLA, cost unit rates from 26-E-37934
- Deterministic Python tools, SHA-256 audit, SQLite persistence
- Two-page TS layout (no ESO logo) and GIS annex geometry

**Synthetic / fixture (do not claim as production)**

- Hero coordinates and pole/cabinet geometry
- Voltage conductor 4A-50 and 230 V baseline on L-200
- TS number `26-E-DEMO-…`, redacted parties
- Adapter reads (GIS, smart meter data, CRM, pricing, registry) until Phase 1 swaps them

**Human**

- Engineer always approves, edits §3, or overrides with a reason
