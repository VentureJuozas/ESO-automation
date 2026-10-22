"""Line load check from the ESO calculator "Skaičiuoklė nuo 2018 m." / "iki 2018 m.".

Segments are given from the transformer outward. For each segment the calculator
sums the houses and the permitted power from that segment to the end of the line,
looks up a diversity coefficient by the house count, then:

    Psk  = cumulative permitted power x diversity coefficient
    Imax = cumulative permitted power / 0.624
    Isk  = Psk / 0.624
    dU   = (length_km) x Psk x voltage-drop factor of the conductor

The short-circuit current at a segment is 230 V divided by the transformer impedance
plus the impedance of every segment up to and including it. A segment of length 0
is reported as 0 A, as the sheet does.

"new" uses the coefficients in rows 63-662 of "Skaičiuoklė nuo 2018 m.".
"old" uses the same rows of "Skaičiuoklė iki 2018 m.".
"""
import json
from pathlib import Path

_TABLES = json.loads((Path(__file__).with_name("line_load_tables.json")).read_text(encoding="utf-8"))
VOLTAGE_DROP = _TABLES["voltage_drop_per_km"]
IMPEDANCE = _TABLES["impedance_ohm_per_km"]
TRANSFORMER = {str(k): v for k, v in _TABLES["transformer_ohm"].items()}
DIVERSITY = {"new": _TABLES["diversity_new"], "old": _TABLES["diversity_old"]}
AMPERE_DIVISOR = _TABLES["ampere_divisor"]


def diversity(houses, method="new"):
    if isinstance(houses, float) and not houses.is_integer():
        raise ValueError(f"house count must be a whole number, got {houses}")
    houses = int(houses)
    if houses < 1 or houses > len(DIVERSITY[method]):
        return 0.0
    return DIVERSITY[method][houses - 1]


def evaluate(segments, transformer_kva, method="new"):
    """segments: list of dicts with conductor, length_m, permitted_kw, houses.
    Ordered from the transformer toward the end of the line.
    transformer_kva: 63, or a text key such as "63(Y/Z)".
    """
    if method not in DIVERSITY:
        raise ValueError(method)
    key = str(transformer_kva)
    if key not in TRANSFORMER:
        raise ValueError(f"no transformer impedance for {transformer_kva!r}")
    n = len(segments)
    houses_cum = [0] * n
    power_cum = [0.0] * n
    for i in range(n - 1, -1, -1):
        houses_cum[i] = int(segments[i]["houses"]) + (houses_cum[i + 1] if i + 1 < n else 0)
        power_cum[i] = float(segments[i]["permitted_kw"]) + (power_cum[i + 1] if i + 1 < n else 0)

    rows = []
    impedance = 0.0
    for i, seg in enumerate(segments):
        conductor = seg["conductor"]
        if conductor not in VOLTAGE_DROP:
            raise ValueError(f"unknown conductor {conductor!r}")
        length_m = float(seg["length_m"])
        coef = diversity(houses_cum[i], method)
        psk = power_cum[i] * coef
        impedance += IMPEDANCE[conductor] * length_m / 1000
        rows.append({
            "conductor": conductor,
            "length_m": length_m,
            "houses_total": houses_cum[i],
            "diversity": coef,
            "permitted_kw_total": power_cum[i],
            "psk_kw": psk,
            "imax_a": power_cum[i] / AMPERE_DIVISOR,
            "isk_a": psk / AMPERE_DIVISOR,
            "voltage_drop": (length_m / 1000) * psk * VOLTAGE_DROP[conductor],
            "short_circuit_a": (230 / (TRANSFORMER[key] + impedance)) if length_m else 0.0,
        })
    return {
        "segments": rows,
        "length_m": sum(r["length_m"] for r in rows),
        "permitted_kw": rows[0]["permitted_kw_total"] if rows else 0.0,
        "psk_kw": rows[0]["psk_kw"] if rows else 0.0,
        "imax_a": rows[0]["imax_a"] if rows else 0.0,
        "isk_a": rows[0]["isk_a"] if rows else 0.0,
        "voltage_drop_pct": sum(r["voltage_drop"] for r in rows),
    }
