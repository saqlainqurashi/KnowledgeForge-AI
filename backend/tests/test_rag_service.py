from unittest.mock import MagicMock, patch

import pytest

from app.services.rag_service import answer_question


def test_invalid_document_id():
    db = MagicMock()

    with pytest.raises(ValueError):
        answer_question(
            db=db,
            question="What is RAG?",
            document_id=-1,
        )

def test_reject_empty_question():
    db = MagicMock()

    with pytest.raises(ValueError, match="Question cannot be empty"):
        answer_question(db, "   ")


def test_no_documents_found():
    db = MagicMock()

    with patch(
        "app.services.rag_service.search_similar_chunks",
        return_value=[],
    ):
        result = answer_question(
            db,
            "What is RAG?",
        )

    assert result["question"] == "What is RAG?"
    assert result["answer"] == "No relevant documents were found."
    assert result["sources"] == []


def test_rag_generates_grounded_answer():
    db = MagicMock()

    fake_chunks = [
        {
            "chunk_id": 1,
            "document_id": 10,
            "filename": "AI Concepts.txt",
            "chunk_index": 0,
            "content": "RAG combines retrieval with generation.",
            "similarity": 0.92,
        },
        {
            "chunk_id": 2,
            "document_id": 10,
            "filename": "AI Concepts.txt",
            "chunk_index": 1,
            "content": "Embeddings help find relevant information.",
            "similarity": 0.85,
        },
    ]

    with (
        patch(
            "app.services.rag_service.search_similar_chunks",
            return_value=fake_chunks,
        ) as mock_search,
        patch(
            "app.services.rag_service.generate_answer",
            return_value=(
                "RAG retrieves relevant information "
                "before generating an answer [1]."
            ),
        ) as mock_generate,
    ):
        result = answer_question(
            db=db,
            question="How does RAG work?",
            top_k=2,
        )

    assert result["question"] == "How does RAG work?"
    assert "[1]" in result["answer"]
    assert len(result["sources"]) == 2
    assert result["sources"][0]["document_id"] == 10
    assert result["sources"][0]["source_number"] == 1

    mock_search.assert_called_once_with(
        db=db,
        query="How does RAG work?",
        top_k=2,
        min_similarity=0.60,
        document_id=None,
    )

    mock_generate.assert_called_once()

    generated_context = mock_generate.call_args.kwargs["context"]

    assert "[1] Source: AI Concepts.txt" in generated_context
    assert "RAG combines retrieval with generation." in generated_context
    assert "[2] Source: AI Concepts.txt" in generated_context



def test_irrelevant_context_does_not_call_gemini():
    db = MagicMock()

    with (
        patch(
            "app.services.rag_service.search_similar_chunks",
            return_value=[],
        ),
        patch(
            "app.services.rag_service.generate_answer",
        ) as mock_generate,
    ):
        result = answer_question(
            db,
            "What is the capital of France?",
        )

    assert result["sources"] == []
    assert result["answer"] == "No relevant documents were found."
    mock_generate.assert_not_called()




def test_rag_passes_document_filter():
    db = MagicMock()

    with patch(
        "app.services.rag_service.search_similar_chunks",
        return_value=[],
    ) as mock_search:
        result = answer_question(
            db=db,
            question="What is RAG?",
            document_id=7,
        )

    mock_search.assert_called_once_with(
        db=db,
        query="What is RAG?",
        top_k=3,
        min_similarity=0.60,
        document_id=7,
    )

    assert result["sources"] == []
    assert result["answer"] == "No relevant documents were found."