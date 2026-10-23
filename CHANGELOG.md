# Changelog

## Round 10 — Pitch wrap-up

No product-code change. Pitch facts (`docs/PITCH_FACTS.md`), 1920×1080 screenshot set in `docs/media/`, README wiring, and full LT/EN autoplay backup videos (~5 min 10 s, under 25 MB each) in `docs/media/` and artifacts. Capture helper: `scripts/capture_pitch_assets.mjs`.

## Round 9 — Agento sekimas

Visible LangGraph tool-call trace next to the n8n canvas. Overlay **LLM / Python / Žmogus** colour-codes nodes and edges. Each step lists kind (LLM parse/phrasing, deterministic Python, or human gate), summarised I/O with expandable JSON, duration, provenance tags, and the rule / KNOWLEDGE section. Header: X LLM calls, Y deterministic tools, 1 human gate. One present beat; autoplay stays under 5:15. Playwright asserts the overlay.

## Round 8 — Official TS + Analitika

Two-page official-looking TS demo blank (no ESO logo): header, 26-E-DEMO-… number, dates, redacted parties, technical parameters, numbered conditions, cost and obligations, engineer signature from the audit, SHA-256 footer. Page 2 is an offline GIS annex (connection point, pole/cabinet, line, legend, scale). Lithuanian glyphs stay in DejaVu. Playwright asserts both pages.

Analitika view in the n8n desk language: throughput/day, median agent vs engineer stage, bottleneck hours (missing data / approval), SLA-risk queue, A/B/C/escalate/waiting mix, cumulative hours saved tagged as an assumption. Seeded synthetic month in SQLite. One present beat; autoplay stays ~4 min 52 s. DEMO_SCRIPT and the one-pager updated.

## Round 7 — Hardening

Playwright jury e2e in CI (customer → approve → PDF, missing-data, fail brief, what-if 11→100, present LT/EN). Per-beat autoplay totals 4.5 minutes with a hold on split and a restart on the last beat. Compact high-contrast present bar with LT/EN. DejaVu-embedded TS / brief / one-pager PDFs (ąčęėįšųūž). One-pager has a full-screen layout and a print stylesheet. Customer tracker is a status page: summary, timeline with timestamps, Laukia duomenų as its own step, SLA date, download card. FastAPI lifespan. History trimmed. `make demo` still builds `web/dist` when missing.

## Round 6 — Close the loop

Customer mock, five adapters (mock + stub), Integracijos canvas, autoplay, A4 leave-behind, GitHub Actions pytest + build.

## Round 5 — Guided path

Frozen Pristatymas, request_missing_data + resume, live what-if, gallery what-if fill 6/7.

## Round 4 — Honest back-test

Mismatch taxonomy a/b/c/d. Tool fixes only for (c). In-scope 95 %, overall 84 %, tool errors 0. SQLite desk.

## Round 3 — Manager desk

Queue, inbox, historical gallery, reinforcement brief, audit export.

## Round 2 — Rich inspectors

n8n node inspectors, fail path, printed TS, timings on cards.

## Round 1 — Hero canvas

LangGraph + FastAPI + Vite. 11 kW 3F on TP 12-608, pole 200/3, solution B. Deterministic Python; LLM only parse/§3.
