from app.memory.conversation_memory import ConversationMemory


class ConversationStore:
    """In-process store of short-term memories keyed by user and conversation."""

    def __init__(self, max_messages: int = 10):
        self.max_messages = max_messages
        self._conversations: dict[str, ConversationMemory] = {}

    def get(self, user_id: str, conversation_id: str) -> ConversationMemory:
        key = f"{user_id}:{conversation_id}"

        if key not in self._conversations:
            self._conversations[key] = ConversationMemory(
                max_messages=self.max_messages
            )

        return self._conversations[key]
