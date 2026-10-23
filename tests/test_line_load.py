from line_load import diversity, evaluate


def test_diversity_25_houses_new():
    assert abs(diversity(25, "new") - 0.464) < 0.01


def test_short_head_of_line_small_drop():
    rows = evaluate(
        [{"conductor": "4A-50", "length_m": 52, "permitted_kw": 346, "houses": 48}],
        transformer_kva=400,
        method="new",
    )
    assert rows["length_m"] == 52
    assert rows["voltage_drop_pct"] > 0
    assert rows["voltage_drop_pct"] < 15
