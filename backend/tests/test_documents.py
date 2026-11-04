from io import BytesIO
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.core.database import get_db
from app.main import app
from app.services.document_loader import MAX_FILE_SIZE

client = TestClient(app)


@pytest.fixture(autouse=True)
def mock_database():
    def override_get_db():
        yield object()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()


def test_upload_txt_successfully():
    with (
        patch(
            "app.api.documents.generate_embeddings",
            return_value=[[0.0] * 384],
        ),
        patch(
            "app.api.documents.save_document",
            return_value=SimpleNamespace(id=1),
        ) as mock_save,
    ):
        response = client.post(
            "/documents/upload",
            files={
                "file": (
                    "knowledge.txt",
                    b"KnowledgeForge AI is a RAG system.",
                    "text/plain",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["document_id"] == 1
    assert data["filename"] == "knowledge.txt"
    assert data["status"] == "stored"
    assert data["total_chunks"] == 1

    mock_save.assert_called_once()


def test_reject_blank_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    pdf_buffer = BytesIO()
    writer.write(pdf_buffer)

    # A blank PDF has no extractable text.
    # The endpoint should reject it.
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "document.pdf",
                pdf_buffer.getvalue(),
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("No extractable text found in document")


def test_reject_unsupported_file_type():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "document.docx",
                b"Some document content",
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("Only PDF and TXT files are supported")


def test_reject_empty_txt_file():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "empty.txt",
                b"",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "File is empty"


def test_reject_oversized_file():
    content = b"x" * (MAX_FILE_SIZE + 1)

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "large.txt",
                content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 413
    assert response.json()["detail"] == ("File exceeds the 10 MB size limit")


def test_reject_malformed_pdf():
    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "broken.pdf",
                b"This is not a valid PDF",
                "application/pdf",
            )
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == ("Could not read PDF file")
