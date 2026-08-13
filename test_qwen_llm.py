from app.llm.qwen_llm import QwenLLM


llm = QwenLLM()

answer = llm.generate(
    "Объясни простыми словами, что такое RAG. Ответь максимум в трех предложениях."
)

print("\nОтвет Qwen:")
print(answer)