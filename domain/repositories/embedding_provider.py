"""Embedding Provider interface - contract for embedding model implementations."""

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Abstract base class for Embedding providers.
    
    Implementations (e.g., SentenceTransformer-based adapters) should inherit
    from this and implement the embed() method to generate embeddings for texts.
    """

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate an embedding vector for the given text.
        
        Args:
            text: The text to embed.
            
        Returns:
            list[float]: The embedding vector (list of floats).
            
        Raises:
            RuntimeError: If the embedding model is unavailable or misconfigured.
            ValueError: If the text is invalid or cannot be embedded.
        """
        pass
