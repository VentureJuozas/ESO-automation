# Next steps — production roadmap

Ranked leftover product work, then a phased path out of the hackathon demo.

## Round 5 (next, this session)

**Guided presentation / demo mode** on the same n8n canvas: a 4–5 minute jury path with speaker beats (desk → Paleisti visas → inbox → fail brief → gallery taxonomy → audit hash), a “Kaip demonstruoti” overlay, and a one-click freeze of the recorded replay.

## Phase 1 — Real ESO data

- Power BI: free transformer capacity, 35–10 kV line loads, reserved consumption
- GIS / redacted `Objects_network_power.csv` once privacy is signed off (replace synthetic poles)
- Official application queue (proper-submission clock) instead of the 12 synthetic rows
- SharePoint issued-TS templates for §1 / §2 variants

## Phase 2 — Authoritative annexes

- Technologinės plėtros standartas PDFs (annex 12 for 0.4 kV)
- Replace unverified 600 m / 80 kW snippets with signed rule text
- Full `Kofai` diversity sheets
- Real fuse and conductor per feeder (today only L-KS14330 315 A is real)

## Phase 3 — Security and data protection

- No personal data in prompts, logs, maps or SQLite (already redacted in the demo)
- Persist audit with access control; sign exports with an ESO key, not just SHA-256
- Role split: manager desk vs engineer inbox vs read-only auditor
- Retention and deletion aligned with the customer portal

## Phase 4 — Human-in-the-loop policy

- Override remains mandatory on failed checks; no silent issue
- Engineer correction loop (26-E-37536 style) then re-issue
- Write the issued TS and GIS annex back to the document store
- Sample 100 % of escalations and a rotating % of issued A/B/C for QA

## Phase 5 — Rollout and KPIs

- Pilot: one desk on 12-608 / Vilnius district, shadow mode (agent prepares, engineer still owns)
- KPIs: median minutes to draft, % issued without override, in-scope back-test ≥ 90 %, SLA misses, engineer minutes saved (measured, not assumed)
- Then expand feeders and customer types inside 0.4 kV + 0.4/10 kV only (SCOPE)

Do not expand to generation, 10 kV works, or other substations until Phase 1 data is real.
