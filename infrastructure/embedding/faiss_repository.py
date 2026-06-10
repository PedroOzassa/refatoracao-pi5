"""FAISS Context Repository - semantic similarity search with lazy-load."""

import json
from pathlib import Path
from typing import Optional

import faiss
import numpy as np

from domain.repositories.context_repository import ContextRepository
from domain.repositories.embedding_provider import EmbeddingProvider
from infrastructure.config import get_settings
from infrastructure.embedding.faiss_embedding import FAISSEmbedding


class FAISSRepository(ContextRepository):
    """Context repository using FAISS for semantic similarity search.
    
    Implements the ContextRepository interface by searching pre-computed
    embeddings stored in a FAISS index file. Supports lazy-loading of
    the index and mapping to defer file I/O until first use.
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider = None,
        index_path: str = None,
        mapping_path: str = None,
        base_path: str = None,
    ):
        """Initialize FAISS context repository.
        
        Args:
            embedding_provider: EmbeddingProvider to encode queries (lazy defaults to FAISSEmbedding).
            index_path: Path to the FAISS index file (defaults to settings.INDEX_FILE in current dir).
            mapping_path: Path to the mapping JSON file (defaults to settings.MAPPING_FILE in current dir).
            base_path: Base directory for relative paths (defaults to current working directory).
            
        Raises:
            FileNotFoundError: If index or mapping files don't exist when accessed.
        """
        settings = get_settings()
        
        # Embedding provider (defaults to FAISSEmbedding)
        self.embedding_provider = embedding_provider or FAISSEmbedding()
        
        # Paths with lazy resolution
        self.base_path = Path(base_path or ".")
        self.index_path = Path(index_path or (self.base_path / settings.INDEX_FILE))
        self.mapping_path = Path(mapping_path or (self.base_path / settings.MAPPING_FILE))
        
        # Configuration for search
        self.default_top_k = settings.FAISS_TOP_K
        self.default_threshold = settings.FAISS_THRESHOLD
        
        # Lazy-loaded resources
        self._index: Optional[faiss.IndexFlatIP] = None
        self._mapping: Optional[dict] = None

    @property
    def index(self) -> faiss.IndexFlatIP:
        """Lazy-load the FAISS index.
        
        Returns:
            faiss.IndexFlatIP: The loaded FAISS index.
            
        Raises:
            FileNotFoundError: If the index file doesn't exist.
            RuntimeError: If the index cannot be loaded.
        """
        if self._index is None:
            if not self.index_path.exists():
                raise FileNotFoundError(
                    f"FAISS index file not found at: {self.index_path}. "
                    f"Run embedding.load_embeddings() to generate it."
                )

            try:
                self._index = faiss.read_index(str(self.index_path))
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load FAISS index from {self.index_path}: {e}"
                ) from e

        return self._index

    @property
    def mapping(self) -> dict:
        """Lazy-load the document mapping.
        
        Returns:
            dict: Mapping from index to document metadata (title, content, mongo_id).
            
        Raises:
            FileNotFoundError: If the mapping file doesn't exist.
            ValueError: If the mapping JSON is invalid.
        """
        if self._mapping is None:
            if not self.mapping_path.exists():
                raise FileNotFoundError(
                    f"Mapping file not found at: {self.mapping_path}. "
                    f"Run embedding.load_embeddings() to generate it."
                )

            try:
                with open(self.mapping_path, "r", encoding="utf-8") as f:
                    self._mapping = json.load(f)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON in mapping file {self.mapping_path}: {e}"
                ) from e
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load mapping file {self.mapping_path}: {e}"
                ) from e

        return self._mapping

    def find_context(
        self, query: str, top_k: Optional[int] = None, threshold: Optional[float] = None
    ) -> str:
        """Find relevant context documents for the given query.
        
        Performs semantic similarity search by:
        1. Encoding the query using the embedding provider
        2. Searching the FAISS index for the top-k most similar documents
        3. Filtering by similarity threshold
        4. Returning concatenated document content
        
        Args:
            query: The search query (user question).
            top_k: Maximum number of results to retrieve (defaults to settings.FAISS_TOP_K).
            threshold: Minimum similarity score threshold (defaults to settings.FAISS_THRESHOLD).
            
        Returns:
            str: Concatenated text of relevant documents (title + content), separated by "\\n\\n".
                 Returns empty string if no documents meet the threshold.
                 
        Raises:
            ValueError: If the query is empty.
            RuntimeError: If embedding or search fails.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        top_k = top_k or self.default_top_k
        threshold = threshold or self.default_threshold

        try:
            # Step 1: Encode the query using the embedding provider
            # Add BGE-specific prefix for better retrieval
            query_with_prefix = (
                f"Represent this sentence for searching relevant passages: {query}"
            )
            query_embedding = self.embedding_provider.embed(query_with_prefix)

            # Step 2: Prepare the query for FAISS search
            query_array = np.array([query_embedding]).astype("float32")
            faiss.normalize_L2(query_array)

            # Step 3: Search the FAISS index
            distances, indices = self.index.search(query_array, top_k)

            # Step 4: Process results
            context_texts = []
            
            for score, idx in zip(distances[0], indices[0]):
                # Skip invalid indices (-1 means no result found)
                if idx == -1:
                    continue

                # Filter by similarity threshold
                if score < threshold:
                    continue

                # Retrieve document from mapping
                mapped_data = self.mapping.get(str(idx))
                if not mapped_data:
                    continue

                title = mapped_data.get("title", "").strip()
                content = mapped_data.get("content", "").strip()

                # Concatenate title and content
                if title and content:
                    context_texts.append(f"{title}\n{content}")
                elif content:
                    context_texts.append(content)

            # Step 5: Return concatenated context
            return "\n\n".join(context_texts)

        except ValueError:
            # Re-raise ValueError (empty query)
            raise
        except RuntimeError:
            # Re-raise RuntimeError (embedding/FAISS failures)
            raise
        except Exception as e:
            raise RuntimeError(
                f"Error during context search for query '{query}': {e}"
            ) from e
