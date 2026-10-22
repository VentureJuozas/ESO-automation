# Test: new KAS on substation 12-608

One case. A new household customer, 11 kW, three-phase, asks to connect on substation 12-608. The solution under test is a new commercial metering cabinet (KAS) on the nearest overhead pole, not a breaker change in an existing cabinet and not a cut into a cable.

Open `demo/dashboard.html`. Under **Paraiškos**, select **Naujas vartotojas, TP 12-608**. Leave **Testavimas** closed for this run. Those three items (line reinforcement, transformer change, generation and storage) must stay **Neveikia**.

## The request

| Field | Value | Where it comes from |
| --- | --- | --- |
| Power | 11 kW | Synthetic request |
| Phases | 3 | Synthetic request |
| Type | Household | Synthetic request |
| Coordinates | 54,55929, 25,27955 | Synthetic, about 52 m north of the station |
| Customer name, address, meter | None | Must not appear |

The run is **Paleisti eigą**, then **Paleisti nuo čia** after each value you type. It walks forward and stops at the first empty input. An empty reserved-power field is 0 kW and must not stop the run.

Type these three things, and nothing else:

1. Feeder fuse, any amperage, for example `160`. The file has no feeder rating, so the number is recorded and not compared.
2. Conductor and segment lengths, any non-empty text, for example `4A-50` and `17`. The voltage drop stays uncalculated.
3. Free place in the existing cabinet: **ne, statyti naują šalia**.

## Steps and what must be true

### 1. Paraiška

Inner steps: Paraiška gauta, Tinkamumas, Poreikis. None of these stop the run.

| Check | Expected |
| --- | --- |
| Paraiška gauta | 11 kW, three phases, household, coordinates 54,55929, 25,27955. Result: accepted into this sequence. |
| Tinkamumas | Documents and the preparation fee are not in the files. The demo treats the application as properly submitted so the run can pass. |
| Poreikis | Permitted power 11 kW, 3 phases. Rule: up to 250 kW is issued in 3 working days. Result: 3 working days. |

### 2. Taškas

| Check | Expected |
| --- | --- |
| Nearest element | Overhead line L-200, pole 200/3 |
| Distance | 17 m from the request, 52 m from the substation |
| Feeder size | 47 points |
| What must not appear | A street name, a cabinet name, a customer identifier |
| Map | **Žemėlapis** opens `demo/topology_map.html` |

This is an overhead feeder, so the later solution is a pole KAS, not a cable cut-in.

### 3. Patikros

Four checks. The run stops twice inside this node, then passes the last two on its own.

**Pajėgumas.** Stops until the fuse is typed.

| Check | Expected | Tag |
| --- | --- | --- |
| Breaker | Three-phase C 20 A, from the kW table (3-phase, up to 11 kW) | Rule |
| Transformer | 227,7 + 11 = 238,7 kW | Measured peak 227,7 kW on 2026-02-06 19:15 UTC, plus this request |
| Share of nominal | 60 % of 400 kW | Measured |
| Limit | 80 % is 320 kW, and 238,7 is under it | Rule on the substation file |
| Feeder | The typed fuse is shown. No feeder verdict, because the file has no feeder rating | Gap, not a failure |

**Kokybė.** Stops until both the conductor and the segment lengths are typed.

| Check | Expected |
| --- | --- |
| Measured voltage | 25 meters on L-200. After the 2026-02-04 event and the 0 V readings are set aside, no trustworthy minimum remains. Do not invent a voltage. |
| Voltage drop | Stays uncalculated after the two fields are filled. The line calculator is not connected on this screen. |
| Run | Continues. An uncalculated drop is not a failed check. |

**Patikimumas.** Does not stop.

| Check | Expected |
| --- | --- |
| Transformer | One unit, 400 kW. N-1 reserve equals the nominal. There is no spare. |
| Feeder | L-200 is radial overhead. No backup path is lost. |
| This solution | A new cabinet on the pole does not disconnect neighbours. A cable cut-in does not apply on L-200. |

**Ateitis.** Does not stop. Leave reserved applications empty.

| Check | Expected |
| --- | --- |
| Reserved | 0 kW |
| Headroom | 320 − 238,7 = 81,3 kW left after this connection |

### 4. Sprendinys

Stops until the free-place field is set. For this test choose **ne, statyti naują šalia**.

| Check | Expected |
| --- | --- |
| Place | New KAS at pole 200/3 on L-200 |
| Breaker | Three-phase C 20 A |
| Cable | 16 mm² from the existing overhead conductors to the cabinet |
| Wording | Ant esamos 0,4 kV oro linijos L-200 iš transformatorinės 12-608 atramos Nr. 200/3 įrengti komercinės apskaitos spintą (KAS) su trifaziu „C“ charakteristikos 20 A automatiniu jungikliu. KAS prijungti nuo esamos oro linijos laidų įrengiant 16 mm² skerspjūvio kabelių liniją. |

Choosing **taip, jungti į esamą** is a different case. It must not be the result of this test.

### 5. Išdavimas

Inner steps: Juodraštis, Patvirtinimas, Išdavimas.

The draft appears once the run has passed Sprendinys. **Patvirtinti** is enabled only then. Until it is pressed, Patvirtinimas stays waiting and no issue date is shown. After it is pressed, all five nodes read **Atlikta**.

| Check | Expected |
| --- | --- |
| Draft text | The §3 sentence in the table above |
| Capacity line | Breaker 20 A, transformer 238,7 kW out of 320 kW |
| Quality line | No trustworthy L-200 voltage. Drop entered, not calculated |
| Reliability line | One transformer, radial overhead line |
| Future line | Reserved 0 kW, headroom 81,3 kW, new KAS at pole 200/3 |
| Issued | Parengta 2026-10-22. Galioja iki 2027-10-22 |

## Cost

Reference prices from case 26-E-37934. Labelled as an orientyras. Labour is 11,78 % of the priced lines only. VAT is 21 %. The 16 mm² cable has no price in that case, so it is excluded from the labour base.

| Line | Amount, EUR |
| --- | --- |
| Jungiklis 3F C 20 A | 64,79 |
| KS/KAS spinta | 1 533,79 |
| Kabelis 16 mm² | kaina nenurodyta |
| Kapitalizuotas darbas 11,78 % | 188,31 |
| Iš viso be PVM | 1 786,89 |
| Iš viso su PVM 21 % | 2 162,14 |

Design cost from the cable cut-in case is not added. A pole KAS does not use the 4×150 mm² cable price.

## Pass

The test passes when every row above matches, the run stopped only at the fuse, the conductor and lengths, the free-place choice, and the approval, and the three **Testavimas** items were never executed.

It does not pass if a street or a customer identifier appears, if a voltage or a voltage drop is invented, if the feeder fuse is treated as a pass or a fail, if reserved power of 0 kW blocks the run, or if the draft describes a breaker change in an existing cabinet.
