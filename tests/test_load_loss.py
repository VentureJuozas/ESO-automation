from eso_agent.engine import run_sync_until_interrupt
from eso_agent.load_loss import estimate_load_loss
from eso_agent.network import load_network


def test_estimator_before_after_hero():
    net = load_network()
    feeder = next(f for f in net["feeders"] if f["name"] == "L-200")
    out = estimate_load_loss(
        feeder,
        connection_id="200/3",
        added_kw=11.0,
        peak_before_kw=227.7,
        peak_after_kw=238.7,
    )
    assert out["line"]["after"]["isk_a"] >= out["line"]["before"]["isk_a"]
    assert out["feeder_loss"]["after_kw"] >= out["feeder_loss"]["before_kw"]
    assert out["transformer_loss"]["after"]["total_kw"] >= out["transformer_loss"]["before"]["total_kw"]
    assert out["to_customer"]
    assert out["to_customer"][-1]["id"] == "200/3"
    assert out["ampacity_a"] == 160
    assert "3 × Isk" in out["formula"]["feeder_loss"]


def test_hero_capacity_and_voltage_carry_load_loss():
    snap = run_sync_until_interrupt("hero", delay=0)
    cap = snap["capacity"]
    volt = snap["quality"]
    assert cap["load_loss"]["line"]["after"]["isk_a"] > 0
    assert volt["load_loss"]["to_customer"][-1]["id"] == "200/3"
    assert cap["load_loss"]["feeder_loss"]["after_kwh_year"] > 0
