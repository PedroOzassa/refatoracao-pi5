"""DIContainer - Dependency Injection container for application dependencies."""

from typing import Optional

from infrastructure.config import get_settings, Settings
from infrastructure.llm.llm_chain import LLMChain
from infrastructure.llm.mistral_adapter import MistralAdapter
from infrastructure.llm.gpt_adapter import GPTAdapter
from infrastructure.embedding.faiss_embedding import FAISSEmbedding
from infrastructure.embedding.faiss_repository import FAISSRepository
from infrastructure.database.mongodb_adapter import MongoDBDocumentRepository
from domain.repositories.embedding_provider import EmbeddingProvider
from domain.repositories.context_repository import ContextRepository
from domain.repositories.document_repository import DocumentRepository
from domain.repositories.llm_provider import LLMProvider


class DIContainer:
    """Dependency Injection Container.
    
    Manages the creation and lifecycle of all application dependencies.
    Provides factory methods to retrieve fully-configured service instances.
    
    Uses lazy initialization and caching for singleton-like services.
    All configuration is loaded from Settings (environment variables).
    
    Example usage:
        container = DIContainer()
        
        llm_chain = container.get_llm_chain()
        embedding = container.get_embedding_provider()
        context_repo = container.get_context_repository()
        doc_repo = container.get_document_repository()
    """

    def __init__(self):
        """Initialize the DI Container.
        
        Loads settings and initializes internal cache for singleton services.
        """
        self.settings: Settings = get_settings()
        
        # Caches for singleton instances
        self._llm_mistral: Optional[MistralAdapter] = None
        self._llm_gpt: Optional[GPTAdapter] = None
        self._llm_chain: Optional[LLMChain] = None
        self._embedding_provider: Optional[EmbeddingProvider] = None
        self._context_repository: Optional[ContextRepository] = None
        self._document_repository: Optional[DocumentRepository] = None

    # =====================================================================
    # LLM Providers
    # =====================================================================

    def get_mistral_adapter(self) -> MistralAdapter:
        """Get or create Mistral LLM adapter (singleton).
        
        Returns:
            MistralAdapter: Configured Mistral adapter instance.
            
        Raises:
            RuntimeError: If MISTRAL_HOST_URL is not configured.
        """
        if self._llm_mistral is None:
            self._llm_mistral = MistralAdapter(
                host_url=self.settings.MISTRAL_HOST_URL,
                model=self.settings.MISTRAL_MODEL,
                timeout=self.settings.MISTRAL_TIMEOUT,
            )
        return self._llm_mistral

    def get_gpt_adapter(self) -> GPTAdapter:
        """Get or create GPT LLM adapter (singleton).
        
        Returns:
            GPTAdapter: Configured GPT adapter instance.
            
        Raises:
            RuntimeError: If OPENAI_API_KEY is not configured.
        """
        if self._llm_gpt is None:
            self._llm_gpt = GPTAdapter(
                api_key=self.settings.OPENAI_API_KEY,
                model=self.settings.OPENAI_MODEL,
                base_url=self.settings.OPENAI_BASE_URL,
                timeout=self.settings.OPENAI_TIMEOUT,
            )
        return self._llm_gpt

    def get_llm_chain(self) -> LLMChain:
        """Get or create LLM Chain with fallback strategy (singleton).
        
        Creates a chain that tries Mistral first, then falls back to GPT.
        This provides high availability and cost optimization.
        
        Returns:
            LLMChain: Configured chain with ordered providers.
        """
        if self._llm_chain is None:
            providers = []
            
            # Try Mistral if configured
            if self.settings.MISTRAL_HOST_URL:
                try:
                    providers.append(self.get_mistral_adapter())
                except RuntimeError:
                    pass
            
            # Always add GPT as fallback if configured
            if self.settings.OPENAI_API_KEY:
                try:
                    providers.append(self.get_gpt_adapter())
                except RuntimeError:
                    pass
            
            if not providers:
                raise RuntimeError(
                    "No LLM providers configured. "
                    "Configure MISTRAL_HOST_URL or OPENAI_API_KEY."
                )
            
            self._llm_chain = LLMChain(providers)
        
        return self._llm_chain

    # =====================================================================
    # Embedding Providers
    # =====================================================================

    def get_embedding_provider(self) -> EmbeddingProvider:
        """Get or create Embedding provider (singleton).
        
        Returns:
            EmbeddingProvider: Configured embedding provider instance.
        """
        if self._embedding_provider is None:
            self._embedding_provider = FAISSEmbedding(
                model_name=self.settings.EMBEDDING_MODEL
            )
        return self._embedding_provider

    # =====================================================================
    # Repository Providers
    # =====================================================================

    def get_context_repository(self) -> ContextRepository:
        """Get or create Context Repository (singleton).
        
        Creates a FAISS-based repository for semantic similarity search.
        Uses the embedding provider to encode queries.
        
        Returns:
            ContextRepository: Configured context repository instance.
        """
        if self._context_repository is None:
            self._context_repository = FAISSRepository(
                embedding_provider=self.get_embedding_provider(),
                index_path=self.settings.INDEX_FILE,
                mapping_path=self.settings.MAPPING_FILE,
            )
        return self._context_repository

    def get_document_repository(self) -> DocumentRepository:
        """Get or create Document Repository (singleton).
        
        Creates a MongoDB-based repository for document persistence.
        
        Returns:
            DocumentRepository: Configured document repository instance.
        """
        if self._document_repository is None:
            self._document_repository = MongoDBDocumentRepository(
                uri=self.settings.MONGODB_URI,
                database=self.settings.MONGODB_DATABASE,
                collection=self.settings.MONGODB_COLLECTION,
            )
        return self._document_repository

    # =====================================================================
    # Lifecycle Management
    # =====================================================================

    def close(self) -> None:
        """Close all managed resources.
        
        Should be called when the container is no longer needed to ensure
        proper cleanup (e.g., close database connections).
        """
        if self._document_repository is not None:
            if hasattr(self._document_repository, 'close'):
                self._document_repository.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - clean up resources."""
        self.close()


# Global singleton instance (optional, for convenience)
_global_container: Optional[DIContainer] = None


def get_container() -> DIContainer:
    """Get or create the global DI container (singleton).
    
    This provides a convenient way to access the DI container throughout
    the application without having to pass it around.
    
    Returns:
        DIContainer: The global container instance.
    """
    global _global_container
    if _global_container is None:
        _global_container = DIContainer()
    return _global_container


def reset_container() -> None:
    """Reset the global container instance.
    
    Useful for testing to ensure a fresh container for each test.
    """
    global _global_container
    if _global_container is not None:
        _global_container.close()
    _global_container = None
