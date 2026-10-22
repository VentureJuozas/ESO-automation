"""Replay issued 12-608 (and two detailed reference) TS cases. Honest mismatches."""
from __future__ import annotations

import csv
import re
from pathlib import Path
from typing import Any

from eso_agent.network import HERO_LAT, HERO_LON, element_by_id

ROOT = Path(__file__).resolve().parents[2]
HISTORY = ROOT / "data" / "substation_12-608" / "ts_history_redacted.csv"

_BREAKER = re.compile(r"(\d+)\s*A", re.I)
_CAB = re.compile(r"KS-?\s*(\d+)", re.I)
_KAS = re.compile(r"KAS", re.I)
_CUT = re.compile(r"įsipjauti|isipjauti|kabelin", re.I)
_POLE_KAS = re.compile(r"oro linij|atramos|16\s*mm", re.I)
_TR_SWAP = re.compile(r"transformatorių pakeisti|400 kVA", re.I)


def _cabinet_coord(cab_id: str) -> dict[str, float] | None:
    try:
        el = element_by_id(cab_id)
        return {"lat": el["lat"], "lon": el["lon"], "id": el["id"]}
    except KeyError:
        return None


def _classify(text: str, pole: str, kas: str, cabinet: str) -> str:
    if _TR_SWAP.search(text or ""):
        return "escalate"
    if _CUT.search(text or "") and "pakeisti esamą" not in (text or "")[:80]:
        if "įsipjauti" in (text or "") or "isipjauti" in (text or ""):
            return "C"
    if _POLE_KAS.search(text or "") or pole or kas:
        if "pakeisti esamą" in (text or "") and cabinet and not pole:
            return "A"
        if pole or kas or "16 mm" in (text or "") or "16mm" in (text or ""):
            return "B"
    if cabinet or "Esamoje" in (text or "") or "pakeisti esamą" in (text or ""):
        return "A"
    return "unknown"


def _breaker_amps(text: str) -> int | None:
    hits = [int(m.group(1)) for m in _BREAKER.finditer(text or "")]
    household = [a for a in hits if a <= 80]
    return household[-1] if household else (hits[-1] if hits else None)


def load_history_cases() -> list[dict[str, Any]]:
    rows = []
    if not HISTORY.exists():
        return rows
    with HISTORY.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for raw in reader:
            text = raw.get("TS tekstas") or ""
            cab = (raw.get("0,4 kV KS(PP,SP)") or "").split("_")[-1] if raw.get("0,4 kV KS(PP,SP)") else ""
            cab = cab.replace("12-608_", "")
            if cab and not cab.startswith("KS") and cab.isdigit():
                cab = f"KS-{cab}"
            m = _CAB.search(text)
            if m and not cab:
                cab = f"KS-{m.group(1)}"
            pole = (raw.get("Atramos Nr.") or "").strip()
            if pole in {"NULL", "None"}:
                pole = ""
            kas = (raw.get("KAS Nr.") or "").strip()
            if kas in {"NULL", "None"}:
                kas = ""
            kw = raw.get("LG nauja") or raw.get("Leist. Galia suma")
            try:
                kw_f = float(str(kw).replace(",", "."))
            except (TypeError, ValueError):
                kw_f = None
            expected = _classify(text, pole, kas, cab)
            coord = _cabinet_coord(cab) if cab else None
            if not coord and pole:
                try:
                    el = element_by_id(pole)
                    coord = {"lat": el["lat"], "lon": el["lon"], "id": el["id"]}
                except KeyError:
                    coord = None
            rows.append(
                {
                    "id": raw.get("Reg. numeris"),
                    "source": "ts_history_redacted",
                    "tp_issued": "12-608",
                    "kw": kw_f,
                    "phases": 1 if "vienfaz" in text.lower() else 3,
                    "expected_solution": expected,
                    "expected_breaker_a": _breaker_amps(text),
                    "expected_cost_net": None,
                    "expected_section3": text,
                    "cabinet": cab or None,
                    "pole": pole or None,
                    "feeder": raw.get("TR linija (prijunginys)") or raw.get("KS linija (prijunginys)"),
                    "coord": coord,
                    "note": "Redaguota TS istorija. Be kliento vardo ir adreso.",
                }
            )
    return rows


