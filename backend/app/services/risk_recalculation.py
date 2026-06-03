from datetime import UTC, datetime

from backend.app.risk.scoring import calculate_risk_score
from backend.app.schemas.risk import (
    Disruption,
    Document,
    HistoricalShipment,
    Region,
    RiskBreakdown,
    RiskLevel,
    RiskScoreResult,
    TradeMetric,
)
from backend.app.services.datastore import datastore

TRACKED_REGIONS = ["Germany", "Netherlands", "China", "Spain"]
NEGATIVE_TERMS = {
    "congestion",
    "crisis",
    "delay",
    "delayed",
    "disruption",
    "risk",
    "shortage",
    "shutdown",
    "storm",
}


def calculate_live_risk_scores() -> list[RiskScoreResult]:
    disruptions = datastore.list_disruptions()
    documents = datastore.list_documents()
    shipments = datastore.list_historical_shipments()
    trade_metrics = datastore.list_trade_metrics()

    results = [
        calculate_risk_score(
            region,
            build_risk_breakdown(region, disruptions, documents, shipments, trade_metrics),
        )
        for region in TRACKED_REGIONS
    ]
    return sorted(results, key=lambda result: result.score, reverse=True)


def recalculate_live_risk_scores() -> list[RiskScoreResult]:
    results = calculate_live_risk_scores()
    datastore.save_regions([region_from_score(result) for result in results])
    return results


def build_risk_breakdown(
    region: str,
    disruptions: list[Disruption],
    documents: list[Document],
    shipments: list[HistoricalShipment],
    trade_metrics: list[TradeMetric],
) -> RiskBreakdown:
    regional_disruptions = [item for item in disruptions if item.region == region]
    regional_documents = [
        item
        for item in documents
        if item.region in {region, "Europe", "Global"}
        or region.lower() in f"{item.title} {item.content}".lower()
    ]
    regional_shipments = [item for item in shipments if item.region == region]
    regional_trade = [item for item in trade_metrics if item.country == region or item.partner_country == region]

    return RiskBreakdown(
        weather_severity=weather_points(regional_disruptions),
        news_disruption_frequency=min(25, len(regional_documents) * 5),
        negative_sentiment=negative_sentiment_points(regional_documents),
        historical_delay_patterns=historical_delay_points(regional_shipments),
        trade_activity_changes=trade_activity_points(regional_trade),
    )


def weather_points(disruptions: list[Disruption]) -> int:
    source_items = [item for item in disruptions if "weather" in item.source.lower() or "weather" in item.id]
    severity_points = {RiskLevel.high: 15, RiskLevel.medium: 8, RiskLevel.low: 2}
    return min(30, sum(severity_points[item.severity] for item in source_items))


def negative_sentiment_points(documents: list[Document]) -> int:
    total_hits = 0
    for document in documents:
        text = f"{document.title} {document.content}".lower()
        total_hits += sum(1 for term in NEGATIVE_TERMS if term in text)
    return min(20, total_hits * 3)


def historical_delay_points(shipments: list[HistoricalShipment]) -> int:
    if not shipments:
        return 0
    delayed = [item for item in shipments if item.delay_days > 0 or "delay" in item.delivery_status.lower()]
    average_delay = sum(item.delay_days for item in shipments) / len(shipments)
    return min(15, round((len(delayed) / len(shipments)) * 10 + average_delay))


def trade_activity_points(trade_metrics: list[TradeMetric]) -> int:
    if not trade_metrics:
        return 0
    max_value = max(item.trade_value for item in trade_metrics)
    if max_value >= 1_000_000_000:
        return 10
    if max_value >= 100_000_000:
        return 7
    if max_value >= 1_000_000:
        return 4
    return 2


def region_from_score(result: RiskScoreResult) -> Region:
    return Region(
        id=result.region.lower().replace(" ", "-"),
        name=result.region,
        risk_score=result.score,
        risk_level=result.level,
        last_updated=datetime.now(UTC),
    )
