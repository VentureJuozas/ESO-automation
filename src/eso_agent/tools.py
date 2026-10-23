"""Deterministic engineering tools. The LLM does not call these with free judgement."""
from __future__ import annotations

from typing import Any

from line_load import evaluate as evaluate_line

from eso_agent.catalog import tool_by_id
from eso_agent.cost import estimate_cost as build_cost
from eso_agent.load_loss import estimate_load_loss
from eso_agent.brief import build_reinforcement_brief
from eso_agent.document import REDACTED_ADDRESS, REDACTED_CUSTOMER, build_ts_document
from eso_agent.llm import llm_mode, parse_request as llm_parse, phrase_ts_offline, phrase_ts_with_llm
from eso_agent.models import RequestForm
from eso_agent.adapters import get_adapters
from eso_agent.network import STATION, haversine_m, load_network, nearest_element
from eso_agent.rules import (
    CABINET_AT_PLOT_M,
    NEW_CABLE_MAX_M,
    NEW_RADIAL_CABLE_MAX_KW,
    VOLTAGE_MIN_V,
    VOLTAGE_NOMINAL_V,
    breaker_table,
    added_demand_kw,
    cable_mm2_for_solution,
    diversity_coefficient,
    issuing_deadline_days,
    select_solution,
    size_breaker as size_breaker_rule,
    usable_voltage_baseline,
)
from eso_agent.ts_text import issue_dates, ownership_boundary, section3_blocks


def _feeder_path(feeder_name: str) -> list[list[float]]:
    net = load_network()
    els = [e for e in net["elements"] if e["feeder"] == feeder_name]
    els.sort(key=lambda e: haversine_m(STATION["lat"], STATION["lon"], e["lat"], e["lon"]))
    path = [[STATION["lat"], STATION["lon"]]]
    path.extend([e["lat"], e["lon"]] for e in els)
    return path


def _map_payload(parsed: dict[str, Any], location_out: dict[str, Any], solution_id: str | None = None) -> dict[str, Any]:
    net = load_network()
    feeder = location_out.get("feeder")
    return {
        "request": {"lat": parsed["lat"], "lon": parsed["lon"]},
        "selected": location_out.get("element"),
        "distance_m": location_out.get("distance_m"),
        "solution": solution_id,
        "substation": net["substation"],
        "elements": net["elements"],
        "feeders": [{"name": f["name"], "type": f["type"], "color": f["color"], "points": f["points"]} for f in net["feeders"]],
        "line": {
            "name": feeder,
            "path": _feeder_path(feeder) if feeder else [],
            "source": "synthetic",
        },
    }


def _annotate(result: dict[str, Any]) -> dict[str, Any]:
    meta = tool_by_id(result["tool"])
    result["rule_ref"] = meta.get("rule_ref")
    result["engineer"] = meta.get("engineer")
    result["kind"] = meta.get("kind", "tool")
    result["title_lt"] = meta.get("title_lt") or result.get("title")
    return result


def parse_request(text: str = "", form: dict[str, Any] | None = None) -> dict[str, Any]:
    parsed = llm_parse(text, RequestForm(**(form or {})))
    deadline = issuing_deadline_days(parsed.kw, parsed.customer_type)
    return _annotate({
        "tool": "parse_request",
        "title": "Paraiškos skaitymas",
        "llm": parsed.parse_mode == "llm",
        "inputs": {"text": text, "form": form or {}, "llm_mode": llm_mode()},
        "outputs": {
            "parsed": parsed.model_dump(),
            "deadline": deadline,
            "source_text": parsed.source_text,
            "extraction": parsed.extraction,
            "highlights": parsed.highlights,
            "missing": parsed.missing,
            "customer_placeholder": REDACTED_CUSTOMER,
            "address_placeholder": REDACTED_ADDRESS,
            "properly_submitted": {
                "value": True,
                "source": "synthetic",
                "note": "Dokumentų ir įmokos bylose nėra; demonstracijoje laikoma tinkamai pateikta.",
            },
        },
        "source_tags": list({*parsed.source_tags, "synthetic", "rule"}),
        "notes": parsed.warnings + [deadline["note"]],
        "ok": True,
    })


