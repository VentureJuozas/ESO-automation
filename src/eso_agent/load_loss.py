"""Feeder and transformer load / loss estimate from src/line_load.py tables.

Segments run from TP 12-608 outward. Diversified current Isk and permitted
current Imax come from the 2018 calculator. Feeder I²R uses the sheet
impedance (3-phase). Transformer copper + iron losses use the 400 kVA
nameplate pair in the same calculator family.
"""
from __future__ import annotations

from typing import Any

from line_load import IMPEDANCE, evaluate

from eso_agent.network import STATION, haversine_m, load_network

HOURS_YEAR = 8760
# 400 kVA oil distribution transformer — calculator family (Trafai).
TR_SN_KVA = 400.0
TR_P0_KW = 0.93
TR_PK_KW = 4.60
# Continuous rating used for % loading. 4A-50 ≈ 160 A.
AMPACITY_A = {
    "4A-16": 80,
    "4A-25": 105,
    "4A-35": 130,
    "4A-50": 160,
    "4A-70": 200,
    "4x25": 110,
    "4x50": 155,
    "4x70": 190,
    "4x95": 230,
    "4x120": 260,
    "4x150": 275,
    "4x185": 310,
}


def _segments(feeder: dict[str, Any], connection_id: str, added_kw: float) -> tuple[list[dict], list[dict], list[dict]]:
    net = load_network()
    els = [e for e in net["elements"] if e["feeder"] == feeder["name"]]
    els.sort(key=lambda e: haversine_m(STATION["lat"], STATION["lon"], e["lat"], e["lon"]))
    if not els:
        stub = [{"conductor": feeder["conductor"], "length_m": 50.0, "permitted_kw": feeder["permitted_kw"], "houses": max(1, feeder["points"])}]
        after = [{**stub[0], "permitted_kw": feeder["permitted_kw"] + added_kw, "houses": stub[0]["houses"] + 1}]
        return stub, after, [{"id": connection_id, "kind": "connection"}]
    n = len(els)
    kw_each = feeder["permitted_kw"] / n
    houses_each = max(1, feeder["points"] // n)
    before, after, meta = [], [], []
    prev_lat, prev_lon = STATION["lat"], STATION["lon"]
    for el in els:
        dist = max(8.0, haversine_m(prev_lat, prev_lon, el["lat"], el["lon"]))
        extra_kw = added_kw if el["id"] == connection_id else 0.0
        extra_h = 1 if el["id"] == connection_id else 0
        before.append({"conductor": feeder["conductor"], "length_m": dist, "permitted_kw": kw_each, "houses": houses_each})
        after.append({
            "conductor": feeder["conductor"],
            "length_m": dist,
            "permitted_kw": kw_each + extra_kw,
            "houses": houses_each + extra_h,
        })
        meta.append(el)
        prev_lat, prev_lon = el["lat"], el["lon"]
    return before, after, meta


def _i2r_kw(rows: dict[str, Any]) -> tuple[float, list[dict[str, Any]]]:
    total = 0.0
    segs = []
    for r in rows.get("segments") or []:
        cond = r["conductor"]
        r_ohm = IMPEDANCE[cond] * float(r["length_m"]) / 1000.0
        i = float(r["isk_a"])
        p_kw = 3.0 * (i ** 2) * r_ohm / 1000.0
        total += p_kw
        segs.append({
            "conductor": cond,
            "length_m": round(float(r["length_m"]), 1),
            "isk_a": round(i, 1),
            "imax_a": round(float(r["imax_a"]), 1),
            "psk_kw": round(float(r["psk_kw"]), 2),
            "voltage_drop_pct": round(float(r["voltage_drop"]), 4),
            "loss_kw": round(p_kw, 3),
        })
    return round(total, 3), segs


def _transformer_loss_kw(load_kw: float) -> dict[str, float]:
    share = max(0.0, float(load_kw) / TR_SN_KVA)
    copper = TR_PK_KW * share * share
    iron = TR_P0_KW
    total = iron + copper
    return {
        "iron_kw": round(iron, 3),
        "copper_kw": round(copper, 3),
        "total_kw": round(total, 3),
        "load_kw": round(float(load_kw), 2),
        "share": round(share, 4),
    }


def _energy(kw: float, utilisation: float) -> float:
    return round(float(kw) * HOURS_YEAR * max(0.05, min(1.0, utilisation)), 1)


def estimate_load_loss(
    feeder: dict[str, Any],
    *,
    connection_id: str,
    added_kw: float,
    peak_before_kw: float,
    peak_after_kw: float,
) -> dict[str, Any]:
    segs_b, segs_a, meta = _segments(feeder, connection_id, added_kw)
    before = evaluate(segs_b, transformer_kva=400, method="new")
    after = evaluate(segs_a, transformer_kva=400, method="new")
    loss_b, rows_b = _i2r_kw(before)
    loss_a, rows_a = _i2r_kw(after)
    ampacity = AMPACITY_A.get(feeder["conductor"], 160)
    path = []
    cum = 0.0
    drop_b = 0.0
    drop_a = 0.0
    customer_idx = 0
    for i, el in enumerate(meta):
        cum += segs_b[i]["length_m"]
        drop_b += before["segments"][i]["voltage_drop"]
        drop_a += after["segments"][i]["voltage_drop"]
        if el["id"] == connection_id:
            customer_idx = i
        path.append({
            "id": el["id"],
            "kind": "connection" if el["id"] == connection_id else el.get("kind"),
            "m": round(cum, 1),
            "length_m": round(segs_b[i]["length_m"], 1),
            "i_before_a": rows_b[i]["isk_a"],
            "i_after_a": rows_a[i]["isk_a"],
            "load_before_pct": round(100.0 * rows_b[i]["isk_a"] / ampacity, 1),
            "load_after_pct": round(100.0 * rows_a[i]["isk_a"] / ampacity, 1),
            "du_before_pct": round(before["segments"][i]["voltage_drop"], 4),
            "du_after_pct": round(after["segments"][i]["voltage_drop"], 4),
            "v_before": round(230.0 * (1 - drop_b / 100.0), 1),
            "v_after": round(230.0 * (1 - drop_a / 100.0), 1),
            "loss_before_kw": rows_b[i]["loss_kw"],
            "loss_after_kw": rows_a[i]["loss_kw"],
        })
    util_b = before["psk_kw"] / before["permitted_kw"] if before["permitted_kw"] else 0.4
    util_a = after["psk_kw"] / after["permitted_kw"] if after["permitted_kw"] else 0.4
    tr_b = _transformer_loss_kw(peak_before_kw)
    tr_a = _transformer_loss_kw(peak_after_kw)
    to_customer = path[: customer_idx + 1] if path else []
    return {
        "method": "line_load 2018",
        "conductor": feeder["conductor"],
        "ampacity_a": ampacity,
        "formula": {
            "psk": "ΣP_perm × k(n)",
            "isk": "Psk / 0.624",
            "du": "L_km × Psk × kU",
            "feeder_loss": "3 × Isk² × R",
            "transformer_loss": "P0 + Pk × (S/Sn)²",
            "energy": "P × 8760 × (Psk / Pperm)",
        },
        "line": {
            "before": {
                "psk_kw": round(before["psk_kw"], 2),
                "isk_a": round(before["isk_a"], 1),
                "imax_a": round(before["imax_a"], 1),
                "load_pct": round(100.0 * before["isk_a"] / ampacity, 1),
            },
            "after": {
                "psk_kw": round(after["psk_kw"], 2),
                "isk_a": round(after["isk_a"], 1),
                "imax_a": round(after["imax_a"], 1),
                "load_pct": round(100.0 * after["isk_a"] / ampacity, 1),
            },
        },
        "feeder_loss": {
            "before_kw": loss_b,
            "after_kw": loss_a,
            "delta_kw": round(loss_a - loss_b, 3),
            "before_kwh_year": _energy(loss_b, util_b),
            "after_kwh_year": _energy(loss_a, util_a),
        },
        "transformer_loss": {
            "before": tr_b,
            "after": tr_a,
            "delta_kw": round(tr_a["total_kw"] - tr_b["total_kw"], 3),
            "before_kwh_year": _energy(tr_b["total_kw"], peak_before_kw / TR_SN_KVA),
            "after_kwh_year": _energy(tr_a["total_kw"], peak_after_kw / TR_SN_KVA),
        },
        "to_customer": to_customer,
        "segments": path,
    }
