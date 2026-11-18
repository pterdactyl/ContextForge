
import re


def split_sentences(text: str) -> list[str]:
    # Split at sentence-ending punctuation followed by whitespace.
    # Preserve the punctuation with its sentence.
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", text.strip())
        if sentence.strip()
    ]


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
) -> list[str]:

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be between 0 and chunk size")

    if not text.strip():
        return []

    sentences = split_sentences(text)
    chunks = []
    current = ""

    for sentence in sentences:
        # Handle sentences longer than chunk_size
        if len(sentence) > chunk_size:
            if current:
                chunks.append(current)
                current = ""

            start = 0

            while start < len(sentence):
                end = min(start + chunk_size, len(sentence))
                part = sentence[start:end]

                if part.strip():
                    chunks.append(part)

                if end == len(sentence):
                    break

                start = end - overlap

            continue

        # Add sentence if it fits
        if not current:
            current = sentence

        elif len(current) + 1 + len(sentence) <= chunk_size:
            current += " " + sentence

        else:
            chunks.append(current)

            # Preserve overlap using complete trailing sentences
            previous_sentences = split_sentences(current)
            overlap_text = ""

            for previous in reversed(previous_sentences):
                candidate = (
                    previous + " " + overlap_text
                    if overlap_text else previous
                )

                if len(candidate) > overlap:
                    break

                overlap_text = candidate

            if (
                overlap_text
                and len(overlap_text) + 1 + len(sentence) <= chunk_size
            ):
                current = overlap_text + " " + sentence
            else:
                current = sentence

    if current:
        chunks.append(current)

    return chunks

