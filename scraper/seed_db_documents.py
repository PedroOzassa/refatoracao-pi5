import json
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from db.mongodb_client import MongoDBClient
from db.template import Document
from scraper.crawler import crawl
from scraper.parser import parse_site


def load_documents_from_json(filepath: str) -> list[Document]:
    """Load documents from a JSON file and convert to Document objects."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    documents = []
    for item in data:
        date_str = item.get("date", "")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            date = datetime.now()

        documents.append(
            Document(
                title=item["title"],
                content=item["content"],
                date=date,
                source=item["source"],
                tag=item.get("tag"),
                _id=None,
            )
        )

    return documents


def load_scraped_documents(start_url: str) -> list[Document]:
    """Crawl the site, parse each page, and convert results to Document objects."""
    documents: list[Document] = []
    seen: set[tuple[str, str, str]] = set()

    for url in sorted(crawl(start_url)):
        try:
            for item in parse_site(url):
                key = (item["source"], item["title"], item["content"])
                if key in seen:
                    continue
                seen.add(key)

                date_str = item.get("date", "")
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    date = datetime.now()

                tag = item.get("tag")
                documents.append(
                    Document(
                        title=item["title"],
                        content=item["content"],
                        date=date,
                        source=item["source"],
                        tag=tag if isinstance(tag, list) else [tag] if tag else None,
                    )
                )
        except Exception as exc:
            print(f"Skipping {url}: {exc}")

    return documents


def seed_db_documents() -> None:
    base_path = Path(__file__).resolve().parents[1]
    json_documents = load_documents_from_json(str(base_path / "faq_documents.json"))
    scraped_documents = load_scraped_documents("https://agibank.com.br/")

    with MongoDBClient(database="chatbot-data") as client:
        if json_documents:
            client.insert_many("rag_documents", json_documents)

        if scraped_documents:
            client.insert_many("scraped_documents", scraped_documents)
