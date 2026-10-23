# Architecture

**ESO helper** is a LangGraph orchestrator behind a FastAPI service and an English node-graph dashboard. Deterministic Python makes every engineering decision. The LLM, when a key is present, only parses free text and may rephrase TS §3. An engineer always approves. The only Lithuanian surface is the issued two-page *Prijungimo sąlygos* document.

One case is in scope: 11 kW, 3-phase, TP 12-608, L-200, pole 200/3, solution B.

```mermaid
flowchart LR
  UI[ESO helper] --> API[FastAPI]
  API --> G[LangGraph]
  G --> T[Python tools]
  T --> GIS[GIS topology]
  T --> CAP[Power BI / SCADA]
  T --> PRICE[Pricing catalogue]
  T --> REG[TS registry]
  T --> LL[line_load estimator]
  G --> H[Engineer interrupt]
  H --> UI
  H --> TS[Lithuanian TS + GIS annex]
```

```mermaid
flowchart TD
  parse_request --> locate_connection_point --> select_solution --> size_breaker
  size_breaker --> check_capacity --> check_voltage_drop --> check_reliability --> check_future
  check_future --> draft_ts_section3 --> estimate_cost --> render_map --> engineer_approval --> issue_ts
```

## Step panels

Every opened step uses the same structure:

| Block | Content |
|---|---|
| Data source | System, dataset, fields, timestamp (GIS, Power BI/SCADA, CRM, pricing, TS registry) |
| Requirements and rules | Quoted clause + KNOWLEDGE / SCOPE / standard reference |
| Calculation | Numbers, formula, gauges, map, A/B/C, breaker table, cost table, load/loss |
| Result | Pass or fail |

Capacity and voltage attach `estimate_load_loss()` from `src/eso_agent/load_loss.py`, which uses `src/line_load.py` tables:

- `Psk = ΣP_perm × k(n)`
- `Isk = Psk / 0.624`
- `ΔU = L_km × Psk × kU`
- feeder loss `3 × Isk² × R`
- transformer loss `P0 + Pk × (S/Sn)²` on 400 kVA
- energy `P × 8760 × (Psk / Pperm)`

The solution step shows a compact before/after summary of the same estimate.

## Tool contracts

| Tool | Input | Output | LLM? |
|---|---|---|---|
| parse_request | text + form | kW, phases, coords | optional |
| locate_connection_point | lat, lon | nearest pole/cabinet | no |
| select_solution | feeder type, distance | A / B / C | no |
| size_breaker | total kW, phases | C n A | no |
| check_capacity | added kW + load | 80/90 %, load/loss | no |
| check_voltage_drop | added kW + feeder | V ≥ 207, profile, load/loss | no |
| check_reliability / future | location, solution | N-1, headroom | no |
| draft_ts_section3 | solution + numbers | Lithuanian §3 | optional wording |
| estimate_cost / render_map | pricing / GIS | net/gross, annex | no |
| engineer_approval / issue_ts | decision | audit, 2-page TS | no |

## LLM vs Python vs human

Python decides. LLM only parses text and may rephrase §3. Offline if no key. The trace overlay colour-codes LLM (amber), Python (teal) and Human (coral). `/api/runs/{id}/trace` returns the same payload.

## Data and persistence

Adapters (GIS, capacity, CRM, pricing, registry) still sit behind the tools. Their contracts and fixture tags live in the docs, not in the dashboard. Runs and the SHA-256 audit persist in SQLite.

## Out of the product UI

Scenario pickers, the 12-case queue, history gallery, customer split view, presentation autoplay, what-if, and time-saved HUD are not part of the dashboard. Backend endpoints for those experiments may still exist; they are not the product.
