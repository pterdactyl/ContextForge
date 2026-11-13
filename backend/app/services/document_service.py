import pymupdf

def extract_text(filename: str, content: bytes) -> str:
    if filename.lower().endswith(".txt"):
        return content.decode("utf-8")

    if filename.lower().endswith(".pdf"):
        with pymupdf.open(stream=content, filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc)

    raise ValueError("Unsupported file type")
