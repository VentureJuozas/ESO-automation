"""Production-path adapters. Demo uses mocks; stubs document the real ESO systems."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from eso_agent.adapters.capacity import CapacityPort, MockCapacity, StubCapacity
from eso_agent.adapters.crm import CrmPort, MockCrm, StubCrm
from eso_agent.adapters.gis import GisPort, MockGis, StubGis
from eso_agent.adapters.pricing import MockPricing, PricingPort, StubPricing
from eso_agent.adapters.registry import MockRegistry, RegistryPort, StubRegistry

Mode = Literal["mock", "stub"]


@dataclass
class Adapters:
    gis: GisPort
    capacity: CapacityPort
    crm: CrmPort
    pricing: PricingPort
    registry: RegistryPort
    mode: Mode


_BUNDLE: Adapters | None = None


def adapter_mode() -> Mode:
    raw = (os.environ.get("ESO_ADAPTERS") or "mock").lower()
    return "stub" if raw == "stub" else "mock"


def get_adapters() -> Adapters:
    global _BUNDLE
    if _BUNDLE is not None:
        return _BUNDLE
    mode = adapter_mode()
    if mode == "stub":
        _BUNDLE = Adapters(
            gis=StubGis(),
            capacity=StubCapacity(),
            crm=StubCrm(),
            pricing=StubPricing(),
            registry=StubRegistry(),
            mode="stub",
        )
    else:
        _BUNDLE = Adapters(
            gis=MockGis(),
            capacity=MockCapacity(),
            crm=MockCrm(),
            pricing=MockPricing(),
            registry=MockRegistry(),
            mode="mock",
        )
    return _BUNDLE


def reset_adapters() -> None:
    global _BUNDLE
    _BUNDLE = None


def adapter_catalog() -> list[dict]:
    a = get_adapters()
    return [
        {
            "id": "gis",
            "title": "GIS / topologija",
            "real_system": "ESO GIS + Objects_network_power",
            "mode": a.gis.mode,
            "supplies": "TP 12-608, linijos, atramos, spintos, atstumai",
            "consumed_by": ["locate_connection_point", "select_solution", "render_map", "check_voltage_drop"],
            "status": "mock" if a.gis.mode == "mock" else "stub",
        },
        {
            "id": "capacity",
            "title": "Power BI / SCADA pajėgumas",
            "real_system": "Power BI + 15 min SCADA (pastotes_load)",
            "mode": a.capacity.mode,
            "supplies": "Viršūnė 227,7 kW, 80/90 % ribos, rezervuotos kW",
            "consumed_by": ["check_capacity", "check_future"],
            "status": "mock" if a.capacity.mode == "mock" else "stub",
        },
        {
            "id": "crm",
            "title": "Klientų portalas / CRM",
            "real_system": "ESO savitarna + paraiškų eilė",
            "mode": a.crm.mode,
            "supplies": "Paraiška, būsena, trūkstamų duomenų atsakymas",
            "consumed_by": ["parse_request", "request_missing_data", "issue_ts"],
            "status": "mock" if a.crm.mode == "mock" else "stub",
        },
        {
            "id": "pricing",
            "title": "Kainų katalogas",
            "real_system": "Prijungimo įkainių metodika / SAP",
            "mode": a.pricing.mode,
            "supplies": "Orientyrinės eilutės, PVM, kapitalizuotas darbas",
            "consumed_by": ["estimate_cost"],
            "status": "mock" if a.pricing.mode == "mock" else "stub",
        },
        {
            "id": "registry",
            "title": "TS registras",
            "real_system": "SharePoint / dokumentų saugykla",
            "mode": a.registry.mode,
            "supplies": "Išduotos TS numeris, PDF, SHA-256",
            "consumed_by": ["issue_ts", "audit"],
            "status": "mock" if a.registry.mode == "mock" else "stub",
        },
    ]
