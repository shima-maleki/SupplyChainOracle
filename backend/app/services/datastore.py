import logging
from collections.abc import Callable
from typing import TypeVar

import httpx
from pydantic import BaseModel

from backend.app.config import get_settings
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

logger = logging.getLogger(__name__)

ModelT = TypeVar("ModelT", bound=BaseModel)


class SupabaseRestClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.supabase_url.rstrip("/") if settings.supabase_url else None
        self.api_key = settings.supabase_service_role_key or settings.supabase_anon_key

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key)

    def list_rows(self, table: str, model: type[ModelT], order: str | None = None) -> list[ModelT]:
        if not self.configured:
            return []

        params = {"select": "*"}
        if order:
            params["order"] = order

        try:
            response = httpx.get(
                f"{self.base_url}/rest/v1/{table}",
                headers=self._headers(),
                params=params,
                timeout=10,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Supabase read failed for %s: %s", table, exc)
            return []

        return [model.model_validate(row) for row in response.json()]

    def upsert_rows(self, table: str, rows: list[BaseModel]) -> int:
        if not self.configured or not rows:
            return 0

        payload = [row.model_dump(mode="json") for row in rows]
        try:
            response = httpx.post(
                f"{self.base_url}/rest/v1/{table}",
                headers=self._headers(prefer="resolution=merge-duplicates,return=minimal"),
                params={"on_conflict": "id"},
                json=payload,
                timeout=10,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Supabase upsert failed for %s: %s", table, exc)
            return 0

        return len(rows)

    def _headers(self, prefer: str | None = None) -> dict[str, str]:
        headers = {
            "apikey": self.api_key or "",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if prefer:
            headers["Prefer"] = prefer
        return headers


class Datastore:
    """Repository layer that prefers Supabase and falls back to mock data."""

    def __init__(self) -> None:
        self.supabase = SupabaseRestClient()

    def list_regions(self) -> list[Region]:
        return self._list_or_mock("regions", Region, mock_regions, order="risk_score.desc")

    def list_disruptions(self) -> list[Disruption]:
        return self._list_or_mock("disruptions", Disruption, mock_disruptions, order="created_at.desc")

    def list_documents(self) -> list[Document]:
        return self._list_or_mock("documents", Document, mock_documents, order="published_at.desc")

    def list_trade_metrics(self) -> list[TradeMetric]:
        return self._list_or_mock("trade_metrics", TradeMetric, mock_trade_metrics, order="created_at.desc")

    def list_historical_shipments(self) -> list[HistoricalShipment]:
        return self._list_or_mock(
            "historical_shipments",
            HistoricalShipment,
            mock_historical_shipments,
            order="created_at.desc",
        )

    def seed_mock_data(self) -> dict[str, int | bool]:
        if not self.supabase.configured:
            return {"configured": False}

        return {
            "configured": True,
            "regions": self.supabase.upsert_rows("regions", mock_regions()),
            "disruptions": self.supabase.upsert_rows("disruptions", mock_disruptions()),
            "documents": self.supabase.upsert_rows("documents", mock_documents()),
            "trade_metrics": self.supabase.upsert_rows("trade_metrics", mock_trade_metrics()),
            "historical_shipments": self.supabase.upsert_rows(
                "historical_shipments",
                mock_historical_shipments(),
            ),
        }

    def save_disruptions(self, disruptions: list[Disruption]) -> int:
        return self.supabase.upsert_rows("disruptions", disruptions)

    def save_documents(self, documents: list[Document]) -> int:
        return self.supabase.upsert_rows("documents", documents)

    def save_trade_metrics(self, trade_metrics: list[TradeMetric]) -> int:
        return self.supabase.upsert_rows("trade_metrics", trade_metrics)

    def save_regions(self, regions: list[Region]) -> int:
        return self.supabase.upsert_rows("regions", regions)

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

    def _list_or_mock(
        self,
        table: str,
        model: type[ModelT],
        fallback: Callable[[], list[ModelT]],
        order: str | None = None,
    ) -> list[ModelT]:
        rows = self.supabase.list_rows(table, model, order=order)
        return rows or fallback()


datastore = Datastore()
