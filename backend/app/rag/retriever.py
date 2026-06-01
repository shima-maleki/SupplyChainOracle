from backend.app.schemas.risk import Document
from backend.app.services.datastore import datastore


def retrieve_documents(question: str, region: str | None = None, limit: int = 4) -> list[Document]:
    """Simple lexical retriever used until Qdrant credentials are configured."""
    terms = {term.lower().strip(".,?!") for term in question.split() if len(term) > 2}
    documents = datastore.list_documents()

    if region:
        documents = [doc for doc in documents if doc.region.lower() in {region.lower(), "europe"}]

    def score(document: Document) -> int:
        haystack = f"{document.title} {document.content} {document.region} {document.source}".lower()
        return sum(1 for term in terms if term in haystack)

    ranked = sorted(documents, key=score, reverse=True)
    return [doc for doc in ranked if score(doc) > 0][:limit] or ranked[:limit]
