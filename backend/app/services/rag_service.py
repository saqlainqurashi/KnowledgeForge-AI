from sqlalchemy.orm import Session

from app.services.gemini_service import generate_answer
from app.services.semantic_search import search_similar_chunks


def answer_question(
    db: Session,
    question: str,
    top_k: int = 3,
) -> dict:
    """Retrieve relevant chunks and generate a grounded answer."""

    if not question.strip():
        raise ValueError("Question cannot be empty")

    chunks = search_similar_chunks(
        db=db,
        query=question,
        top_k=top_k,
    )

    if not chunks:
        return {
            "question": question,
            "answer": "No relevant documents were found.",
            "sources": [],
        }

    context_parts = []

    for index, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"[{index}] Source: {chunk['filename']}\n"
            f"Content: {chunk['content']}"
        )

    context = "\n\n".join(context_parts)

    answer = generate_answer(
        question=question,
        context=context,
    )

    sources = [
        {
            "source_number": index,
            "document_id": chunk["document_id"],
            "filename": chunk["filename"],
            "chunk_index": chunk["chunk_index"],
            "similarity": chunk["similarity"],
        }
        for index, chunk in enumerate(chunks, start=1)
    ]

    return {
        "question": question,
        "answer": answer,
        "sources": sources,
    }