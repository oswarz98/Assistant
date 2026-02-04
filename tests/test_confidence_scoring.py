from engine.scoring import ConfidenceScorer


def test_confidence_breakdown_and_drivers() -> None:
    scorer = ConfidenceScorer()
    confidence, breakdown, drivers = scorer.score(
        team_strength=0.8,
        recent_form=0.6,
        matchup_edges=0.7,
        injuries=0.2,
        rest_travel=0.4,
        market_signal=0.5,
    )
    assert 0 <= confidence <= 100
    assert breakdown.team_strength > breakdown.injuries
    assert len(drivers) == 3
