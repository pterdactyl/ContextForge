from app.services.embedding_service import generate_embeddings

def test_generate_embeddings():
    chunks = [
        "Python is a programming language.",
        "FastAPI is a web framework."
    ]

    embeddings = generate_embeddings(chunks)

    assert len(embeddings) == 2
    assert len(embeddings[0]) == 384
    assert len(embeddings[1]) == 384
    
def test_empty_chunks():
    embeddings = generate_embeddings([])

    assert embeddings == []
