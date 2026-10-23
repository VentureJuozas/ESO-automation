"""Architecture, tool catalogue and next-steps copy for the dashboard and docs."""
from __future__ import annotations

from eso_agent.llm import llm_mode
from eso_agent.rules import MANUAL_TIME_ASSUMPTION_NOTE

ESO_PROCESS = "https://www.eso.lt/apie-mus/ataskaitos-ir-dokumentai/3111#c3853"
ESO_STANDARD = "https://www.eso.lt/partneriams/partneriams-rangovams/elektros-darbu-rangovams-ir-tiekejams/techniniai-reikalavimai/4216#c2479"
ESO_VOLTAGE = "https://www.eso.lt/verslui/elektra/elektros-planiniai-atjungimai-ir-itampos-svyravimai/itampos-kokybe/4033"

TOOLS = [
    {
        "id": "parse_request",
        "title": "parse_request",
        "title_lt": "Paraiškos skaitymas",
        "kind": "llm",
        "inputs": "Laisvas tekstas ir/ar forma: kW, 1F/3F, koordinatės",
        "outputs": "Sutvarkyti laukai, terminas (3 d.d. jei ≤250 kW)",
        "rule": "KNOWLEDGE.md §5 terminai; dokumentai demonstracijoje laikomi pateiktais",
        "rule_ref": {"label": "Prijungimo sąlygų nustatymas (ESO)", "url": ESO_PROCESS, "local": "data/sources/02_eso_prijungimo_saligu_nustatymas_page.md"},
        "engineer": "Patikrinkite galią, fazes ir koordinates prieš leisdami eigą toliau.",
        "data": "Paraiška (sintetinė). Asmens duomenų nėra.",
    },
    {
        "id": "locate_connection_point",
        "title": "locate_connection_point",
        "title_lt": "Prijungimo taškas",
        "kind": "tool",
        "inputs": "lat, lon",
        "outputs": "Artimiausia atrama/spinta, linija, atstumai, taškų skaičius",
        "rule": "Artimiausias tinklo elementas",
        "rule_ref": {"label": "Prijungimo sąlygų nustatymas — tinklo parinkimas", "url": ESO_PROCESS, "local": "data/SCOPE.md"},
        "engineer": "Artimiausia atrama/spinta be kliento adreso. Jei smeigtukas ne ten — taisykite koordinates.",
        "data": "Sintetinės atramų/spintų koordinatės iš README rėmo; suvestinės iš Objects_network_power (real)",
    },
    {
        "id": "select_solution",
        "title": "select_solution",
        "title_lt": "Sprendinys A/B/C",
        "kind": "tool",
        "inputs": "Linijos tipas, elemento rūšis, atstumas, ar spinta sklype",
        "outputs": "A esama KS, B KAS ant atramos, C įsipjovimas; kabelio mm²",
        "rule": "SCOPE.md sprendinių lentelė",
        "rule_ref": {"label": "Technologinės plėtros standartas", "url": ESO_STANDARD, "local": "data/SCOPE.md"},
        "engineer": "Palyginkite A/B/C: kodėl laimėjo pasirinktas ir kodėl kiti netinka.",
        "data": "Feeder type from 12-608 topology",
    },
    {
        "id": "size_breaker",
        "title": "size_breaker",
        "title_lt": "Jungiklis",
        "kind": "tool",
        "inputs": "kW, fazės",
        "outputs": "C charakteristikos amperai",
        "rule": "KNOWLEDGE.md §15 Srovės transf. įvertinimas",
        "rule_ref": {"label": "Skaičiuoklė — srovės transf. įvertinimas", "url": ESO_STANDARD, "local": "data/KNOWLEDGE.md"},
        "engineer": "11 kW 3F → 20 A. Palyginkite su istoriniais TS (13/14 sutapo).",
        "data": "Skaičiuoklės lentelė (rule)",
    },
    {
        "id": "check_capacity",
        "title": "check_capacity",
        "title_lt": "Pajėgumas",
        "kind": "tool",
        "inputs": "kW, linija, viršūnė, jungiklis",
        "outputs": "1a–1d: jungiklis, spintos saugiklis, Isk vs fuse, TR 80/90 %",
        "rule": "SCOPE 1a–1d; nesutapimo k. feederiui; TR = viršūnė + kW vs 320/360",
        "rule_ref": {"label": "Prijungimo sąlygų nustatymas — pajėgumas", "url": ESO_PROCESS, "local": "data/SCOPE.md"},
        "engineer": "Žiūrėkite TR juostą: viršūnė prieš/po, 80 % ir 90 % brūkšnius.",
        "data": "pastotes_load_kas15min 227,7 kW (real); fuse 315 A L-KS14330 (real); kiti fuse synthetic",
    },
    {
        "id": "check_voltage_drop",
        "title": "check_voltage_drop",
        "title_lt": "Kokybė",
        "kind": "tool",
        "inputs": "Laidininkas, ilgis, kW",
        "outputs": "ΔU %, V po prijungimo, 2c taisyklės (600 m / 80 kW)",
        "rule": "LST EN 50160 ≥207 V; skaičiuoklė nuo 2018; 12 priedo ištraukos",
        "rule_ref": {"label": "Įtampos kokybė (LST EN 50160)", "url": ESO_VOLTAGE, "local": "data/sources/04_eso_itampos_kokybe_page.md"},
        "engineer": "Profilis palei liniją. Hero L-200: išmatuotos min. nėra — 230 V tik palyginimui.",
        "data": "min_itampa suvestinės (real, su filtrais); laidininkas/ilgis synthetic+inferred",
    },
    {
        "id": "check_reliability",
        "title": "check_reliability",
        "title_lt": "Patikimumas",
        "kind": "tool",
        "inputs": "TR skaičius, sprendinys, linija",
        "outputs": "N-1, radialumas, C atveju atjungiamų taškų skaičius",
        "rule": "SCOPE 3a–3c",
        "rule_ref": {"label": "Prijungimo sąlygų nustatymas — patikimumas", "url": ESO_PROCESS, "local": "data/SCOPE.md"},
        "engineer": "N-1 rezervas nulinis. C atveju — kiek apskaitos taškų atjungiama įsipjovimui.",
        "data": "transformer_count=1, N-1=400 kW (real); taškai pagal liniją (real)",
    },
    {
        "id": "check_future",
        "title": "check_future",
        "title_lt": "Ateitis",
        "kind": "tool",
        "inputs": "Rezervuota kW, atsarga iki 80 %",
        "outputs": "Likutis kitiems, teritorijų planai = nėra info",
        "rule": "SCOPE 4a–4c",
        "rule_ref": {"label": "Prijungimo sąlygų nustatymas — ateitis", "url": ESO_PROCESS, "local": "data/SCOPE.md"},
        "engineer": "Atsargos matuoklis iki 80 %. Rezervacijos šiame demo = 0 kW (nėra Power BI).",
        "data": "Rezervacijos default 0 kW (synthetic); TR serija real",
    },
    {
        "id": "draft_ts_section3",
        "title": "draft_ts_section3",
        "title_lt": "TS §3 juodraštis",
        "kind": "llm",
        "inputs": "Sprendinys, jungiklis, linija, elementas",
        "outputs": "§3 tekstas, vandenženklis PROJEKTAS",
        "rule": "Uždaras veiksmų rinkinys iš pavyzdinių TS",
        "rule_ref": {"label": "Prijungimo sąlygų nustatymas — sąlygų turinys", "url": ESO_PROCESS, "local": "data/case_26-E-37536/case_summary.md"},
        "engineer": "Kairėje juodraštis, dešinėje oficialus maketas. Skaičių nekeiskite be perskaičiavimo.",
        "data": "case_26-E-37536, 26-E-37934, ts_history_redacted",
    },
    {
        "id": "estimate_cost",
        "title": "estimate_cost",
        "title_lt": "Sąmata",
        "kind": "tool",
        "inputs": "Sprendinys, kabelio m",
        "outputs": "Eilutės, darbas 11,78 %, PVM 21 %",
        "rule": "Kainos = orientyras",
        "rule_ref": {"label": "Prijungimo įkainių metodika (orientyras 26-E-37934)", "url": ESO_PROCESS, "local": "data/case_26-E-37934/cost_estimate_26-E-37934.md"},
        "engineer": "Eilutės iš 26-E-37934. 16 mm² neturi kainos — neįtraukiama į darbų bazę.",
        "data": "cost_estimate_26-E-37934.md (real rates, other municipality)",
    },
    {
        "id": "render_map",
        "title": "render_map",
        "title_lt": "Žemėlapis",
        "kind": "tool",
        "inputs": "Paraiškos koordinatės, parinktas elementas",
        "outputs": "TP, linijos, atramos/spintos, smeigtukas",
        "rule": "GIS priedas prie TS",
        "rule_ref": {"label": "Techniniai reikalavimai", "url": ESO_STANDARD, "local": "data/substation_12-608/README.md"},
        "engineer": "Smeigtukas = paraiška, ryškus taškas = parinktas elementas. Be adresų.",
        "data": "Sintetinė topologija; jokio PII",
    },
    {
        "id": "request_missing_data",
        "title": "request_missing_data",
        "title_lt": "Trūkstami duomenys",
        "kind": "human",
        "inputs": "Laukai, kurių parseris ar GIS nerado",
        "outputs": "Sąrašas, kam rašyti, laiško peržiūra, laikinas A/B/C",
        "rule": "Be privalomos įvesties eiga nestabdoma tyloje — prašoma duomenų",
        "rule_ref": {"label": "Prijungimo sąlygų nustatymas — paraiška", "url": ESO_PROCESS, "local": "data/SCOPE.md"},
        "engineer": "Peržiūrėkite laišką. Nieko nesiunčiame. Užpildę laukus tęskite drobėje.",
        "data": "Sintetinės spragos. Be asmens duomenų.",
    },
    {
        "id": "engineer_approval",
        "title": "engineer_approval",
        "title_lt": "Inžinieriaus patvirtinimas",
        "kind": "human",
        "inputs": "Juodraštis, patikros, sąmata",
        "outputs": "approve / edit / escalate-ack",
        "rule": "Žmogus visada išduoda sąlygas",
        "rule_ref": {"label": "Prijungimo sąlygų nustatymas — išdavimas", "url": ESO_PROCESS, "local": "data/case_26-E-37536/case_summary.md"},
        "engineer": "Patvirtinkite, pataisykite §3 arba grąžinkite perskaičiuoti. Be šio žingsnio sąlygos neišduodamos.",
        "data": "Inžinieriaus sprendimas",
    },
    {
        "id": "escalate",
        "title": "escalate",
        "title_lt": "Perdavimas inžinieriui",
        "kind": "tool",
        "inputs": "Nepraėjusios patikros",
        "outputs": "Priežastis ir kita pakopa (4–6)",
        "rule": "SCOPE: jei patikra nepraeina — stabdyti ir perduoti",
        "rule_ref": {"label": "Prijungimo sąlygų nustatymas", "url": ESO_PROCESS, "local": "data/SCOPE.md"},
        "engineer": "Perskaitykite priežastį. 4–6 pakopos šiame demo neįgyvendintos.",
        "data": "Patikrų rezultatai",
    },
    {
        "id": "issue_ts",
        "title": "issue_ts",
        "title_lt": "Sąlygų išdavimas",
        "kind": "tool",
        "inputs": "Patvirtintas juodraštis",
        "outputs": "Numeris, parengta, galioja iki (+1 m.)",
        "rule": "Galiojimas = parengimo data + 1 metai",
        "rule_ref": {"label": "Prijungimo sąlygų nustatymas", "url": ESO_PROCESS, "local": "data/case_26-E-37934/ts_output_template.md"},
        "engineer": "Atsisiųskite / spausdinkite. Kliento laukai redaguoti.",
        "data": "Inžinieriaus patvirtinimas",
    },
]


