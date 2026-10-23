# Demo script — ESO helper

Stage: `make demo`. Open http://127.0.0.1:8000. The product is one case.

The UI is English. The issued TS stays Lithuanian.

## Path

1. **Request bar** — 11 kW, 3-phase, TP 12-608, L-200, pole 200/3, solution B · C 20 A.
2. **Run** — the node graph walks Application → Connection point → Checks → Solution → Issue.
3. **Sidebar** — five dropdown groups. Click a step to open its panel.
4. **Capacity** — transformer after = 227.7 + 11 = 238.7 kW vs 320 kW (80 %); coincident = 230.34 kW (peak + request × k(n), not the gate). Load and loss: L-200 meter peak 79.3 → 90.3 kW, 127.1 → 144.7 A, 90.4 % of 160 A, 224.0 V at 200/3.
5. **Voltage** — profile vs 207 V (LST EN 50160). Same estimator, segment table to the customer.
6. **Solution** — A rejected (no cabinet), B selected (overhead pole KAS), C not applicable. Compact load/loss summary. Breaker C 20 A. Cost from the 26-E-37934 sheet.
7. **Engineer** — review §3, open the audit, **Approve and issue**.
8. **Prijungimo sąlygų dokumentas** — two A4 pages, GIS annex, HTML and PDF.

## Trace

**Trace** or **LLM / Python / Human** on the canvas. Amber = LLM parse/phrase. Teal = Python. Coral = engineer gate.

## Numbers to say

| Item | Value |
|---|---|
| Peak → after | 227.7 → 238.7 kW (coincident 230.34 kW) |
| 80 % / 90 % | 320 / 360 kW on 400 kVA |
| L-200 feeder | 79.3 → 90.3 kW · 127.1 → 144.7 A · 90.4 % of 160 A |
| Feeder / TR loss | 2.738 → 3.570 kW · 2.421 → 2.568 kW |
| Voltage at 200/3 | 224.0 V |
| Voltage floor | 207 V |
| Point | pole 200/3 on L-200 |
| Solution / breaker | B / C 20 A |
| Cost (orientyras) | 1 786.89 € net / 2 162.14 € gross |

Do not quote hours saved, monthly extrapolations, or what-if scores. Fixture tags (real / rule / inferred / synthetic) stay in [PITCH_FACTS.md](PITCH_FACTS.md).
