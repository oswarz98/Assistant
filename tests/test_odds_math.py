from engine.odds import american_to_decimal, decimal_to_american, expected_value, implied_probability_from_american


def test_american_to_decimal_roundtrip() -> None:
    assert american_to_decimal(150) == 2.5
    assert american_to_decimal(-200) == 1.5
    assert decimal_to_american(2.5) == 150
    assert decimal_to_american(1.5) == -200


def test_implied_probability() -> None:
    assert implied_probability_from_american(100) == 0.5
    assert implied_probability_from_american(-110) == 0.5238


def test_expected_value_positive_edge() -> None:
    ev = expected_value(0.6, 150)
    assert ev > 0
