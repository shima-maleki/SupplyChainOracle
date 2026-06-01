from datetime import UTC, datetime, timedelta

from backend.app.risk.scoring import calculate_risk_score, classify_risk
from backend.app.schemas.risk import (
    Disruption,
    Document,
    HistoricalShipment,
    Region,
    RiskBreakdown,
    TradeMetric,
)

NOW = datetime.now(UTC)

RISK_INPUTS: dict[str, RiskBreakdown] = {
    "Germany": RiskBreakdown(
        weather_severity=26,
        news_disruption_frequency=18,
        negative_sentiment=15,
        historical_delay_patterns=11,
        trade_activity_changes=8,
    ),
    "Netherlands": RiskBreakdown(
        weather_severity=10,
        news_disruption_frequency=22,
        negative_sentiment=12,
        historical_delay_patterns=7,
        trade_activity_changes=5,
    ),
    "China": RiskBreakdown(
        weather_severity=8,
        news_disruption_frequency=20,
        negative_sentiment=13,
        historical_delay_patterns=10,
        trade_activity_changes=9,
    ),
    "Spain": RiskBreakdown(
        weather_severity=6,
        news_disruption_frequency=7,
        negative_sentiment=5,
        historical_delay_patterns=4,
        trade_activity_changes=2,
    ),
}


def mock_regions() -> list[Region]:
    regions: list[Region] = []
    for region_name, breakdown in RISK_INPUTS.items():
        result = calculate_risk_score(region_name, breakdown)
        regions.append(
            Region(
                id=region_name.lower().replace(" ", "-"),
                name=region_name,
                risk_score=result.score,
                risk_level=result.level,
                last_updated=NOW,
            )
        )
    return sorted(regions, key=lambda region: region.risk_score, reverse=True)


def mock_disruptions() -> list[Disruption]:
    return [
        Disruption(
            id="weather-de-storm",
            title="Heavy storms detected near southern Germany",
            description="OpenWeather-style alert showing severe wind and rain risk for freight routes.",
            region="Germany",
            severity=classify_risk(78),
            source="OpenWeather API",
            url=None,
            created_at=NOW - timedelta(hours=2),
        ),
        Disruption(
            id="news-rotterdam-congestion",
            title="Port congestion reported around Rotterdam",
            description="News signals indicate delays affecting container handling and North Sea routes.",
            region="Netherlands",
            severity=classify_risk(56),
            source="NewsAPI",
            url="https://example.com/rotterdam-port-congestion",
            created_at=NOW - timedelta(hours=5),
        ),
        Disruption(
            id="trade-cn-export-slowdown",
            title="China export activity shows week-over-week softness",
            description="UN Comtrade-style trade metric suggests reduced export volume in selected categories.",
            region="China",
            severity=classify_risk(60),
            source="UN Comtrade API",
            url=None,
            created_at=NOW - timedelta(days=1),
        ),
        Disruption(
            id="historical-spain-stable",
            title="Spain historical delivery delay rate remains low",
            description="Historical shipment data indicates mostly on-time deliveries for recent comparable lanes.",
            region="Spain",
            severity=classify_risk(24),
            source="Kaggle historical dataset",
            url=None,
            created_at=NOW - timedelta(days=2),
        ),
    ]


def mock_documents() -> list[Document]:
    return [
        Document(
            id="doc-1",
            title="Germany heavy storms may affect deliveries",
            content="Heavy storms and wind alerts in Germany may disrupt road freight and regional distribution.",
            region="Germany",
            source="OpenWeather API",
            url=None,
            published_at=NOW - timedelta(hours=2),
            embedding_id="weather-de-storm",
        ),
        Document(
            id="doc-2",
            title="Shipping delays and port congestion in Rotterdam",
            content="Port congestion in Rotterdam is causing container delays and possible North Sea route disruption.",
            region="Netherlands",
            source="NewsAPI",
            url="https://example.com/rotterdam-port-congestion",
            published_at=NOW - timedelta(hours=5),
            embedding_id="news-rotterdam-congestion",
        ),
        Document(
            id="doc-3",
            title="European supply chain risk summary",
            content="Europe faces mixed risk from Germany storms, Rotterdam congestion, and regional shipping delays.",
            region="Europe",
            source="NewsAPI",
            url="https://example.com/europe-supply-chain-risk",
            published_at=NOW - timedelta(hours=8),
            embedding_id="news-eu-summary",
        ),
    ]


def mock_trade_metrics() -> list[TradeMetric]:
    return [
        TradeMetric(
            id="trade-de-imports",
            country="Germany",
            partner_country="China",
            trade_flow="Import",
            commodity="Industrial components",
            period="2026-05",
            trade_value=1240000000,
            quantity=380000,
            created_at=NOW,
        ),
        TradeMetric(
            id="trade-cn-exports",
            country="China",
            partner_country="Germany",
            trade_flow="Export",
            commodity="Manufactured goods",
            period="2026-05",
            trade_value=2100000000,
            quantity=740000,
            created_at=NOW,
        ),
    ]


def mock_historical_shipments() -> list[HistoricalShipment]:
    return [
        HistoricalShipment(
            id="hist-1",
            order_id="ORD-1001",
            region="Germany",
            warehouse="Berlin DC",
            delivery_status="Delayed",
            delay_days=3,
            shipping_mode="Road",
            created_at=NOW - timedelta(days=15),
        ),
        HistoricalShipment(
            id="hist-2",
            order_id="ORD-1002",
            region="Spain",
            warehouse="Madrid DC",
            delivery_status="On Time",
            delay_days=0,
            shipping_mode="Road",
            created_at=NOW - timedelta(days=12),
        ),
    ]
