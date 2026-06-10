"""Context Repository interface - contract for retrieving relevant document context."""

from abc import ABC, abstractmethod


class ContextRepository(ABC):
    """Abstract base class for context retrieval repositories.
    
    Implementations (e.g., FAISSRepository) should inherit from this and implement
    the find_context() method to retrieve relevant documents based on semantic search.
    """

    @abstractmethod
    def find_context(self, query: str, top_k: int = 3, threshold: float = 0.45) -> str:
        """Find relevant context documents for the given query.
        
        Performs semantic similarity search to retrieve the most relevant documents
        from the indexed corpus.
        
        Args:
            query: The search query (user question).
            top_k: Maximum number of top results to retrieve (default: 3).
            threshold: Minimum similarity score threshold for results (default: 0.45).
            
        Returns:
            str: Concatenated text of relevant documents (formatted with titles and content).
                 Returns empty string if no relevant context is found.
                 
        Raises:
            RuntimeError: If the index or embedding model is unavailable.
            ValueError: If the query is invalid.
        """
        pass
