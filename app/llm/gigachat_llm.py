from gigachat import GigaChat

from app.config.settings import settings
from app.llm.base_llm import LLMProvider


class GigaChatProvider(LLMProvider):

    def generate(self, prompt: str) -> str:
        with GigaChat(
            credentials=settings.GIGACHAT_CREDENTIALS,
            verify_ssl_certs=False,
        ) as giga:
            response = giga.chat(prompt)
            return response.choices[0].message.content or ""
