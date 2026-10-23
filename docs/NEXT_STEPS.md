# Next steps — production roadmap

Adapters are the map. Each phase replaces one mock with the real ESO system named in the stub.

## After the jury (production)

Round 7 closed the demo loop. Remaining work is swapping adapters, not more canvas chrome.

## Phase 1 — Swap mocks for live reads

| Adapter | Connect |
|---|---|
| GIS | Redacted `Objects_network_power.csv` once privacy is signed off |
| Capacity | Power BI free transformer capacity + reserved kW |
| CRM | Official application queue (proper-submission clock) |

## Phase 2 — Authoritative write-back

| Adapter | Connect |
|---|---|
| Pricing | Signed tariff annex, not 26-E-37934 as orientyras |
| Registry | Write issued TS + GIS annex to SharePoint |
| Rules | Technologinės plėtros standartas PDFs (annex 12) |

## Phase 3 — Security and data protection

- No personal data in prompts, logs, maps or SQLite
- Sign exports with an ESO key, not only SHA-256
- Role split: customer mock vs manager desk vs engineer vs auditor
- Retention aligned with savitarna

## Phase 4 — Human-in-the-loop policy

- Override remains mandatory on failed checks
- Engineer correction loop then re-issue
- Sample 100 % of escalations and a rotating % of issued A/B/C

## Phase 5 — Rollout and KPIs

- Pilot: one desk on 12-608, shadow mode
- KPIs: median minutes to draft, % issued without override, in-scope back-test ≥ 90 %, SLA misses, minutes saved (measured)

Do not expand to generation, 10 kV works, or other substations until Phase 1 adapters are real.
