"""LLM steps: parse free-text request and phrase TS §3.

Without an API key the demo uses a deterministic offline/replay parser and
the Lithuanian TS templates. The LLM never makes engineering decisions.
"""
from __future__ import annotations

import json
import os
import re
from typing import Any

from eso_agent.models import ParsedRequest, RequestForm
from eso_agent.network import HERO_LAT, HERO_LON

_KW = re.compile(r"(\d+(?:[.,]\d+)?)\s*k\s*w", re.I)
_PHASE3 = re.compile(r"(3\s*f|trifaz|trys faz|3\s*faz)", re.I)
_PHASE1 = re.compile(r"(1\s*f|vienfaz|viena faz)", re.I)
_DOT_COORDS = re.compile(r"(-?\d{1,3}\.\d+)\s*[,;]\s*(-?\d{1,3}\.\d+)")
_LT_COORDS = re.compile(r"(\d{1,3}),(\d{3,6})\s*[,;]\s*(\d{1,3}),(\d{3,6})")
_OBJECT = re.compile(r"(sodyba|namas|sklypas|objektas|garažas|ūkis)[^\n,.]{0,40}", re.I)


def llm_mode() -> str:
    if os.environ.get("OPENAI_API_KEY"):
        return "openai"
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    return "offline"


def llm_available() -> bool:
    return llm_mode() != "offline"


def _f(v: Any) -> float | None:
    if v is None or v == "":
        return None
    if isinstance(v, (int, float)):
        return float(v)
    return float(str(v).replace(",", ".").strip())


def _hit(value: Any, source: str, confidence: float, match: re.Match | None = None, field: str = "") -> dict[str, Any]:
    span = [match.start(), match.end()] if match else None
    return {
        "field": field,
        "value": value,
        "source": source,
        "confidence": round(confidence, 2),
        "start": span[0] if span else None,
        "end": span[1] if span else None,
        "snippet": match.group(0) if match else "",
    }


