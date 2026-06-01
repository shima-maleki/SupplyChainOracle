from datetime import UTC, datetime

from backend.app.schemas.risk import Document

NEWS_KEYWORDS = [
    "supply chain disruption",
    "shipping delays",
    "port congestion",
    "logistics crisis",
    "container shortage",
    "factory shutdown",
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

    return Document(
        id=f"news-{abs(hash(title))}",
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
