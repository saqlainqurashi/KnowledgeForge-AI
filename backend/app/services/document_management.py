from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk


def list_documents(db: Session) -> list[dict]:
    """Return stored documents and their chunk counts."""

    statement = (
        select(
            Document.id,
            Document.filename,
            Document.created_at,
            func.count(DocumentChunk.id).label("total_chunks"),
        )
        .outerjoin(
            DocumentChunk,
            DocumentChunk.document_id == Document.id,
        )
        .group_by(
            Document.id,
            Document.filename,
            Document.created_at,
        )
        .order_by(Document.created_at.desc(), Document.id.desc())
    )

    rows = db.execute(statement).all()

    return [
        {
            "id": row.id,
            "filename": row.filename,
            "created_at": row.created_at,
            "total_chunks": row.total_chunks,
        }
        for row in rows
    ]


def delete_document(db: Session, document_id: int) -> bool:
    """Delete a document and its associated chunks."""

    document = db.get(Document, document_id)

    if document is None:
        return False

    try:
        db.delete(document)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return True