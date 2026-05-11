import json
from pathlib import Path

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

from db.mongodb_client import MongoDBClient

load_dotenv()

INDEX_FILE = "index.faiss"
MAPPING_FILE = "mapping.json"
EMBEDDING_MODEL = "BAAI/bge-m3"
DATABASE_NAME = "chatbot-data"
COLLECTION_NAME = "rag_documents"


def load_embeddings() -> None:
    base_path = Path(__file__).resolve().parents[1]
    index_path = base_path / INDEX_FILE
    mapping_path = base_path / MAPPING_FILE

    model = SentenceTransformer(EMBEDDING_MODEL)

    with MongoDBClient(database=DATABASE_NAME) as client:
        collection = client._collection(COLLECTION_NAME)
        documents = list(collection.find())

    if not documents:
        print("Nenhum documento encontrado.")
        return

    embeddings = []
    mapping = {}
    valid_index = 0

    for doc in documents:
        texto = doc.get("content", "").strip()
        if not texto:
            continue

        embedding = model.encode(texto)
        embeddings.append(embedding)
        mapping[valid_index] = {
            "mongo_id": str(doc["_id"]),
            "titulo": doc.get("title", ""),
        }
        valid_index += 1

    if not embeddings:
        print("Nenhum embedding foi gerado. Verifique se os documentos tem o campo 'content'.")
        return

    vectors = np.array(embeddings).astype("float32")
    faiss.normalize_L2(vectors)

    dimension = vectors.shape[1]
    index = faiss.IndexFlatIP(dimension)
    index.add(vectors)

    faiss.write_index(index, str(index_path))
    print(f"Indice salvo em: {index_path}")

    with open(mapping_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, ensure_ascii=False, indent=4)

    print(f"Mapeamento salvo em: {mapping_path}")
