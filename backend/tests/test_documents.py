from io import BytesIO

from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.main import app
from app.services.document_loader import MAX_FILE_SIZE

client = TestClient(app)


def test_upload_txt_successfully():
    content = b"KnowledgeForge AI is an enterprise knowledge assistant."

    response = client.post(
        "/documents/upload",
        files={
            "file": (
                "knowledge.txt",
                content,
                "text/plain",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "knowledge.txt"
    assert data["status"] == "stored"
    assert data["total_characters"] == len(content.decode())
    assert data["total_chunks"] == 1
    assert len(data["chunks"]) == 1


def test_upload_pdf_successfully():
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
