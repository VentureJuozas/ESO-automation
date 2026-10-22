# Demo scope: new customer connects to substation 12-608

Fixed on 2026-10-22. Everything else in `KNOWLEDGE.md` is context.

## The case we run
A **new customer** (new accounting point, household-type load, 1F or 3F, requested kW) asks for a connection on substation 12-608.
Evaluated on the **0.4 kV network and the 0.4/10 kV station only**. The solution is one of three:

| ID | Solution | When it applies (hypothesis, confirm with an engineer) | TS §3 content | Seen in TS history |
|----|----------|--------------------------------------------------------|---------------|--------------------|
| A | **Connect to an existing cabinet** (KS/KAS): set or change the breaker in it | A cabinet already stands at the plot or serves the object | "in existing KS-x change the breaker to 3F C NN A" | 24-88201 |
| B | **New KAS on a pole** of an overhead line | Nearest supply element is an overhead feeder (L-200, L-204, L-300) or a pole of L-KS13058 | KAS with C breaker on pole N/M + 16 mm² cable from the line wires | 21-26840 (1F 16 A) (analogue: 21-64496) |
| C | **New KS/KAS cut into a cable line** | Nearest supply element is a cable feeder (L-KS14330, L-KS39685, L-KS13058) | KS/KAS at the plot boundary, cut-in into the cable line, ≥150 mm² cable to the cut-in, fuse/switch block, re-check of downstream protection | 23-44040 |

Out of scope: transformer swap (ladder rung 5), new transformer station or 10 kV works (rung 6), everything above 0.4/10 kV, generation/storage,
existing-customer power increases, voltage-drop methods beyond what the data allows. Feeder reinforcement (rung 4) is not built: if a check fails
at feeder level the run stops with a reason and a "needs engineer / next level" status.

## The four checks, grounded
Every number carries a tag: `real` (from the 12-608 files), `rule` (from ESO text or the calculator), `inferred`, `synthetic`.

### 1. Capacity (pajėgumas) – can the network deliver the power?
| Step | Computation | Data | Tag |
|------|-------------|------|-----|
| 1a | Breaker from requested kW (3F: ≤11→20 A, ≤14→25 A, ≤18→32 A, ≤22→40 A ...; 1F: 3 kW→16 A, 7 kW→40 A) | table in KNOWLEDGE §15 | rule |
| 1b | Cabinet / cut-in fuse ≥ new breaker; downstream fuses after the cut-in still selective | not provided | synthetic (per feeder default) |
| 1c | Feeder load after connection = existing load + new kW × diversity factor, against feeder rating | existing load: Σ per-meter max (partial, 66% metered) or permitted power × diversity; rating missing | real + inferred + synthetic |
| 1d | Transformer: measured peak (227.7 kW) + new kW vs 80% = 320 kW and 90% = 360 kW | `pastotes_load_kas15min.csv`, `Substations_info.csv` | real |

### 2. Quality (kokybė) – will the voltage stay within LST EN 50160?
| Step | Computation | Data | Tag |
|------|-------------|------|-----|
| 2a | Baseline: minimum voltage of meters on the same feeder (≥207 V = 230 V −10%), after dropping artefacts (0 V, 66–81 V on 2026-02-04) | `min_itampa.csv` | real |
| 2b | Voltage-drop change from the new load on the path transformer → connection point | needs conductor type and length per segment; lengths from coordinates | inferred / synthetic |
| 2c | Rule limits on new cable lines: ≤600 m, ≤80 kW single radial, 3-phase only | standard annex 12 snippets (non-authoritative) | rule (unverified) |

### 3. Reliability (patikimumas) – does it worsen modes, backup, N-1?
| Step | Computation | Data | Tag |
|------|-------------|------|-----|
| 3a | N-1: one transformer, so reserve = nominal (no spare); the connection must not make this worse | `nominal_power_n_1_kW` = 400, `transformer_count` = 1 | real |
| 3b | Radial feeder: no backup path exists in the data, so no backup is lost | topology has no ring links | inferred |
| 3c | Option C only: the cut-in needs a planned interruption of existing customers on that cable line (count them from `Objects_network_power.csv` by feeder) | feeder membership | real |

### 4. Future (ateitis) – does it fit expansion and growth?
| Step | Computation | Data | Tag |
|------|-------------|------|-----|
| 4a | Reserved / pending capacity on the feeder and transformer (other open applications) | not provided; the calculator counts pending requests, e.g. "26-E-14495(8,2)" | synthetic input, default 0 kW |
| 4b | Growth margin: headroom to 80% after the new load, and the share left for later requests | transformer series | real + rule |
| 4c | Territory plans | not provided | out of data, show "no information" |

## Flow
1. Request: coordinates, kW, phases, type (household).
2. Locate: nearest feeder / pole / cabinet by coordinates (`Objects_network_power.csv`), feeder type (overhead or cable), existing cabinet at the plot.
3. Select solution A, B or C (rule above), then derive breaker and cable size.
4. Run checks 1–4. Pass → draft TS §3 + GIS-style map + cost lines. Fail → stop with the reason and the failed check; hand over to an engineer.
5. Engineer approves or edits (draft state, then issue date and validity one year).

## Open questions (need a decision before building)
1. How to decide A vs B vs C when several are possible: only feeder type and distance, or also a cabinet-has-free-slot flag? (Not in the data.)
2. Which defaults to use for the missing data: fuse per feeder, conductor type and length, rating. The TS history gives only one hard number: feeder L-KS14330 fuse changed to 315 A in case 23-31728.
3. Household thresholds for transformer loading: 80% / 90% from the substation file (320 / 360 kW), or the 0.8 / 1.0 from the earlier planning chat?
4. Pending/reserved capacity: stay at 0 or synthesize a few open applications to show check 4?
