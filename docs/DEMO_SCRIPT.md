# Demo script — ~5 minutes

Stage: `make demo`. Open http://127.0.0.1:8000. Click **Pristatymas**. Autoplay is **~5 min 10 s** with a hold on the split beat. **Pauzė** / space to pause. The compact bar has an obvious **LT / EN** switch. Last beat ends with **Iš naujo**. Arrow keys still work. The TS stays Lithuanian.

The path is a **frozen replay**. Leave-behind: `/api/onepager.html` (screen + print) and `/api/onepager.pdf`. Issued TS: two A4 pages — official-looking demo blank + GIS annex.

| Time | Beat | Dwell | Key |
|---|---|---|---|
| 0:00 | Split | 20 s | Customer mock on the left, desk on the right. Minutes, not days. |
| 0:20 | Desk HUD | 5 s | Twelve redacted 12-608 cases. SLA three working days. |
| 0:25 | Paleisti visas | 25 s | Frozen statuses flip. Python decides. |
| 0:50 | Inbox | 25 s | Approve / edit §3 / override. Waiting-for-data cards sit here too. |
| 1:15 | Hero map | 20 s | 11 kW, pole 200/3. Paper map if tiles fail. |
| 1:35 | Solution B | 15 s | Overhead, no cabinet → new KAS. |
| 1:50 | Capacity | 15 s | 227.7 + 11 vs 320 kW. |
| 2:05 | TS §3 | 20 s | Lithuanian wording. Engineer signs. |
| 2:25 | Fail brief | 25 s | 100 kW → 327.7 vs 320. Reinforcement pack. |
| 2:50 | Gallery | 30 s | In-scope 95 %, overall 84 %. Taxonomy. 26-E-37934 is (a). |
| 3:20 | Audit | 20 s | SHA-256, SQLite. |
| 3:40 | Agento sekimas | 18 s | Overlay: LLM reads/phrases, Python decides, human signs. Trace next to the canvas. |
| 3:58 | Integracijos | 20 s | Five adapters, all mock. Stubs name the ESO systems. |
| 4:18 | Analitika | 22 s | Synthetic month: throughput, medians, bottlenecks, SLA risk, A/B/C mix. Hours saved are an assumption. |
| 4:40 | Time saved | 30 s | Replay ms vs 2–4 h assumption. Ends clean; **Iš naujo**. |

## Live extras (if asked)

- **Agento sekimas:** sidebar or the canvas button **LLM / Python / Žmogus**. Timeline of every tool call, expandable JSON, rule refs.
- **Official TS:** after approve, open the HTML/PDF. Page 1 is the demo blank (26-E-DEMO-…, parties, parameters, conditions, cost, signatures). Page 2 is the GIS annex. No ESO logo.
- **Analitika** in the sidebar: same charts as the present beat. Banner says synthetic.
- **What-if bar** on a case: drag 11 → 100 kW. Capacity fails, the canvas branch switches to escalate.
- **Missing data:** open a `Laukia duomenų` row. The graph stopped at `request_missing_data`. Letter preview is not sent. Supply coords → the graph resumes on the same canvas.
- **What-if fill** in the gallery: of the 7 missing-input files, **6** become matches when the issued TS point is added as virtual GIS. 22-26356 stays an engineer-judgment miss (historical TR swap). This is labelled what-if, not the live score.

**Atstatyti demo** if you need a clean desk after the live extras.