def locate_connection_point(parsed: dict[str, Any]) -> dict[str, Any]:
    gis = get_adapters().gis
    found = gis.nearest(parsed["lat"], parsed["lon"])
    el = found["element"]
    feeder = found["feeder"]
    cabinet_at_plot = el["kind"] == "cabinet" and found["distance_m"] <= CABINET_AT_PLOT_M
    ranked = []
    for cand in gis.load_network()["elements"]:
        d = haversine_m(parsed["lat"], parsed["lon"], cand["lat"], cand["lon"])
        ranked.append({"id": cand["id"], "kind": cand["kind"], "feeder": cand["feeder"], "distance_m": round(d, 1)})
    ranked.sort(key=lambda x: x["distance_m"])
    return _annotate({
        "tool": "locate_connection_point",
        "title": "Prijungimo taškas",
        "llm": False,
        "inputs": {"lat": parsed["lat"], "lon": parsed["lon"]},
        "outputs": {
            "feeder": feeder["name"],
            "feeder_type": feeder["type"],
            "element_id": el["id"],
            "element_kind": el["kind"],
            "distance_m": round(found["distance_m"], 1),
            "to_station_m": round(found["to_station_m"], 1),
            "element_to_station_m": round(found["element_to_station_m"], 1),
            "feeder_points": feeder["points"],
            "cabinet_at_plot": cabinet_at_plot,
            "element": el,
            "feeder_record": feeder,
            "substation": STATION,
            "nearest": ranked[:6],
            "map": _map_payload(parsed, {
                "feeder": feeder["name"],
                "element": el,
                "distance_m": round(found["distance_m"], 1),
            }),
        },
        "source_tags": ["synthetic", "inferred", "real"],
        "notes": [
            "Artimiausias tinklo elementas pagal WGS84 atstumą iki sintetinių atramų/spintų.",
            "Klientų adresai ir skaitiklių numeriai nenaudojami.",
            el.get("note", ""),
        ],
        "ok": True,
    })


def select_solution_tool(location: dict[str, Any]) -> dict[str, Any]:
    out = location["outputs"]
    chosen = select_solution(
        feeder_type=out["feeder_type"] if out["feeder_type"] != "mixed" else (
            "overhead" if out["element_kind"] == "pole" else "cable"
        ),
        feeder_name=out["feeder"],
        nearest_kind=out["element_kind"],
        distance_m=out["distance_m"],
        cabinet_at_plot=out["cabinet_at_plot"],
    )
    mm2 = cable_mm2_for_solution(chosen["id"])
    overhead = (out["feeder_type"] == "overhead") or (
        out["feeder_type"] == "mixed" and out["element_kind"] == "pole"
    )
    cable = not overhead
    comparison = [
        {
            "id": "A",
            "title": "Use existing cabinet",
            "applicable": bool(out["cabinet_at_plot"]),
            "chosen": chosen["id"] == "A",
            "why": "A KS/KAS already stands on the plot — replace the breaker only.",
            "why_not": f"No cabinet on the plot (nearest > {CABINET_AT_PLOT_M:.0f} m).",
            "ts_hint": "Esamoje KS-… pakeisti jungiklį į C NN A.",
        },
        {
            "id": "B",
            "title": "New pole-mounted KAS",
            "applicable": overhead and not out["cabinet_at_plot"],
            "chosen": chosen["id"] == "B",
            "why": f"Overhead feeder {out['feeder']}, pole {out['element_id']} — pole KAS + 16 mm².",
            "why_not": "Nearest element is not an overhead pole, or a cabinet already stands on the plot.",
            "ts_hint": "Ant oro linijos atramos įrengti KAS su C NN A ir 16 mm² kabelį.",
        },
        {
            "id": "C",
            "title": "Cable cut-in",
            "applicable": cable and not out["cabinet_at_plot"],
            "chosen": chosen["id"] == "C",
            "why": f"Cable feeder {out['feeder']} — KS/KAS at the plot boundary, ≥150 mm² to the cut-in.",
            "why_not": "Overhead feeder (use B) or a cabinet already on the plot (use A).",
            "ts_hint": "Įsipjauti į kabelinę liniją, KS/KAS, saugiklių blokas, perskaičiuoti apsaugas.",
        },
    ]
    stub = out["distance_m"]
    for card in comparison:
        sid = card["id"]
        cable = stub if sid == "B" else (max(stub, 20.0) if sid == "C" else 0.0)
        cost = build_cost(sid, cable if sid != "A" else None)
        card["cost_net"] = cost["net"]
        card["cost_gross"] = cost["gross"]
        card["works"] = {
            "A": "Breaker swap in the existing KS/KAS.",
            "B": "Pole KAS + 16 mm² service from the overhead wires.",
            "C": "KS/KAS at the plot boundary, cable cut-in, ≥150 mm².",
        }[sid]
        card["constraints"] = {
            "A": f"Cabinet must stand on the plot (≤{CABINET_AT_PLOT_M:.0f} m).",
            "B": "Overhead feeders only.",
            "C": "Radial ≤80 kW, new cable ≤600 m, 3-phase.",
        }[sid]
        card["cost_source"] = "real"
    return _annotate({
        "tool": "select_solution",
        "title": "Sprendinio parinkimas",
        "llm": False,
        "inputs": {
            "feeder": out["feeder"],
            "feeder_type": out["feeder_type"],
            "element": out["element_id"],
            "distance_m": out["distance_m"],
            "cabinet_at_plot": out["cabinet_at_plot"],
        },
        "outputs": {**chosen, "cable_mm2": mm2, "comparison": comparison},
        "source_tags": ["rule"],
        "notes": [chosen["reason"], "SCOPE.md: A esama spinta, B KAS ant atramos, C įsipjovimas į kabelį."],
        "ok": True,
    })


