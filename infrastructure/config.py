"""Centralized configuration management."""

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    # Database
    MONGODB_URI: str
    MONGODB_DATABASE: str = "chatbot-data"
    MONGODB_COLLECTION: str = "rag_documents"

    # LLM - Mistral
    MISTRAL_HOST_URL: str = ""
    MISTRAL_MODEL: str = "mistral:7b"
    MISTRAL_TIMEOUT: int = 10

    # LLM - OpenAI/GPT
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_TIMEOUT: int = 60

    # Embedding
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    INDEX_FILE: str = "index.faiss"
    MAPPING_FILE: str = "mapping.json"
    FAISS_TOP_K: int = 3
    FAISS_THRESHOLD: float = 0.45

    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True

    def __post_init__(self):
        """Validate required settings."""
        if not self.MONGODB_URI:
            raise ValueError("MONGODB_URI is required")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Load and cache settings from environment.
    
    Returns:
        Settings: Application configuration object (singleton).
    """
    load_dotenv()

    return Settings(
        MONGODB_URI=os.getenv("MONGODB_URI", ""),
        MONGODB_DATABASE=os.getenv("MONGODB_DATABASE", "chatbot-data"),
        MONGODB_COLLECTION=os.getenv("MONGODB_COLLECTION", "rag_documents"),
        MISTRAL_HOST_URL=os.getenv("MISTRAL_HOST_URL", ""),
        MISTRAL_MODEL=os.getenv("MISTRAL_MODEL", "mistral:7b"),
        MISTRAL_TIMEOUT=int(os.getenv("MISTRAL_TIMEOUT", "10")),
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY", ""),
        OPENAI_MODEL=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        OPENAI_BASE_URL=os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        OPENAI_TIMEOUT=int(os.getenv("OPENAI_TIMEOUT", "60")),
        EMBEDDING_MODEL=os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3"),
        INDEX_FILE=os.getenv("INDEX_FILE", "index.faiss"),
        MAPPING_FILE=os.getenv("MAPPING_FILE", "mapping.json"),
        FAISS_TOP_K=int(os.getenv("FAISS_TOP_K", "3")),
        FAISS_THRESHOLD=float(os.getenv("FAISS_THRESHOLD", "0.45")),
        API_HOST=os.getenv("API_HOST", "0.0.0.0"),
        API_PORT=int(os.getenv("API_PORT", "8000")),
        API_RELOAD=os.getenv("API_RELOAD", "true").lower() == "true",
    )
