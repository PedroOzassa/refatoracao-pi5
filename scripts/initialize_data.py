"""scripts/initialize_data.py - Initialize database with documents and embeddings.

This script orchestrates the full data initialization workflow:
1. Load or extract documents from PDF
2. Seed documents to MongoDB
3. Load embeddings using FAISS

Uses dependency injection (DIContainer) for all component creation.
"""

import logging
import sys
from pathlib import Path

from di.container import get_container, reset_container
from scraper.seed_service import SeedService


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_data(
    pdf_path: str = "faq.pdf",
    json_path: str = "faq_documents.json",
    force_rebuild: bool = False,
) -> bool:
    """Initialize database with documents and embeddings.
    
    Workflow:
    1. If JSON exists and not force_rebuild, load from JSON
    2. Otherwise, extract from PDF and save to JSON
    3. Seed documents to MongoDB
    4. (Optional) Load embeddings to FAISS
    
    Args:
        pdf_path: Path to FAQ PDF file.
        json_path: Path to documents JSON file.
        force_rebuild: If True, always extract from PDF (ignore existing JSON).
        
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        logger.info("=" * 70)
        logger.info("INITIALIZING CHATBOT DATABASE")
        logger.info("=" * 70)

        # Initialize DI container
        logger.info("\n[Step 1] Initializing DI Container...")
        container = get_container()
        logger.info("  [OK] DIContainer created")

        # Get repositories from container
        logger.info("\n[Step 2] Getting repositories from container...")
        doc_repository = container.get_document_repository()
        logger.info("  [OK] DocumentRepository obtained")

        # Create seed service with DI
        logger.info("\n[Step 3] Creating SeedService...")
        seed_service = SeedService(doc_repository)
        logger.info("  [OK] SeedService created with injected DocumentRepository")

        # Seed documents
        logger.info("\n[Step 4] Seeding documents...")
        json_file = Path(json_path)

        if force_rebuild or not json_file.exists():
            # Extract from PDF and save to JSON
            logger.info(f"  Extracting documents from {pdf_path}...")
            if not Path(pdf_path).exists():
                logger.error(f"  [ERROR] PDF file not found: {pdf_path}")
                return False

            count = seed_service.seed_from_pdf(pdf_path, json_path)
            logger.info(f"  [OK] Extracted and seeded {count} documents from PDF")
        else:
            # Load from existing JSON
            logger.info(f"  Loading documents from {json_path}...")
            count = seed_service.seed_from_json(json_path)
            logger.info(f"  [OK] Seeded {count} documents from JSON")

        # Load embeddings (optional)
        logger.info("\n[Step 5] Loading embeddings...")
        try:
            embedding_provider = container.get_embedding_provider()
            logger.info("  [OK] FAISS embedding provider loaded")
            logger.info("  [INFO] Embeddings will be lazy-loaded on first query")
        except Exception as e:
            logger.warning(f"  [WARNING] Could not load embeddings: {e}")
            logger.info("  [INFO] Embeddings will be loaded on first use")

        # Cleanup
        logger.info("\n[Step 6] Cleaning up resources...")
        container.close()
        logger.info("  [OK] Resources cleaned up")

        logger.info("\n" + "=" * 70)
        logger.info("[SUCCESS] Database initialization complete!")
        logger.info("=" * 70)
        logger.info("\nYou can now start the FastAPI server:")
        logger.info("  python -m uvicorn api.handlers:app --reload")

        return True

    except Exception as e:
        logger.error(f"\n[ERROR] Initialization failed: {e}", exc_info=True)
        return False


def main():
    """Main entry point for script execution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Initialize Chatbot-AGI database with documents and embeddings."
    )
    parser.add_argument(
        "--pdf",
        default="faq.pdf",
        help="Path to FAQ PDF file (default: faq.pdf)"
    )
    parser.add_argument(
        "--json",
        default="faq_documents.json",
        help="Path to documents JSON file (default: faq_documents.json)"
    )
    parser.add_argument(
        "--force-rebuild",
        action="store_true",
        help="Force rebuild from PDF even if JSON exists"
    )

    args = parser.parse_args()

    # Run initialization
    success = initialize_data(
        pdf_path=args.pdf,
        json_path=args.json,
        force_rebuild=args.force_rebuild,
    )

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
