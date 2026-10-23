"""Pricing catalogue. Mock = 26-E-37934 rates. Stub = official tariff service."""
from __future__ import annotations

from typing import Any, Protocol

from eso_agent import rules


class PricingPort(Protocol):
    mode: str

    def rates(self) -> dict[str, Any]: ...


class MockPricing:
    mode = "mock"

    def rates(self) -> dict[str, Any]:
        return {
            "breaker_3f": rules.COST_BREAKER_3F_INSTALL,
            "ks_kas": rules.COST_KS_KAS,
            "cable_4x150_per_m": rules.COST_CABLE_4X150_PER_M,
            "termination_4x150": rules.COST_TERMINATION_4X150,
            "design": rules.COST_DESIGN,
            "labour_share": rules.CAPITALISED_LABOUR_RATE,
            "vat": rules.VAT_RATE,
            "source": "real",
            "note": "Orientyras iš 26-E-37934 (kita savivaldybė).",
        }


class StubPricing:
    mode = "stub"
    target = "Prijungimo įkainių metodika / SAP"

    def rates(self) -> dict[str, Any]:
        raise NotImplementedError(f"Connect {self.target}")
