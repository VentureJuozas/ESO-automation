"""Feeder and transformer load / loss estimate.

Feeder current uses L-200's own measured peak (meter_max_kw), not the
transformer peak and not contracted permitted kW. Segment current tapers
with remaining poles. I²R is 3 · I² · R with R = r_Ω/km × L_km.

Voltage to the customer uses the same line_load evaluate() span as the
Voltage step (permitted × k(n) over TP → pole), so V matches 224 V.

Annual energy uses a loss factor and equivalent hours, not peak × 8760.
"""
from __future__ import annotations

from typing import Any

from line_load import AMPERE_DIVISOR, IMPEDANCE, evaluate

from eso_agent.network import FEEDERS, STATION, haversine_m, load_network

HOURS_YEAR = 8760
# 400 kVA oil distribution transformer (calculator family / Trafai).
TR_SN_KVA = 400.0
TR_P0_KW = 0.93
TR_PK_KW = 4.60
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
    "4x150": 315,
    "4x185": 310,
}


def loss_factor(load_factor: float) -> float:
    """IEEE-style loss factor F = 0.3 LF + 0.7 LF²."""
    lf = max(0.05, min(1.0, float(load_factor)))
    return 0.3 * lf + 0.7 * lf * lf


def equivalent_hours(load_factor: float) -> float:
    return HOURS_YEAR * loss_factor(load_factor)


def feeder_peak_kw(feeder: dict[str, Any]) -> float:
    """Own feeder peak. Prefer the metered maximum; else share of the TP peak."""
    if feeder.get("meter_max_kw"):
        return float(feeder["meter_max_kw"])
    permitted = float(feeder.get("permitted_kw") or 0)
    total = float(STATION.get("permitted_total_kw") or 0)
    if permitted and total:
        return STATION["peak_kw"] * permitted / total
    return 0.0


def station_load_factor() -> float:
    avg = sum(float(s.get("meter_avg_kw") or 0) for s in FEEDERS.values())
    return avg / STATION["peak_kw"] if STATION["peak_kw"] else 0.4


def feeder_load_factor(feeder: dict[str, Any]) -> float:
    peak = feeder_peak_kw(feeder)
    avg = float(feeder.get("meter_avg_kw") or 0)
    if peak <= 0:
        return 0.3
    return avg / peak if avg else 0.3


def current_a(power_kw: float) -> float:
    return float(power_kw) / AMPERE_DIVISOR


def transformer_loss_kw(load_kw: float) -> dict[str, float]:
    share = max(0.0, float(load_kw) / TR_SN_KVA)
    copper = TR_PK_KW * share * share
    iron = TR_P0_KW
    return {
        "iron_kw": round(iron, 3),
        "copper_kw": round(copper, 3),
        "total_kw": round(iron + copper, 3),
        "load_kw": round(float(load_kw), 2),
        "share": round(share, 4),
    }


def feeder_path(feeder: dict[str, Any]) -> list[dict[str, Any]]:
    """Poles/cabinets from the TP outward, with segment length in metres."""
    name = feeder.get("name")
    if not name:
        raise ValueError("feeder name is required")
    net = load_network()
    els = [e for e in net["elements"] if e["feeder"] == name]
    els.sort(key=lambda e: haversine_m(STATION["lat"], STATION["lon"], e["lat"], e["lon"]))
    path = []
    prev_lat, prev_lon = STATION["lat"], STATION["lon"]
    cum = 0.0
    for el in els:
        length = max(8.0, haversine_m(prev_lat, prev_lon, el["lat"], el["lon"]))
        cum += length
        path.append({
            "id": el["id"],
            "kind": el.get("kind"),
            "length_m": length,
            "m": cum,
            "from_station_m": haversine_m(STATION["lat"], STATION["lon"], el["lat"], el["lon"]),
        })
        prev_lat, prev_lon = el["lat"], el["lon"]
    return path


def _i2r_kw(current_a: float, length_m: float, conductor: str) -> float:
    r_ohm = IMPEDANCE[conductor] * float(length_m) / 1000.0
    return 3.0 * (float(current_a) ** 2) * r_ohm / 1000.0


def _voltage_to_customer(feeder: dict[str, Any], length_m: float, added_kw: float) -> dict[str, Any]:
    houses = int(feeder.get("points") or 1)
    before = evaluate(
        [{"conductor": feeder["conductor"], "length_m": length_m, "permitted_kw": feeder["permitted_kw"], "houses": houses}],
        transformer_kva=400,
        method="new",
    )
    after = evaluate(
        [{
            "conductor": feeder["conductor"],
            "length_m": length_m,
            "permitted_kw": feeder["permitted_kw"] + added_kw,
            "houses": houses + 1,
        }],
        transformer_kva=400,
        method="new",
    )
    return {"before": before, "after": after}


