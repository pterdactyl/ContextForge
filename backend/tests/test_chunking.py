
from app.services.chunking_service import chunk_text


def test_sentence_chunking():
    text = (
        "ContextForge uses PostgreSQL. "
        "It stores document embeddings. "
        "It retrieves relevant information. "
        "The system uses Ollama for generation."
    )

    chunks = chunk_text(
        text,
        chunk_size=65,
        overlap=30
    )

    assert len(chunks) > 1
    assert all(len(chunk) <= 65 for chunk in chunks)

    for chunk in chunks:
        print(chunk)
        print("-" * 40)


def test_empty_text():
    assert chunk_text("") == []


def test_invalid_overlap():
    try:
        chunk_text("Hello world", chunk_size=10, overlap=10)
        assert False, "Expected ValueError"
    except ValueError:
        pass

