"""
MongoDB Atlas client for Document documents.

Schema:
    - title   (str)
    - content (str)
    - date    (datetime)
    - tag     (str | list[str])
    - source     (str)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.errors import DuplicateKeyError, PyMongoError
from .template import Document

class MongoDBClient:
    """
    Manages the connection to MongoDB Atlas and exposes insert / retrieve
    operations for Document documents.

    Usage:
        client = MongoDBClient()                          # reads MONGODB_URI env var

        with MongoDBClient() as client:
            client.insert_one("Documents", Document)
    """

    def __init__(
        self,
        database: str = "mydb",
    ) -> None:
        self._uri = os.environ.get("MONGODB_URI")
        if not self._uri:
            raise ValueError(
                "No MongoDB URI provided. "
                "Pass it explicitly or set the MONGODB_URI environment variable."
            )
        self._database_name = database
        self._client: Optional[MongoClient] = None

    # ------------------------------------------------------------------
    # Connection management
    # ------------------------------------------------------------------

    def connect(self) -> None:
        """Open the connection to MongoDB Atlas."""
        self._client = MongoClient(self._uri)
        # Ping to verify credentials early
        self._client.admin.command("ping")
        print(f"Connected to MongoDB Atlas — database: '{self._database_name}'")

    def disconnect(self) -> None:
        """Close the connection."""
        if self._client:
            self._client.close()
            self._client = None
            print("Disconnected from MongoDB Atlas.")

    def __enter__(self) -> "MongoDBClient":
        self.connect()
        return self

    def __exit__(self, *_) -> None:
        self.disconnect()

    def _collection(self, name: str) -> Collection:
        if self._client is None:
            raise RuntimeError("Not connected. Call connect() first.")
        return self._client[self._database_name][name]

    # ------------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------------

    def insert_one(self, collection: str, Document: Document) -> ObjectId:
        """Insert a single Document. Returns the new document's ObjectId."""
        try:
            result = self._collection(collection).insert_one(Document.to_dict())
            print(f"Inserted document: {result.inserted_id}")
            return result.inserted_id
        except DuplicateKeyError as exc:
            raise ValueError(f"Duplicate document: {exc}") from exc
        except PyMongoError as exc:
            raise RuntimeError(f"Insert failed: {exc}") from exc

    def insert_many(self, collection: str, Documents: list[Document]) -> list[ObjectId]:
        """Insert multiple Documents. Returns a list of new ObjectIds."""
        docs = [a.to_dict() for a in Documents]
        try:
            result = self._collection(collection).insert_many(docs, ordered=False)
            print(f"Inserted {len(result.inserted_ids)} documents.")
            return result.inserted_ids
        except PyMongoError as exc:
            raise RuntimeError(f"Bulk insert failed: {exc}") from exc

    # ------------------------------------------------------------------
    # Retrieve
    # ------------------------------------------------------------------


    def find_by_source(self, collection: str, source: str) -> Optional[Document]:
        """Return the Document with a specific source (expected to be unique)."""
        doc = self._collection(collection).find_one({"source": source})
        return Document.from_dict(doc) if doc else None

    def find_all(
        self,
        collection: str,
        limit: int = 100,
        skip: int = 0,
        sort_by: str = "date",
        sort_order: int = DESCENDING,
    ) -> list[Document]:
        """Return Documents with optional pagination and sorting."""
        cursor = (
            self._collection(collection)
            .find()
            .sort(sort_by, sort_order)
            .skip(skip)
            .limit(limit)
        )
        return [Document.from_dict(d) for d in cursor]

    def search_title(self, collection: str, keyword: str) -> list[Document]:
        """Case-insensitive search on the title field."""
        cursor = self._collection(collection).find(
            {"title": {"$regex": keyword, "$options": "i"}}
        )
        return [Document.from_dict(d) for d in cursor]
