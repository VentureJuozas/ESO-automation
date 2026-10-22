"""Substation 12-608 network fixture.

Raw CSVs are git-ignored (customer locations, meter serials). This module
rebuilds a redacted working set from README/summary numbers plus tagged
synthetic network elements (poles and cabinets only — no customer PII).
"""
from __future__ import annotations

import math
from functools import lru_cache
from typing import Any

STATION = {
    "id": "12-608",
    "name": "12-608",
    "display": 'MT-1 "Ozas", Dusinėnų k.',
    "lat": 54.55884,
    "lon": 25.27935,
    "nominal_kw": 400.0,
    "n1_kw": 400.0,
    "transformer_count": 1,
    "limit_80_kw": 320.0,
    "limit_90_kw": 360.0,
    "peak_kw": 227.7,
    "peak_at": "2026-02-06T19:15:00Z",
    "accounting_points": 221,
    "permitted_total_kw": 1877.5,
    "source": "real",
    "note": "Substations_info.csv + pastotes_load_kas15min.csv (README).",
}

# Hero request from data/test_new_kas_12-608.md
HERO_LAT = 54.55929
HERO_LON = 25.27955

FEEDERS: dict[str, dict[str, Any]] = {
    "L-200": {
        "type": "overhead",
        "points": 47,
        "permitted_kw": 335.0,
        "metered": 25,
        "meter_max_kw": 79.3,
        "meter_avg_kw": 16.1,
        "poles": 24,
        "fuse_a": 250,
        "fuse_source": "synthetic",
        "fuse_note": "Linijos nominalo byloje nėra; 250 A parinkta kaip sintetinis numatytasis, kad Isk ~200 A tilptų. Hero eigoje žingsnis neužblokuojamas.",
        "conductor": "4A-50",
        "conductor_source": "synthetic",
        "voltage_min_v": None,
        "voltage_source": "real",
        "voltage_note": "25 skaitikliai 66–81 V 2026-02-04; atmetus įvykį ir 0 V, patikimos įtampos L-200 nelieka.",
        "bearing_deg": 18.0,
        "color": "#1e88e5",
    },
    "L-204": {
        "type": "overhead",
        "points": 29,
        "permitted_kw": 230.0,
        "metered": 18,
        "meter_max_kw": 81.2,
        "meter_avg_kw": 20.2,
        "poles": 14,
        "fuse_a": 200,
        "fuse_source": "synthetic",
        "fuse_note": "Sintetinis numatytasis; byloje saugiklio nėra.",
        "conductor": "4A-50",
        "conductor_source": "synthetic",
        "voltage_min_v": None,
        "voltage_source": "real",
        "voltage_note": "17 skaitiklių 0 V; po atmetimo patikimos įtampos nenaudojame.",
        "bearing_deg": 280.0,
        "color": "#7c4dff",
    },
    "L-300": {
        "type": "overhead",
        "points": 35,
        "permitted_kw": 223.0,
        "metered": 17,
        "meter_max_kw": 53.6,
        "meter_avg_kw": 12.1,
        "poles": 22,
        "fuse_a": 200,
        "fuse_source": "synthetic",
        "fuse_note": "Sintetinis numatytasis; byloje saugiklio nėra.",
        "conductor": "4A-50",
        "conductor_source": "synthetic",
        "voltage_min_v": None,
        "voltage_source": "real",
        "voltage_note": "Išmatuotos min. įtampos po filtrų šiai linijai atskirai neduotos.",
        "bearing_deg": 165.0,
        "color": "#00a99d",
    },
    "L-KS14330": {
        "type": "cable",
        "points": 59,
        "permitted_kw": 622.0,
        "metered": 46,
        "meter_max_kw": 165.7,
        "meter_avg_kw": 34.0,
        "poles": 0,
        "fuse_a": 315,
        "fuse_source": "real",
        "fuse_note": "TS 23-31728: L-KS14330 saugiklis pakeistas į 315 A.",
        "conductor": "4x150",
        "conductor_source": "synthetic",
        "voltage_min_v": None,
        "voltage_source": "real",
        "voltage_note": "2 skaitikliai 0 V; 160 V / 184 V išskirtys. Po atmetimo visos linijos min. nenaudojame.",
        "bearing_deg": 85.0,
        "color": "#e5484d",
        "cabinets": [
            "KS-14330",
            "KS-14331",
            "KS-14332",
            "KS-14333",
            "KS-14335",
            "KS-14336",
            "KS-14338",
            "KS-14339",
            "KS-14340",
            "KS-14342",
        ],
    },
    "L-KS39685": {
        "type": "cable",
        "points": 32,
        "permitted_kw": 347.0,
        "metered": 27,
        "meter_max_kw": 113.0,
        "meter_avg_kw": 25.0,
        "poles": 0,
        "fuse_a": 250,
        "fuse_source": "synthetic",
        "fuse_note": "Sintetinis numatytasis; byloje saugiklio nėra.",
        "conductor": "4x150",
        "conductor_source": "synthetic",
        "voltage_min_v": 217.0,
        "voltage_source": "inferred",
        "voltage_note": "README: šioje linijoje žemos įtampos nėra. 217 V — konservatyvi stoties daugumos (≥217 V) riba, ne išmatuotas min.",
        "bearing_deg": 230.0,
        "color": "#fb8c00",
        "cabinets": ["KS-39685", "KS-39686", "KS-39687", "KS-14347"],
    },
    "L-KS13058": {
        "type": "mixed",
        "points": 19,
        "permitted_kw": 120.5,
        "metered": 12,
        "meter_max_kw": 48.1,
        "meter_avg_kw": 11.6,
        "poles": 11,
        "fuse_a": 160,
        "fuse_source": "synthetic",
        "fuse_note": "Sintetinis numatytasis; byloje saugiklio nėra.",
        "conductor": "4A-50",
        "conductor_source": "synthetic",
        "voltage_min_v": 205.0,
        "voltage_source": "real",
        "voltage_note": "Vienas 205 V įrašas (žemiau 207 V). Hero eiga šios linijos nenaudoja.",
        "bearing_deg": 125.0,
        "color": "#2e9e5b",
        "cabinets": ["KS-26429"],
    },
}


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(min(1.0, math.sqrt(a)))


