
from app.database.connection import SessionLocal
from app.database.models import Conversation

from app.services.conversation_service import (
    create_conversation,
    save_message,
    get_conversation_history
)


def test_conversation_service():
    with SessionLocal() as db:
        conversation = create_conversation(db)

        try:
            save_message(
                db,
                conversation.id,
                "user",
                "What database does ContextForge use?"
            )

            save_message(
                db,
                conversation.id,
                "assistant",
                "ContextForge uses PostgreSQL."
            )

            history = get_conversation_history(
                db,
                conversation.id
            )

            assert len(history) == 2
            assert history[0]["role"] == "user"
            assert history[1]["role"] == "assistant"

            print("Conversation history:", history)

        finally:
            db.delete(conversation)
            db.commit()

