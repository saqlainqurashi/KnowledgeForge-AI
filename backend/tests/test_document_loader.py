from io import BytesIO

import pytest  # type: ignore
from pypdf import PdfWriter  # type: ignore

from app.services.document_loader import (
    MAX_FILE_SIZE,
    extract_text,
)


def test_extract_text_from_txt():
    content = b"KnowledgeForge AI processes documents."

    result = extract_text("notes.txt", content)

    assert result == "KnowledgeForge AI processes documents."


def test_extract_text_strips_outer_whitespace():
    result = extract_text("notes.txt", b"  Hello world  \n")

    assert result == "Hello world"


def test_reject_unsupported_extension():
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text("notes.docx", b"some content")


def test_reject_empty_file():
    with pytest.raises(ValueError, match="File is empty"):
        extract_text("notes.txt", b"")


def test_reject_file_over_size_limit():
    content = b"x" * (MAX_FILE_SIZE + 1)

    with pytest.raises(ValueError, match="10 MB"):
        extract_text("notes.txt", content)


def test_reject_invalid_utf8():
    with pytest.raises(ValueError, match="UTF-8"):
        extract_text("notes.txt", b"\xff\xfe\xfa")


def test_extract_text_from_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=300, height=300)

    # Generate a valid PDF, then verify that an empty-text PDF is rejected.
    pdf_buffer = BytesIO()
    writer.write(pdf_buffer)

    with pytest.raises(ValueError, match="No extractable text"):
        extract_text("notes.pdf", pdf_buffer.getvalue())


def test_reject_malformed_pdf():
    with pytest.raises(ValueError, match="Could not read PDF"):
        extract_text("notes.pdf", b"This is not a PDF")


def test_reject_blank_filename():
    with pytest.raises(ValueError, match="Filename"):
        extract_text(" ", b"some content")
