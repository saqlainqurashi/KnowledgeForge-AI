from fastapi import FastAPI
from app.api.search import router as search_router
from app.api.documents import router as documents_router

app = FastAPI(
    title="KnowledgeForge AI",
    description="An enterprise RAG knowledge assistant",
    version="0.1.0",
)

app.include_router(documents_router)
app.include_router(search_router)

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
