from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from app.api.documents import router as documents_router
from app.api.rag import router as rag_router
from app.api.search import router as search_router

app = FastAPI(
    title="KnowledgeForge AI",
    description="An enterprise RAG knowledge assistant",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(documents_router)
app.include_router(search_router)
app.include_router(rag_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to KnowledgeForge AI",
        "status": "running",
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
    }
