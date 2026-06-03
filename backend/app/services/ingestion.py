import httpx

from backend.app.integrations.newsapi import NEWS_KEYWORDS, fetch_news_documents
from backend.app.integrations.openweather import WEATHER_REGIONS, fetch_weather_disruptions
from backend.app.services.datastore import datastore


def run_ingestion() -> dict:
    """Placeholder ingestion orchestration.

    Live API clients can be added behind this function. The current result
    documents what would run and keeps local development deterministic.
    """
    seeded = datastore.seed_mock_data()
    live_sources = {
        "openweather": ingest_openweather(),
        "newsapi": ingest_newsapi(),
    }
    return {
        "status": "ok",
        "mode": "live-plus-mock-seed" if any(source["saved"] for source in live_sources.values()) else "mock-seed",
        "sources": {
            "openweather": {
                "ready": True,
                "regions": list(WEATHER_REGIONS),
            },
            "newsapi": {"ready": True, "keywords": NEWS_KEYWORDS},
            "un_comtrade": "ready",
            "kaggle": "seed-data",
        },
        "live": live_sources,
        "seeded": seeded,
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
