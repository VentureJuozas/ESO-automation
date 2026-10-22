# Next steps

Honest follow-on work after the hackathon demo. Ranked by how much they would change a jury’s view of a finished product.

## 1. Real ESO data instead of tagged fixtures (highest demo value)

- Power BI exports: free transformer capacity, 35–10 kV line loads, reserved consumption capacity
- Internal TR load tool (hackathon network only today)
- SharePoint issued-TS examples for §1/§2 template variants
- Redacted `Objects_network_power.csv` coordinates once privacy is signed off, replacing synthetic poles/cabinets

## 2. Authoritative standard annexes

- Ingest the Technologinės plėtros standartas PDFs (annex 12 for 0.4 kV lines)
- Replace the unverified 600 m / 80 kW snippets with signed rule text
- Load full `Kofai` diversity sheets rather than the extracted arrays

## 3. Upgrade ladder rungs 4–6

- Feeder reinforcement when Isk exceeds the fuse
- Transformer swap when 80%/90% fail
- New transformer station / 10 kV works
- Generation and storage (reverse power, LGG)

## 4. Full voltage-drop path

- Real conductor type and length per segment
- Per-meter usable min voltage after event filters, all three phases
- Short-circuit current and selectivity as a blocking check

## 5. ESO systems, evaluation, security

- Read applications from the official queue (proper-submission clock)
- Write the issued TS and GIS annex back to the document store
- Engineer correction loop (as in 26-E-37536) then re-issue
- Backtest against the 14 historical TS on 12-608 (breaker table already 13/14)
- Keep personal data out of prompts, logs and maps; persist the audit trail
