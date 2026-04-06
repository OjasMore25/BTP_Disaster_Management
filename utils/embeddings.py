"""Embedding utilities for text vectorization."""

from typing import List

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional dependency
    np = None

try:
    from sentence_transformers import SentenceTransformer
except ImportError:  # pragma: no cover - optional dependency
    SentenceTransformer = None

try:
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:  # pragma: no cover - optional dependency
    cosine_similarity = None


class EmbeddingModel:
    """Handle transformer-backed text embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        if SentenceTransformer is None:
            raise ImportError("Install sentence-transformers: pip install sentence-transformers")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str):
        return self.model.encode(text)

    def embed_texts(self, texts: List[str]):
        return self.model.encode(texts)

    def similarity(self, text1: str, text2: str) -> float:
        embeddings = self.model.encode([text1, text2])
        return _safe_cosine(embeddings[0], embeddings[1])

    def semantic_search(self, query: str, texts: List[str], top_k: int = 5) -> List[tuple]:
        query_embedding = self.embed_text(query)
        text_embeddings = self.embed_texts(texts)

        similarities = [_safe_cosine(query_embedding, vec) for vec in text_embeddings]
        top_indices = sorted(range(len(similarities)), key=lambda idx: similarities[idx], reverse=True)[:top_k]
        return [(texts[idx], similarities[idx], idx) for idx in top_indices]


class SimpleEmbedding:
    """Simple hash-based fallback embedding."""

    def __init__(self):
        self.vocab = {}
        self.embedding_dim = 100

    def embed_text(self, text: str):
        words = text.lower().split()
        if np is None:
            embedding = [0.0] * self.embedding_dim
        else:
            embedding = np.zeros(self.embedding_dim)
        for i, word in enumerate(words[: self.embedding_dim]):
            embedding[i] = hash(word) % 100 / 100.0
        return embedding

    def embed_texts(self, texts: list):
        embeddings = [self.embed_text(text) for text in texts]
        if np is None:
            return embeddings
        return np.array(embeddings)


def _safe_cosine(vec1, vec2) -> float:
    if cosine_similarity is not None:
        return float(cosine_similarity([vec1], [vec2])[0][0])

    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (norm1 * norm2)
