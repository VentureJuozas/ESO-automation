from eso_agent.engine import approve_sync, run_sync_until_interrupt
from eso_agent.network import HERO_LAT, HERO_LON, nearest_element
from eso_agent.rules import size_breaker


def test_hero_locates_pole_200_3():
    found = nearest_element(HERO_LAT, HERO_LON)
    assert found["element"]["id"] == "200/3"
    assert found["feeder"]["name"] == "L-200"
    assert found["element"]["kind"] == "pole"
    assert found["distance_m"] < 25
    assert found["to_station_m"] < 80


def test_hero_run_to_approval():
    snap = run_sync_until_interrupt("hero", delay=0)
    assert snap["status"] == "awaiting_approval"
    assert snap["failed"] is False
    assert snap["solution"]["id"] == "B"
    assert snap["breaker"]["amps"] == 20
    assert snap["location"]["element_id"] == "200/3"
    assert snap["location"]["feeder"] == "L-200"
    assert snap["capacity"]["pass"] is True
    assert snap["quality"]["pass"] is True
    assert snap["reliability"]["pass"] is True
    assert snap["future"]["pass"] is True
    assert snap["draft"]["section3"]
    assert "200/3" in snap["draft"]["section3"]
    assert "20 A" in snap["draft"]["section3"]
    assert snap["cost"]["net"] > 0
    assert snap["map"]["selected"]["id"] == "200/3"
    tools = [e["tool"] for e in snap["events"] if e.get("type") == "tool"]
    for name in (
        "parse_request",
        "locate_connection_point",
        "select_solution",
        "size_breaker",
        "check_capacity",
        "check_voltage_drop",
        "check_reliability",
        "check_future",
        "draft_ts_section3",
        "estimate_cost",
        "render_map",
    ):
        assert name in tools
    assert any(e.get("type") == "interrupt" for e in snap["events"])
    # no blocked empty inputs
    assert snap["quality"]["conductor"]
    assert snap["quality"]["length_m"] > 0
    assert snap["capacity"]["transformer_bar"]["after_kw"] == 238.7
    issued = approve_sync(snap["id"])
    assert issued["status"] == "issued"
    assert issued["issued"]["issue_date"]
    assert issued["issued"]["valid_until"]
    assert issued["issued"]["ts_number"].startswith("26-E-DEMO-")


def test_hero_breaker_from_table():
    assert size_breaker(11, 3)["amps"] == 20
