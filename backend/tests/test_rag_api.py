from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.core.database import get_db
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_database():
    previous_overrides = app.dependency_overrides.copy()

    def override_get_db():
        yield object()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides = previous_overrides


def test_rag_ask_success():
    fake_response = {
        "question": "What is RAG?",
        "answer": "RAG combines retrieval and generation [1].",
        "sources": [
            {
                "source_number": 1,
                "document_id": 10,
                "filename": "AI Concepts.txt",
                "chunk_index": 0,
                "similarity": 0.92,
            }
        ],
    }

    with patch(
        "app.api.rag.answer_question",
        return_value=fake_response,
    ) as mock_answer:
        response = client.post(
            "/rag/ask",
            json={
                "question": "What is RAG?",
                "top_k": 3,
            },
        )

    assert response.status_code == 200
    assert response.json() == fake_response
    mock_answer.assert_called_once()


def test_rag_reject_empty_question():
    response = client.post(
        "/rag/ask",
        json={
            "question": "",
            "top_k": 3,
        },
    )

    assert response.status_code == 422


def test_rag_reject_invalid_top_k():
    response = client.post(
        "/rag/ask",
        json={
            "question": "What is RAG?",
            "top_k": 25,
        },
    )

    assert response.status_code == 422


def test_rag_reject_whitespace_question():
    with patch(
        "app.api.rag.answer_question",
        side_effect=ValueError("Question cannot be empty"),
    ):
        response = client.post(
            "/rag/ask",
            json={
                "question": "   ",
                "top_k": 3,
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Question cannot be empty"