"""GIS / network topology. Mock = synthetic 12-608. Stub = real ESO GIS."""
from __future__ import annotations

from typing import Any, Protocol

from eso_agent import network as net


class GisPort(Protocol):
    mode: str

    def load_network(self) -> dict[str, Any]: ...
    def nearest(self, lat: float, lon: float) -> dict[str, Any]: ...
    def element(self, eid: str) -> dict[str, Any]: ...
    def station(self) -> dict[str, Any]: ...


class MockGis:
    mode = "mock"

    def load_network(self) -> dict[str, Any]:
        return net.load_network()

    def nearest(self, lat: float, lon: float) -> dict[str, Any]:
        return net.nearest_element(lat, lon)

    def element(self, eid: str) -> dict[str, Any]:
        return net.element_by_id(eid)

    def station(self) -> dict[str, Any]:
        return dict(net.STATION)


class StubGis:
    """Documented hook for ESO GIS. Not wired — do not call in the demo."""

    mode = "stub"
    target = "ESO GIS / redacted Objects_network_power.csv"

    def load_network(self) -> dict[str, Any]:
        raise NotImplementedError(f"Connect {self.target}")

    def nearest(self, lat: float, lon: float) -> dict[str, Any]:
        raise NotImplementedError(f"Connect {self.target}")

    def element(self, eid: str) -> dict[str, Any]:
        raise NotImplementedError(f"Connect {self.target}")

    def station(self) -> dict[str, Any]:
        raise NotImplementedError(f"Connect {self.target}")