def size_breaker(parsed: dict[str, Any]) -> dict[str, Any]:
    br = size_breaker_rule(parsed["kw"], parsed["phases"])
    table = breaker_table(parsed["phases"])
    return _annotate({
        "tool": "size_breaker",
        "title": "Jungiklio parinkimas",
        "llm": False,
        "inputs": {"kw": parsed["kw"], "phases": parsed["phases"]},
        "outputs": {**br, "table": table, "requested_kw": parsed["kw"]},
        "source_tags": ["rule"],
        "notes": [br["note"]],
        "ok": True,
    })


def check_capacity(parsed: dict[str, Any], location: dict[str, Any], breaker: dict[str, Any]) -> dict[str, Any]:
    feeder = location["outputs"]["feeder_record"]
    new_kw = added_demand_kw(parsed["kw"], parsed.get("existing_kw") or 0)
    houses_feeder = feeder["points"] + 1
    k_feeder = diversity_coefficient(houses_feeder)
    k_station = diversity_coefficient(STATION["accounting_points"] + 1)
    permitted_after = feeder["permitted_kw"] + new_kw
    psk = permitted_after * k_feeder
    isk = psk / 0.624
    fuse = feeder["fuse_a"]
    fuse_ok = isk <= fuse
    # 1b synthetic cabinet fuse
    cabinet_fuse = 63 if parsed["phases"] == 1 else 100
    cabinet_ok = cabinet_fuse >= breaker["outputs"]["amps"]

    limits = get_adapters().capacity.limits()
    peak = limits["peak_kw"]
    conservative = peak + new_kw
    coincident = peak + new_kw * k_station
    limit80 = limits["limit_80_kw"]
    limit90 = limits["limit_90_kw"]
    # Binding check: SCOPE 1d peak + requested kW vs 80%/90%.
    # Measured peak already includes existing diversity; adding full new kW is conservative
    # for a household that may coincide with the winter evening peak.
    trafo_ok = conservative <= limit80
    trafo90_ok = conservative <= limit90

    steps = {
        "1a_breaker": {
            "pass": True,
            "detail": breaker["outputs"]["label"],
            "source": "rule",
        },
        "1b_cabinet_fuse": {
            "pass": cabinet_ok,
            "detail": f"Sintetinis spintos saugiklis {cabinet_fuse} A ≥ jungiklis {breaker['outputs']['amps']} A",
            "source": "synthetic",
        },
        "1c_feeder": {
            "pass": fuse_ok,
            "detail": (
                f"Psk = ({feeder['permitted_kw']} + {new_kw}) × k({houses_feeder})={k_feeder:.3f} "
                f"= {psk:.1f} kW, Isk = {isk:.0f} A, saugiklis {fuse} A"
            ),
            "source": feeder["fuse_source"],
            "psk_kw": round(psk, 2),
            "isk_a": round(isk, 1),
            "fuse_a": fuse,
            "diversity": round(k_feeder, 4),
        },
        "1d_transformer": {
            "pass": trafo_ok,
            "detail": (
                f"Viršūnė {peak} kW + {new_kw} kW = {conservative:.1f} kW; "
                f"80 % riba {limit80} kW, 90 % {limit90} kW. "
                f"Sutaptinė su k({STATION['accounting_points']+1})={k_station:.3f}: {coincident:.1f} kW."
            ),
            "source": "real",
            "peak_kw": peak,
            "after_kw": round(conservative, 2),
            "coincident_kw": round(coincident, 2),
            "limit_80_kw": limit80,
            "limit_90_kw": limit90,
            "share_of_nominal": round(conservative / STATION["nominal_kw"], 3),
        },
    }
    failed = [k for k, v in steps.items() if not v["pass"]]
    reason = None
    escalate = False
    if not trafo_ok:
        escalate = True
        reason = (
            f"Transformatoriaus 80 % riba ({limit80} kW) viršyta: {conservative:.1f} kW. "
            "Reikia inžinieriaus / kitos pakopos (transformatoriaus keitimas, 5 pakopa)."
        )
    elif not trafo90_ok:
        escalate = True
        reason = f"Transformatoriaus 90 % riba ({limit90} kW) viršyta."
    elif not fuse_ok:
        if feeder.get("fuse_source") == "real":
            escalate = True
            reason = (
                f"Linijos Isk {isk:.0f} A viršija saugiklį {fuse} A. "
                "Reikia inžinieriaus / linijos stiprinimo (4 pakopa)."
            )
        else:
            steps["1c_feeder"]["note"] = (
                f"Isk {isk:.0f} A > sintetinis saugiklis {fuse} A. "
                "Saugiklis byloje nėra — neblokuojame (tag: synthetic)."
            )
    elif not cabinet_ok:
        escalate = True
        reason = "Spintos saugiklis mažesnis už naują jungiklį."

    return _annotate({
        "tool": "check_capacity",
        "title": "Pajėgumas",
        "llm": False,
        "inputs": {
            "kw": parsed["kw"],
            "existing_kw": parsed.get("existing_kw") or 0,
            "added_kw": new_kw,
            "feeder": feeder["name"],
            "peak_kw": peak,
        },
        "outputs": {
            "pass": not failed,
            "escalate": escalate,
            "reason": reason,
            "steps": steps,
            "headroom_80_kw": round(limit80 - conservative, 1),
            "transformer_bar": {
                "nominal_kw": STATION["nominal_kw"],
                "limit_80_kw": limit80,
                "limit_90_kw": limit90,
                "before_kw": peak,
                "after_kw": round(conservative, 2),
                "coincident_kw": round(coincident, 2),
                "added_kw": new_kw,
            },
            "feeder_bar": {
                "fuse_a": fuse,
                "isk_a": round(isk, 1),
                "psk_kw": round(psk, 2),
                "diversity": round(k_feeder, 4),
                "fuse_source": feeder["fuse_source"],
            },
            "load_loss": estimate_load_loss(
                feeder,
                connection_id=location["outputs"]["element_id"],
                added_kw=new_kw,
                peak_before_kw=peak,
                peak_after_kw=conservative,
            ),
        },
        "source_tags": ["rule", "real", "synthetic"],
        "notes": [feeder["fuse_note"], steps["1d_transformer"]["detail"]],
        "ok": True,
    })