def reference_detail_cases() -> list[dict[str, Any]]:
    return [
        {
            "id": "26-E-37934",
            "source": "case_26-E-37934",
            "tp_issued": "Pg-452",
            "kw": 22,
            "phases": 3,
            "expected_solution": "KS_at_TP",
            "expected_breaker_a": 40,
            "expected_cost_net": 10678.99,
            "expected_section3": "KS/KAS prie TP, 40 A, 150 mm², T-2",
            "cabinet": None,
            "pole": None,
            "feeder": None,
            "coord": None,
            "note": "Kita TP (Pg-452). Agentas visada skaičiuoja 12-608 — sprendinys ir kaina nesutaps. Tai sąmoningas neatitikimas.",
        },
        {
            "id": "26-E-37536",
            "source": "case_26-E-37536",
            "tp_issued": "Rg-202",
            "kw": 11,
            "phases": 3,
            "expected_solution": "B",
            "expected_breaker_a": 20,
            "expected_cost_net": None,
            "expected_section3": "KAS ant L-300 atramos 300/1, C 20 A, 16 mm²",
            "cabinet": None,
            "pole": "300/1",
            "feeder": "L-300",
            "coord": _cabinet_coord("300/1") or {"lat": HERO_LAT, "lon": HERO_LON, "id": "fallback"},
            "note": "Išduota Rg-202. Perleidžiame analogą ant 12-608 L-300. TP laukas nesutaps.",
        },
    ]


def all_gallery_cases() -> list[dict[str, Any]]:
    return reference_detail_cases() + load_history_cases()


def _form_for(case: dict[str, Any]) -> dict[str, Any]:
    coord = case.get("coord") or {"lat": HERO_LAT, "lon": HERO_LON}
    kw = case.get("kw") or 11
    phases = case.get("phases") or 3
    text = (
        f"Istorinė byla {case['id']}: {kw} kW, {phases}F, "
        f"koordinatės {coord.get('lat')}, {coord.get('lon')}. Be asmens duomenų."
    )
    return {
        "kw": kw,
        "phases": phases,
        "lat": coord.get("lat"),
        "lon": coord.get("lon"),
        "customer_type": "household",
        "pending_kw": 0,
        "text": text,
        "object_name": f"Istorinis objektas {case['id']} (redaguota)",
    }


def _tokens(text: str) -> set[str]:
    return {t.lower() for t in re.findall(r"[a-zA-Ząčęėįšųūž0-9]{3,}", text or "", flags=re.I)}


