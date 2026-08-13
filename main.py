from pathlib import Path
from app.llm.gigachat_llm import GigaChatLLM
from app.pipelines.rag_pipeline import RagPipeline
from app.rag.prompt_builder import PromptBuilder
from app.rag.retriever import Retriever
from app.vectorstore.vector_store import VectorStore
from app.config.settings import settings
from app.llm.gigachat_llm import GigaChatLLM
from app.llm.qwen_llm import QwenLLM


def main():

    # Создаем зависимости

    vector_store = VectorStore()

    retriever = Retriever(vector_store)

    prompt_path = Path("prompts/rag_system_prompt.txt")

    system_prompt = prompt_path.read_text(
    encoding="utf-8"
    )

    prompt_builder = PromptBuilder(
    system_prompt=system_prompt
    )

    if settings.LLM_PROVIDER == "qwen":
        llm = QwenLLM()
    else:
        llm = GigaChatLLM()

    # Собираем Pipeline

    pipeline = RagPipeline(
        retriever=retriever,
        prompt_builder=prompt_builder,
        llm=llm
    )

    # Запрашиваем вопрос

    question = input("Введите вопрос: ")

    answer = pipeline.ask(question)

    print("\n" + "=" * 80)
    print("Ответ AI")
    print("=" * 80)
    print(answer)


if __name__ == "__main__":
    main()