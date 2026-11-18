
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Conversation, ChatMessage


def create_conversation(db: Session) -> Conversation:
    conversation = Conversation()

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


def get_conversation(
    db: Session,
    conversation_id: UUID
) -> Conversation | None:

    return db.get(Conversation, conversation_id)


def save_message(
    db: Session,
    conversation_id: UUID,
    role: str,
    content: str
) -> ChatMessage:

    if role not in ("user", "assistant"):
        raise ValueError("Invalid message role")

    if not content.strip():
        raise ValueError("Message content cannot be empty")

    if get_conversation(db, conversation_id) is None:
        raise ValueError("Conversation not found")

    message = ChatMessage(
        conversation_id=conversation_id,
        role=role,
        content=content
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message


def get_conversation_history(
    db: Session,
    conversation_id: UUID,
    limit: int = 10
) -> list[dict]:

    if limit < 1:
        raise ValueError("Limit must be positive")

    statement = (
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(
            ChatMessage.created_at.desc(),
            ChatMessage.id.desc()
        )
        .limit(limit)
    )

    messages = db.scalars(statement).all()

    return [
        {
            "role": message.role,
            "content": message.content
        }
        for message in reversed(messages)
    ]

