"""
Embedding utilities for text vectorization
"""
import numpy as np
from typing import List, Union
try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMER = True
except ImportError:
    HAS_SENTENCE_TRANSFORMER = False


class EmbeddingModel:
    """Handle text embeddings"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding model
        
        Args:
            model_name: Name of sentence-transformer model
        """
        if not HAS_SENTENCE_TRANSFORMER:
            raise ImportError("Install sentence-transformers: pip install sentence-transformers")
        
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Embed single text
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        return self.model.encode(text)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Embed multiple texts
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Array of embedding vectors
        """
        return self.model.encode(texts)
    
    def similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        embeddings = self.model.encode([text1, text2])
        # Calculate cosine similarity
        from sklearn.metrics.pairwise import cosine_similarity
        return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    
    def semantic_search(self, query: str, texts: List[str], top_k: int = 5) -> List[tuple]:
        """
        Find most similar texts to query
        
        Args:
            query: Query text
            texts: List of texts to search
            top_k: Number of results to return
            
        Returns:
            List of tuples (text, similarity_score, index)
        """
        from sklearn.metrics.pairwise import cosine_similarity
        
        query_embedding = self.embed_text(query)
        text_embeddings = self.embed_texts(texts)
        
        similarities = cosine_similarity([query_embedding], text_embeddings)[0]
        
        # Get top k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append((texts[idx], similarities[idx], idx))
        
        return results


class SimpleEmbedding:
    """Simple TF-IDF style embedding (fallback if transformers unavailable)"""
    
    def __init__(self):
        self.vocab = {}
        self.embedding_dim = 100
    
    def embed_text(self, text: str) -> np.ndarray:
        """Create simple word-based embedding with fixed size"""
        words = text.lower().split()
        # Create fixed-size embedding filled with zeros
        embedding = np.zeros(self.embedding_dim)
        # Fill with word hashes up to embedding dimension
        for i, word in enumerate(words[:self.embedding_dim]):
            embedding[i] = hash(word) % 100 / 100.0
        return embedding
    
    def embed_texts(self, texts: list) -> np.ndarray:
        """Create embeddings for multiple texts with consistent dimensions"""
        embeddings = []
        for text in texts:
            embedding = self.embed_text(text)
            embeddings.append(embedding)
        return np.array(embeddings)
