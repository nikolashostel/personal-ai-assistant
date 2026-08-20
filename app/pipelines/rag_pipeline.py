from app.llm.base_llm import LLMProvider
from app.memory.conversation_memory import ConversationMemory
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import Retriever


class RagPipeline:

    def __init__(
        self,
        retriever: Retriever,
        prompt_builder: PromptBuilder,
        llm: LLMProvider,
    ):
        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.llm = llm

    def ask(self, question: str, memory: ConversationMemory) -> str:
        conversation_history = memory.format_for_prompt()

        print("Поиск релевантных документов...")
        documents = self.retriever.retrieve(question)
        print(f"✓ Найдено документов: {len(documents)}")

        print("Формирование промпта...")
        prompt = self.prompt_builder.build(
            question=question,
            documents=documents,
            conversation_history=conversation_history,
        )
        print("✓ Промпт сформирован")

        print("Получение ответа от LLM...")
        answer = self.llm.generate(prompt)
        print("✓ Ответ получен")

        memory.add_user_message(question)
        memory.add_assistant_message(answer)

        sources = self._build_sources(documents)
        return f"{answer}\n\nИсточники:\n{sources}"

    def _build_sources(self, documents):
        sources = {}

        for document in documents:
            document_name = document.metadata.get(
                "document_name",
                "Неизвестный документ"
            )
            chunk_id = document.metadata.get("chunk_id")

            if document_name not in sources:
                sources[document_name] = []

            if chunk_id:
                chunk_number = chunk_id.split(":")[-1]
                sources[document_name].append(chunk_number)

        result = []
        for document_name, chunks in sources.items():
            if chunks:
                result.append(
                    f"- {document_name}\n"
                    f"  Чанки: {', '.join(chunks)}"
                )
            else:
                result.append(f"- {document_name}")

        return "\n".join(result)
