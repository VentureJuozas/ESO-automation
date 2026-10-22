# ESO prijungimo sąlygos — agent demo

An AI **orchestrator** (LangGraph) prepares 0.4 kV grid-connection technical conditions (prijungimo sąlygos) for a new household on substation **12-608**. Deterministic Python makes every engineering decision. The LLM only parses the request and phrases TS §3. An engineer always approves.

The dashboard is an **n8n-style workflow canvas**: each tool is a node, edges animate as the run proceeds, and clicking a node opens an inspector (inputs, output, JSON, ESO rule link).

## One command

```bash
make demo
```

Then open http://127.0.0.1:8000

Needs Python 3.11+ and Node 20+. No API key required (`offline` / replay mode). If `OPENAI_API_KEY` is set, parse and §3 wording use the LLM.

```bash
make test          # pytest
cd web && npm run dev   # UI with /api proxied to :8000
```

## 2-minute pitch

1. Leave the **Hero** scenario selected (11 kW, 3F, 54.55929, 25.27955).
2. Click **Paleisti eigą**. Watch nodes light up: parse → locate L-200 / 200/3 → solution B → 20 A breaker → four checks → draft → cost → map → approval gate.
3. Open **Pajėgumas** (transformer bar 227.7 → 238.7 kW vs 80/90 %), **Kokybė** (voltage profile), **Sprendinys** (A/B/C cards).
4. Click **Patvirtinti ir išduoti**. Open the printable TS.
5. Open the official A4 TS (print / PDF). Customer fields are redacted placeholders.
6. Switch to **Kaip tai veikia** for the same canvas showing frontend → API → LangGraph → tools → data.
7. Optionally run **Nauja paraiška** (paste a Lithuanian sample) or **Nepraeina** — the fail path branches at `check_capacity`, greys skipped nodes, and needs an audited engineer override.

**Rankinis vs Agentas** compares recorded replay timings with assumed desk minutes (not ESO statistics) and extrapolates 40 cases/month.

## What is real vs synthetic

| Tag | Examples |
|---|---|
| real | TP peak 227.7 kW, 400 kW nominal, 80/90 % = 320/360, feeder point counts, L-KS14330 315 A from TS 23-31728, 26-E-37934 prices |
| rule | Breaker table, diversity coefficients, 207 V, A/B/C selection |
| inferred | Distances and segment lengths from coordinates |
| synthetic | Pole/cabinet coordinates, other feeder fuses, conductors, pending kW = 0 |

Customer names, addresses and meter serials are not in the demo. Raw CSVs stay git-ignored.

## Architecture

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md). Scope is fixed in [data/SCOPE.md](data/SCOPE.md).

```
web/          React + Vite dashboard (n8n canvas)
app/          FastAPI (SSE + TS HTML)
src/eso_agent tools, LangGraph, engine
src/line_load.py   ESO calculator (voltage drop / diversity)
tests/        breaker, locate, A/B/C, hero E2E, fail case
```
