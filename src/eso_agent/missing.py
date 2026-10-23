"""Detect missing inputs, draft a request (never sent), and a provisional A/B/C."""
from __future__ import annotations

from typing import Any


def detect_gaps(parsed: dict[str, Any], form: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    form = form or {}
    gaps = list(parsed.get("missing") or [])
    seen = {g.get("id") for g in gaps}
    req = form.get("required_element")
    if req and "element" not in seen:
        from eso_agent.network import element_by_id

        try:
            element_by_id(str(req))
        except KeyError:
            gaps.append(
                {
                    "id": "element",
                    "field": "required_element",
                    "value": req,
                    "party": "gis",
                    "party_lt": "GIS / lauko inžinierius",
                    "why": "locate_connection_point",
                    "note": f"Elemento {req} nėra 12-608 tinkle.",
                }
            )
    return gaps


def draft_message(gaps: list[dict[str, Any]], object_name: str) -> dict[str, Any]:
    """Lithuanian preview only. Nothing is sent."""
    parties = sorted({g.get("party_lt") or g.get("party") for g in gaps})
    lines = [
        f"Tema: Trūkstami duomenys prijungimo sąlygoms — {object_name} (redaguota)",
        "",
        "Sveiki,",
        "",
        "Ruošiame 0,4 kV prijungimo sąlygas transformatorinei 12-608. "
        "Eiga sustabdyta, nes trūksta šių įvesčių:",
    ]
    for g in gaps:
        lines.append(f"- {g.get('field')}: {g.get('note')} (reikia {g.get('why')}).")
    lines += [
        "",
        "Prašome atsiųsti trūkstamus duomenis. Laiškas neišsiųstas — tai tik peržiūra.",
        "",
        "Pagarbiai,",
        "ESO prijungimo demonstracija (be asmens duomenų)",
    ]
    return {
        "to": ", ".join(parties) or "Klientas",
        "sent": False,
        "body": "\n".join(lines),
        "note": "Peržiūra. Nieko nesiunčiame.",
    }


def provisional(gaps: list[dict[str, Any]]) -> dict[str, Any]:
    """Default if we used the hero point, plus sensitivity — not an issued decision."""
    ids = {g.get("id") for g in gaps}
    default = "B"
    reason = "Hero numatytasis (L-200 / 200/3) → KAS ant atramos."
    if "element" in ids:
        default = "A"
        reason = "Jei trūkstama KS atsiranda tinkle prie sklypo — keičiamas jungiklis esamoje spintoje."
    rows = [
        {"if": "Koordinatės prie L-200 atramos", "then": "B", "note": "Nauja KAS, 16 mm²"},
        {"if": "Koordinatės ≤12 m nuo KS", "then": "A", "note": "Jungiklis esamoje spintoje"},
        {"if": "Koordinatės prie kabelio, spintos nėra", "then": "C", "note": "Įsipjovimas, ≥150 mm²"},
        {"if": "kW > 80 % TR ribos (320 kW − 227,7 kW)", "then": "escalate", "note": "Stiprinimo paketas"},
    ]
    return {
        "solution": default,
        "reason": reason,
        "sensitivity": rows,
        "source": "rule",
        "note": "Laikinas. Galutinis A/B/C skaičiuojamas tik užpildžius įvestį.",
    }
