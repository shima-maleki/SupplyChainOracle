from backend.app.schemas.risk import Document
from backend.app.services.datastore import datastore
from backend.app.rag.vector_store import search_documents


def retrieve_documents(question: str, region: str | None = None, limit: int = 4) -> list[Document]:
    documents = datastore.list_documents()
    if region:
        documents = [doc for doc in documents if doc.region.lower() in {region.lower(), "europe"}]

    vector_documents = retrieve_vector_documents(question, documents, limit)
    if vector_documents:
        return vector_documents

    return retrieve_lexical_documents(question, documents, limit)


def retrieve_vector_documents(question: str, documents: list[Document], limit: int) -> list[Document]:
    document_by_id = {document.id: document for document in documents}
    document_ids = search_documents(question, limit=limit)
    return [document_by_id[document_id] for document_id in document_ids if document_id in document_by_id]


def retrieve_lexical_documents(question: str, documents: list[Document], limit: int) -> list[Document]:
    terms = {term.lower().strip(".,?!") for term in question.split() if len(term) > 2}

    def score(document: Document) -> int:
        haystack = f"{document.title} {document.content} {document.region} {document.source}".lower()
        return sum(1 for term in terms if term in haystack)

    ranked = sorted(documents, key=score, reverse=True)
    return [doc for doc in ranked if score(doc) > 0][:limit] or ranked[:limit]
