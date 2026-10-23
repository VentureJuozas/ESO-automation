"""Hand-calculated hero checks for the L-200 load / loss estimator."""
from eso_agent.engine import run_sync_until_interrupt
from eso_agent.load_loss import (
    AMPACITY_A,
    TR_P0_KW,
    TR_PK_KW,
    TR_SN_KVA,
    equivalent_hours,
    estimate_load_loss,
    feeder_path,
    feeder_peak_kw,
    loss_factor,
)
from eso_agent.network import HERO_LAT, HERO_LON, load_network
from line_load import AMPERE_DIVISOR, IMPEDANCE, evaluate


def _hero_feeder():
    return next(f for f in load_network()["feeders"] if f["name"] == "L-200")


def _estimate(added_kw=11.0, peak_after_kw=238.7):
    return estimate_load_loss(
        _hero_feeder(),
        connection_id="200/3",
        added_kw=added_kw,
        peak_before_kw=227.7,
        peak_after_kw=peak_after_kw,
    )


def test_hero_feeder_current_from_meter_peak_not_transformer():
    feeder = _hero_feeder()
    p_before = feeder_peak_kw(feeder)
    assert p_before == 79.3
    p_after = p_before + 11.0
    i_before = 79.3 / 0.624
    i_after = 90.3 / 0.624
    assert abs(i_before - 127.08333333333333) < 1e-9
    assert abs(i_after - 144.71153846153845) < 1e-9
    out = _estimate()
    assert out["feeder_peak_kw"] == 79.3
    assert out["feeder_peak_after_kw"] == 90.3
    assert out["line"]["before"]["p_kw"] == 79.3
    assert out["line"]["after"]["p_kw"] == 90.3
    assert out["line"]["before"]["isk_a"] == round(i_before, 1) == 127.1
    assert out["line"]["after"]["isk_a"] == round(i_after, 1) == 144.7
    assert out["line"]["after"]["load_pct"] == round(100.0 * i_after / 160.0, 1) == 90.4
    assert out["line"]["after"]["load_pct"] < 100
    assert out["ampacity_a"] == AMPACITY_A["4A-50"] == 160


def test_hero_i2r_three_phase_ohm_per_km_on_customer_span():
    feeder = _hero_feeder()
    path = feeder_path(feeder)
    customer_idx = next(i for i, seg in enumerate(path) if seg["id"] == "200/3")
    n = len(path)
    r_per_km = IMPEDANCE["4A-50"]
    assert r_per_km == 1.44
    assert AMPERE_DIVISOR == 0.624
    loss_before = 0.0
    loss_after = 0.0
    for i, seg in enumerate(path[: customer_idx + 1]):
        remain = (n - i) / n
        i_b = (79.3 * remain) / 0.624
        i_a = (79.3 * remain + 11.0) / 0.624
        r_ohm = r_per_km * seg["length_m"] / 1000.0
        loss_before += 3.0 * i_b * i_b * r_ohm / 1000.0
        loss_after += 3.0 * i_a * i_a * r_ohm / 1000.0
    out = _estimate()
    assert out["voltage"]["length_m"] == round(path[customer_idx]["m"], 1)
    assert abs(out["feeder_loss"]["before_kw"] - loss_before) < 0.02
    assert abs(out["feeder_loss"]["after_kw"] - loss_after) < 0.02
    assert 0.5 < out["feeder_loss"]["before_kw"] < 5.0
    assert out["feeder_loss"]["after_kw"] >= out["feeder_loss"]["before_kw"]
    assert out["feeder_loss"]["span"] == "TP → 200/3"


def test_hero_energy_uses_loss_factor_not_peak_times_8760():
    lf = 16.1 / 79.3
    assert abs(lf - 0.20302648171500634) < 1e-12
    f = 0.3 * lf + 0.7 * lf * lf
    hours = 8760 * f
    assert abs(loss_factor(lf) - f) < 1e-12
    assert abs(equivalent_hours(lf) - hours) < 1e-9
    out = _estimate()
    assert out["feeder_loss"]["load_factor"] == round(lf, 4)
    assert out["feeder_loss"]["loss_factor"] == round(f, 4)
    assert out["feeder_loss"]["equivalent_hours"] == round(hours, 1)
    assert abs(out["feeder_loss"]["after_kwh_year"] - out["feeder_loss"]["after_kw"] * hours) < 1.0
    assert out["feeder_loss"]["after_kwh_year"] < out["feeder_loss"]["after_kw"] * 8760 * 0.2


