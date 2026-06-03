from datetime import UTC, datetime
from hashlib import sha256

import httpx

from backend.app.config import get_settings
from backend.app.schemas.risk import Document

NEWS_KEYWORDS = [
    "supply chain disruption",
    "shipping delays",
    "port congestion",
    "logistics crisis",
    "container shortage",
    "factory shutdown",
]


def fetch_news_documents(page_size: int = 10) -> list[Document]:
    settings = get_settings()
    if not settings.news_api_key:
        return []

    query = " OR ".join(f'"{keyword}"' for keyword in NEWS_KEYWORDS)
    response = httpx.get(
        "https://newsapi.org/v2/everything",
        params={
            "apiKey": settings.news_api_key,
            "q": query,
            "language": "en",
            "sortBy": "publishedAt",
            "pageSize": page_size,
        },
        timeout=15,
    )
    response.raise_for_status()

    articles = response.json().get("articles", [])
    return [
        normalize_news_article(article)
        for article in articles
        if article.get("title") and article.get("title") != "[Removed]"
    ]


def normalize_news_article(payload: dict) -> Document:
    published_at = payload.get("publishedAt") or payload.get("published_at")
    source = payload.get("source")
    if isinstance(source, dict):
        source_name = source.get("name") or "NewsAPI"
    else:
        source_name = str(source or "NewsAPI")

    title = str(payload.get("title") or "Supply chain article")
    content = str(payload.get("content") or payload.get("description") or "")
    region = str(payload.get("region") or infer_region(f"{title} {content}"))
    document_key = f"{title}|{payload.get('url')}"

    return Document(
        id=f"news-{sha256(document_key.encode()).hexdigest()[:16]}",
        title=title,
        content=content,
        region=region,
        source=source_name,
        url=payload.get("url"),
        published_at=datetime.fromisoformat(published_at.replace("Z", "+00:00")) if published_at else datetime.now(UTC),
        embedding_id=None,
    )


def infer_region(text: str) -> str:
    text_lower = text.lower()
    for region in ["Germany", "Netherlands", "China", "Spain", "Europe", "UK"]:
        if region.lower() in text_lower:
            return region
    return "Global"