def destination(lat: float, lon: float, bearing_deg: float, dist_m: float) -> tuple[float, float]:
    r = 6371000.0
    br = math.radians(bearing_deg)
    lat1 = math.radians(lat)
    lon1 = math.radians(lon)
    d_r = dist_m / r
    lat2 = math.asin(
        math.sin(lat1) * math.cos(d_r) + math.cos(lat1) * math.sin(d_r) * math.cos(br)
    )
    lon2 = lon1 + math.atan2(
        math.sin(br) * math.sin(d_r) * math.cos(lat1),
        math.cos(d_r) - math.sin(lat1) * math.sin(lat2),
    )
    return math.degrees(lat2), math.degrees(lon2)


def _hero_pole_coord() -> tuple[float, float]:
    """Pole 200/3 sits ~12 m from the hero request so locate() always picks it."""
    return destination(HERO_LAT, HERO_LON, 170.0, 12.0)


@lru_cache(maxsize=1)
def load_network() -> dict[str, Any]:
    elements: list[dict[str, Any]] = []
    hero_lat, hero_lon = _hero_pole_coord()

    for name, spec in FEEDERS.items():
        bearing = spec["bearing_deg"]
        if spec["type"] in {"overhead", "mixed"} and spec["poles"]:
            n = spec["poles"]
            for i in range(1, n + 1):
                dist = 18 + (i - 1) * 22
                lat, lon = destination(STATION["lat"], STATION["lon"], bearing, dist)
                pole_id = f"{name.split('-')[-1]}/{i}" if name != "L-KS13058" else f"100/{i}"
                if name == "L-200" and i == 3:
                    pole_id = "200/3"
                    lat, lon = hero_lat, hero_lon
                elif name == "L-200":
                    pole_id = f"200/{i}"
                elif name == "L-204":
                    pole_id = f"204/{i}"
                elif name == "L-300":
                    pole_id = f"300/{i}"
                if name == "L-200" and i != 3:
                    dist_from_hero = haversine_m(HERO_LAT, HERO_LON, lat, lon)
                    if dist_from_hero < 30:
                        lat, lon = destination(lat, lon, 90.0, 45.0)
                elements.append(
                    {
                        "id": pole_id,
                        "kind": "pole",
                        "feeder": name,
                        "lat": round(lat, 6),
                        "lon": round(lon, 6),
                        "source": "synthetic",
                        "note": "Atramos koordinatės sintetinės, išvestos iš TP taško ir linijos azimuto. Pole 200/3 pririštas prie hero paraiškos.",
                    }
                )
        for j, cab in enumerate(spec.get("cabinets") or []):
            dist = 40 + j * 28
            side = 12 if j % 2 == 0 else -12
            lat, lon = destination(STATION["lat"], STATION["lon"], bearing + side * 0.15, dist)
            elements.append(
                {
                    "id": cab,
                    "kind": "cabinet",
                    "feeder": name,
                    "lat": round(lat, 6),
                    "lon": round(lon, 6),
                    "source": "synthetic",
                    "note": "Spintos koordinatės sintetinės; vardai iš redaguotos TS istorijos (tinklo turtas, ne klientas).",
                }
            )

    feeders_out = []
    for name, spec in FEEDERS.items():
        item = {"name": name, **{k: v for k, v in spec.items() if k not in {"cabinets", "bearing_deg", "poles"}}}
        item["source"] = "real"
        feeders_out.append(item)

    return {
        "substation": STATION,
        "feeders": feeders_out,
        "elements": elements,
        "pending_kw_default": {
            "value": 0.0,
            "source": "synthetic",
            "note": "Rezervuotų paraiškų byloje nėra; numatytasis 0 kW.",
        },
        "tags_legend": {
            "real": "Iš TP 12-608 bylų arba TS istorijos",
            "rule": "Iš ESO taisyklės / skaičiuoklės lentelės",
            "inferred": "Išvesta iš koordinačių ar suvestinių",
            "synthetic": "Sintetinis numatytasis, pažymėtas kaip toks",
        },
    }


def feeder_by_name(name: str) -> dict[str, Any]:
    net = load_network()
    for f in net["feeders"]:
        if f["name"] == name:
            return f
    raise KeyError(name)


def element_by_id(eid: str) -> dict[str, Any]:
    for el in load_network()["elements"]:
        if el["id"] == eid:
            return el
    raise KeyError(eid)


def nearest_element(lat: float, lon: float) -> dict[str, Any]:
    best = None
    best_d = 1e18
    for el in load_network()["elements"]:
        d = haversine_m(lat, lon, el["lat"], el["lon"])
        if d < best_d:
            best_d = d
            best = el
    assert best is not None
    feeder = feeder_by_name(best["feeder"])
    to_station = haversine_m(lat, lon, STATION["lat"], STATION["lon"])
    to_element_station = haversine_m(best["lat"], best["lon"], STATION["lat"], STATION["lon"])
    return {
        "element": best,
        "distance_m": best_d,
        "feeder": feeder,
        "to_station_m": to_station,
        "element_to_station_m": to_element_station,
    }
