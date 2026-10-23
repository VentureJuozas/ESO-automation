# Pitch facts — ESO 0.4 kV TS product demo

Every number a slide can quote. Each row has a **source** and a **tag**.

Tags:

| Tag | Meaning |
|---|---|
| `real` | Taken from issued 12-608 files or Substations_info / cost sheets in the repo |
| `rule` | Written in a published table or standard used by the tools |
| `inferred` | Calculated from real or rule inputs |
| `assumption` | Demo hypothesis, **not** ESO statistics |
| `synthetic` | Generated for the demo (geometry, month, conductor, baseline) |

Live autoplay is frozen (`docs` + `src/eso_agent/present.py`). No network, no API key.

## Problem (one paragraph)

A household 0.4 kV connection on TP **12-608** still takes an engineer through GIS, capacity, voltage, a solution letter and a signed TS. The desk is a queue, not a chatbot, and the SLA is **three working days**. This demo shows a LangGraph orchestrator that reads the request, runs deterministic Python for every engineering decision, writes Lithuanian §3, and stops for a human signature — so a request in becomes a two-page TS out in **minutes, not days**, with an immutable SHA-256 audit. The LLM only parses text and may phrase §3. It does not pick the breaker, the feeder or the cost.

## Agent run time vs assumed manual time

| Fact | Value | Source | Tag |
|---|---|---|---|
| Recorded replay, hero until human gate | **6 160 ms** (sum of `REPLAY_MS` without `issue_ts`) | `src/eso_agent/timing.py` `REPLAY_MS` | `synthetic` (recorded offline replay) |
| Recorded replay, issued hero | **6 480 ms** | same + `issue_ts` 320 ms | `synthetic` |
| Value-panel agent ms (issued path) | **6 480 ms** | `comparison_payload()` on hero events | `synthetic` |
| Assumed manual desk time (fired tools) | **226.0 min** (~3 h 46 min) | `MANUAL_MINUTES` summed for hero tools | `assumption` |
| Minutes saved per issued hero | **225.9 min** | `manual_min − agent_ms/60000` | `assumption` |
| Monthly case load used on slides | **40** household 0.4 kV files / engineer | `MONTHLY_CASES_ASSUMPTION` | `assumption` |
| Monthly hours saved at that load | **150.6 h** | `225.9/60 × 40` | `assumption` |
| Slide range “2–4 hours manual” | **120–240 min** | `rules.MANUAL_TIME_ASSUMPTION_MINUTES` | `assumption` |
| Present line on time | “40 cases a month is not ESO statistics” | `present.py` beat `time` | `assumption` |

Do not present 150.6 h or 226 min as ESO measured time. They are labelled `assumption` in the UI.

## Back-test accuracy

History CSV was **not** edited to raise the score (`docs/BACKTEST.md`).

| Fact | Value | Source | Tag |
|---|---|---|---|
| Cases in the gallery | **16** issued TS | `eso_agent.backtest.run_gallery()` | `real` (redacted issued files) |
| Round 3 overall | **51 %** | recorded `BEFORE.accuracy` | `inferred` (field-score mean) |
| Current overall | **84 %** | `run_gallery()["accuracy"]` = 0.84 | `inferred` |
| In-scope count | **7** (cabinet/pole exists on 12-608) | `in_scope_count` | `inferred` |
| In-scope accuracy | **95 %** | `in_scope_accuracy` = 0.95 | `inferred` |
| Tool-error cases | **0** | taxonomy | `inferred` |
| What-if fill of missing GIS points | **6 / 7** match | `/api/gallery/whatif` | `inferred` |

Taxonomy (**cases**):

| Bucket | Count | Tag |
|---|---|---|
| Out of scope (other TP / voltage) | 2 | `inferred` |
| Missing input | 7 | `inferred` |
| Tool error | 0 | `inferred` |
| Engineer judgment | 1 | `inferred` |
| Match | 6 | `inferred` |

In-scope 95 % is six full matches plus one judgment score (issued C 25 A at 18 kW vs table C 32 A). It is not 100 %.

## Test counts

| Suite | Count | Source | Tag |
|---|---|---|---|
| pytest | **60** | `pytest --collect-only -q` | `real` (this repo) |
| Playwright jury e2e | **6** | `web/e2e/jury.spec.js` | `real` |
| Present beats | **15** | `present.BEATS` | `real` |
| Present autoplay | **310 000 ms** (~5 min 10 s) | `present.TOTAL_MS` | `real` |

## LLM / Python / human

From `build_trace(hero)` / Agento sekimas (`/api/runs/{id}/trace`).

| State | LLM | Deterministic Python | Human | Source | Tag |
|---|---|---|---|---|---|
| Awaiting engineer (hero) | **2** | **9** | **1** | `trace.stats` | `real` (this run) |
| After issue | **2** | **10** | **1** | same + `issue_ts` | `real` |