def estimate_load_loss(
    feeder: dict[str, Any],
    *,
    connection_id: str,
    added_kw: float,
    peak_before_kw: float,
    peak_after_kw: float,
) -> dict[str, Any]:
    path = feeder_path(feeder)
    n = len(path) or 1
    conductor = feeder["conductor"]
    ampacity = AMPACITY_A.get(conductor, 160)
    p_b = feeder_peak_kw(feeder)
    p_a_head = p_b + added_kw
    i_head_b = current_a(p_b)
    i_head_a = current_a(p_a_head)
    customer_idx = 0
    for i, seg in enumerate(path):
        if seg["id"] == connection_id:
            customer_idx = i
            break
    to_m = path[customer_idx]["m"] if path else 50.0
    volt = _voltage_to_customer(feeder, to_m, added_kw)
    du_b = float(volt["before"]["voltage_drop_pct"])
    du_a = float(volt["after"]["voltage_drop_pct"])

    rows = []
    loss_b = 0.0
    loss_a = 0.0
    drop_b = 0.0
    drop_a = 0.0
    max_after_pct = 0.0
    for i, seg in enumerate(path):
        remain = (n - i) / n
        i_b = i_head_b * remain
        extra = added_kw if i <= customer_idx else 0.0
        i_a = current_a(p_b * remain + extra)
        p_loss_b = _i2r_kw(i_b, seg["length_m"], conductor)
        p_loss_a = _i2r_kw(i_a, seg["length_m"], conductor)
        load_b_pct = 100.0 * i_b / ampacity
        load_a_pct = 100.0 * i_a / ampacity
        max_after_pct = max(max_after_pct, load_a_pct)
        share = seg["length_m"] / to_m if i <= customer_idx and to_m else 0.0
        seg_du_b = du_b * share
        seg_du_a = du_a * share
        if i <= customer_idx:
            loss_b += p_loss_b
            loss_a += p_loss_a
            drop_b += seg_du_b
            drop_a += seg_du_a
        rows.append({
            "id": seg["id"],
            "kind": "connection" if seg["id"] == connection_id else seg["kind"],
            "m": round(seg["m"], 1),
            "length_m": round(seg["length_m"], 1),
            "i_before_a": round(i_b, 1),
            "i_after_a": round(i_a, 1),
            "load_before_pct": round(load_b_pct, 1),
            "load_after_pct": round(load_a_pct, 1),
            "du_before_pct": round(seg_du_b, 4),
            "du_after_pct": round(seg_du_a, 4),
            "v_before": round(230.0 * (1 - drop_b / 100.0), 1) if i <= customer_idx else None,
            "v_after": round(230.0 * (1 - drop_a / 100.0), 1) if i <= customer_idx else None,
            "loss_before_kw": round(p_loss_b, 3),
            "loss_after_kw": round(p_loss_a, 3),
        })

    lf_f = feeder_load_factor(feeder)
    hours_f = equivalent_hours(lf_f)
    lf_t = station_load_factor()
    hours_t = equivalent_hours(lf_t)
    tr_b = transformer_loss_kw(peak_before_kw)
    tr_a = transformer_loss_kw(peak_after_kw)
    line_ok = max_after_pct <= 100.0 + 1e-9
    to_customer = rows[: customer_idx + 1] if rows else []
    v_customer = to_customer[-1]["v_after"] if to_customer else None
    return {
        "method": "feeder meter peak + line_load voltage",
        "conductor": conductor,
        "ampacity_a": ampacity,
        "feeder_peak_kw": round(p_b, 2),
        "feeder_peak_after_kw": round(p_a_head, 2),
        "formula": {
            "i": "I = P_feeder / 0.624",
            "psk": "ΣP_perm × k(n)  (voltage only)",
            "du": "L_km × Psk × kU",
            "feeder_loss": "3 × I² × R, R = r_Ω/km × L_km",
            "transformer_loss": "P0 + Pk × (S/Sn)²",
            "energy": "P_peak × 8760 × (0.3 LF + 0.7 LF²)",
        },
        "line": {
            "before": {
                "p_kw": round(p_b, 2),
                "isk_a": round(i_head_b, 1),
                "load_pct": round(100.0 * i_head_b / ampacity, 1),
            },
            "after": {
                "p_kw": round(p_a_head, 2),
                "isk_a": round(i_head_a, 1),
                "load_pct": round(100.0 * i_head_a / ampacity, 1),
            },
        },
        "line_loading": {
            "pass": line_ok,
            "limit_pct": 100.0,
            "max_after_pct": round(max_after_pct, 1),
            "ampacity_a": ampacity,
            "i_after_a": round(i_head_a, 1),
            "i_before_a": round(i_head_b, 1),
        },
        "feeder_loss": {
            "before_kw": round(loss_b, 3),
            "after_kw": round(loss_a, 3),
            "delta_kw": round(loss_a - loss_b, 3),
            "before_kwh_year": round(loss_b * hours_f, 1),
            "after_kwh_year": round(loss_a * hours_f, 1),
            "loss_factor": round(loss_factor(lf_f), 4),
            "equivalent_hours": round(hours_f, 1),
            "load_factor": round(lf_f, 4),
            "span": f"TP → {connection_id}",
            "length_m": round(to_m, 1),
        },
        "transformer_loss": {
            "before": tr_b,
            "after": tr_a,
            "delta_kw": round(tr_a["total_kw"] - tr_b["total_kw"], 3),
            "before_kwh_year": round(tr_b["total_kw"] * hours_t, 1),
            "after_kwh_year": round(tr_a["total_kw"] * hours_t, 1),
            "loss_factor": round(loss_factor(lf_t), 4),
            "equivalent_hours": round(hours_t, 1),
            "load_factor": round(lf_t, 4),
        },
        "voltage": {
            "before_v": round(230.0 * (1 - du_b / 100.0), 1),
            "after_v": v_customer,
            "drop_before_pct": round(du_b, 4),
            "drop_after_pct": round(du_a, 4),
            "length_m": round(to_m, 1),
        },
        "to_customer": to_customer,
        "segments": rows,
    }
