from datetime import UTC, datetime

from backend.app.schemas.risk import TradeMetric


def normalize_trade_metric(payload: dict) -> TradeMetric:
    country = str(payload.get("country") or payload.get("reporterDesc") or "Unknown")
    partner = str(payload.get("partner_country") or payload.get("partnerDesc") or "World")
    period = str(payload.get("period") or payload.get("periodDesc") or datetime.now(UTC).strftime("%Y-%m"))

    return TradeMetric(
        id=f"trade-{country.lower()}-{partner.lower()}-{period}".replace(" ", "-"),
        country=country,
        partner_country=partner,
        trade_flow=str(payload.get("trade_flow") or payload.get("flowDesc") or "Import"),
        commodity=str(payload.get("commodity") or payload.get("cmdDesc") or "All commodities"),
        period=period,
        trade_value=float(payload.get("trade_value") or payload.get("primaryValue") or 0),
        quantity=float(payload["quantity"]) if payload.get("quantity") is not None else None,
        created_at=datetime.now(UTC),
    )
