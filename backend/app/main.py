
from fastapi import FastAPI

app = FastAPI(
    title="KnowledgeForge AI",
    description="An enterprise RAG knowledge assistant",
    version="0.1.0",
)


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
