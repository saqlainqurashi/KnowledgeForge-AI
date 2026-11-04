from unittest.mock import MagicMock, patch

import pytest

from app.services.semantic_search import search_similar_chunks


def test_reject_empty_query():
    db = MagicMock()

    with pytest.raises(ValueError, match="cannot be empty"):
        search_similar_chunks(db, "   ")


def test_reject_invalid_top_k():
    db = MagicMock()

    with pytest.raises(ValueError, match="top_k"):
        search_similar_chunks(db, "What is RAG?", top_k=0)

    with pytest.raises(ValueError, match="top_k"):
        search_similar_chunks(db, "What is RAG?", top_k=21)


def test_search_returns_ranked_chunks():
    db = MagicMock()

    first_chunk = MagicMock()
    first_chunk.id = 10
    first_chunk.document_id = 1
    first_chunk.chunk_index = 0
    first_chunk.content = "RAG retrieves relevant information."

    second_chunk = MagicMock()
    second_chunk.id = 11
    second_chunk.document_id = 1
    second_chunk.chunk_index = 1
    second_chunk.content = "Embeddings represent text numerically."

    db.execute.return_value.all.return_value = [
        (first_chunk, "AI Concepts.txt", 0.10),
        (second_chunk, "AI Concepts.txt", 0.25),
    ]

    with patch(
        "app.services.semantic_search.generate_embeddings",
        return_value=[[0.0] * 384],
    ):
        results = search_similar_chunks(
            db,
            "How does RAG work?",
            top_k=2,
        )

    assert len(results) == 2
    assert results[0]["chunk_id"] == 10
    assert results[0]["similarity"] == 0.9
    assert results[1]["similarity"] == 0.75

    db.execute.assert_called_once()