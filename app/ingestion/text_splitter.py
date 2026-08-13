from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.settings import settings


class TextSplitter:

    def __init__(self):

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP
        )

    def split(self, documents):

        chunks = self.splitter.split_documents(documents)

        for index, chunk in enumerate(chunks, start=1):

            document_name = chunk.metadata.get(
                "document_name",
                "unknown_document"
            )

            chunk.metadata["chunk_id"] = f"{document_name}:{index}"

        return chunks