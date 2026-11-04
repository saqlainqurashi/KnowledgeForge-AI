from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk
from app.services.embeddings import generate_embeddings


def search_similar_chunks(
    db: Session,
    query: str,
    top_k: int = 3,
    min_similarity: float = 0.0,
) -> list[dict]:
    """Find document chunks most similar to a question."""

    if not query.strip():
        raise ValueError("Search query cannot be empty")

    if not 1 <= top_k <= 20:
        raise ValueError("top_k must be between 1 and 20")

    if not 0.0 <= min_similarity <= 1.0:
        raise ValueError(
            "min_similarity must be between 0 and 1"
        )

    # Generate the question embedding
    query_embedding = generate_embeddings([query])[0]

    # Calculate cosine distance
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    # Retrieve chunks that meet the similarity threshold
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
        .where(distance <= 1 - min_similarity)
        .order_by(distance)
        .limit(top_k)
    )

    results = db.execute(statement).all()

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