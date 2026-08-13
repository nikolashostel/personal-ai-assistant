from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

from app.config.settings import settings


class VectorStore:

    def __init__(self):

        self.embeddings = HuggingFaceEmbeddings(
            model_name=settings.EMBEDDING_MODEL
        )

        self.vector_store = Chroma(
            persist_directory=settings.VECTOR_DB_PATH,
            embedding_function=self.embeddings
        )

    def add(self, chunks):

        self.vector_store.add_documents(chunks)

    def clear(self):

        self.vector_store.reset_collection()

    def count(self):

        return self.vector_store._collection.count()

    def similarity_search(self, query: str, k: int = 3):

        return self.vector_store.similarity_search(
            query=query,
            k=k
        )

    def similarity_search_with_score(self, query: str, k: int = 3):

        return self.vector_store.similarity_search_with_score(
            query=query,
            k=k
        )