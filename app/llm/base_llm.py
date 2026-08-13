from abc import ABC, abstractmethod


class BaseLLM(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Генерирует ответ по переданному промпту."""
        pass