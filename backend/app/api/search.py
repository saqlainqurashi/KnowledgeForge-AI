from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.semantic_search import search_similar_chunks

router = APIRouter(prefix="/search", tags=["Semantic Search"])


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=20)


@router.post("/")
def semantic_search(
    request: SearchRequest,
    db: Session = Depends(get_db),
):
    try:
        results = search_similar_chunks(
            db=db,
            query=request.query,
            top_k=request.top_k,
        )

        return {
            "query": request.query,
            "total_results": len(results),
            "results": results,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc