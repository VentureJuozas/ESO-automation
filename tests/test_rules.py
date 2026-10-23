from eso_agent.rules import breaker_table, diversity_coefficient, size_breaker


def test_breaker_hero_11kw_3f():
    b = size_breaker(11, 3)
    assert b["amps"] == 20
    assert b["label"] == "3F C 20 A"
    assert b["source"] == "rule"


def test_breaker_table_matches_history():
    assert size_breaker(14, 3)["amps"] == 25
    assert size_breaker(22, 3)["amps"] == 40
    assert size_breaker(3, 1)["amps"] == 16
    assert size_breaker(18, 3)["amps"] == 32


def test_breaker_table_highlights_11kw():
    table = breaker_table(3)
    assert table[0]["amps"] == 10
    row = next(r for r in table if r["kw_max"] == 11)
    assert row["amps"] == 20


def test_diversity_known_points():
    assert abs(diversity_coefficient(25) - 0.464) < 0.01
    assert diversity_coefficient(1) == 1
    assert diversity_coefficient(3) == 1
