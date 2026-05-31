from scraper.seed_db_documents import seed_db_documents
from scraper.pdf_scraper import build_documents
from scraper.pdf_scraper import save_documents_to_json
from embedding.load_embeddings import load_embeddings

docs = build_documents("faq.pdf")
save_documents_to_json(docs, "faq_documents.json")
seed_db_documents()
load_embeddings()