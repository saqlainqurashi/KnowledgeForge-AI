from app.services.embeddings import generate_embeddings

texts = [
    "KnowledgeForge AI is an enterprise RAG system.",
    "Retrieval-Augmented Generation combines search with AI."
]

print("Generating embeddings...", flush=True)

vectors = generate_embeddings(texts)

print("Number of vectors:", len(vectors))
print("Dimensions:", len(vectors[0]))
print("First five values:", vectors[0][:5])