"""Main entry point for data initialization (refactored).

This is a wrapper around scripts/initialize_data.py that orchestrates
the full data initialization workflow using dependency injection.

Workflow:
1. Load or extract documents from PDF
2. Seed documents to MongoDB
3. Load embeddings using FAISS
"""

from scripts.initialize_data import initialize_data


if __name__ == "__main__":
    # Run initialization with default parameters
    success = initialize_data(
        pdf_path="faq.pdf",
        json_path="faq_documents.json",
        force_rebuild=False,
    )
    
    # Exit with appropriate status code
    import sys
    sys.exit(0 if success else 1)