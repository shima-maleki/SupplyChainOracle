from backend.app.rag.vector_store import document_text, qdrant_point_id
from backend.app.services.mock_data import mock_documents


def test_qdrant_point_id_is_stable_uuid() -> None:
    first = qdrant_point_id("doc-1")
    second = qdrant_point_id("doc-1")

    assert first == second
    assert len(first) == 36


def test_document_text_contains_retrieval_context() -> None:
    document = mock_documents()[0]
    text = document_text(document)

    assert document.title in text
    assert document.region in text
    assert document.source in text
