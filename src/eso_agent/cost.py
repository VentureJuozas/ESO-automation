"""Cost lines from the 26-E-37934 expert calculator (orientyras)."""
from __future__ import annotations

from typing import Any

from eso_agent.rules import (
    CAPITALISED_LABOUR_RATE,
    COST_BREAKER_3F_INSTALL,
    COST_CABLE_4X150_PER_M,
    COST_DESIGN,
    COST_KS_KAS,
    COST_TERMINATION_4X150,
    VAT_RATE,
)


def estimate_cost(solution_id: str, cable_m: float | None) -> dict[str, Any]:
    lines: list[dict[str, Any]] = []
    lines.append(
        {
            "id": "68",
            "item": "Trifazio automatinio jungiklio įrengimas (orientyras 40 A įkainis)",
            "unit": "vnt.",
            "qty": 1,
            "price": COST_BREAKER_3F_INSTALL,
            "source": "real",
            "note": "26-E-37934, ID 68 = 64,79 EUR. Naudojama ir 20 A atvejui kaip orientyras.",
        }
    )
    if solution_id == "B":
        lines.append(
            {
                "id": "117",
                "item": "KS/KAS spinta (viena vieta)",
                "unit": "vnt.",
                "qty": 1,
                "price": COST_KS_KAS,
                "source": "real",
                "note": "26-E-37934, ID 117 = 1 533,79 EUR / vnt.",
            }
        )
        lines.append(
            {
                "id": "16mm2",
                "item": "Kabelis 16 mm² nuo oro linijos laidų",
                "unit": "m",
                "qty": round(cable_m or 17.0, 1),
                "price": None,
                "source": "synthetic",
                "note": "16 mm² kainos 26-E-37934 byloje nėra — į darbo bazę neįtraukiama.",
            }
        )
    elif solution_id == "C":
        length = max(20.0, float(cable_m or 40.0))
        lines.append(
            {
                "id": "117",
                "item": "KS/KAS – kirtiklių-saugiklių blokas (2 vnt.)",
                "unit": "vnt.",
                "qty": 2,
                "price": COST_KS_KAS * 2,
                "source": "real",
                "note": "26-E-37934: 2 × 1 533,79 EUR.",
            }
        )
        lines.append(
            {
                "id": "254",
                "item": "Aliuminiai 0,4 kV kabeliai (KL) 4x150 mm²",
                "unit": "m",
                "qty": round(length, 1),
                "price": round(length * COST_CABLE_4X150_PER_M, 2),
                "source": "real",
                "note": f"52,50 EUR/m × {length:.0f} m (įkainis iš 26-E-37934).",
            }
        )
        lines.append(
            {
                "id": "260",
                "item": "Aliuminiai 0,4 kV kabelių galinės movos 4x150 mm²",
                "unit": "kompl.",
                "qty": 4,
                "price": round(COST_TERMINATION_4X150 * 4, 2),
                "source": "real",
                "note": "4 × 188,98 EUR.",
            }
        )
        lines.append(
            {
                "id": "294",
                "item": "Projektavimas iki 35 000 EUR be PVM (su topografine nuotrauka)",
                "unit": "projekt.",
                "qty": 1,
                "price": COST_DESIGN,
                "source": "real",
                "note": "26-E-37934, ID 294.",
            }
        )

    materials = round(sum(x["price"] or 0 for x in lines), 2)
    labour = round(materials * CAPITALISED_LABOUR_RATE, 2)
    net = round(materials + labour, 2)
    gross = round(net * (1 + VAT_RATE), 2)
    lines.append(
        {
            "id": "labour",
            "item": "Kapitalizuotas darbas 11,78 %",
            "unit": "",
            "qty": 1,
            "price": labour,
            "source": "real",
            "note": "1 257,99 / 10 678,99 iš 26-E-37934.",
        }
    )
    return {
        "lines": lines,
        "materials": materials,
        "labour": labour,
        "net": net,
        "gross": gross,
        "vat_rate": VAT_RATE,
        "currency": "EUR",
        "source": "real",
        "note": "Orientyras iš 26-E-37934, ne oficiali šios paraiškos sąmata.",
    }