def tool_by_id(tool_id: str) -> dict:
    for t in TOOLS:
        if t["id"] == tool_id:
            return t
    return {"id": tool_id, "title_lt": tool_id, "kind": "tool"}


NEXT_STEPS = [
    {
        "id": "data",
        "title": "Real ESO data sources",
        "items": [
            "Power BI exports: free transformer capacity, 35–10 kV line loads, reserved consumption capacity",
            "Internal TR load tool (currently only on the hackathon network)",
            "SharePoint folder of issued TS examples for template variants",
            "Replace synthetic poles/cabinets with Objects_network_power.csv once a redacted coordinate extract is approved",
        ],
    },
    {
        "id": "standard",
        "title": "Authoritative standard annexes",
        "items": [
            "Ingest the actual Technologinės plėtros standartas PDFs (annex 12 for 0.4 kV lines and the rest)",
            "Replace unverified 600 m / 80 kW snippets with the signed rule text",
            "Load full Kofai diversity sheets rather than the extracted arrays",
        ],
    },
    {
        "id": "ladder",
        "title": "Upgrade ladder rungs 4–6",
        "items": [
            "Feeder reinforcement when Isk exceeds the fuse",
            "Transformer swap when 80%/90% limits fail",
            "New transformer station / 10 kV works",
            "Generation and storage (reverse power, LGG)",
        ],
    },
    {
        "id": "voltage",
        "title": "Full voltage-drop path",
        "items": [
            "Real conductor type and length per segment (not inferred geodesics)",
            "Per-meter usable min voltage after event filters, all three phases",
            "Short-circuit current and selectivity as a blocking check",
        ],
    },
    {
        "id": "integration",
        "title": "ESO systems and evaluation",
        "items": [
            "Read applications from the official queue (proper-submission clock)",
            "Write the issued TS and GIS annex back to the document store",
            "Engineer feedback loop: corrections like 26-E-37536, then re-issue",
            "Backtest against the 14 historical TS on 12-608 (breaker table already 13/14)",
        ],
    },
    {
        "id": "security",
        "title": "Security and privacy",
        "items": [
            "Keep customer personal data out of prompts, logs and maps",
            "Role-based access for the approval gate",
            "Audit trail as an immutable record, not only in-memory demo state",
        ],
    },
]


