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
_LT_COORDS = re.compile(r"(\d{2}),(\d{3,6})\s*[,;]\s*(\d{2}),(\d{3,6})")


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


def parse_offline(text: str, form: RequestForm | None = None) -> ParsedRequest:
    form = form or RequestForm()
    warnings: list[str] = []
    tags: list[str] = []

    kw = _f(form.kw)
    phases = form.phases
    lat = _f(form.lat)
    lon = _f(form.lon)
    pending = _f(form.pending_kw)
    text = (form.text or text or "").strip()

    if kw is None and text:
        m = _KW.search(text)
        if m:
            kw = float(m.group(1).replace(",", "."))
    if phases is None and text:
        if _PHASE1.search(text) and not _PHASE3.search(text):
            phases = 1
        elif _PHASE3.search(text):
            phases = 3
    if (lat is None or lon is None) and text:
        m = _DOT_COORDS.search(text.replace(",", ".")) if "." in text else None
        lt = _LT_COORDS.search(text)
        if lt:
            lat = float(lt.group(1) + "." + lt.group(2))
            lon = float(lt.group(3) + "." + lt.group(4))
        elif _DOT_COORDS.search(text):
            dm = _DOT_COORDS.search(text)
            lat = float(dm.group(1))
            lon = float(dm.group(2))

    parse_mode: str = "form" if form.kw and form.lat and form.lon else "offline"

    if kw is None:
        kw = 11.0
        warnings.append("Galia nerasta — naudojamas hero numatytasis 11 kW.")
        tags.append("synthetic")
    if phases not in (1, 3):
        phases = 3
        warnings.append("Fazės nerastos — naudojamos 3 fazės.")
        tags.append("synthetic")
    if lat is None or lon is None:
        lat, lon = HERO_LAT, HERO_LON
        warnings.append("Koordinatės nerastos — naudojamas hero taškas prie 12-608.")
        tags.append("synthetic")
    if pending is None:
        pending = 0.0
        tags.append("synthetic")

    if not tags:
        tags.append("real")

    customer = form.customer_type or "household"
    return ParsedRequest(
        kw=float(kw),
        phases=3 if int(phases) == 3 else 1,
        lat=float(lat),
        lon=float(lon),
        customer_type=customer,
        pending_kw=float(pending or 0),
        object_name=form.object_name or "Naujas buitinis objektas",
        parse_mode=parse_mode,  # type: ignore[arg-type]
        warnings=warnings,
        source_tags=tags,  # type: ignore[arg-type]
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
