from pathlib import Path

from langchain_community.document_loaders import Docx2txtLoader


class DocumentLoader:

    def load(self, file_path: str):

        loader = Docx2txtLoader(file_path)

        documents = loader.load()

        document_name = Path(file_path).stem

        for document in documents:
            document.metadata["document_name"] = document_name

        return documents