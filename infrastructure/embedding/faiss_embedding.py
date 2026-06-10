"""FAISS Embedding Provider - SentenceTransformer-based embeddings with lazy-load."""

from typing import List

from sentence_transformers import SentenceTransformer

from domain.repositories.embedding_provider import EmbeddingProvider
from infrastructure.config import get_settings


class FAISSEmbedding(EmbeddingProvider):
    """Embedding provider using SentenceTransformer with lazy-load.
    
    Implements the EmbeddingProvider interface using the BAAI/bge-m3 model
    (or any configurable SentenceTransformer model). Supports lazy-loading
    of the model to defer initialization until first use.
    """

    def __init__(self, model_name: str = None):
        """Initialize FAISS embedding provider.
        
        Args:
            model_name: SentenceTransformer model name (defaults to settings.EMBEDDING_MODEL).
                       Examples: "BAAI/bge-m3", "sentence-transformers/all-MiniLM-L6-v2"
        """
        settings = get_settings()
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self._model: SentenceTransformer = None  # Lazy-load on first use

    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load the SentenceTransformer model.
        
        Returns:
            SentenceTransformer: The embedding model (loaded on first access).
        """
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.model_name)
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load SentenceTransformer model '{self.model_name}': {e}"
                ) from e

        return self._model

    def embed(self, text: str) -> List[float]:
        """Generate an embedding vector for the given text.
        
        Args:
            text: The text to embed.
            
        Returns:
            List[float]: The embedding vector.
            
        Raises:
            ValueError: If the text is empty.
            RuntimeError: If the model fails to generate an embedding.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        try:
            # The model.encode() returns a numpy array; convert to list
            embedding = self.model.encode(text)
            return embedding.tolist()

        except Exception as e:
            raise RuntimeError(
                f"Failed to generate embedding for text: {e}"
            ) from e
