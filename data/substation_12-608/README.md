# Substation 12-608 (MT-1 "Ozas", Dusinėnų k., Vilniaus r.) – the working dataset

Provided 2026-10-22. This is the one real substation the demo/challenge runs on. Raw files live in `raw/` (**git-ignored**:
they contain customer locations and meter serials). `ts_history_redacted.csv` is safe to commit (no addresses, meter/client/object numbers).
Rebuild with `python scripts/ingest_substation_12_608.py [source_dir]`.

## Files
| File | Rows | Content |
|------|------|---------|
| `Substations_info.csv` | 1 | The substation: id 12269532, name 12-608, 10 kV, modular transformer station (MT-1), commissioned 2014-01-16, **1 transformer, nominal 400 kW, N-1 400 kW, 90% = 360 kW, 80% = 320 kW**, WGS84 lon 25.27935, lat 54.55884 |
| `Objects_network_power.csv` | 221 | Every accounting point on the station: full path 110 kV Rudamina T-1 → 10 kV feeder L-SP312 (SP-312) → 12-608 → 0.4 kV feeder → pole or cable cabinet → metering cabinet (KAS/KS) → permitted power, phases, meter serial, WGS84 coordinates |
| `pastotes_load_kas15min.csv` | 1,344 | Substation total load, 15-min, 2026-02-01 … 2026-02-14 (14 days) |
| `meter_min_max_avg_load.csv` | 145 | Per-meter min/max/avg load kW over the same period |
| `min_itampa.csv` | 145 | Per-meter minimum voltage, with time and phase OBIS code (`32.24.0` = L1 min) |
| `TS_istorija.xlsx` | 14 | Past TS cases on this substation (inputs, network path, TS clauses). Redacted copy: `ts_history_redacted.csv` |

## Topology (from `Objects_network_power.csv`)
Six 0.4 kV feeders; 221 accounting points; sum of permitted power 1,877.5 kW (max single 22 kW); 188 three-phase / 30 single-phase meters
(3 unknown). Area bounding box lon 25.2720–25.2837, lat 54.5557–54.5634 (~0.9 km × 0.9 km).

| Feeder | Type | Points | Permitted kW | Metered (has load data) | Σ meter max kW | Σ meter avg kW | Notes |
|--------|------|-------:|-------------:|------------------------:|---------------:|---------------:|-------|
| L-KS14330 | cable (KS cabinets) | 59 | 622.0 | 46 | 165.7 | 34.0 | largest; 2 meters at 0 V; min 160 V / 184 V outliers |
| L-KS39685 | cable | 32 | 347.0 | 27 | 113.0 | 25.0 | no low voltage |
| L-KS13058 | cable + poles (11) | 19 | 120.5 | 12 | 48.1 | 11.6 | one 205 V reading |
| L-200 | overhead, 24 poles | 47 | 335.0 | 25 | 79.3 | 16.1 | 25 meters show 66–81 V on 2026-02-04 (see data quality) |
| L-204 | overhead, 14 poles | 29 | 230.0 | 18 | 81.2 | 20.2 | 17 meters at 0 V |
| L-300 | overhead, 22 poles | 35 | 223.0 | 17 | 53.6 | 12.1 | poles 300/6 … 311/3 |

Address-free pointers: pole (`pole`), cabinet (`cable_cabinet`, `cable_cabinet_feeder`), KAS (`metering_cabinet`), and `electrical_address`
(a comma-joined path: SP-312 → L-12-608 → 12-608 → feeder → T → pole → KAS). **Not in the data:** conductor type and length per segment, fuse ratings
per feeder / cabinet, pole coordinates, topology edges (only membership: feeder → pole/cabinet → KAS). Segment lengths can only be
*inferred* from customer coordinates (tag as `inferred`).

## Measured behaviour (14 days, February = winter)
- Substation load: min 68.7 kW, mean 127.0 kW, **peak 227.7 kW on 2026-02-06 19:15 UTC (21:15 local)**; evening peak 17–22 h (hourly mean 142–156 kW), night minimum ~102 kW at 03 h.
- Daily peaks fall from 211 kW (02-01) to 119 kW (02-13): the first week is the loaded one.
- Headroom: 227.7 kW = 57% of 400 kW (≈62% of 400 kVA at cos φ 0.92). Limit 80% = 320 kW → ~92 kW headroom; 90% = 360 kW.
  Only one transformer, so N-1 reserve = 0 (N-1 column equals nominal).
- Permitted power is 4.7× the transformer rating (1,877.5 kW vs 400 kW) but measured peak is 12% of permitted: real load, not permitted power, must drive the check.
- Σ of per-meter max (540.9 kW over 145 meters) is 2.4× the simultaneous substation peak: meters peak at different times (diversity ≈ 0.42).
  76 of 221 points (34%) have no load data, so a feeder-level load needs scaling or the permitted-power-with-coefficient method.
