from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk


def save_document(
    db: Session,
    filename: str,
    chunks: list[str],
    embeddings: list[list[float]],
) -> Document:
    """Store a document and its embedded chunks."""

    if not chunks:
        raise ValueError("Document must contain at least one chunk")

    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings must have equal lengths")

    document = Document(filename=filename)

    for index, (content, embedding) in enumerate(zip(chunks, embeddings)):
        document.chunks.append(
            DocumentChunk(
                chunk_index=index,
                content=content,
                embedding=embedding,
            )
        )

    try:
        db.add(document)
        db.commit()
        db.refresh(document)
    except Exception:
        db.rollback()
        raise

    return document
