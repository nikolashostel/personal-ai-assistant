from app.ingestion.document_loader import DocumentLoader
from app.ingestion.text_splitter import TextSplitter
from app.vectorstore.vector_store import VectorStore


class DocumentPipeline:

    def __init__(self):

        self.loader = DocumentLoader()
        self.splitter = TextSplitter()
        self.vector_store = VectorStore()

    def process(self, file_path: str):

        print("Шаг 1. Загрузка документа...")

        documents = self.loader.load(file_path)

        print("✓ Документ загружен")

        print("Шаг 2. Разбиение на чанки...")

        chunks = self.splitter.split(documents)

        print(f"✓ Получено {len(chunks)} чанков")

        print("Шаг 3. Индексация...")

        self.vector_store.add(chunks)

        print("✓ Документ сохранен в ChromaDB")

        print(f"Всего чанков в базе: {self.vector_store.count()}")

    def rebuild(self, file_path: str):

        print("Пересборка индекса...")

        self.vector_store.clear()

        print("✓ Старый индекс очищен")

        self.process(file_path)

        print("✓ Индекс пересобран")