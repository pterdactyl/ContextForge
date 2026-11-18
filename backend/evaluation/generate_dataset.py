import json
import random
import re
from pathlib import Path

import requests
from sqlalchemy import select

from app.database.connection import SessionLocal
from app.database.models import DocumentChunk


OUTPUT_PATH = Path(__file__).with_name("eval_dataset.json")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

MAX_QUESTIONS = 10
MIN_CHUNK_LENGTH = 100


def generate_question(content: str) -> str | None:
    prompt = f"""
Generate ONE specific factual question that can be
answered using only the following document excerpt.

Rules:
- The answer must be explicitly supported by the excerpt.
- Do not ask vague or opinion-based questions.
- Do not include the answer.
- Return only the question, without numbering.

Document excerpt:
{content}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0}
        },
        timeout=120
    )
    response.raise_for_status()

    question = response.json()["response"].strip()
    question = re.sub(r"^\s*(?:\d+[.)]|[-*])\s*", "", question)
    question = question.strip("\"' \n")

    if not question or "?" not in question:
        return None

    return question.split("?")[0].strip() + "?"


def generate_dataset():
    with SessionLocal() as db:
        chunks = db.scalars(
            select(DocumentChunk)
        ).all()

        eligible_chunks = [
            chunk for chunk in chunks
            if len(chunk.content.strip()) >= MIN_CHUNK_LENGTH
        ]

        random.Random(42).shuffle(eligible_chunks)

        dataset = []

        for chunk in eligible_chunks:
            if len(dataset) >= MAX_QUESTIONS:
                break

            try:
                question = generate_question(chunk.content)
            except (requests.RequestException, KeyError, ValueError) as e:
                print(f"Skipping chunk {chunk.id}: {e}")
                continue

            if not question:
                continue

            dataset.append({
                "query": question,
                "relevant_chunk_ids": [str(chunk.id)],
                "source_filename": chunk.document.filename,
                "source_chunk_index": chunk.chunk_index,
                "source_excerpt": chunk.content[:300],
                "verified": False
            })

            print(f"Generated {len(dataset)}: {question}")

    OUTPUT_PATH.write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"\nSaved {len(dataset)} questions to {OUTPUT_PATH}")


if __name__ == "__main__":
    generate_dataset()