- Voltage: of 145 meters, 89 ≥ 217 V, 7 in 207–216 V, 1 in 187–206 V (205 V), 2 in 100–186 V (160, 184 V), 27 below 100 V and 19 at 0 V.
  Real quality violations (< 207 V, excluding the artefacts below) are rare: 3 meters. Limit used is 207 V (230 V −10%, LST EN 50160).

## Data-quality flags (do not trust blindly)
1. **27 meters with 66–81 V min voltage, 25 on L-200, 26 of 27 dated 2026-02-04** → a single event (outage/restoration or reading artefact), not a quality problem.
   Filter or flag events when computing voltage compliance.
2. **19 meters at exactly 0.0 V**, 17 of them on L-204 → meters off/no supply during the window, or phase L1 absent. Treat as missing, not as a violation.
3. Min voltage is for one phase only (OBIS 32.24.0 = L1); a three-phase check needs L2/L3 which are not provided.
4. 3 accounting points have meter serial `NULL` (and phase count `NULL`).
5. Load data covers 145 of 219 serial numbers (66%); 76 points unmetered in the window.
6. Feeder name mismatch between systems: `Objects` uses `L-KS14330`, TS history uses `L-MT12-608` for the 10 kV cable line and `L-12-608`; and "L-200" appears under pole `206/2` in one TS text ("L-206"). Normalise names via the `feeder_04kv_ata_id`.
7. The TS history 22-26356 says the transformer was swapped to 400 kVA; the substation record shows 400 kW nominal, commissioned 2014 → the record reflects the post-swap state.
8. Data is a snapshot from 2026-02 while the TS history spans 2020–2025 requests: the network state at the time of each historical TS is not reproduced.

## TS history (14 cases on this substation) – what the engineers did
Source: `ts_history_redacted.csv` (customer identifiers removed). Process: 11 "existing user, permitted-power increase", 3 new user.

| Step on the upgrade ladder | Cases | Typical TS §4 text |
|----------------------------|------:|--------------------|
| 1. Breaker change in existing KS/KAS | 9 (21-62367, 25-78962, 23-93436*, 22-35508, 20-80254, 20-67807, 22-77660, 22-83797, 24-88201) | "Esamoje komercinės apskaitos spintoje KS-xxxxx iš transformatorinės 12-608 pakeisti esamą automatinį jungiklį į trifazį „C" charakteristikos NN A" |
| 2. Fuse change (feeder / cabinet) + breaker | 1 (23-31728, 22 kW) | feeder fuse → 315 A; cabinet fuses 125–250 A or replaced by a link (trumpiklis); then breaker 40 A |
| 3. New KAS / KS cut-in cable | 3 (21-64496, 21-26840, 23-44040) | new KAS on pole with 20 A (or 1F 16 A) breaker + 16 mm² cable; or KS/KAS cut into cable line with ≥150 mm² cable + fuse/switch block |
| 5. Transformer swap | 1 (22-26356) | transformer → 400 kVA, 0.4 kV fuses 630 A, 10 kV fuses 50 A; then breaker 25 A |
(* automatically cancelled application.) 4. "Feeder reinforcement" and 6. "new TP" do not occur in this history.
Roughly **64% (9/14) of cases are pure level-1** (breaker change); with step 2 it is 71%.

Sanity check of the breaker table against these 14 cases (total permitted power → breaker):
11 kW → 20 A ✓ (×4), 14 kW → 25 A ✓ (×6), 22 kW → 40 A ✓ (×2), 3 kW 1F → 16 A ✓ (×1) = 13 of 14 match. The exception: 18 kW → **25 A in the TS but 32 A in the table**
(24-88201: it also cites KS-14347 while the network column says KS-39685 → probably a typo or a different rule; flag).

## How this feeds the demo
- The topology is real: the demo request is a synthetic application at coordinates on this substation. Step: nearest accounting point/pole → feeder → run checks.
- Checks supported by the data: breaker lookup (permitted power), transformer loading from the 15-min series (peak 227.7 kW vs 320/360 kW), feeder load from meter data
  (partial) or from permitted power × diversity, voltage from the min-voltage per meter (with event filtering).
- Checks that need data not provided: line impedance/voltage drop (no conductor type/length), short-circuit current, fuse ratings.
  Fill these with explicit `synthetic` or `inferred` values and tag them.
- The 14 TS cases are a backtest set for the logic: feed the request fields (existing/new, power, network path) and compare the predicted ladder step and breaker size
  with the issued TS text.
