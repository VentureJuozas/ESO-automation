"""Frozen presentation pack — no live timing, no network."""
from __future__ import annotations

from typing import Any

BEATS: list[dict[str, Any]] = [
    {
        "id": "split",
        "view": "split",
        "spot": "split",
        "lt": {
            "title": "Klientas ir stalas",
            "say": "Kairėje — demonstracinis klientų maketas. Dešinėje — vadovo eilė. Paraiška įeina, TS išeina per minutes, ne dienas.",
        },
        "en": {
            "title": "Customer and desk",
            "say": "Left: a demo customer mock. Right: the manager desk. A request goes in, a TS comes out in minutes, not days.",
        },
        "dwell_ms": 20000,
    },
    {
        "id": "desk",
        "view": "queue",
        "spot": "hud",
        "lt": {
            "title": "Vadovo eilė",
            "say": "Tai stalas, ne pokalbių robotas. Dvylika redaguotų 12-608 paraiškų. SLA — trys darbo dienos.",
        },
        "en": {
            "title": "Manager desk",
            "say": "This is a desk, not a chatbot. Twelve redacted 12-608 applications. SLA is three working days.",
        },
        "dwell_ms": 5000,
    },
    {
        "id": "batch",
        "view": "queue",
        "spot": "table",
        "apply": "queue_after",
        "lt": {
            "title": "Paleisti visas",
            "say": "Vienas mygtukas paleidžia LangGraph. Python priima sprendimus. LLM tik skaito tekstą. Replay užšaldytas — nelaukiame tinklo.",
        },
        "en": {
            "title": "Run all",
            "say": "One click runs LangGraph. Python decides. The LLM only reads text. This replay is frozen — no network wait.",
        },
        "dwell_ms": 25000,
    },
    {
        "id": "inbox",
        "view": "queue",
        "spot": "inbox",
        "apply": "queue_after",
        "lt": {
            "title": "Pašto dėžutė",
            "say": "A/B/C laukia inžinieriaus. Eskalacijos neišduodamos. Patvirtinti, taisyti §3 arba override su priežastimi.",
        },
        "en": {
            "title": "Engineer inbox",
            "say": "A/B/C wait for an engineer. Fails do not issue. Approve, edit §3, or override with a reason.",
        },
        "dwell_ms": 25000,
    },
    {
        "id": "hero_map",
        "view": "case",
        "spot": "canvas",
        "apply": "hero",
        "select": "render_map",
        "lt": {
            "title": "Hero drobė · žemėlapis",
            "say": "11 kW, 3F, atrama 200/3. Žemėlapis — mūsų geometrija. Plytelių serveris nebūtinas.",
        },
        "en": {
            "title": "Hero canvas · map",
            "say": "11 kW, 3-phase, pole 200/3. The map is our geometry. Tile servers are optional.",
        },
        "dwell_ms": 20000,
    },
    {
        "id": "hero_abc",
        "view": "case",
        "apply": "hero",
        "select": "select_solution",
        "lt": {
            "title": "Sprendinys B",
            "say": "Oro linija, spintos sklype nėra — nauja KAS ant atramos ir 16 mm². A ir C atmesti taisykle, ne LLM.",
        },
        "en": {
            "title": "Solution B",
            "say": "Overhead feeder, no cabinet on the plot — new pole KAS and 16 mm². A and C are ruled out by the table, not the LLM.",
        },
        "dwell_ms": 15000,
    },
    {
        "id": "hero_cap",
        "view": "case",
        "apply": "hero",
        "select": "check_capacity",
        "lt": {
            "title": "Pajėgumas",
            "say": "227,7 + 11 = 238,7 kW. 80 % riba 320 kW. Keturios patikros žalios.",
        },
        "en": {
            "title": "Capacity",
            "say": "227.7 + 11 = 238.7 kW. The 80 % limit is 320 kW. All four checks pass.",
        },
        "dwell_ms": 15000,
    },
    {
        "id": "hero_ts",
        "view": "case",
        "apply": "hero",
        "select": "draft_ts_section3",
        "lt": {
            "title": "TS §3",
            "say": "Sąlygų tekstas lieka lietuviškas. Skaičiai iš įrankių. Inžinierius visada pasirašo.",
        },
        "en": {
            "title": "TS §3",
            "say": "The conditions document stays Lithuanian. Numbers come from tools. An engineer always signs.",
        },
        "dwell_ms": 20000,
    },
    {
        "id": "fail",
        "view": "case",
        "apply": "fail",
        "select": "escalate",
        "lt": {
            "title": "Fail kelias",
            "say": "100 kW: 327,7 prieš 320. Šaka į escalate. Produktas — stiprinimo paketas: 400→630 kVA.",
        },
        "en": {
            "title": "Fail path",
            "say": "100 kW: 327.7 vs 320. The graph branches to escalate. The product is a reinforcement brief: 400→630 kVA.",
        },
        "dwell_ms": 25000,
    },
    {
        "id": "gallery",
        "view": "gallery",
        "spot": "taxonomy",
        "apply": "gallery",
        "lt": {
            "title": "Galerija",
            "say": "Šešiolika išduotų TS. In-scope 95 %, visų 84 %. 51 % buvo prieaugis vietoj sumos. Įrankio klaidų — nulis.",
        },
        "en": {
            "title": "Gallery",
            "say": "Sixteen issued files. In-scope 95 %, overall 84 %. The old 51 % sized the increment, not the total. Tool errors: zero.",
        },
        "dwell_ms": 30000,
    },
    {
        "id": "audit",
        "view": "case",
        "apply": "hero",
        "select": "engineer_approval",
        "spot": "audit",
        "lt": {
            "title": "Auditas",
            "say": "Kiekvienas įrankis, įvestys, tagai, override, SHA-256. Išlieka po restarto — SQLite.",
        },
        "en": {
            "title": "Audit",
            "say": "Every tool, inputs, tags, overrides, SHA-256. Survives a restart — SQLite.",
        },
        "dwell_ms": 20000,
    },
    {
        "id": "integrations",
        "view": "integrations",
        "spot": "canvas",
        "lt": {
            "title": "Integracijos",
            "say": "Penki adapteriai: GIS, Power BI, CRM, kainos, TS registras. Šiandien mock. Stubai rodo kelią į ESO sistemas.",
        },
        "en": {
            "title": "Integrations",
            "say": "Five adapters: GIS, Power BI, CRM, pricing, TS registry. Today they are mocks. Stubs show the path to ESO systems.",
        },
        "dwell_ms": 20000,
    },
    {
        "id": "time",
        "view": "case",
        "apply": "hero",
        "spot": "time",
        "lt": {
            "title": "Sutaupytas laikas",
            "say": "Replay milisekundės prieš 2–4 val. prielaidą. 40 bylų per mėnesį — ne ESO statistika.",
        },
        "en": {
            "title": "Time saved",
            "say": "Replay milliseconds versus a 2–4 hour assumption. Forty cases a month is not ESO statistics.",
        },
        "dwell_ms": 30000,
    },
]

