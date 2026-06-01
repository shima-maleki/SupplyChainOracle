from backend.app.risk.scoring import calculate_risk_score
from backend.app.schemas.risk import RiskBreakdown, RiskLevel


def test_calculate_risk_score_classifies_high_risk() -> None:
    result = calculate_risk_score(
        "Germany",
        RiskBreakdown(
            weather_severity=30,
            news_disruption_frequency=25,
            negative_sentiment=20,
            historical_delay_patterns=15,
            trade_activity_changes=10,
        ),
    )

    assert result.score == 100
    assert result.level == RiskLevel.high
