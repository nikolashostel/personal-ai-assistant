class PromptBuilder:

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    def build(
        self,
        question: str,
        documents,
        conversation_history: str = "История разговора отсутствует.",
    ) -> str:

        context = "\n\n".join(
            doc.page_content for doc in documents
        )

        prompt = f"""
{self.system_prompt}

История текущего разговора:

{conversation_history}

Контекст документов:

{context}

Текущий вопрос:

{question}

Ответ:
"""

        return prompt
