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

1. Open **Vadovo eilė** (default). Twelve redacted cases mix A/B/C, fails and missing data. HUD shows processed, engineer minutes saved (assumption), and approval-queue depth. SLA clocks use the 3 working-day household rule.
2. Click **Paleisti visas**. Rows flip new → running → awaiting / escalated. Open the inbox: approve, edit §3, or override with a reason (audited).
3. Click a fail row (100 kW). The n8n canvas branches at `check_capacity`. The inspector shows the reinforcement brief (400→630 kVA, feeder split, new TP) with inferred cost ranges. Open the printable paketą.
4. Open **Istorinė galerija**. Run the back-test. 26-E-37934 (Pg-452) and other mismatches stay visible with an explanation. Accuracy is honest.
5. From any case, open the immutable **Auditas** (JSON + HTML, SHA-256).
6. Hero still works: scenario **Hero** → Paleisti eigą → 200/3 → B → 20 A → approve → A4 TS.

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
tests/        breaker, locate, A/B/C, hero E2E, fail case, queue batch, gallery, audit
```
