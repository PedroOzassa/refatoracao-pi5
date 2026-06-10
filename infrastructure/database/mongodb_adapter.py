"""MongoDB Document Repository Adapter."""

from typing import Optional

from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError

from domain.entities.document import Document
from domain.repositories.document_repository import DocumentRepository
from infrastructure.config import get_settings


class MongoDBDocumentRepository(DocumentRepository):
    """MongoDB implementation of DocumentRepository.
    
    Implements the DocumentRepository interface by providing CRUD operations
    on Document entities stored in MongoDB Atlas or MongoDB Server.
    
    Supports lazy-loading of the database connection and configurable
    collection name and database name via settings.
    """

    def __init__(
        self,
        uri: str = None,
        database: str = None,
        collection: str = None,
    ):
        """Initialize MongoDB Document Repository.
        
        Args:
            uri: MongoDB connection URI (defaults to settings.MONGODB_URI).
            database: Database name (defaults to settings.MONGODB_DATABASE).
            collection: Default collection name (defaults to settings.MONGODB_COLLECTION).
            
        Raises:
            ValueError: If URI is not provided or empty.
        """
        settings = get_settings()
        
        self.uri = uri or settings.MONGODB_URI
        self.database_name = database or settings.MONGODB_DATABASE
        self.collection_name = collection or settings.MONGODB_COLLECTION
        
        if not self.uri:
            raise ValueError(
                "MongoDB URI is required. "
                "Set MONGODB_URI environment variable or pass it to the constructor."
            )
        
        self._client: Optional[MongoClient] = None

    def _ensure_connected(self) -> None:
        """Ensure MongoDB connection is established.
        
        Raises:
            RuntimeError: If the connection fails.
        """
        if self._client is None:
            try:
                self._client = MongoClient(self.uri)
                # Verify connection with ping
                self._client.admin.command("ping")
            except PyMongoError as e:
                raise RuntimeError(f"Failed to connect to MongoDB: {e}") from e

    def _get_collection(self, collection: str = None):
        """Get a MongoDB collection.
        
        Args:
            collection: Collection name (defaults to self.collection_name).
            
        Returns:
            pymongo.collection.Collection: The collection object.
        """
        self._ensure_connected()
        coll_name = collection or self.collection_name
        return self._client[self.database_name][coll_name]

    def close(self) -> None:
        """Close the MongoDB connection.
        
        Should be called when the repository is no longer needed.
        """
        if self._client is not None:
            self._client.close()
            self._client = None

    def insert_one(self, document: Document) -> str:
        """Insert a single document.
        
        Args:
            document: The Document entity to insert.
            
        Returns:
            str: The ID of the inserted document (MongoDB ObjectId as string).
            
        Raises:
            ValueError: If the document already exists (duplicate key).
            RuntimeError: If the database operation fails.
        """
        try:
            doc_dict = document.to_dict()
            result = self._get_collection().insert_one(doc_dict)
            return str(result.inserted_id)
        except DuplicateKeyError as e:
            raise ValueError(f"Duplicate document with source '{document.source}': {e}") from e
        except PyMongoError as e:
            raise RuntimeError(f"Failed to insert document: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error during insert: {e}") from e

    def insert_many(self, documents: list[Document]) -> list[str]:
        """Insert multiple documents.
        
        Args:
            documents: List of Document entities to insert.
            
        Returns:
            list[str]: List of IDs of the inserted documents (MongoDB ObjectIds as strings).
            
        Raises:
            RuntimeError: If the bulk insert operation fails.
        """
        if not documents:
            return []
        
        try:
            docs_dicts = [doc.to_dict() for doc in documents]
            result = self._get_collection().insert_many(docs_dicts, ordered=False)
            return [str(oid) for oid in result.inserted_ids]
        except PyMongoError as e:
            raise RuntimeError(f"Failed to insert {len(documents)} documents: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error during bulk insert: {e}") from e

    def find_by_source(self, source: str) -> Optional[Document]:
        """Find a single document by its source field.
        
        Args:
            source: The source identifier (expected to be unique).
            
        Returns:
            Optional[Document]: The matching document, or None if not found.
            
        Raises:
            RuntimeError: If the database query fails.
        """
        try:
            doc_dict = self._get_collection().find_one({"source": source})
            return Document.from_dict(doc_dict) if doc_dict else None
        except PyMongoError as e:
            raise RuntimeError(f"Failed to find document by source '{source}': {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error during find by source: {e}") from e

    def find_all(self) -> list[Document]:
        """Retrieve all documents from the repository.
        
        Returns:
            list[Document]: List of all documents, or empty list if none exist.
            
        Raises:
            RuntimeError: If the database query fails.
        """
        try:
            cursor = self._get_collection().find()
            return [Document.from_dict(doc_dict) for doc_dict in cursor]
        except PyMongoError as e:
            raise RuntimeError(f"Failed to retrieve all documents: {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error during find all: {e}") from e

    def search_title(self, keyword: str) -> list[Document]:
        """Search documents by title (case-insensitive).
        
        Args:
            keyword: The search keyword to match in document titles.
            
        Returns:
            list[Document]: List of matching documents, or empty list if none found.
            
        Raises:
            ValueError: If the keyword is empty.
            RuntimeError: If the database query fails.
        """
        if not keyword or not keyword.strip():
            raise ValueError("Keyword cannot be empty")
        
        try:
            cursor = self._get_collection().find(
                {"title": {"$regex": keyword, "$options": "i"}}
            )
            return [Document.from_dict(doc_dict) for doc_dict in cursor]
        except PyMongoError as e:
            raise RuntimeError(f"Failed to search documents by title '{keyword}': {e}") from e
        except Exception as e:
            raise RuntimeError(f"Unexpected error during title search: {e}") from e
