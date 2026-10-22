"""Preset demo scenarios. Hero is the default live-pitch path."""
from __future__ import annotations

from typing import Any

from eso_agent.network import HERO_LAT, HERO_LON, element_by_id, haversine_m

HERO_TEXT = (
    "Naujas buitinis vartotojas, 11 kW, trys fazės, koordinatės 54,55929, 25,27955, "
    "transformatorinė 12-608."
)


def _form(kw: float, phases: int, lat: float, lon: float, text: str, pending: float = 0.0, name: str = "") -> dict[str, Any]:
    return {
        "kw": kw,
        "phases": phases,
        "lat": lat,
        "lon": lon,
        "customer_type": "household",
        "pending_kw": pending,
        "text": text,
        "object_name": name or "Naujas buitinis objektas",
    }


def all_scenarios() -> list[dict[str, Any]]:
    cab = element_by_id("KS-39685")
    ks = element_by_id("KS-14336")
    # Offset ~40 m from cabinet so A does not trigger; cable feeder → C.
    c_lat = ks["lat"] + 0.00036  # ~40 m north
    c_lon = ks["lon"] + 0.00012
    fail_lat, fail_lon = HERO_LAT, HERO_LON
    return [
        {
            "id": "hero",
            "code": "B",
            "title": "Hero · nauja KAS ant atramos",
            "subtitle": "11 kW, 3F, L-200, atrama 200/3",
            "pitch": True,
            "expected_solution": "B",
            "expected_escalate": False,
            "form": _form(11, 3, HERO_LAT, HERO_LON, HERO_TEXT, name="Sodyba (demonstracija)"),
            "notes": "Vienintelis kelias, rodomas gyvai: visos patikros su rezultatu, be tuščių laukų.",
        },
        {
            "id": "solution_a",
            "code": "A",
            "title": "Sprendinys A · esama spinta",
            "subtitle": "11 kW, 3F, KS-39685",
            "pitch": False,
            "expected_solution": "A",
            "expected_escalate": False,
            "form": _form(
                11,
                3,
                cab["lat"],
                cab["lon"],
                f"Naujas buitinis, 11 kW, 3 fazės, koordinatės {cab['lat']}, {cab['lon']}. Sklype jau stovi KS-39685.",
                name="Sklypas prie esamos KS",
            ),
            "notes": "Artimiausias elementas — kabelių spinta sklype → jungiklio keitimas.",
        },
        {
            "id": "solution_c",
            "code": "C",
            "title": "Sprendinys C · įsipjovimas į kabelį",
            "subtitle": "14 kW, 3F, L-KS14330",
            "pitch": False,
            "expected_solution": "C",
            "expected_escalate": False,
            "form": _form(
                14,
                3,
                c_lat,
                c_lon,
                f"Naujas buitinis, 14 kW, 3 fazės, koordinatės {c_lat:.5f}, {c_lon:.5f}, prie kabelių linijos.",
                name="Sklypas prie L-KS14330",
            ),
            "notes": f"Atstumas iki {ks['id']}: {haversine_m(c_lat, c_lon, ks['lat'], ks['lon']):.0f} m — ne sklype, todėl C.",
        },
        {
            "id": "fail_capacity",
            "code": "!",
            "title": "Nepraeina · inžinieriui",
            "subtitle": "100 kW, 3F, ta pati vieta kaip hero",
            "pitch": False,
            "expected_solution": "B",
            "expected_escalate": True,
            "form": _form(
                100,
                3,
                fail_lat,
                fail_lon,
                "Naujas vartotojas, 100 kW, 3 fazės, koordinatės 54,55929, 25,27955.",
                name="Didelė apkrova (demonstracija)",
            ),
            "notes": "227,7 + 100 = 327,7 kW > 320 kW (80 %). Eiga perduodama inžinieriui, 5 pakopa už SCOPE.",
        },
    ]


def get_scenario(sid: str) -> dict[str, Any]:
    for s in all_scenarios():
        if s["id"] == sid:
            return s
    raise KeyError(sid)
