import inspect

from eso_agent.adapters import adapter_catalog, get_adapters, reset_adapters
from eso_agent.adapters.capacity import MockCapacity, StubCapacity
from eso_agent.adapters.crm import MockCrm, StubCrm
from eso_agent.adapters.gis import MockGis, StubGis
from eso_agent.adapters.pricing import MockPricing, StubPricing
from eso_agent.adapters.registry import MockRegistry, StubRegistry


def _methods(cls):
    return {n for n, v in inspect.getmembers(cls, predicate=inspect.isfunction) if not n.startswith("_")}


def test_stub_matches_mock_contract():
    pairs = [
        (MockGis, StubGis),
        (MockCapacity, StubCapacity),
        (MockCrm, StubCrm),
        (MockPricing, StubPricing),
        (MockRegistry, StubRegistry),
    ]
    for mock, stub in pairs:
        assert mock.mode == "mock"
        assert stub.mode == "stub"
        assert _methods(mock) == _methods(stub)


def test_mock_gis_and_capacity_serve_12_608():
    reset_adapters()
    a = get_adapters()
    assert a.mode == "mock"
    net = a.gis.load_network()
    assert net["substation"]["id"] == "12-608"
    near = a.gis.nearest(54.55929, 25.27955)
    assert near["element"]["id"] == "200/3"
    lim = a.capacity.limits()
    assert lim["peak_kw"] == 227.7
    assert lim["limit_80_kw"] == 320
    assert a.pricing.rates()["vat"] == 0.21
    cat = adapter_catalog()
    assert {c["id"] for c in cat} == {"gis", "capacity", "crm", "pricing", "registry"}
    assert all(c["status"] == "mock" for c in cat)
