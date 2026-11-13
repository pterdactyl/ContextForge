from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)

def generate_embeddings(chunks: list[str]) -> list[list[float]]:
    if not chunks:
        return []

    embeddings = model.encode(chunks)

    return embeddings.tolist()
