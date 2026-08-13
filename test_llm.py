from app.llm.gigachat_llm import GigaChatLLM

llm = GigaChatLLM()

answer = llm.generate(
    "Что такое RAG? Ответь одним предложением."
)

print(answer)