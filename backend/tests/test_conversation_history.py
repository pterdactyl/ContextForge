
from unittest.mock import patch

from app.services.llm_service import generate_answer


def test_generate_answer_with_history():
    chunks = [
        {
            "filename": "architecture.txt",
            "content": "ContextForge uses PostgreSQL for document storage."
        }
    ]

    history = [
        {
            "role": "user",
            "content": "What database does ContextForge use?"
        },
        {
            "role": "assistant",
            "content": "ContextForge uses PostgreSQL."
        }
    ]

    with patch("app.services.llm_service.client.chat") as mock_chat:
        mock_chat.return_value.message.content = "PostgreSQL supports vector search."

        answer = generate_answer(
            question="Why was it chosen?",
            chunks=chunks,
            history=history
        )

        messages = mock_chat.call_args.kwargs["messages"]

        assert len(messages) == 4
        assert messages[1] == history[0]
        assert messages[2] == history[1]
        assert "Why was it chosen?" in messages[3]["content"]
        assert answer == "PostgreSQL supports vector search."

