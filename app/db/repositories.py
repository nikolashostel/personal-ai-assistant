from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Conversation, Message, User


class ConversationRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(self, external_id: str) -> User:
        user = self.db.scalar(
            select(User).where(User.external_id == external_id)
        )
        if user:
            return user

        user = User(external_id=external_id)
        self.db.add(user)
        self.db.flush()
        return user

    def get_or_create_conversation(
        self,
        user: User,
        external_id: str,
    ) -> Conversation:
        conversation = self.db.scalar(
            select(Conversation).where(
                Conversation.user_id == user.id,
                Conversation.external_id == external_id,
            )
        )
        if conversation:
            return conversation

        conversation = Conversation(
            user_id=user.id,
            external_id=external_id,
        )
        self.db.add(conversation)
        self.db.flush()
        return conversation

    def get_recent_messages(
        self,
        conversation: Conversation,
        limit: int = 10,
    ) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation.id)
            .order_by(Message.created_at.desc(), Message.id.desc())
            .limit(limit)
        )
        return list(reversed(self.db.scalars(statement).all()))

    def add_message(
        self,
        conversation: Conversation,
        role: str,
        content: str,
    ) -> Message:
        message = Message(
            conversation_id=conversation.id,
            role=role,
            content=content,
        )
        self.db.add(message)
        return message
