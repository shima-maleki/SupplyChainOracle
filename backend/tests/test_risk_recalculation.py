from datetime import UTC, datetime

from backend.app.risk.scoring import calculate_risk_score
from backend.app.schemas.risk import Disruption, Document, HistoricalShipment, RiskLevel, TradeMetric
from backend.app.services.risk_recalculation import build_risk_breakdown


def test_build_risk_breakdown_uses_live_signals() -> None:
    now = datetime.now(UTC)
    breakdown = build_risk_breakdown(
        "Germany",
        disruptions=[
            Disruption(
                id="weather-germany",
                title="Storm conditions reported in Germany",
                description="High wind on freight routes",
                region="Germany",
                severity=RiskLevel.high,
                source="OpenWeather API",
                created_at=now,
            )
        ],
        documents=[
            Document(
                id="doc-germany",
                title="Germany supply chain disruption",
                content="Port congestion and shipping delay risk",
                region="Germany",
                source="NewsAPI",
                published_at=now,
            )
        ],
        shipments=[
            HistoricalShipment(
                id="hist-germany",
                order_id="ORD-1",
                region="Germany",
                warehouse="Berlin DC",
                delivery_status="Delayed",
                delay_days=3,
                shipping_mode="Road",
                created_at=now,
            )
        ],
        trade_metrics=[
            TradeMetric(
                id="trade-germany",
                country="Germany",
                partner_country="China",
                trade_flow="Import",
                commodity="All Commodities",
                period="2024",
                trade_value=1_500_000_000,
                quantity=None,
                created_at=now,
            )
        ],
    )
    result = calculate_risk_score("Germany", breakdown)

    assert breakdown.weather_severity == 15
    assert breakdown.news_disruption_frequency == 5
    assert breakdown.negative_sentiment == 12
    assert breakdown.historical_delay_patterns == 13
    assert breakdown.trade_activity_changes == 10
    assert result.level == RiskLevel.medium
