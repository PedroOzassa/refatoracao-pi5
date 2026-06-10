"""Seed database documents - legacy entry point (refactored to use SeedService)."""

from pathlib import Path

from di.container import get_container
from scraper.seed_service import SeedService


def seed_db_documents() -> None:
    """Seed database with documents from FAQ JSON file.
    
    Uses dependency injection to get DocumentRepository from container.
    Inserts documents from faq_documents.json into the database.
    """
    # Get DI container
    container = get_container()

    # Get document repository from container
    doc_repository = container.get_document_repository()

    # Create seed service with injected repository
    seed_service = SeedService(doc_repository)

    # Get path to FAQ JSON file (relative to project root)
    base_path = Path(__file__).resolve().parents[1]
    json_filepath = str(base_path / "faq_documents.json")

    try:
        # Seed documents from JSON
        count = seed_service.seed_from_json(json_filepath)
        print(f"Successfully seeded {count} documents from {json_filepath}")
    except FileNotFoundError:
        print(f"Warning: FAQ documents file not found at {json_filepath}")
    except Exception as e:
        print(f"Error seeding documents: {e}")
        raise


if __name__ == "__main__":
    # Can be called directly for testing/setup
    seed_db_documents()