def test_hero_transformer_p0_plus_pk_share_squared():
    def tr(load_kw):
        share = load_kw / TR_SN_KVA
        return round(TR_P0_KW + TR_PK_KW * share * share, 3)

    assert TR_P0_KW == 0.93
    assert TR_PK_KW == 4.60
    assert TR_SN_KVA == 400.0
    assert tr(227.7) == 2.421
    assert tr(238.7) == 2.568
    out = _estimate()
    assert out["transformer_loss"]["before"]["total_kw"] == 2.421
    assert out["transformer_loss"]["after"]["total_kw"] == 2.568
    assert out["transformer_loss"]["before"]["iron_kw"] == 0.93
    assert out["transformer_loss"]["after"]["iron_kw"] == 0.93


def test_hero_voltage_matches_line_load_span_224v():
    feeder = _hero_feeder()
    out = _estimate()
    length = out["voltage"]["length_m"]
    after = evaluate(
        [{"conductor": "4A-50", "length_m": length, "permitted_kw": 346.0, "houses": 48}],
        transformer_kva=400,
        method="new",
    )
    v_after = round(230.0 * (1 - after["voltage_drop_pct"] / 100.0), 1)
    assert v_after == 224.0
    assert out["voltage"]["after_v"] == 224.0
    assert out["to_customer"][-1]["id"] == "200/3"
    assert out["to_customer"][-1]["v_after"] == 224.0
    assert feeder["points"] == 47


def test_line_loading_fails_when_segment_over_ampacity():
    # 79.3 + 30 = 109.3 kW → I = 109.3 / 0.624 = 175.160 A → 109.5 % of 160 A
    i_after = 109.3 / 0.624
    assert i_after > 160
    out = _estimate(added_kw=30.0, peak_after_kw=257.7)
    assert out["line"]["after"]["isk_a"] == round(i_after, 1) == 175.2
    assert out["line"]["after"]["load_pct"] == round(100.0 * i_after / 160.0, 1) == 109.5
    assert out["line_loading"]["pass"] is False
    assert out["line_loading"]["max_after_pct"] > 100


def test_hero_capacity_and_voltage_carry_consistent_load_loss():
    snap = run_sync_until_interrupt("hero", delay=0)
    cap = snap["capacity"]
    volt = snap["quality"]
    ll = cap["load_loss"]
    assert cap["pass"] is True
    assert cap["steps"]["1e_line_loading"]["pass"] is True
    assert cap["line_loading"]["pass"] is True
    assert volt["pass"] is True
    assert volt["line_loading"]["pass"] is True
    assert volt["voltage_after_v"] == 224.0
    assert volt["profile"][-1]["label"] == "200/3"
    assert volt["profile"][-1]["v_after"] == 224.0
    assert ll["line"]["after"]["isk_a"] == 144.7
    assert ll["line"]["after"]["load_pct"] == 90.4
    assert ll["voltage"]["after_v"] == 224.0
    assert volt["load_loss"]["line"] == ll["line"]
    assert volt["load_loss"]["feeder_loss"] == ll["feeder_loss"]
    assert cap["transformer_bar"]["before_kw"] == 227.7
    assert cap["transformer_bar"]["after_kw"] == 238.7
    assert cap["transformer_bar"]["coincident_kw"] == 230.34
    assert cap["transformer_bar"]["added_kw"] == 11.0
    assert cap["headroom_80_kw"] == 81.3
    assert snap["future"]["gauge"]["after_kw"] == 238.7
    assert snap["future"]["headroom_kw"] == 81.3
    assert ll["feeder_loss"]["after_kw"] < 5
    assert "3 × I² × R" in ll["formula"]["feeder_loss"]


def test_line_loading_over_ampacity_fails_capacity_and_does_not_pass():
    snap = run_sync_until_interrupt(
        "intake",
        delay=0,
        form={
            "kw": 30,
            "phases": 3,
            "lat": HERO_LAT,
            "lon": HERO_LON,
            "text": "30 kW 3F, 54.55929, 25.27955, TP 12-608.",
        },
    )
    assert snap["capacity"]["transformer_bar"]["after_kw"] == 257.7
    assert snap["capacity"]["transformer_bar"]["after_kw"] < 320
    assert snap["capacity"]["steps"]["1e_line_loading"]["pass"] is False
    assert snap["capacity"]["pass"] is False
    assert snap["capacity"]["escalate"] is True
    assert snap["failed"] is True
    assert snap["status"] == "escalated"
    tools = [e["tool"] for e in snap["events"] if e.get("type") == "tool"]
    assert "check_voltage_drop" not in tools