def compare_case(case: dict[str, Any], snap: dict[str, Any]) -> dict[str, Any]:
    sol = (snap.get("solution") or {}).get("id")
    br = (snap.get("breaker") or {}).get("amps")
    cost = (snap.get("cost") or {}).get("net")
    section = (snap.get("draft") or {}).get("section3") or ""
    failed = bool(snap.get("failed"))
    agent_sol = "escalate" if failed else sol
    fields = []

    def add(name, expected, got, ok, explain):
        fields.append({"field": name, "expected": expected, "got": got, "match": ok, "explain": explain})

    if case["expected_solution"] == "KS_at_TP":
        add("solution", "KS_at_TP", agent_sol, False, "Išduota prie kitos TP (Pg-452). Agentas dirba tik 12-608 A/B/C.")
    elif case["expected_solution"] == "escalate":
        add("solution", "escalate", agent_sol, agent_sol == "escalate", "Istorijoje TR keitimas. Agentas eskaluoja tik jei 80 % netelpa.")
    elif case["expected_solution"] == "unknown":
        add("solution", "unknown", agent_sol, None, "Istorijos tekstas neleidžia vienareikšmiškai priskirti A/B/C.")
    else:
        add("solution", case["expected_solution"], agent_sol, agent_sol == case["expected_solution"],
            "" if agent_sol == case["expected_solution"] else "Lokacija sintetinė — artimiausias elementas gali skirtis nuo išduotos KS/atramos.")

    exp_a = case.get("expected_breaker_a")
    if exp_a:
        add("breaker", f"C {exp_a} A", f"C {br} A" if br else None, br == exp_a,
            "" if br == exp_a else "Jungiklis iš KNOWLEDGE §15 lentelės pagal kW.")
    else:
        add("breaker", None, br, None, "Istorijos tekste amperai neišskaitomi.")

    if case.get("expected_cost_net"):
        add("cost", case["expected_cost_net"], cost, False,
            "26-E-37934 sąmata kitai TP ir kitam darbų rinkiniui. Orientyras nesulyginamas 1:1.")
    else:
        add("cost", None, cost, None, "Istorinėje 12-608 eilutėje kainos nėra.")

    exp_txt = case.get("expected_section3") or ""
    overlap = _tokens(exp_txt) & _tokens(section)
    cond_ok = False
    if section and exp_a and str(exp_a) in section:
        cond_ok = True
    if case["expected_solution"] == "B" and "16" in section and "KAS" in section:
        cond_ok = True
    if case["expected_solution"] == "A" and "pakeisti" in section.lower():
        cond_ok = True
    if case["expected_solution"] == "C" and ("150" in section or "įsipj" in section.lower()):
        cond_ok = True
    add("conditions", exp_txt[:180], section[:180], cond_ok if section else False,
        f"Bendri žodžiai: {len(overlap)}. Tekstas lyginamas laisvai — ne visos istorinės eilutės 4.x = agento §3.")

    scored = [f for f in fields if f["match"] is not None]
    score = round(sum(1 for f in scored if f["match"]) / len(scored), 2) if scored else 0.0
    return {
        "id": case["id"],
        "source": case["source"],
        "tp_issued": case["tp_issued"],
        "note": case.get("note"),
        "expected": {
            "solution": case["expected_solution"],
            "breaker_a": exp_a,
            "cost_net": case.get("expected_cost_net"),
            "section3": exp_txt,
        },
        "agent": {
            "solution": agent_sol,
            "breaker_a": br,
            "cost_net": cost,
            "section3": section,
            "status": snap.get("status"),
            "run_id": snap.get("id"),
        },
        "fields": fields,
        "score": score,
        "redacted": True,
    }


LAST_GALLERY: dict[str, Any] | None = None


def gallery_index() -> dict[str, Any]:
    return {
        "cases": [
            {
                "id": c["id"],
                "source": c["source"],
                "tp_issued": c["tp_issued"],
                "kw": c["kw"],
                "phases": c.get("phases"),
                "expected_solution": c["expected_solution"],
                "expected_breaker_a": c.get("expected_breaker_a"),
                "expected_cost_net": c.get("expected_cost_net"),
                "note": c.get("note"),
                "cabinet": c.get("cabinet"),
                "pole": c.get("pole"),
                "redacted": True,
            }
            for c in all_gallery_cases()
        ],
        "last": LAST_GALLERY,
        "note": "Tik redaguoti TS. Be kliento vardo, adreso ir skaitiklio.",
    }


def run_gallery(limit: int | None = None) -> dict[str, Any]:
    from eso_agent.engine import run_sync_until_interrupt

    cases = all_gallery_cases()
    if limit:
        cases = cases[:limit]
    results = []
    for case in cases:
        snap = run_sync_until_interrupt("intake", delay=0, text=case.get("expected_section3") or "", form=_form_for(case))
        results.append(compare_case(case, snap))
    scored = [r["score"] for r in results]
    payload = {
        "results": results,
        "count": len(results),
        "accuracy": round(sum(scored) / len(scored), 2) if scored else 0,
        "note": "Sąžiningas back-test: neatitikimai palikti ir paaiškinti. Be asmens duomenų.",
    }
    global LAST_GALLERY
    LAST_GALLERY = payload
    return payload
