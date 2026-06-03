from datetime import UTC, datetime
from hashlib import sha256
from time import sleep

import httpx

from backend.app.config import get_settings
from backend.app.schemas.risk import TradeMetric

COMTRADE_BASE_URL = "https://comtradeapi.un.org/data/v1/get/C/A/HS"
COMTRADE_PERIOD = "2024"
COMTRADE_TRADE_LANES = [
    {
        "country": "Germany",
        "reporter_code": "276",
        "partner_code": "156",
        "partner_country": "China",
        "flow_code": "M",
    },
    {
        "country": "China",
        "reporter_code": "156",
        "partner_code": "276",
        "partner_country": "Germany",
        "flow_code": "X",
    },
    {
        "country": "Netherlands",
        "reporter_code": "528",
        "partner_code": "0",
        "partner_country": "World",
        "flow_code": "M",
    },
    {
        "country": "Spain",
        "reporter_code": "724",
        "partner_code": "0",
        "partner_country": "World",
        "flow_code": "M",
    },
]


def fetch_trade_metrics(period: str = COMTRADE_PERIOD) -> tuple[list[TradeMetric], list[str]]:
    settings = get_settings()
    if not settings.un_comtrade_api_key:
        return [], []

    metrics: list[TradeMetric] = []
    errors: list[str] = []
    for lane in COMTRADE_TRADE_LANES:
        try:
            response = httpx.get(
                COMTRADE_BASE_URL,
                headers={"Ocp-Apim-Subscription-Key": settings.un_comtrade_api_key},
                params={
                    "reporterCode": lane["reporter_code"],
                    "partnerCode": lane["partner_code"],
                    "cmdCode": "TOTAL",
                    "flowCode": lane["flow_code"],
                    "period": period,
                    "includeDesc": "true",
                },
                timeout=20,
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            errors.append(f"{lane['country']}: {exc.response.status_code}")
            if exc.response.status_code == 429:
                sleep(2)
            continue
        except httpx.HTTPError as exc:
            errors.append(f"{lane['country']}: {exc}")
            continue

        rows = response.json().get("data", [])
        if rows:
            row = rows[0] | {
                "country": lane["country"],
                "partner_country": lane["partner_country"],
                "period": period,
            }
            metrics.append(normalize_trade_metric(row))
        sleep(1)

    return metrics, errors


def normalize_trade_metric(payload: dict) -> TradeMetric:
    country = str(payload.get("country") or payload.get("reporterDesc") or "Unknown")
    partner = str(payload.get("partner_country") or payload.get("partnerDesc") or "World")
    period = str(payload.get("period") or payload.get("periodDesc") or datetime.now(UTC).strftime("%Y-%m"))
    trade_flow = str(payload.get("trade_flow") or payload.get("flowDesc") or "Import")
    commodity = str(payload.get("commodity") or payload.get("cmdDesc") or "All commodities")
    metric_key = f"{country}|{partner}|{period}|{trade_flow}|{commodity}"

    return TradeMetric(
        id=f"trade-{sha256(metric_key.encode()).hexdigest()[:16]}",
        country=country,
        partner_country=partner,
        trade_flow=trade_flow,
        commodity=commodity,
        period=period,
        trade_value=float(payload.get("trade_value") or payload.get("primaryValue") or 0),
        quantity=extract_quantity(payload),
        created_at=datetime.now(UTC),
    )


def extract_quantity(payload: dict) -> float | None:
    for key in ("quantity", "qty", "netWgt"):
        value = payload.get(key)
        if value is not None:
            return float(value)
    return None
