"""Document Repository interface - contract for document persistence."""

from abc import ABC, abstractmethod
from typing import Optional

from db.template import Document


class DocumentRepository(ABC):
    """Abstract base class for document repositories.
    
    Implementations (e.g., MongoDBDocumentRepository) should inherit from this
    and implement methods for CRUD operations on Document entities.
    """

    @abstractmethod
    def insert_one(self, document: Document) -> str:
        """Insert a single document.
        
        Args:
            document: The Document entity to insert.
            
        Returns:
            str: The ID of the inserted document.
            
        Raises:
            ValueError: If the document already exists (duplicate).
            RuntimeError: If the database operation fails.
        """
        pass

    @abstractmethod
    def insert_many(self, documents: list[Document]) -> list[str]:
        """Insert multiple documents.
        
        Args:
            documents: List of Document entities to insert.
            
        Returns:
            list[str]: List of IDs of the inserted documents.
            
        Raises:
            RuntimeError: If the bulk insert operation fails.
        """
        pass

    @abstractmethod
    def find_by_source(self, source: str) -> Optional[Document]:
        """Find a single document by its source field.
        
        Args:
            source: The source identifier (expected to be unique).
            
        Returns:
            Optional[Document]: The matching document, or None if not found.
            
        Raises:
            RuntimeError: If the database query fails.
        """
        pass

    @abstractmethod
    def find_all(self) -> list[Document]:
        """Retrieve all documents from the repository.
        
        Returns:
            list[Document]: List of all documents, or empty list if none exist.
            
        Raises:
            RuntimeError: If the database query fails.
        """
        pass

    @abstractmethod
    def search_title(self, keyword: str) -> list[Document]:
        """Search documents by title (case-insensitive).
        
        Args:
            keyword: The search keyword to match in document titles.
            
        Returns:
            list[Document]: List of matching documents, or empty list if none found.
            
        Raises:
            RuntimeError: If the database query fails.
        """
        pass
