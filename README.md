# Chatbot Agi

Basic data-ingestion project for the Agi FAQ and website content.

## What it does

- Loads documents from `documents.json`
- Crawls the Agi site and parses page content
- Inserts the data into MongoDB collections

## Project Structure

- `db/` - MongoDB client and document model
- `scraper/` - site crawler and parser
- `scripts/seed_documents.py` - one-off ingestion script
- `documents.json` - source FAQ dataset

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Add your MongoDB connection string to `.env`:

```bash
MONGODB_URI="your-mongodb-uri"
```

## Run

Run the ingestion job with:

```bash
python scripts/seed_documents.py
```

This inserts:

- `documents.json` data into `rag_documents`
- scraped website content into `scraped_documents`
