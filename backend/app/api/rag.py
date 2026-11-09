import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from google.genai import errors as genai_errors
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.rag_service import answer_question

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["RAG"])


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=20)
    document_id: int | None = Field(
        default=None,
        gt=0,
    )


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
            document_id=request.document_id,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
    
    except genai_errors.APIError as exc:
        logger.error(
            "Gemini API request failed: %s",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=503,
            detail="AI service is temporarily unavailable.",
        ) from exc

    except RuntimeError as exc:
        logger.error(
            "RAG generation failed: %s",
            type(exc).__name__,
        )
        raise HTTPException(
            status_code=503,
            detail="Answer generation is currently unavailable.",
        ) from exc