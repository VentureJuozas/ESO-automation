"""Transformer and feeder capacity. Mock = 12-608 peak. Stub = Power BI / SCADA."""
from __future__ import annotations

from typing import Any, Protocol

from eso_agent.network import STATION


class CapacityPort(Protocol):
    mode: str

    def limits(self) -> dict[str, Any]: ...
    def pending_kw(self) -> float: ...


class MockCapacity:
    mode = "mock"

    def limits(self) -> dict[str, Any]:
        return {
            "nominal_kw": STATION["nominal_kw"],
            "peak_kw": STATION["peak_kw"],
            "limit_80_kw": STATION["limit_80_kw"],
            "limit_90_kw": STATION["limit_90_kw"],
            "accounting_points": STATION["accounting_points"],
            "transformer_count": STATION["transformer_count"],
            "n1_kw": STATION["n1_kw"],
            "source": "real",
            "note": "pastotes_load_kas15min 227,7 kW; 80/90 % iš Substations_info.",
        }

    def pending_kw(self) -> float:
        return 0.0


class StubCapacity:
    mode = "stub"
    target = "Power BI free-capacity + SCADA 15 min"

    def limits(self) -> dict[str, Any]:
        raise NotImplementedError(f"Connect {self.target}")

    def pending_kw(self) -> float:
        raise NotImplementedError(f"Connect {self.target}")
