# ESO prijungimo sąlygos — agent demo

[![CI](https://github.com/VentureJuozas/ESO-automation/actions/workflows/ci.yml/badge.svg)](https://github.com/VentureJuozas/ESO-automation/actions/workflows/ci.yml)

An AI **orchestrator** (LangGraph) prepares 0.4 kV grid-connection technical conditions for a household on substation **12-608**. Deterministic Python decides. The LLM only parses text and may phrase TS §3. An engineer always approves.

The dashboard is an **n8n-style canvas**. The default screen is a **manager queue desk**. A **customer mock** (no ESO branding) sits beside it. Five **adapters** (GIS, Power BI, CRM, pricing, TS registry) are mocks today and stubs for production.

## Quickstart (fresh clone)

Python 3.11+ and Node 20+. No API key.

```bash
make demo
```

Open http://127.0.0.1:8000 — or `bash scripts/demo.sh` / `docker compose up --build`.

```bash
make test
```

Queue, runs and audit persist in `data/demo.sqlite`. **Atstatyti demo** reseeds.

Jury walkthrough: [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md) · A4 leave-behind: `/api/onepager.html` · rounds: [CHANGELOG.md](CHANGELOG.md)

`make demo` installs Python deps and **builds `web/dist` if it is missing**, then serves on :8000.

## Screenshots

After `make demo` (also in the PR walkthrough):

- **Vadovo eilė** — desk HUD, table, engineer inbox
- **Klientų maketas** — status page: summary, timeline (including Laukia duomenų), SLA date, TS download
- **Klientas ir stalas** — request in, TS out
- **Pristatymas** — ~4 min 52 s autoplay, compact LT/EN bar, restart on the last beat
- **TS PDF / HTML** — official-looking demo blank + GIS annex (2 pages), DejaVu, ąčęėįšųūž
- **Analitika** — synthetic month in SQLite: throughput, medians, bottlenecks, SLA risk, A/B/C mix
- **Integracijos** — five adapter nodes, mock / stub

## Pitch in one minute

1. **Pristatymas** — frozen 4–5 min path, LT/EN, autoplay with pause.
2. **Klientų maketas** — submit 11 kW, tracker gauta → išduota, download TS PDF.
3. Split view: request in on the left, TS out on the right, minutes not days.
4. Fail → reinforcement brief. Gallery → 95 % in-scope, 0 tool errors.
5. **Integracijos** — five adapter nodes, all mock, stubs named.

## Back-test

| | Overall (16) | In-scope | Tool errors |
|---|---|---|---|
| Round 3 | 51 % | mixed | hidden |
| Now | **84 %** | **95 %** | **0** |

What-if fill of missing GIS points: **6 / 7** match. History CSV was not tuned.

## Docs

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- [docs/NEXT_STEPS.md](docs/NEXT_STEPS.md)
- [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md)
- [docs/BACKTEST.md](docs/BACKTEST.md)

Customer names, addresses and meter serials are not in the demo.
