from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk
from app.services.embeddings import generate_embeddings


def search_similar_chunks(
    db: Session,
    query: str,
    top_k: int = 3,
) -> list[dict]:
    """Find document chunks most similar to a question."""

    if not query.strip():
        raise ValueError("Search query cannot be empty")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20")

    # Step 1: Convert the question into an embedding.
    query_embedding = generate_embeddings([query])[0]

    # Step 2: Calculate cosine distance.
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    # Step 3: Find the closest document chunks.
    statement = (
        select(
            DocumentChunk,
            Document.filename,
            distance.label("distance"),
        )
        .join(
            Document,
            DocumentChunk.document_id == Document.id,
        )
        .order_by(distance)
        .limit(top_k)
    )

    results = db.execute(statement).all()

    # Step 4: Return results with similarity scores.
    return [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "filename": filename,
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "similarity": round(1 - float(distance_value), 4),
        }
        for chunk, filename, distance_value in results
    ]