LLM steps: `parse_request`, `draft_ts_section3` (offline templates in this demo).
Python steps (gate): locate, select, size, capacity, voltage, reliability, future, cost, map.
Human: `engineer_approval`. After sign-off, `issue_ts` is the tenth Python step.

## Hero case — 11 kW, 3F, TP 12-608

| Fact | Value | Source | Tag |
|---|---|---|---|
| Request | **11 kW**, **3 phases** | `scenarios.hero` / n8n seed | `synthetic` (canonical demo) |
| Coordinates | **54.55929, 25.27955** | same | `synthetic` (plot near 12-608) |
| Substation | **TP 12-608** | `network.SUBSTATION` | `real` |
| Transformer nameplate | **400 kVA** | Substations_info via `network.py` | `real` |
| Recorded peak | **227.7 kW** | `network.SUBSTATION["peak_kw"]` | `real` |
| 80 % limit | **320 kW** | 400 kVA × 0.80 | `rule` |
| 90 % limit | **360 kW** | 400 kVA × 0.90 | `rule` |
| After this 11 kW | **238.7 kW** | 227.7 + 11 | `inferred` |
| Coincident after | **230.34 kW** | capacity tool | `inferred` |
| Connection point | pole **200/3** on **L-200** | locate tool, WGS84 nearest | `inferred` |
| Solution | **B** (new KAS on pole + 16 mm²) | `select_solution` vs A/B/C table | `rule` |
| Breaker | **3F C 20 A** | §15 table, 11 kW 3F | `rule` |
| Voltage baseline used | **230.0 V** | L-200 has no usable min | `synthetic` |
| Voltage after (tool) | **224.0 V** | `quality.voltage_after_v` | `inferred` |
| Voltage at 200/3 after | **222.5 V** | `quality.profile` | `inferred` |
| Drop | **2.60 %** (2.5968) | `voltage_drop_pct` | `inferred` |
| Limit | **207 V** (230 − 10 %) | LST EN 50160 | `rule` |
| Conductor / length | 4A-50, **41.1 m** | `quality` | `synthetic` / `inferred` |
| Cost net / gross | **1 786.89 / 2 162.14 €** | `estimate_cost` | `inferred` |
| Materials / labour | **1 598.58 / 188.31 €** | 11.78 % labour | `inferred` (rate from 26-E-37934) |
| Cost note | Orientyras from **26-E-37934**, not an official quote for this file | `cost.note` | `real` sheet + `assumption` use |
| SLA | **3 working days** | household deadline ≤ 250 kW | `rule` |

## Fail case — 100 kW reinforcement

| Fact | Value | Source | Tag |
|---|---|---|---|
| Request | **100 kW**, 3F, same plot | `fail_capacity` | `synthetic` |
| After kW | **327.7** | 227.7 + 100 | `inferred` |
| vs 80 % limit | **327.7 > 320** (over **7.7 kW**) | capacity tool | `inferred` |
| Graph | branches to `escalate` | LangGraph | `real` (code) |
| Product | reinforcement brief, not a TS | `escalate.brief` | `real` (code) |
| Recommended option | TR **400 → 630 kVA** | brief `tr_630` | `assumption` (rung 5) |
| Option cost band | **18 000–32 000 €** | brief | `assumption` |
| Pending share | **12** queue files, **292 kW** | brief `pending_impact` | `synthetic` (seeded queue) |

## Present pack

| Fact | Value | Source | Tag |
|---|---|---|---|
| Beats | 15 | `present.BEATS` | `real` |
| Total dwell | 310 s (~5 min 10 s) | `TOTAL_MS` | `real` |
| Languages | LT / EN | present bar | `real` |
| Frozen | yes — `delay=0`, no live LLM | `frozen_pack()` | `synthetic` replay |

## What is mock versus real

**Real (in the repo, used by tools)**

- TP 12-608 identity, 400 kVA, recorded peak 227.7 kW
- Issued-TS gallery (16 redacted files) and the back-test comparison
- Breaker table, 80/90 % shares, 207 V limit, 3-day SLA, cost unit rates from 26-E-37934
- Deterministic Python tools, SHA-256 audit, SQLite persistence
- Official-looking 2-page TS **layout** (no ESO logo) and offline GIS annex geometry

**Synthetic / mock (do not claim as production)**

- Customer portal (no ESO branding, no real applicants)
- Five adapters: GIS, Power BI, CRM, pricing, TS registry — mock today, stubs named
- Hero / fail / missing-data scenarios and the 12-row desk seed
- Map tiles: none required; SVG/PDF drawing is our geometry
- Voltage conductor 4A-50 and 230 V baseline on L-200
- Analitika month (throughput, SLA risk, hours saved)
- Replay milliseconds and the 40-cases / 2–4 h manual model
- TS number `26-E-DEMO-…`, redacted parties, engineer signature from the audit

**Human / out of demo**

- Engineer always approves, edits §3, or overrides with a reason
- Reinforcement (630 kVA) is a brief, not a built work order
- Out-of-scope TP / 10 kV / new station work is not decided here
