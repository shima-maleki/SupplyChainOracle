from backend.app.schemas.risk import (
    DashboardSummary,
    Disruption,
    Document,
    HistoricalShipment,
    Region,
    TradeMetric,
)
from backend.app.services.mock_data import (
    mock_disruptions,
    mock_documents,
    mock_historical_shipments,
    mock_regions,
    mock_trade_metrics,
)


class Datastore:
    """Small repository layer.

    The MVP uses mock data by default so the app runs without credentials.
    Supabase integration can replace these methods without changing API routes.
    """

    def list_regions(self) -> list[Region]:
        return mock_regions()

    def list_disruptions(self) -> list[Disruption]:
        return sorted(mock_disruptions(), key=lambda item: item.created_at, reverse=True)

    def list_documents(self) -> list[Document]:
        return sorted(mock_documents(), key=lambda item: item.published_at, reverse=True)

    def list_trade_metrics(self) -> list[TradeMetric]:
        return mock_trade_metrics()

    def list_historical_shipments(self) -> list[HistoricalShipment]:
        return mock_historical_shipments()

    def dashboard_summary(self) -> DashboardSummary:
        regions = self.list_regions()
        disruptions = self.list_disruptions()
        return DashboardSummary(
            global_risk_index=round(sum(region.risk_score for region in regions) / len(regions)),
            high_risk_regions=[region for region in regions if region.risk_level.value == "High"],
            disruptions_today=len(disruptions),
            regions=regions,
            recent_disruptions=disruptions[:6],
            trade_metrics=self.list_trade_metrics(),
            historical_shipments=self.list_historical_shipments(),
        )


datastore = Datastore()