TOTAL_MS = sum(int(b.get("dwell_ms") or 0) for b in BEATS)

_PACK: dict[str, Any] | None = None


def frozen_pack() -> dict[str, Any]:
    global _PACK
    if _PACK:
        return _PACK
    from eso_agent.audit import build_audit
    from eso_agent.backtest import LAST_GALLERY, run_gallery
    from eso_agent.engine import RUNS, run_sync_until_interrupt
    from eso_agent.queue import queue_public, reset_queue

    hero = run_sync_until_interrupt("hero", delay=0)
    fail = run_sync_until_interrupt("fail_capacity", delay=0)
    gallery = LAST_GALLERY or run_gallery()
    reset_queue()
    before = queue_public()
    # Frozen "after batch" without waiting: mark mix cases from the two snaps + placeholders
    after = queue_public()
    for c in after["cases"]:
        if c["mix"] == "missing":
            c["status"] = "waiting_data"
        elif c["mix"] == "fail":
            c["status"] = "escalated"
            c["brief_title"] = "Stiprinimo paketas"
        else:
            c["status"] = "awaiting_approval"
            c["solution"] = c.get("mix")
        c["run_id"] = hero["id"] if c["id"] == "q01" else c.get("run_id")
    after["inbox"] = [c for c in after["cases"] if c["status"] in {"awaiting_approval", "escalated", "waiting_data"}]
    hud = dict(after.get("hud") or {})
    hud.update(
        {
            "new": 0,
            "running": 0,
            "processed": sum(1 for c in after["cases"] if c["status"] in {"awaiting_approval", "escalated"}),
            "inbox_depth": len(after["inbox"]),
            "assumption": True,
        }
    )
    after["hud"] = hud
    hero_run = RUNS.get(hero["id"])
    audit = build_audit(hero_run) if hero_run else {"sha256": ""}
    _PACK = {
        "beats": BEATS,
        "hero": hero,
        "fail": fail,
        "gallery": gallery,
        "queue_before": before,
        "queue_after": after,
        "audit": {"sha256": audit.get("sha256"), "tool_count": len(audit.get("tools") or [])},
        "autoplay_ms": BEATS[0]["dwell_ms"],
        "total_ms": TOTAL_MS,
        "frozen": True,
        "note": "Užšaldytas replay. Jokio tinklo, jokio rakto.",
    }
    return _PACK


def reset_pack() -> None:
    global _PACK
    _PACK = None
