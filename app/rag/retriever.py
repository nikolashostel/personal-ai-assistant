from app.config.settings import settings
from app.vectorstore.vector_store import VectorStore


class Retriever:

    def __init__(self, vector_store: VectorStore):

        self.vector_store = vector_store

    def retrieve(self, query: str):

        return self.vector_store.similarity_search(
            query=query,
            k=settings.TOP_K
        )