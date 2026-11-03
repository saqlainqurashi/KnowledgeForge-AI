
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.services.chunking import chunk_text
from app.services.document_loader import (
    MAX_FILE_SIZE,
    extract_text,
)

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(file: Annotated[UploadFile, File(...)]):
    filename = file.filename or ""

    if not filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported",
        )

    content = await file.read(MAX_FILE_SIZE + 1)

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File exceeds the 10 MB size limit",
        )

    try:
        extracted_text = extract_text(filename, content)

        chunks = chunk_text(
            extracted_text,
            chunk_size=500,
            chunk_overlap=50,
        )

        return {
            "filename": filename,
            "status": "processed",
            "total_characters": len(extracted_text),
            "total_chunks": len(chunks),
            "chunks": chunks,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()
