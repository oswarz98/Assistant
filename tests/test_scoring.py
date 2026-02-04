from scoring.confidence import ConfidenceModel


def test_confidence_score_caps_at_100() -> None:
    model = ConfidenceModel()
    score, breakdown = model.score(1.0, 1.0, 1.0, 1.0, 1.0)
    assert score == 100.0
    assert breakdown.trend_alignment > 0


def test_confidence_score_respects_weights() -> None:
    model = ConfidenceModel()
    score, breakdown = model.score(0.5, 0.0, 0.0, 0.0, 0.0)
    assert score == breakdown.trend_alignment
