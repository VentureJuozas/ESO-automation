# ESO prijungimo sąlygos — agent demo

An AI **orchestrator** (LangGraph) prepares 0.4 kV grid-connection technical conditions (prijungimo sąlygos) for a new household on substation **12-608**. Deterministic Python makes every engineering decision. The LLM only parses the request and phrases TS §3. An engineer always approves.

The dashboard is an **n8n-style workflow canvas**: each tool is a node, edges animate as the run proceeds, and clicking a node opens an inspector (inputs, output, JSON, ESO rule link). The default screen is a **manager queue desk**.

## One command (fresh clone)

Needs Python 3.11+ and Node 20+. **No API key. No network tiles required** (offline paper map if Esri/OSM fail).

```bash
make demo
```

Then open http://127.0.0.1:8000

Same path as a script: `bash scripts/demo.sh`

Docker (also one command, after Docker is installed):

```bash
docker compose up --build
```

```bash
make test          # pytest
cd web && npm run dev   # UI with /api proxied to :8000
```

Queue, runs and audit records persist in `data/demo.sqlite`. **Atstatyti demo** reseeds.

## 2-minute pitch

See [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) for the 4–5 minute jury walkthrough.

1. Open **Vadovo eilė**. Twelve redacted cases. **Paleisti visas**. Inbox: approve / edit §3 / override.
2. Fail row → reinforcement brief (400→630 kVA).
3. **Istorinė galerija** → back-test. In-scope accuracy and taxonomy. 26-E-37934 stays a mismatch (Pg-452).
4. **Auditas** JSON + HTML, SHA-256.
5. Hero: 11 kW → 200/3 → B → 20 A → A4 TS.

## Back-test (honest)

| | Overall (16) | In-scope (12-608 + known point) | Tool errors |
|---|---|---|---|
| Round 3 (before) | 51 % | not separated | hidden in the 51 % |
| Round 4 (after) | **84 %** | **95 %** | **0** |

Fixes were in the tools, not in the history CSV: size breaker on total permitted kW, add only the increment to the transformer peak, filter a 205 V event, do not block on a synthetic fuse, do not parse L-206 as 206 A. Documented in [docs/BACKTEST.md](docs/BACKTEST.md).

## What is real vs synthetic

| Tag | Examples |
|---|---|
| real | TP peak 227.7 kW, 400 kW nominal, 80/90 % = 320/360, feeder point counts, L-KS14330 315 A from TS 23-31728, 26-E-37934 prices |
| rule | Breaker table, diversity coefficients, 207 V, A/B/C selection |
| inferred | Distances and segment lengths from coordinates |
| synthetic | Pole/cabinet coordinates, other feeder fuses, conductors, pending kW = 0 |

Customer names, addresses and meter serials are not in the demo. Raw CSVs stay git-ignored.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md), [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md). Scope is fixed in [data/SCOPE.md](data/SCOPE.md).

```
web/          React + Vite dashboard (n8n canvas + manager desk)
app/          FastAPI (SSE + TS/audit/brief HTML)
src/eso_agent tools, LangGraph, engine, SQLite store
src/line_load.py   ESO calculator (voltage drop / diversity)
tests/        hero, fail, queue, gallery taxonomy, persist
```
