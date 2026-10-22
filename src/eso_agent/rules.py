"""ESO connection rules used by the deterministic tools.

Breaker table and diversity coefficients come from the combined calculator
(KNOWLEDGE.md §15). Transformer 80%/90% limits come from Substations_info
for 12-608. Voltage limit 207 V is LST EN 50160 (230 V − 10%).
"""
from __future__ import annotations

from line_load import diversity as calculator_diversity

# 3-phase permitted power upper bound (kW) -> breaker A.
# Source: sheet "Srovės transf. įvertinimas", KNOWLEDGE.md §15. Tag: rule.
BREAKER_3F: list[tuple[float, int]] = [
    (5, 10),
    (7, 13),
    (9, 16),
    (11, 20),
    (14, 25),
    (18, 32),
    (22, 40),
    (28, 50),
    (35, 63),
    (45, 80),
    (60, 100),
    (76, 125),
    (97, 160),
    (121, 200),
    (152, 250),
    (182, 300),
    (195, 320),
    (243, 400),
    (304, 500),
    (365, 600),
    (487, 800),
]

# 1-phase kW -> A. Above 7 kW is outside the published 1F table.
BREAKER_1F: list[tuple[float, int]] = [
    (1, 6),
    (2, 10),
    (3, 16),
    (4, 20),
    (5, 25),
    (6, 32),
    (7, 40),
]

VOLTAGE_NOMINAL_V = 230.0
VOLTAGE_MIN_V = 207.0  # 230 − 10 %, LST EN 50160
TRANSFORMER_LIMIT_80_SHARE = 0.80
TRANSFORMER_LIMIT_90_SHARE = 0.90
NEW_CABLE_MAX_M = 600
NEW_RADIAL_CABLE_MAX_KW = 80
HOUSEHOLD_DEADLINE_KW = 250
HOUSEHOLD_DEADLINE_DAYS = 3
CABINET_AT_PLOT_M = 12.0
CAPITALISED_LABOUR_RATE = 0.1178  # 26-E-37934: 1,257.99 / 10,678.99
VAT_RATE = 0.21
MANUAL_TIME_ASSUMPTION_MINUTES = (120, 240)  # not ESO statistics
MANUAL_TIME_ASSUMPTION_NOTE = (
    "Prielaida demonstracijai: buitinį 0,4 kV prijungimą inžinierius paprastai "
    "parengia per 2–4 valandas. Tai nėra ESO statistika."
)

# Orientyras from cost_estimate_26-E-37934.md (Kauno r. sav. rates).
COST_BREAKER_3F_INSTALL = 64.79
COST_KS_KAS = 1533.785
COST_CABLE_4X150_PER_M = 52.504  # 4725.38 / 90
COST_TERMINATION_4X150 = 188.98
COST_DESIGN = 2065.34

OVERHEAD_FEEDERS = {"L-200", "L-204", "L-300"}
CABLE_FEEDERS = {"L-KS14330", "L-KS39685", "L-KS13058"}


def size_breaker(kw: float, phases: int) -> dict:
    """Return breaker amperage from the calculator table. Tag: rule."""
    if kw <= 0:
        raise ValueError("kw must be positive")
    if phases not in (1, 3):
        raise ValueError("phases must be 1 or 3")
    table = BREAKER_1F if phases == 1 else BREAKER_3F
    for bound, amps in table:
        if kw <= bound:
            return {
                "amps": amps,
                "phases": phases,
                "characteristic": "C",
                "label": f"{phases}F C {amps} A",
                "table_bound_kw": bound,
                "source": "rule",
                "note": "Srovės transf. įvertinimas, KNOWLEDGE.md §15",
            }
    if phases == 1:
        return {
            "amps": 40,
            "phases": 1,
            "characteristic": "C",
            "label": "1F C 40 A",
            "table_bound_kw": 7,
            "source": "rule",
            "note": "1F lentelė baigiasi ties 7 kW; 40 A yra viršutinė reikšmė, inžinieriui peržiūrėti.",
            "escalation": True,
        }
    return {
        "amps": 1000,
        "phases": 3,
        "characteristic": "C",
        "label": "3F C 1000 A",
        "table_bound_kw": None,
        "source": "rule",
        "note": "≥ 488 kW → 1000 A pagal lentelę.",
    }


def diversity_coefficient(houses: int, method: str = "new") -> float:
    """Nesutapimo coefficient from the calculator. Tag: rule."""
    houses = max(1, int(houses))
    return float(calculator_diversity(houses, method=method))


def select_solution(
    feeder_type: str,
    feeder_name: str,
    nearest_kind: str,
    distance_m: float,
    cabinet_at_plot: bool,
) -> dict:
    """A / B / C from SCOPE.md. Tag: rule (hypothesis, confirmed in TS history)."""
    if cabinet_at_plot or (
        nearest_kind in {"cabinet", "cable_cabinet", "kas"} and distance_m <= CABINET_AT_PLOT_M
    ):
        return {
            "id": "A",
            "title": "Jungti į esamą spintą",
            "reason": (
                f"Artimiausias elementas yra spinta ({distance_m:.0f} m), laikoma stovinti sklype. "
                "Keičiamas jungiklis esamoje KS/KAS."
            ),
            "source": "rule",
        }
    if feeder_type == "overhead" or (
        feeder_name == "L-KS13058" and nearest_kind == "pole"
    ):
        return {
            "id": "B",
            "title": "Nauja KAS ant atramos",
            "reason": (
                f"Artimiausias maitinimo elementas yra oro linija {feeder_name} "
                f"(atrama, {distance_m:.0f} m). Nauja KAS ant atramos + 16 mm² kabelis nuo laidų."
            ),
            "source": "rule",
        }
    return {
        "id": "C",
        "title": "Nauja KS/KAS įsipjovimu į kabelį",
        "reason": (
            f"Artimiausias maitinimo elementas yra kabelių linija {feeder_name} "
            f"({distance_m:.0f} m), sklype esamos spintos nėra. KS/KAS sklypo riboje, "
            "įsipjovimas į kabelį, ≥150 mm² iki įsipjovimo."
        ),
        "source": "rule",
    }


def cable_mm2_for_solution(solution_id: str) -> int | None:
    if solution_id == "B":
        return 16
    if solution_id == "C":
        return 150
    return None


def issuing_deadline_days(kw: float, customer_type: str = "household") -> dict:
    if customer_type == "household" and kw <= HOUSEHOLD_DEADLINE_KW:
        return {
            "days": HOUSEHOLD_DEADLINE_DAYS,
            "unit": "darbo dienos",
            "source": "rule",
            "note": "Vartotojai, LNG ≤ 250 kW → 3 darbo dienos (KNOWLEDGE.md §5).",
        }
    return {
        "days": 5,
        "unit": "darbo dienos",
        "source": "rule",
        "note": "Vartotojai, LNG > 250 kW → 5 darbo dienos.",
    }
