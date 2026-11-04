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


def test_search_successfully():
    fake_results = [
        {
            "chunk_id": 1,
            "document_id": 1,
            "filename": "AI Concepts.txt",
            "chunk_index": 0,
            "content": "RAG retrieves relevant information.",
            "similarity": 0.91,
        }
    ]

    with patch(
        "app.api.search.search_similar_chunks",
        return_value=fake_results,
    ) as mock_search:
        response = client.post(
            "/search/",
            json={
                "query": "What is RAG?",
                "top_k": 3,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["query"] == "What is RAG?"
    assert data["total_results"] == 1
    assert data["results"][0]["similarity"] == 0.91

    mock_search.assert_called_once()


def test_search_rejects_invalid_top_k():
    response = client.post(
        "/search/",
        json={
            "query": "What is RAG?",
            "top_k": 25,
        },
    )

    assert response.status_code == 422


def test_search_rejects_empty_query():
    response = client.post(
        "/search/",
        json={
            "query": "",
            "top_k": 3,
        },
    )

    assert response.status_code == 422


def test_search_rejects_whitespace_query():
    with patch(
        "app.api.search.search_similar_chunks",
        side_effect=ValueError("Search query cannot be empty"),
    ):
        response = client.post(
            "/search/",
            json={
                "query": "   ",
                "top_k": 3,
            },
        )

    assert response.status_code == 400