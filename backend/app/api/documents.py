from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.chunking import chunk_text
from app.services.document_loader import MAX_FILE_SIZE, extract_text
from app.services.document_storage import save_document
from app.services.embeddings import generate_embeddings

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    filename = file.filename or ""

    if not filename.lower().endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported",
        )

    try:
        content = await file.read(MAX_FILE_SIZE + 1)

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail="File exceeds the 10 MB size limit",
            )

        extracted_text = extract_text(filename, content)

        chunks = chunk_text(
            extracted_text,
            chunk_size=500,
            chunk_overlap=50,
        )

        embeddings = generate_embeddings(chunks)

        document = save_document(
            db=db,
            filename=filename,
            chunks=chunks,
            embeddings=embeddings,
        )

        return {
            "document_id": document.id,
            "filename": filename,
            "status": "stored",
            "total_characters": len(extracted_text),
            "total_chunks": len(chunks),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    finally:
        await file.close()