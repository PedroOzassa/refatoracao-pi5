from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import os
from dotenv import load_dotenv

# ====================================
# CONFIGURAÇÕES
# ====================================

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "env"))
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")

if not MONGO_URI:
    raise RuntimeError("Variável MONGODB_URI ou MONGO_URI não encontrada. Verifique o arquivo 'env' ou o ambiente.")

DATABASE_NAME = "chatbot-data"

COLLECTION_NAME = "rag_documents"

INDEX_FILE = "index.faiss"

MAPPING_FILE = "mapping.json"

EMBEDDING_MODEL = "BAAI/bge-m3"

TOP_K = 3

# ====================================
# CONEXÃO MONGODB
# ====================================

client = MongoClient(MONGO_URI)

db = client[DATABASE_NAME]

collection = db[COLLECTION_NAME]
print(f"Conectado ao MongoDB: {MONGO_URI}")

# ====================================
# MODELO DE EMBEDDING
# ====================================

print("Carregando modelo de embedding...")

model = SentenceTransformer(EMBEDDING_MODEL)

print("Modelo carregado.\n")

# ====================================
# BUSCAR DOCUMENTOS
# ====================================

documents = list(collection.find())

if len(documents) == 0:
    print("Nenhum documento encontrado.")
    exit()

# ====================================
# GERAR EMBEDDINGS
# ====================================

embeddings = []

mapping = {}

valid_index = 0

for doc in documents:

    texto = doc.get("content", "").strip()

    if texto == "":
        continue

    print(f"Processando: {doc.get('title', 'Sem título')}")

    embedding = model.encode(texto)

    embeddings.append(embedding)

    mapping[valid_index] = {
        "mongo_id": str(doc["_id"]),
        "titulo": doc.get("title", "")
    }

    valid_index += 1

# ====================================
# CONVERTER PARA NUMPY
# ====================================

embeddings = np.array(embeddings).astype("float32")

if embeddings.size == 0:
    print("Nenhum embedding foi gerado. Verifique se os documentos têm o campo 'content'.")
    exit()

# ====================================
# NORMALIZAÇÃO (COSINE SIMILARITY)
# ====================================

faiss.normalize_L2(embeddings)

# ====================================
# CRIAR ÍNDICE FAISS
# ====================================

dimension = embeddings.shape[1]

index = faiss.IndexFlatIP(dimension)

index.add(embeddings)

# ====================================
# SALVAR ÍNDICE
# ====================================

faiss.write_index(index, INDEX_FILE)

print(f"\nÍndice salvo em: {INDEX_FILE}")

# ====================================
# SALVAR MAPEAMENTO
# ====================================

with open(MAPPING_FILE, "w", encoding="utf-8") as f:
    json.dump(mapping, f, ensure_ascii=False, indent=4)

print(f"Mapeamento salvo em: {MAPPING_FILE}")

print("\nIngestão concluída com sucesso.")