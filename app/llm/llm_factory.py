from app.config.settings import settings
from app.llm.base_llm import LLMProvider
from app.llm.gigachat_llm import GigaChatProvider
from app.llm.qwen_llm import QwenProvider


def create_llm_provider() -> LLMProvider:
    if settings.LLM_PROVIDER == "gigachat":
        return GigaChatProvider()

    if settings.LLM_PROVIDER == "qwen":
        return QwenProvider()

    raise ValueError(
        f"Unsupported LLM provider: {settings.LLM_PROVIDER}"
    )
