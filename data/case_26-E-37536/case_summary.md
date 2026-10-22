# Case TS 26-E-37536 (new 11 kW 3F connection on overhead LV line L-300) – customer data redacted

Sources in `Techninės sąlygos\26-E-37536\`: final TS PDF (issued 2026-10-21), "Manual" draft TS PDF (2026-10-21 09:34),
the combined calculator `Apjungta elektros tinklų skaičiuoklė_26-E-37536_L-300.xlsm`, GIS annex image, and a TS-correction
notification e-mail (.msg). Personal data (customer, address, contacts, ESO staff names) is NOT stored here.

## 1. Request and decision
| Field | Value |
|-------|-------|
| Application type | New consumption connection, "Sodyba" (homestead), Kaišiadorių r. sav. |
| Power | New 11 kW = total 11 kW, 3-phase, 1 meter, standard cabinet colour |
| Network | Existing 0.4 kV overhead line **L-300**, supplied from TP **Rg-202** (63 kVA); pole **300/1** (head of the line, ~5 m from the TP) |
| Investment project | E1N2618978O |
| Issued | 2026-10-21, valid until 2027-10-21 |

**Section 3 as issued (ESO actions) – a level-1-like case:**
- 3.1 "Ant esamos žemos įtampos oro linijos L-300, prijungtos nuo transformatorinės Rg-202 atramos Nr. 300/1 įrengti vienos
  vietos komercinę(-es) apskaitos spintą (KAS) su trifaziu „C" charakteristikos **20 A** automatiniu jungikliu ir elektros
  energijos apskaitos skaitikliu."
- 3.2 "KAS prijungti nuo esamos oro linijos laidų įrengiant **16 mm²** skerspjūvio kabelių liniją."
That is the whole engineering content (2 items). Breaker 20 A = the breaker table for 11 kW 3-phase (see §4).

## 2. Draft vs issued
The "Manual" PDF is the engineer's draft with a watermark "PROJEKTAS. SUTARTIS NEPATVIRTINTA": same Section 3 text, but
"Parengta:" is empty and "Galioja iki" still shows a stale date (2027-10-19). The issued version fills "Parengta 2026-10-21"
and "Galioja iki 2027-10-21". The Annex 4 page carries the same watermark in the draft.
=> A generator should output a draft state first (no issue date, watermark) and stamp dates on approval.

## 3. Correction-request e-mail (.msg, 2026-10-20)
Automated notice "Užregistruota nauja TS korekcija" for the same investment project, reason "Trečiosios šalys"
(third parties), comment: "ar būtų galimybė įrengti klientui apskaitą ant 300/1 atramos?" ("could we install the customer's
metering on pole 300/1?"). The issued TS places the KAS exactly on 300/1. This shows the engineer feedback loop: a
correction request, then a re-issued TS. The dashboard's "engineer edits / requests correction" step maps to this.

## 4. Calculator (`Apjungta ...xlsm`) – sheets and what the case used
| Sheet | Purpose | Used in this case |
|-------|---------|-------------------|
| `Skaičiuoklė nuo 2018 m.` | Overhead/cable LV line check: power and voltage drop along a feeder chain, diversity (nesutapimo) coefficients | **Yes** (new method) |
| `Skaičiuoklė iki 2018 m.` | Same with the older coefficient set; also computes voltage before/after | **Yes** (old method, for comparison) |
| `Trafo apkrovimo skaičiuoklė` | Transformer + 0.4 kV protection + lines check, T-1 and T-2 | Template only (inputs empty) |
| `Smart trafo skaičiuoklė` | SMART-load based transformer check | Only transformer set to 63 kVA with 100 A on the 0.4 kV side; load inputs empty (errors #DIV/0! in the empty template cells) |
| `Srovės transf. įvertinimas` | kW → breaker size and current-transformer table (3F and 1F), plus 10 kV CT check | Breaker for 11 kW (20 A) |
| hidden: `Kofai`, `Sąrašai`, `KL duom`, `OL duom`, `Trafai` (+ "(2)" copies) | Diversity coefficient tables, lists, cable/OL impedance data, transformer list | – |

### Line chain entered for L-300 (sheet "nuo 2018")
Header: transformer Rg-202, 63 kVA, line L-300. Pending requests tagged: "26-E-37536(11); 26-E-14495(8,2)" (11 kW and an
earlier 8.2 kW request counted together).

| Pole / node | 300/1 | 300/4 | 300/7 | 300/8 | 300/9 | 304/4 | 304/17 | 304/24 | 304/30 | 304/34 |
|---|---|---|---|---|---|---|---|---|---|---|
| Conductor | 3x35+50 | 4A-50 | 4A-50 | 4A-50 | 4A-50 | 4A-50 | 4A-25 | 4A-25 | 4A-25 | 2A-25 |
| Length, m | 5 | 120 | 134 | 43 | 37 | 172 | 559 | 305 | 257 | 150 |
| Permitted power added, kW | 0 | 61.6 | 5 | 7 | 20 | 2.8 | 3 | 2.8 | 2.8 | 2.8 |
| Houses | 0 | 11 | 1 | 1 | 7 | 1 | 1 | 1 | 1 | 1 |
| Cumulative houses | 25 | 25 | 14 | 13 | 12 | 5 | 4 | 3 | 2 | 1 |
| Diversity coeff. (new) | 0.464 | 0.464 | 0.632 | 0.657 | 0.681 | 0.947 | 0.973 | 1 | 1 | 1 |
| Cumulative P, kW | 107.8 | 107.8 | 46.2 | 41.2 | 34.2 | 14.2 | 11.4 | 8.4 | 5.6 | 2.8 |
| Psk, kW | 50.05 | 50.05 | 29.21 | 27.05 | 23.29 | 13.44 | 11.10 | 8.40 | 5.60 | 2.80 |
| Imax, A | 172.8 | 172.8 | 74.0 | 66.0 | 54.8 | 22.8 | 18.3 | 13.5 | 9.0 | 4.5 |
| Isk, A | 80.2 | 80.2 | 46.8 | 43.4 | 37.3 | 21.5 | 17.8 | 13.5 | 9.0 | 4.5 |

Relations visible in the data: Imax ≈ cumulative P / 0.624 (kW→A at 0.4 kV, close to √3·0.4·0.9); Psk = diversity coeff. × cumulative P;
Isk = diversity coeff. × Imax (0.4643 × 172.8 = 80.2 A). Formula cells themselves were not decoded (only cached values read).
Line selection helper "Linijinis-50" / "50//63" = the line-protection size selected (50 A fuse, in the old sheet written "50//63").

### Result block ("REZULTATAI")
| Metric | nuo 2018 (new coefficients) | iki 2018 (old coefficients) |
|--------|----------------------------|------------------------------|
| Line length, m | 1,782 | 1,782 |
| Permitted power on line, kW | 107.8 | 110.8 |
| Calculated power Psk, kW | 50.05 | 33.95 |
| Max current, A | 172.8 | 177.6 |
| Calculated current Isk, A | 80.2 | 54.4 |
| Total voltage loss, % | 19.11 | 15.88 |
| Voltage drop change due to the new connection, percentage points | −0.0006 | +0.0044 |
| Voltage before / after the connection, V | – | 234.45 / 234.44 |

Short-circuit currents along the 10 nodes: 416, 317, 250, 235, 222, 179, 83, 64, 54, 49 A (point 1 = at pole 300/1).

**Reading of the decision:** the new 11 kW is at the very head of the line (5 m from the TP), so it barely changes the
voltage at downstream customers (0.004 pp). The absolute voltage loss on this long line is already high (15.9–19.1%),
which the calculator does not block; the check is the *incremental* effect plus the new current staying inside the
line protection. The acceptance limit for the absolute drop is not in the file – ask an engineer.

## 5. Differences between the two TS templates seen so far (26-E-37934 vs 26-E-37536)
| Item | 26-E-37934 (new KS at TP, 22 kW) | 26-E-37536 (KAS on pole, 11 kW) |
|------|----------------------------------|----------------------------------|
| §1 ownership boundary | "...komercinės apskaitos spintoje su tranzitine dalimi (KS/KAS)..." | "...komercinės apskaitos spintos (KAS)..." |
| §2 count | 13 items | 12 items |
| 2.3 | LST EN 50160 supply quality | First-time connection: monthly cost of ESO's unused infrastructure until contractor's act is submitted |
| 2.4 / 2.5 | New application ... / design procedure | Design procedure / new application (order swapped) |
| 2.13 | Monthly power-component invoices if no supply contract in 30 wd (first connection) | absent |
| Meter installation clause | 2.8 | 2.6 |
| Rangovo aktų link | `.../rangovu-aktu-pateikimas/1` | `.../rangovu-aktu-pateikimas` |
So the fixed part of the TS is **not one template**: it varies by case type/version. The generator needs a small catalogue
of §1/§2 variants selected by connection type (new vs existing, cabinet type, first-time connection, generation).
