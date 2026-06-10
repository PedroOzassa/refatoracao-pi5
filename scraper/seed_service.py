"""Seed service - orchestrates data seeding with dependency injection."""

import json
from pathlib import Path
from typing import List

from domain.entities.document import Document
from domain.repositories.document_repository import DocumentRepository


class SeedService:
    """Service to manage document seeding from various sources.
    
    Handles:
    1. Loading documents from JSON files
    2. Inserting documents into the database
    3. Orchestrating the seeding workflow
    """

    def __init__(self, document_repository: DocumentRepository):
        """Initialize seed service with injected repository.
        
        Args:
            document_repository: Repository for persisting documents.
        """
        self.document_repository = document_repository

    def load_documents_from_json(self, filepath: str) -> List[Document]:
        """Load documents from a JSON file.
        
        Args:
            filepath: Path to JSON file.
            
        Returns:
            List of Document entities.
            
        Raises:
            FileNotFoundError: If file doesn't exist.
            json.JSONDecodeError: If JSON is invalid.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        documents = []
        for item in data:
            documents.append(Document.from_dict(item))

        return documents

    def save_documents_to_json(self, documents: List[Document], filepath: str) -> None:
        """Save documents to a JSON file.
        
        Args:
            documents: List of documents to save.
            filepath: Path to output file.
        """
        data = [doc.to_dict() for doc in documents]

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def seed_from_json(self, json_filepath: str) -> int:
        """Load documents from JSON and insert into database.
        
        Args:
            json_filepath: Path to JSON file with documents.
            
        Returns:
            Number of documents inserted.
            
        Raises:
            FileNotFoundError: If JSON file doesn't exist.
        """
        documents = self.load_documents_from_json(json_filepath)

        inserted_ids = self.document_repository.insert_many(documents)

        return len(inserted_ids)

    def seed_from_pdf(self, pdf_path: str, output_json: str = None) -> int:
        """Process PDF and seed documents to database.
        
        Workflow:
        1. Extract documents from PDF
        2. Optionally save to JSON
        3. Insert into database
        
        Args:
            pdf_path: Path to PDF file.
            output_json: Optional path to save extracted documents as JSON.
            
        Returns:
            Number of documents inserted.
            
        Raises:
            FileNotFoundError: If PDF file doesn't exist.
        """
        # Import here to avoid circular dependency
        from scraper.pdf_scraper import build_documents

        # Extract documents from PDF
        documents = build_documents(pdf_path)

        # Optionally save to JSON
        if output_json:
            self.save_documents_to_json(documents, output_json)

        # Insert into database
        inserted_ids = self.document_repository.insert_many(documents)

        return len(inserted_ids)

    def check_and_seed(self, json_filepath: str, pdf_path: str = None) -> int:
        """Check if JSON exists, otherwise extract from PDF and seed.
        
        Workflow:
        1. If JSON exists, load and seed from JSON
        2. Otherwise, extract from PDF, save JSON, and seed
        3. Return count of inserted documents
        
        Args:
            json_filepath: Path to JSON file (for both loading and saving).
            pdf_path: Optional path to PDF (used if JSON doesn't exist).
            
        Returns:
            Number of documents inserted.
            
        Raises:
            FileNotFoundError: If neither JSON nor PDF exist.
        """
        json_path = Path(json_filepath)

        if json_path.exists():
            # Load from existing JSON
            return self.seed_from_json(json_filepath)
        elif pdf_path:
            # Extract from PDF and save to JSON
            return self.seed_from_pdf(pdf_path, json_filepath)
        else:
            raise FileNotFoundError(
                f"Neither JSON file ({json_filepath}) nor PDF path provided"
            )
