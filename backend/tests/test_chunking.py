import pytest

from app.services.chunking import chunk_text


def test_empty_text_returns_empty_list():
    assert chunk_text("") == []
    assert chunk_text("   ") == []


def test_short_text_returns_one_chunk():
    result = chunk_text("KnowledgeForge AI")

    assert result == ["KnowledgeForge AI"]


def test_long_text_is_split_into_chunks():
    text = "abcdefghij"

    result = chunk_text(
        text,
        chunk_size=4,
        chunk_overlap=0,
    )

    assert result == ["abcd", "efgh", "ij"]


def test_chunks_have_expected_overlap():
    text = "abcdefghij"

    result = chunk_text(
        text,
        chunk_size=6,
        chunk_overlap=2,
    )

    assert result == ["abcdef", "efghij"]


def test_invalid_chunk_size_raises_error():
    with pytest.raises(ValueError):
        chunk_text("some text", chunk_size=0)


def test_overlap_must_be_smaller_than_chunk_size():
    with pytest.raises(ValueError):
        chunk_text(
            "some text",
            chunk_size=5,
            chunk_overlap=5,
        )


def test_negative_overlap_raises_error():
    with pytest.raises(ValueError):
        chunk_text(
            "some text",
            chunk_size=5,
            chunk_overlap=-1,
        )
