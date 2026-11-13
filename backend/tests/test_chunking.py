import pytest
from app.services.chunking_service import chunk_text

def test_short_text():
    assert chunk_text("Hello world", chunk_size=20, overlap=0) == ["Hello world"]

def test_overlapping_chunks():
    chunks = chunk_text("abcdefghij", chunk_size=6, overlap=2)

    assert chunks == ["abcdef", "efghij"]

def test_empty_text():
    assert chunk_text("") == []

def test_invalid_overlap():
    with pytest.raises(ValueError):
        chunk_text("Hello", chunk_size=5, overlap = 5)