def parse_offline(text: str, form: RequestForm | None = None) -> ParsedRequest:
    form = form or RequestForm()
    warnings: list[str] = []
    tags: list[str] = []
    source_text = (form.text or text or "").strip()
    hits: dict[str, dict[str, Any]] = {}
    highlights: list[dict[str, Any]] = []

    def remember(hit: dict[str, Any]) -> None:
        hits[hit["field"]] = hit
        if hit.get("start") is not None:
            highlights.append({"field": hit["field"], "start": hit["start"], "end": hit["end"], "snippet": hit.get("snippet")})

    kw = _f(form.kw)
    phases = form.phases
    lat = _f(form.lat)
    lon = _f(form.lon)
    pending = _f(form.pending_kw)
    existing = _f(form.existing_kw)
    object_name = form.object_name or "Naujas buitinis objektas"

    if source_text:
        mk = _KW.search(source_text)
        if mk:
            remember(_hit(float(mk.group(1).replace(",", ".")), "text", 0.93, mk, "kw"))
            if kw is None:
                kw = float(mk.group(1).replace(",", "."))
        elif kw is not None:
            remember(_hit(kw, "form", 0.99, None, "kw"))
        m3 = _PHASE3.search(source_text)
        m1 = _PHASE1.search(source_text)
        if m1 and not m3:
            remember(_hit(1, "text", 0.9, m1, "phases"))
            if phases is None:
                phases = 1
        elif m3:
            remember(_hit(3, "text", 0.92, m3, "phases"))
            if phases is None:
                phases = 3
        elif phases in (1, 3):
            remember(_hit(int(phases), "form", 0.99, None, "phases"))
        lt = _LT_COORDS.search(source_text)
        dm = _DOT_COORDS.search(source_text)
        if lt:
            plat = float(lt.group(1) + "." + lt.group(2))
            plon = float(lt.group(3) + "." + lt.group(4))
            remember(_hit([plat, plon], "text", 0.94, lt, "coords"))
            if lat is None:
                lat = plat
            if lon is None:
                lon = plon
        elif dm:
            remember(_hit([float(dm.group(1)), float(dm.group(2))], "text", 0.94, dm, "coords"))
            if lat is None:
                lat = float(dm.group(1))
            if lon is None:
                lon = float(dm.group(2))
        elif lat is not None and lon is not None:
            remember(_hit([lat, lon], "form", 0.99, None, "coords"))
        mo = _OBJECT.search(source_text)
        if mo and (not form.object_name or form.object_name == "Naujas buitinis objektas"):
            object_name = mo.group(0).strip().capitalize()
            remember(_hit(object_name, "text", 0.7, mo, "object_name"))

    if kw is not None and "kw" not in hits:
        remember(_hit(kw, "form", 0.99, None, "kw"))
    if phases in (1, 3) and "phases" not in hits:
        remember(_hit(int(phases), "form", 0.99, None, "phases"))
    if lat is not None and lon is not None and "coords" not in hits:
        remember(_hit([lat, lon], "form", 0.99, None, "coords"))

    parse_mode: str = "form" if form.kw and form.lat and form.lon else "offline"

    if kw is None:
        kw = 11.0
        warnings.append("Galia nerasta — naudojamas hero numatytasis 11 kW.")
        tags.append("synthetic")
        remember(_hit(kw, "default", 0.35, None, "kw"))
    if phases not in (1, 3):
        phases = 3
        warnings.append("Fazės nerastos — naudojamos 3 fazės.")
        tags.append("synthetic")
        remember(_hit(3, "default", 0.4, None, "phases"))
    if lat is None or lon is None:
        lat, lon = HERO_LAT, HERO_LON
        warnings.append("Koordinatės nerastos — naudojamas hero taškas prie 12-608.")
        tags.append("synthetic")
        remember(_hit([lat, lon], "default", 0.35, None, "coords"))
    if pending is None:
        pending = 0.0
        tags.append("synthetic")
    if existing is None:
        existing = 0.0

    if not tags:
        tags.append("real")

    missing: list[dict[str, Any]] = []
    if hits.get("coords", {}).get("source") == "default":
        missing.append(
            {
                "id": "coords",
                "field": "lat/lon",
                "party": "customer",
                "party_lt": "Klientas",
                "why": "locate_connection_point ir A/B/C",
                "note": "Be koordinačių negalima parinkti artimiausio elemento.",
            }
        )
    if hits.get("kw", {}).get("source") == "default":
        missing.append(
            {
                "id": "kw",
                "field": "kw",
                "party": "customer",
                "party_lt": "Klientas",
                "why": "size_breaker ir check_capacity",
                "note": "Be leistinosios galios jungiklis ir 80 % riba nepatikimi.",
            }
        )
    req = getattr(form, "required_element", None)
    if req:
        from eso_agent.network import element_by_id

        try:
            element_by_id(req)
        except KeyError:
            missing.append(
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

    customer = form.customer_type or "household"
    return ParsedRequest(
        kw=float(kw),
        phases=3 if int(phases) == 3 else 1,
        lat=float(lat),
        lon=float(lon),
        customer_type=customer,
        pending_kw=float(pending or 0),
        existing_kw=float(existing or 0),
        object_name=object_name,
        parse_mode=parse_mode,  # type: ignore[arg-type]
        warnings=warnings,
        source_tags=tags,  # type: ignore[arg-type]
        source_text=source_text,
        extraction=hits,
        highlights=highlights,
        missing=missing,
    )


def parse_with_llm(text: str, form: RequestForm | None = None) -> ParsedRequest:
    """Use OpenAI if a key is set; fall back to offline on any error."""
    form = form or RequestForm()
    fallback = parse_offline(text, form)
    if not os.environ.get("OPENAI_API_KEY"):
        return fallback
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatOpenAI(model=os.environ.get("ESO_LLM_MODEL", "gpt-4o-mini"), temperature=0)
        sys = (
            "Extract a grid-connection request as JSON with keys: "
            "kw (number), phases (1 or 3), lat, lon, customer_type "
            "(household/other), pending_kw (number, default 0), object_name. "
            "Coordinates may use Lithuanian commas (54,55929, 25,27955). "
            "No personal names. Reply with JSON only."
        )
        msg = llm.invoke(
            [
                SystemMessage(content=sys),
                HumanMessage(content=text or json.dumps(form.model_dump())),
            ]
        )
        data = json.loads(str(msg.content))
        merged = RequestForm(
            kw=_f(data.get("kw")) if data.get("kw") is not None else form.kw,
            phases=int(data["phases"]) if data.get("phases") else form.phases,
            lat=_f(data.get("lat")) if data.get("lat") is not None else form.lat,
            lon=_f(data.get("lon")) if data.get("lon") is not None else form.lon,
            customer_type=data.get("customer_type") or form.customer_type,
            pending_kw=_f(data.get("pending_kw")) if data.get("pending_kw") is not None else form.pending_kw,
            text=text,
            object_name=data.get("object_name") or form.object_name,
        )
        out = parse_offline(text, merged)
        out.parse_mode = "llm"
        out.source_tags = ["real"]
        return out
    except Exception as exc:  # noqa: BLE001 — demo must never break on stage
        fallback.warnings.append(f"LLM parse failed, offline used: {exc}")
        fallback.parse_mode = "offline"
        return fallback


def parse_request(text: str, form: RequestForm | None = None) -> ParsedRequest:
    if llm_available() and (text or "").strip():
        return parse_with_llm(text, form)
    return parse_offline(text, form)


def phrase_ts_offline(blocks: list[str], extra: str = "") -> str:
    body = "\n".join(blocks)
    if extra.strip():
        return extra.strip()
    return body


def phrase_ts_with_llm(blocks: list[str], context: dict[str, Any]) -> str:
    fallback = phrase_ts_offline(blocks)
    if not os.environ.get("OPENAI_API_KEY"):
        return fallback
    try:
        from langchain_openai import ChatOpenAI
        from langchain_core.messages import HumanMessage, SystemMessage

        llm = ChatOpenAI(model=os.environ.get("ESO_LLM_MODEL", "gpt-4o-mini"), temperature=0.2)
        sys = (
            "You write Lithuanian ESO prijungimo sąlygos section 3 (operator actions). "
            "Keep the engineering numbers exactly as given (breaker A, cable mm², "
            "feeder, pole/cabinet ids). Do not add customer names. "
            "Number items 3.1, 3.2, ... Return only the section 3 text."
        )
        human = json.dumps({"blocks": blocks, "context": context}, ensure_ascii=False)
        msg = llm.invoke([SystemMessage(content=sys), HumanMessage(content=human)])
        text = str(msg.content).strip()
        return text or fallback
    except Exception:  # noqa: BLE001
        return fallback
