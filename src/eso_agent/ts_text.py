"""Closed-set TS §3 action blocks. LLM may rephrase; numbers stay from tools."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def section3_blocks(solution: dict[str, Any], breaker: dict[str, Any], location: dict[str, Any]) -> list[str]:
    sid = solution["id"]
    amps = breaker["amps"]
    phases = breaker["phases"]
    phase_word = "trifaziu" if phases == 3 else "vienfaziu"
    loc = location.get("outputs") or location
    feeder_val = loc.get("feeder")
    feeder = feeder_val if isinstance(feeder_val, str) else (feeder_val or {}).get("name") or loc.get("feeder_record", {}).get("name")
    el = loc.get("element") or {"id": loc.get("element_id", "")}
    tp = "12-608"

    if sid == "A":
        return [
            (
                f"3.1. Esamoje komercinės apskaitos spintoje {el['id']} iš transformatorinės {tp} "
                f"pakeisti esamą automatinį jungiklį į {phase_word} „C“ charakteristikos {amps} A "
                f"automatinį jungiklį."
            ),
            "3.2. Elektros grandinėje atlikti trumpųjų jungimų skaičiavimus ir parinkti apsaugas pagal selektyvumą.",
        ]
    if sid == "B":
        return [
            (
                f"3.1. Ant esamos 0,4 kV oro linijos {feeder} iš transformatorinės {tp} "
                f"atramos Nr. {el['id']} įrengti komercinės apskaitos spintą (KAS) su "
                f"{phase_word} „C“ charakteristikos {amps} A automatiniu jungikliu ir elektros "
                f"energijos apskaitos skaitikliu."
            ),
            "3.2. KAS prijungti nuo esamos oro linijos laidų įrengiant 16 mm² skerspjūvio kabelių liniją.",
            "3.3. Elektros grandinėje atlikti trumpųjų jungimų skaičiavimus ir parinkti apsaugas pagal selektyvumą.",
        ]
    # C
    return [
        (
            "3.1. Laisvai klientui ir Bendrovei prieinamoje vietoje, išorinėje sklypo ribos pusėje "
            f"(sklypų sandūroje) įrengti komercinės apskaitos spintą su tranzitine dalimi (toliau — KS/KAS) "
            f"su {phase_word} „C“ charakteristikos {amps} A automatiniu jungikliu ir elektros energijos "
            f"apskaitos skaitikliu."
        ),
        (
            f"3.2. KS/KAS prijungimui įsipjauti į esamą kabelinę liniją „{feeder}“, prijungtą nuo "
            f"transformatorinės {tp}. Iki įsipjovimo vietos įrengti žemos įtampos ne mažesnio kaip "
            f"150 mm² skerspjūvio kabelių liniją."
        ),
        (
            "3.3. KS/KAS ant nueinančios kabelinės linijos įrengti saugiklių/kirtiklių bloką su "
            "reikiamo dydžio saugikliais arba trumpikliais."
        ),
        (
            "3.4. Įvertinant esamų klientų ir naujo kliento leistinąją galią 0,4 kV elektros grandinėje "
            "perskaičiuoti esamus komutavimo ir apsaugos aparatus ir esant būtinybei numatyti jų pakeitimą."
        ),
        "3.5. Elektros grandinėje atlikti trumpųjų jungimų skaičiavimus ir parinkti apsaugas pagal selektyvumą.",
    ]


def ownership_boundary(solution_id: str) -> str:
    if solution_id == "B":
        return (
            "Nuosavybės ir turto eksploatavimo riba nustatoma: ant kabelio (įvado), pakloto iš "
            "komercinės apskaitos spintos (KAS) į savininko objekto vidaus elektros tinklą, "
            "prijungimo gnybtų."
        )
    return (
        "Nuosavybės ir turto eksploatavimo riba nustatoma: ant kabelio (įvado), pakloto iš "
        "komercinės apskaitos spintoje su tranzitine dalimi (KS/KAS) į savininko objekto vidaus "
        "elektros tinklą, prijungimo gnybtų."
    )


def issue_dates(today: date | None = None) -> tuple[str, str]:
    today = today or date.today()
    return today.isoformat(), (today + timedelta(days=365)).isoformat()
