from io import BytesIO

from pypdf import PdfReader  # type: ignore

SUPPORTED_EXTENSIONS = {".pdf", ".txt"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def extract_text(
    filename: str,
    content: bytes,
) -> str:
    """Extract text from a PDF or TXT file supplied as bytes."""

    if not filename or not filename.strip():
        raise ValueError("Filename cannot be empty")

    if len(content) > MAX_FILE_SIZE:
        raise ValueError("File exceeds the 10 MB size limit")

    extension = filename.lower().rsplit(".", 1)

    if len(extension) != 2:
        raise ValueError("File must have a .pdf or .txt extension")

    extension = f".{extension[1]}"

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError("Unsupported file type. Use PDF or TXT")

    if not content:
        raise ValueError("File is empty")

    if extension == ".txt":
        try:
            text = content.decode("utf-8-sig")
        except UnicodeDecodeError as exc:
            raise ValueError("TXT file must use UTF-8 encoding") from exc

    else:
        try:
            reader = PdfReader(BytesIO(content))

            if reader.is_encrypted:
                raise ValueError("Encrypted PDFs are not supported")

            text = "\n".join(page.extract_text() or "" for page in reader.pages)

        except ValueError:
            raise
        except Exception as exc:
            raise ValueError("Could not read PDF file") from exc

    if not text.strip():
        raise ValueError("No extractable text found in document")

    return text.strip()
