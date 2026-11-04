from functools import lru_cache

from sentence_transformers import SentenceTransformer

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    """Load the model once and reuse it."""

    return SentenceTransformer(
        MODEL_NAME,
        device="cpu",
    )


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Convert a list of text passages into normalized embeddings."""

    if not texts:
        return []

    if any(not text.strip() for text in texts):
        raise ValueError("Text passages cannot be empty")

    model = get_embedding_model()

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    if embeddings.shape != (len(texts), EMBEDDING_DIMENSION):
        raise RuntimeError("Unexpected embedding dimensions")

    return embeddings.tolist()
