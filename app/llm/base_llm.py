from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Interface for language model providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response for the given prompt."""
        pass
