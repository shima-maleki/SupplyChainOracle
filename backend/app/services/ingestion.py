import httpx

from backend.app.integrations.comtrade import COMTRADE_PERIOD, COMTRADE_TRADE_LANES, fetch_trade_metrics
from backend.app.integrations.newsapi import NEWS_KEYWORDS, fetch_news_documents
from backend.app.integrations.openweather import WEATHER_REGIONS, fetch_weather_disruptions
from backend.app.services.datastore import datastore
from backend.app.services.risk_recalculation import recalculate_live_risk_scores


def run_ingestion() -> dict:
    """Placeholder ingestion orchestration.

    Live API clients can be added behind this function. The current result
    documents what would run and keeps local development deterministic.
    """
    seeded = datastore.seed_mock_data()
    live_sources = {
        "openweather": ingest_openweather(),
        "newsapi": ingest_newsapi(),
        "un_comtrade": ingest_comtrade(),
    }
    risk_scores = recalculate_live_risk_scores()
    return {
        "status": "ok",
        "mode": "live-plus-mock-seed" if any(source["saved"] for source in live_sources.values()) else "mock-seed",
        "sources": {
            "openweather": {
                "ready": True,
                "regions": list(WEATHER_REGIONS),
            },
            "newsapi": {"ready": True, "keywords": NEWS_KEYWORDS},
            "un_comtrade": {
                "ready": True,
                "period": COMTRADE_PERIOD,
                "lanes": len(COMTRADE_TRADE_LANES),
            },
            "kaggle": "seed-data",
        },
        "live": live_sources,
        "seeded": seeded,
        "risk_scores": [
            {"region": result.region, "score": result.score, "level": result.level.value}
            for result in risk_scores
        ],
        "message": "Ingestion completed with live fetch attempts and MVP seed fallback.",
    }


def ingest_openweather() -> dict[str, int | str | None]:
    try:
        disruptions = fetch_weather_disruptions()
    except httpx.HTTPError as exc:
        return {"fetched": 0, "saved": 0, "error": str(exc)}

    return {
        "fetched": len(disruptions),
        "saved": datastore.save_disruptions(disruptions),
        "error": None,
    }


def ingest_newsapi() -> dict[str, int | str | None]:
    try:
        documents = fetch_news_documents()
    except httpx.HTTPError as exc:
        return {"fetched": 0, "saved": 0, "error": str(exc)}

    return {
        "fetched": len(documents),
        "saved": datastore.save_documents(documents),
        "error": None,
    }


def ingest_comtrade() -> dict[str, int | str | None]:
    try:
        trade_metrics, errors = fetch_trade_metrics()
    except httpx.HTTPError as exc:
        return {"fetched": 0, "saved": 0, "error": str(exc)}

    return {
        "fetched": len(trade_metrics),
        "saved": datastore.save_trade_metrics(trade_metrics),
        "error": "; ".join(errors) if errors else None,
    }
