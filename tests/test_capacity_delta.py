from eso_agent.engine import run_sync_until_interrupt
from eso_agent.network import HERO_LAT, HERO_LON
from eso_agent.rules import added_demand_kw, size_breaker, usable_voltage_baseline
from eso_agent.network import load_network


def test_added_demand_excludes_existing_load():
    assert added_demand_kw(11, 5) == 6
    assert added_demand_kw(14, 0) == 14
    assert added_demand_kw(3, 3) == 0


def test_capacity_uses_increment_not_total():
    snap = run_sync_until_interrupt(
        "intake",
        delay=0,
        form={
            "kw": 11,
            "existing_kw": 5,
            "phases": 3,
            "lat": HERO_LAT,
            "lon": HERO_LON,
            "text": "Didinimas 5 → 11 kW, 3F, 54.55929, 25.27955.",
        },
    )
    assert snap["breaker"]["amps"] == 20
    assert snap["capacity"]["transformer_bar"]["added_kw"] == 6
    assert snap["capacity"]["pass"] is True
    assert snap["status"] == "awaiting_approval"


def test_synthetic_fuse_does_not_block_household():
    el = next(e for e in load_network()["elements"] if e["id"] == "KS-39685")
    snap = run_sync_until_interrupt(
        "intake",
        delay=0,
        form={
            "kw": 18,
            "phases": 3,
            "lat": el["lat"],
            "lon": el["lon"],
            "text": "18 kW 3F prie KS-39685.",
        },
    )
    assert snap["solution"]["id"] == "A"
    assert snap["capacity"]["steps"]["1c_feeder"]["source"] == "synthetic"
    assert snap["status"] == "awaiting_approval"
    assert snap["failed"] is False


def test_voltage_filters_205v_event_on_l_ks13058():
    feeder = next(f for f in load_network()["feeders"] if f["name"] == "L-KS13058")
    base = usable_voltage_baseline(feeder)
    assert base["filtered_event"] is True
    assert base["v"] == 230
    assert base["raw"] == 205
    el = next(e for e in load_network()["elements"] if e["id"] == "KS-26429")
    snap = run_sync_until_interrupt(
        "intake",
        delay=0,
        form={
            "kw": 3,
            "existing_kw": 0,
            "phases": 1,
            "lat": el["lat"],
            "lon": el["lon"],
            "text": "3 kW vienfazis prie KS-26429.",
        },
    )
    assert snap["quality"]["filtered_event"] is True
    assert snap["quality"]["escalate"] is False
    assert size_breaker(3, 1)["amps"] == 16
