from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.rag_service import answer_question

router = APIRouter(prefix="/rag", tags=["RAG"])


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=20)


@router.post("/ask")
def ask_question(
    request: QuestionRequest,
    db: Annotated[Session, Depends(get_db)],
):
    try:
        return answer_question(
            db=db,
            question=request.question,
            top_k=request.top_k,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc