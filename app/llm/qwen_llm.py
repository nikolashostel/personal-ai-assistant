from openai import OpenAI

from app.config.settings import settings
from app.llm.base_llm import BaseLLM


class QwenLLM(BaseLLM):
    def __init__(self) -> None:
        self.client = OpenAI(
            base_url=settings.QWEN_BASE_URL,
            api_key="local",
        )

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=settings.QWEN_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=settings.QWEN_TEMPERATURE,
            max_tokens=settings.QWEN_MAX_TOKENS,
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": False,
                }
            },
        )

        return response.choices[0].message.content or ""