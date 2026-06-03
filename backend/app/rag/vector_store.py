import logging
from uuid import NAMESPACE_URL, uuid5

import httpx

from backend.app.config import get_settings
from backend.app.schemas.risk import Document

logger = logging.getLogger(__name__)

EMBEDDING_DIMENSIONS = 1536


class OpenAIEmbeddingClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.openai_api_key
        self.model = settings.openai_embedding_model

    @property
    def configured(self) -> bool:
        return bool(self.api_key)

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self.configured or not texts:
            return []

        response = httpx.post(
            "https://api.openai.com/v1/embeddings",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "input": texts,
                "encoding_format": "float",
            },
            timeout=30,
        )
        response.raise_for_status()
        data = sorted(response.json()["data"], key=lambda item: item["index"])
        return [item["embedding"] for item in data]


class QdrantVectorStore:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.qdrant_url.rstrip("/") if settings.qdrant_url else None
        self.api_key = settings.qdrant_api_key
        self.collection = settings.qdrant_collection

    @property
    def configured(self) -> bool:
        return bool(self.base_url and self.api_key)

    def ensure_collection(self) -> None:
        if not self.configured:
            return

        response = httpx.put(
            f"{self.base_url}/collections/{self.collection}",
            headers=self._headers(),
            json={"vectors": {"size": EMBEDDING_DIMENSIONS, "distance": "Cosine"}},
            timeout=20,
        )
        response.raise_for_status()

    def upsert_documents(self, documents: list[Document], vectors: list[list[float]]) -> int:
        if not self.configured or not documents or not vectors:
            return 0

        points = [
            {
                "id": qdrant_point_id(document.id),
                "vector": vector,
                "payload": {
                    "document_id": document.id,
                    "title": document.title,
                    "region": document.region,
                    "source": document.source,
                    "url": str(document.url) if document.url else None,
                    "published_at": document.published_at.isoformat(),
                },
            }
            for document, vector in zip(documents, vectors, strict=False)
        ]
        response = httpx.put(
            f"{self.base_url}/collections/{self.collection}/points",
            headers=self._headers(),
            params={"wait": "true"},
            json={"points": points},
            timeout=30,
        )
        response.raise_for_status()
        return len(points)

    def search(self, vector: list[float], limit: int) -> list[str]:
        if not self.configured or not vector:
            return []

        response = httpx.post(
            f"{self.base_url}/collections/{self.collection}/points/query",
            headers=self._headers(),
            json={"query": vector, "limit": limit, "with_payload": True},
            timeout=20,
        )
        response.raise_for_status()
        result = response.json().get("result", {})
        points = result.get("points", result if isinstance(result, list) else [])
        return [
            point.get("payload", {}).get("document_id")
            for point in points
            if point.get("payload", {}).get("document_id")
        ]

    def _headers(self) -> dict[str, str]:
        return {
            "api-key": self.api_key or "",
            "Content-Type": "application/json",
        }


def index_documents(documents: list[Document]) -> dict[str, int | str | bool | None]:
    embedding_client = OpenAIEmbeddingClient()
    vector_store = QdrantVectorStore()
    if not embedding_client.configured or not vector_store.configured:
        return {"configured": False, "embedded": 0, "indexed": 0, "error": None}

    try:
        vector_store.ensure_collection()
        vectors = embedding_client.embed_texts([document_text(document) for document in documents])
        indexed = vector_store.upsert_documents(documents, vectors)
    except httpx.HTTPError as exc:
        logger.warning("Document vector indexing failed: %s", exc)
        return {"configured": True, "embedded": 0, "indexed": 0, "error": str(exc)}

    return {"configured": True, "embedded": len(vectors), "indexed": indexed, "error": None}


def search_documents(question: str, limit: int) -> list[str]:
    embedding_client = OpenAIEmbeddingClient()
    vector_store = QdrantVectorStore()
    if not embedding_client.configured or not vector_store.configured:
        return []

    try:
        vectors = embedding_client.embed_texts([question])
        return vector_store.search(vectors[0], limit=limit) if vectors else []
    except httpx.HTTPError as exc:
        logger.warning("Document vector search failed: %s", exc)
        return []


def document_text(document: Document) -> str:
    return f"{document.title}\nRegion: {document.region}\nSource: {document.source}\n{document.content}"


def qdrant_point_id(document_id: str) -> str:
    return str(uuid5(NAMESPACE_URL, f"supply-chain-oracle:{document_id}"))
