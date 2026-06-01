from backend.app.schemas.risk import RiskBreakdown, RiskLevel, RiskScoreResult


def classify_risk(score: int) -> RiskLevel:
    if score >= 70:
        return RiskLevel.high
    if score >= 40:
        return RiskLevel.medium
    return RiskLevel.low


def calculate_risk_score(region: str, breakdown: RiskBreakdown) -> RiskScoreResult:
    score = min(
        100,
        breakdown.weather_severity
        + breakdown.news_disruption_frequency
        + breakdown.negative_sentiment
        + breakdown.historical_delay_patterns
        + breakdown.trade_activity_changes,
    )
    level = classify_risk(score)
    explanation = (
        f"{region} is {level.value} risk with score {score}. "
        "The score combines weather severity, news disruption volume, sentiment, "
        "historical delivery delays, and trade activity changes."
    )
    return RiskScoreResult(region=region, score=score, level=level, breakdown=breakdown, explanation=explanation)