def _voltage_profile(feeder: dict[str, Any], new_kw: float, connection_id: str, baseline_v: float) -> list[dict[str, Any]]:
    """Synthetic path along feeder elements; tagged inferred/synthetic in the parent tool."""
    net = load_network()
    els = [e for e in net["elements"] if e["feeder"] == feeder["name"]]
    els.sort(key=lambda e: haversine_m(STATION["lat"], STATION["lon"], e["lat"], e["lon"]))
    if not els:
        return [
            {"m": 0, "label": "TP 12-608", "v_before": baseline_v, "v_after": baseline_v, "kind": "station"},
            {"m": 50, "label": connection_id, "v_before": baseline_v, "v_after": baseline_v, "kind": "connection"},
        ]
    n = len(els)
    kw_each = feeder["permitted_kw"] / n
    houses_each = max(1, feeder["points"] // n)
    segs_before, segs_after = [], []
    prev_lat, prev_lon = STATION["lat"], STATION["lon"]
    for i, el in enumerate(els):
        dist = max(8.0, haversine_m(prev_lat, prev_lon, el["lat"], el["lon"]))
        extra_kw = new_kw if el["id"] == connection_id else 0.0
        extra_h = 1 if el["id"] == connection_id else 0
        segs_before.append(
            {"conductor": feeder["conductor"], "length_m": dist, "permitted_kw": kw_each, "houses": houses_each}
        )
        segs_after.append(
            {
                "conductor": feeder["conductor"],
                "length_m": dist,
                "permitted_kw": kw_each + extra_kw,
                "houses": houses_each + extra_h,
            }
        )
        prev_lat, prev_lon = el["lat"], el["lon"]
    try:
        before = evaluate_line(segs_before, transformer_kva=400, method="new")
        after = evaluate_line(segs_after, transformer_kva=400, method="new")
    except Exception:
        return [
            {"m": 0, "label": "TP 12-608", "v_before": baseline_v, "v_after": baseline_v, "kind": "station"},
        ]
    points = [{"m": 0, "label": "TP 12-608", "v_before": round(baseline_v, 1), "v_after": round(baseline_v, 1), "kind": "station"}]
    cum = 0.0
    drop_b = 0.0
    drop_a = 0.0
    for i, el in enumerate(els):
        cum += segs_before[i]["length_m"]
        drop_b += before["segments"][i]["voltage_drop"]
        drop_a += after["segments"][i]["voltage_drop"]
        points.append(
            {
                "m": round(cum, 1),
                "label": el["id"],
                "v_before": round(baseline_v * (1 - drop_b / 100.0), 1),
                "v_after": round(baseline_v * (1 - drop_a / 100.0), 1),
                "kind": "connection" if el["id"] == connection_id else el["kind"],
            }
        )
    return points


def check_voltage_drop(parsed: dict[str, Any], location: dict[str, Any], solution: dict[str, Any]) -> dict[str, Any]:
    feeder = location["outputs"]["feeder_record"]
    length_m = max(5.0, location["outputs"]["element_to_station_m"])
    conductor = feeder["conductor"]
    houses = feeder["points"] + 1
    added_kw = added_demand_kw(parsed["kw"], parsed.get("existing_kw") or 0)
    permitted = feeder["permitted_kw"] + added_kw
    segments = [
        {
            "conductor": conductor,
            "length_m": length_m,
            "permitted_kw": permitted,
            "houses": houses,
        }
    ]
    before = evaluate_line(
        [{"conductor": conductor, "length_m": length_m, "permitted_kw": feeder["permitted_kw"], "houses": feeder["points"]}],
        transformer_kva=400,
        method="new",
    )
    after = evaluate_line(segments, transformer_kva=400, method="new")
    delta_pp = after["voltage_drop_pct"] - before["voltage_drop_pct"]
    baseline_info = usable_voltage_baseline(feeder)
    baseline = baseline_info["raw"]
    used_v = baseline_info["v"]
    used_tag = baseline_info["tag"]
    baseline_note = baseline_info["note"]
    v_after = used_v * (1 - after["voltage_drop_pct"] / 100.0)
    v_ok = v_after >= VOLTAGE_MIN_V

    stub_m = location["outputs"]["distance_m"]
    new_cable_m = stub_m if solution["outputs"]["id"] in {"B", "C"} else 0.0
    if solution["outputs"]["id"] == "C":
        new_cable_m = max(stub_m, 20.0)
    rule_2c = {
        "length_ok": new_cable_m <= NEW_CABLE_MAX_M,
        "radial_kw_ok": parsed["kw"] <= NEW_RADIAL_CABLE_MAX_KW,
        "three_phase_ok": parsed["phases"] == 3 or solution["outputs"]["id"] != "C",
        "note": "Standarto 12 priedo ištraukos (neautorizuotos): nauja 0,4 kV KL ≤ 600 m, viena radialė ≤ 80 kW, 3 fazės.",
        "source": "rule",
    }
    rule_2c_pass = rule_2c["length_ok"] and rule_2c["radial_kw_ok"] and rule_2c["three_phase_ok"]

    failed_reasons = []
    if not v_ok:
        failed_reasons.append(
            f"Skaičiuota įtampa {v_after:.1f} V < {VOLTAGE_MIN_V:.0f} V (LST EN 50160)."
        )
    if not rule_2c["radial_kw_ok"] and solution["outputs"]["id"] == "C":
        failed_reasons.append(
            f"Vienos radialinės kabelių linijos riba {NEW_RADIAL_CABLE_MAX_KW} kW viršyta ({parsed['kw']} kW)."
        )
    if not rule_2c["length_ok"]:
        failed_reasons.append(f"Naujo kabelio ilgis {new_cable_m:.0f} m > {NEW_CABLE_MAX_M} m.")

    escalate = bool(failed_reasons)
    reason = " ".join(failed_reasons) if failed_reasons else None
    if escalate:
        reason = (reason or "") + " Reikia inžinieriaus / linijos stiprinimo (4 pakopa)."

    return _annotate({
        "tool": "check_voltage_drop",
        "title": "Kokybė",
        "llm": False,
        "inputs": {
            "conductor": conductor,
            "length_m": round(length_m, 1),
            "kw": parsed["kw"],
            "added_kw": added_kw,
        },
        "outputs": {
            "pass": not escalate,
            "escalate": escalate,
            "reason": reason,
            "conductor": conductor,
            "conductor_source": feeder["conductor_source"],
            "length_m": round(length_m, 1),
            "length_source": "inferred",
            "voltage_drop_pct": round(after["voltage_drop_pct"], 4),
            "voltage_drop_before_pct": round(before["voltage_drop_pct"], 4),
            "delta_pp": round(delta_pp, 4),
            "baseline_v": baseline,
            "baseline_used_v": used_v,
            "baseline_tag": used_tag,
            "filtered_event": baseline_info["filtered_event"],
            "voltage_after_v": round(v_after, 1),
            "limit_v": VOLTAGE_MIN_V,
            "rule_2c": {**rule_2c, "pass": rule_2c_pass, "new_cable_m": round(new_cable_m, 1)},
            "line_load": {
                "psk_kw": round(after["psk_kw"], 2),
                "isk_a": round(after["isk_a"], 1),
                "permitted_kw": after["permitted_kw"],
            },
            "profile": _voltage_profile(
                feeder, added_kw, location["outputs"]["element_id"], used_v
            ),
            "load_loss": estimate_load_loss(
                feeder,
                connection_id=location["outputs"]["element_id"],
                added_kw=added_kw,
                peak_before_kw=STATION["peak_kw"],
                peak_after_kw=STATION["peak_kw"] + added_kw,
            ),
        },
        "source_tags": [feeder["conductor_source"], "inferred", "rule", used_tag],
        "notes": [
            baseline_note,
            f"Laidininkas {conductor} ({feeder['conductor_source']}), ruožas TP→elementas {length_m:.0f} m (iš koordinačių).",
            "Skaičiuoklė: src/line_load.py, metodas nuo 2018 m., transformatorius 400 kVA.",
        ],
        "ok": True,
    })


def check_reliability(location: dict[str, Any], solution: dict[str, Any]) -> dict[str, Any]:
    feeder = location["outputs"]["feeder_record"]
    affected = feeder["points"] if solution["outputs"]["id"] == "C" else 0
    els = [e for e in load_network()["elements"] if e["feeder"] == feeder["name"]]
    n_el = max(len(els), 1)
    base = feeder["points"] // n_el
    rem = feeder["points"] % n_el
    groups = []
    for i, el in enumerate(els):
        groups.append(
            {
                "id": el["id"],
                "kind": el["kind"],
                "points": base + (1 if i < rem else 0),
                "note": "Apskaitos taškai be adresų ir skaitiklių.",
            }
        )
    return _annotate({
        "tool": "check_reliability",
        "title": "Patikimumas",
        "llm": False,
        "inputs": {
            "transformer_count": STATION["transformer_count"],
            "solution": solution["outputs"]["id"],
            "feeder": feeder["name"],
        },
        "outputs": {
            "pass": True,
            "escalate": False,
            "reason": None,
            "n1": {
                "transformer_count": 1,
                "nominal_kw": STATION["nominal_kw"],
                "n1_kw": STATION["n1_kw"],
                "reserve": 0,
                "note": "Vienas transformatorius, N-1 galia = nominalas, rezervo nėra. Prijungimas to neblogina.",
                "source": "real",
            },
            "backup": {
                "radial": True,
                "lost": False,
                "note": "Topologijoje žiedų nėra — atsarginis kelias neprarandamas.",
                "source": "inferred",
            },
            "cut_in": {
                "applies": solution["outputs"]["id"] == "C",
                "affected_customers": affected,
                "note": (
                    f"Įsipjovimas į {feeder['name']}: planinis atjungimas, {affected} apskaitos taškai šioje linijoje."
                    if solution["outputs"]["id"] == "C"
                    else "Oro linijos KAS / esamos spintos keitimas kaimynų neatjungia."
                ),
                "source": "real" if solution["outputs"]["id"] == "C" else "rule",
                "groups": groups if solution["outputs"]["id"] == "C" else [],
            },
        },
        "source_tags": ["real", "inferred", "rule"],
        "notes": ["Patikimumas 0,4 kV + 0,4/10 kV lygiu; aukštesni lygiai už SCOPE ribų."],
        "ok": True,
    })


def check_future(parsed: dict[str, Any], capacity: dict[str, Any]) -> dict[str, Any]:
    pending = float(parsed.get("pending_kw") or 0)
    headroom = capacity["outputs"]["headroom_80_kw"] - pending
    growth_ok = headroom >= 0
    reason = None
    if not growth_ok:
        reason = (
            f"Po prijungimo ir rezervuotų {pending} kW iki 80 % ribos lieka {headroom:.1f} kW. "
            "Reikia inžinieriaus (ateities rezervas)."
        )
    bar = capacity["outputs"].get("transformer_bar") or {}
    return _annotate({
        "tool": "check_future",
        "title": "Ateitis",
        "llm": False,
        "inputs": {"pending_kw": pending, "headroom_before_pending": capacity["outputs"]["headroom_80_kw"]},
        "outputs": {
            "pass": growth_ok,
            "escalate": not growth_ok,
            "reason": reason,
            "pending_kw": pending,
            "pending_source": "synthetic" if pending == 0 else "real",
            "headroom_kw": round(headroom, 1),
            "territory_plans": {
                "value": None,
                "source": "synthetic",
                "note": "Teritorijų planų byloje nėra.",
            },
            "gauge": {
                "nominal_kw": STATION["nominal_kw"],
                "limit_80_kw": STATION["limit_80_kw"],
                "peak_kw": STATION["peak_kw"],
                "after_kw": bar.get("after_kw"),
                "pending_kw": pending,
                "headroom_kw": round(headroom, 1),
            },
        },
        "source_tags": ["synthetic", "real", "rule"],
        "notes": [
            "Rezervuotų paraiškų Power BI eksportas neįkeltas; numatytasis 0 kW nestabdo eigos.",
            "Teritorijų planai: nėra informacijos.",
        ],
        "ok": True,
    })


def draft_ts_section3(
    parsed: dict[str, Any],
    location: dict[str, Any],
    solution: dict[str, Any],
    breaker: dict[str, Any],
    edited_text: str | None = None,
) -> dict[str, Any]:
    blocks = section3_blocks(solution["outputs"], breaker["outputs"], location)
    if edited_text:
        text = edited_text.strip()
        mode = "engineer"
    elif llm_mode() != "offline":
        text = phrase_ts_with_llm(
            blocks,
            {
                "solution": solution["outputs"]["id"],
                "breaker": breaker["outputs"]["label"],
                "feeder": location["outputs"]["feeder"],
            },
        )
        mode = "llm"
    else:
        text = phrase_ts_offline(blocks)
        mode = "offline"
    issued, valid = issue_dates()
    document = build_ts_document(
        parsed, location, solution, breaker, text, issued=False, valid_until=valid
    )
    document["placeholder_dates"] = {"valid_until_example": valid, "issue_date_example": issued}
    document["parse_mode"] = mode
    document["blocks"] = blocks
    return _annotate({
        "tool": "draft_ts_section3",
        "title": "Sąlygų §3 juodraštis",
        "llm": mode == "llm",
        "inputs": {"solution": solution["outputs"]["id"], "breaker": breaker["outputs"]["label"], "mode": mode},
        "outputs": {
            "section3": text,
            "blocks": blocks,
            "ownership_boundary": ownership_boundary(solution["outputs"]["id"]),
            "watermark": document["watermark"],
            "parse_mode": mode,
            "document": document,
        },
        "source_tags": ["rule"],
        "notes": [
            "LLM (jei yra raktas) tik perrašo formuluotę; skaičiai iš įrankių.",
            "Be rakto naudojamas šablonų replay.",
        ],
        "ok": True,
    })


def estimate_cost_tool(solution: dict[str, Any], location: dict[str, Any]) -> dict[str, Any]:
    sid = solution["outputs"]["id"]
    cable_m = location["outputs"]["distance_m"] if sid in {"B", "C"} else None
    if sid == "C":
        cable_m = max(location["outputs"]["distance_m"], 20.0)
    cost = build_cost(sid, cable_m)
    return _annotate({
        "tool": "estimate_cost",
        "title": "Sąmatos orientyras",
        "llm": False,
        "inputs": {"solution": sid, "cable_m": cable_m},
        "outputs": cost,
        "source_tags": ["real", "synthetic"] if sid == "B" else ["real"],
        "notes": [cost["note"]],
        "ok": True,
    })


def render_map(parsed: dict[str, Any], location: dict[str, Any], solution: dict[str, Any]) -> dict[str, Any]:
    return _annotate({
        "tool": "render_map",
        "title": "Prijungimo žemėlapis",
        "llm": False,
        "inputs": {"lat": parsed["lat"], "lon": parsed["lon"]},
        "outputs": _map_payload(parsed, location["outputs"], solution["outputs"]["id"]),
        "source_tags": ["synthetic", "real"],
        "notes": ["Žemėlapis: TP, atramos ir spintos. Be klientų adresų ir skaitiklių."],
        "ok": True,
    })


def escalate_package(checks: list[dict[str, Any]]) -> dict[str, Any]:
    failed = [c for c in checks if c and (c.get("outputs") or {}).get("escalate")]
    reasons = [c["outputs"].get("reason") for c in failed if c["outputs"].get("reason")]
    cap = next((c for c in failed if c.get("tool") == "check_capacity"), failed[0] if failed else {})
    out = (cap or {}).get("outputs") or {}
    bar = out.get("transformer_bar") or {}
    after = bar.get("after_kw")
    limit = bar.get("limit_80_kw") or 320
    numbers = {
        "peak_kw": bar.get("before_kw"),
        "requested_kw": bar.get("added_kw"),
        "after_kw": after,
        "limit_80_kw": limit,
        "limit_90_kw": bar.get("limit_90_kw"),
        "over_kw": round((after or 0) - limit, 1) if after is not None else None,
    }
    pending_kw, pending_n = 0.0, 0
    try:
        from eso_agent.queue import pending_queue_load
        pending_kw, pending_n = pending_queue_load()
    except Exception:  # noqa: BLE001
        pending_kw, pending_n = 0.0, 0
    brief = build_reinforcement_brief(numbers, pending_kw=pending_kw, pending_cases=pending_n)
    return _annotate({
        "tool": "escalate",
        "title": "Perdavimas inžinieriui",
        "llm": False,
        "inputs": {"failed_tools": [c["tool"] for c in failed]},
        "outputs": {
            "status": "needs_engineer",
            "failed_at": (cap or {}).get("tool") or "check_capacity",
            "reasons": reasons,
            "reason": reasons[0] if reasons else None,
            "numbers": numbers,
            "brief": brief,
            "suggested_next": brief["options"][0]["next_step"],
            "next_level": "4–6 pakopa (linijos stiprinimas / transformatorius / nauja TP)",
            "attachments": {
                "steps": out.get("steps"),
                "transformer_bar": bar,
                "source_tags": (cap or {}).get("source_tags") or ["real", "rule"],
            },
            "safety": brief["safety"],
        },
        "source_tags": ["rule", "real", "inferred"],
        "notes": reasons,
        "ok": True,
    })


def issue_ts(
    parsed: dict[str, Any],
    location: dict[str, Any],
    solution: dict[str, Any],
    breaker: dict[str, Any],
    draft: dict[str, Any],
    approval: dict[str, Any],
    run_id: str,
) -> dict[str, Any]:
    issued, valid = issue_dates()
    number = f"26-E-DEMO-{run_id[:6].upper()}"
    section3 = approval.get("section3") or draft["outputs"]["section3"]
    document = build_ts_document(
        parsed, location, solution, breaker, section3,
        issued=True, ts_number=number, issue_date=issued, valid_until=valid, run_id=run_id,
    )
    get_adapters().registry.register(
        {"ts_number": number, "run_id": run_id, "kw": parsed.get("kw"), "solution": solution["outputs"]["id"]}
    )
    return _annotate({
        "tool": "issue_ts",
        "title": "Sąlygų išdavimas",
        "llm": False,
        "inputs": {"approved": True, "ts_number": number},
        "outputs": {
            "ts_number": number,
            "issue_date": issued,
            "valid_until": valid,
            "watermark": None,
            "section3": section3,
            "ownership_boundary": draft["outputs"]["ownership_boundary"],
            "document": document,
            "application": {
                "kw": parsed["kw"],
                "phases": parsed["phases"],
                "object_name": parsed.get("object_name"),
                "tp": "12-608",
                "feeder": location["outputs"]["feeder"],
                "element": location["outputs"]["element_id"],
                "solution": solution["outputs"]["id"],
                "breaker": breaker["outputs"]["label"],
                "customer": document["customer"],
                "address": document["address"],
            },
        },
        "source_tags": ["rule"],
        "notes": ["Galiojimas = parengimo data + 1 metai. Kliento asmens duomenų nėra."],
        "ok": True,
    })


def request_missing_data(parsed_event: dict[str, Any], form: dict[str, Any] | None = None) -> dict[str, Any]:
    from eso_agent.missing import detect_gaps, draft_message, provisional

    parsed = (parsed_event.get("outputs") or {}).get("parsed") or parsed_event
    gaps = detect_gaps(parsed, form)
    letter = draft_message(gaps, parsed.get("object_name") or "Objektas (redaguota)")
    prov = provisional(gaps)
    return _annotate({
        "tool": "request_missing_data",
        "title": "Trūkstami duomenys",
        "llm": False,
        "inputs": {"gaps": [g.get("id") for g in gaps]},
        "outputs": {
            "gaps": gaps,
            "letter": letter,
            "provisional": prov,
            "waiting": True,
            "sent": False,
        },
        "source_tags": ["rule", "synthetic"],
        "notes": ["Laiškas nebuvo išsiųstas. Eiga laukia įvesties ir tęsia nuo šio mazgo."],
        "ok": True,
    })
