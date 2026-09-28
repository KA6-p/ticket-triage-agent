import chromadb

from ..config import settings


class SimilarityService:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection("tickets")

    def add(self, ticket_id: int, text: str, embedding: list[float]):
        self.collection.upsert(
            ids=[str(ticket_id)], documents=[text], embeddings=[embedding]
        )

    def find(self, embedding: list[float], threshold: float):
        if self.collection.count() == 0:
            return None
        r = self.collection.query(
            query_embeddings=[embedding],
            n_results=1,
            include=["distances", "documents"],
        )
        if not r["ids"][0]:
            return None
        # Chroma cosine distance = 1 - cosine similarity for normalized vectors.
        distance = r["distances"][0][0]
        similarity = 1 - distance
        return (
            {
                "ticket_id": int(r["ids"][0][0]),
                "similarity": similarity,
                "document": r["documents"][0][0],
            }
            if similarity >= threshold
            else None
        )