def architecture_payload() -> dict:
    from eso_agent.adapters import adapter_catalog, adapter_mode

    return {
        "llm_mode": llm_mode(),
        "adapter_mode": adapter_mode(),
        "adapters": adapter_catalog(),
        "manual_time_note": MANUAL_TIME_ASSUMPTION_NOTE,
        "tools": TOOLS,
        "next_steps": NEXT_STEPS,
        "principles": [
            "Deterministic Python makes every engineering decision.",
            "The LLM only parses free text and phrases TS wording.",
            "Every number is tagged real / rule / inferred / synthetic.",
            "The engineer always approves or edits before issue.",
            "No customer personal data in the demo.",
        ],
        "layers": [
            {"id": "ui", "title": "Dashboard", "note": "Orchestrator / manager view (Lithuanian)"},
            {"id": "api", "title": "FastAPI", "note": "REST + SSE tool-call events"},
            {"id": "graph", "title": "LangGraph", "note": "Ordered nodes, interrupt at approval"},
            {"id": "tools", "title": "Deterministic tools", "note": "Breaker, locate, A/B/C, four checks, cost, map"},
            {"id": "data", "title": "12-608 + rules", "note": "README/summary + tagged synthetic fixtures"},
            {"id": "human", "title": "Engineer gate", "note": "Approve, edit §3, or rerun a step"},
        ],
    }
