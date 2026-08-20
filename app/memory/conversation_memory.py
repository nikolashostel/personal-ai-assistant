from collections import deque


class ConversationMemory:
    """In-memory short-term conversation history for a single process."""

    def __init__(self, max_messages: int = 10):
        self.messages = deque(maxlen=max_messages)

    def add_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})

    def get_messages(self) -> list[dict[str, str]]:
        return list(self.messages)

    def format_for_prompt(self) -> str:
        if not self.messages:
            return "История разговора отсутствует."

        return "\n".join(
            f"{message['role']}: {message['content']}"
            for message in self.messages
        )
