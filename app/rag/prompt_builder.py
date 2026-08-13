class PromptBuilder:

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    def build(self, question: str, documents) -> str:

        context = "\n\n".join(
            doc.page_content for doc in documents
        )

        prompt = f"""
{self.system_prompt}

Контекст:

{context}

Вопрос:

{question}

Ответ:
"""

        return prompt