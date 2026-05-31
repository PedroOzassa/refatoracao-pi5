from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json

INDEX_FILE = "index.faiss"
MAPPING_FILE = "mapping.json"
EMBEDDING_MODEL = "BAAI/bge-m3"

model = SentenceTransformer(EMBEDDING_MODEL)
print("Modelo carregado.")

index = faiss.read_index(INDEX_FILE)
print("Índice carregado.")

with open(MAPPING_FILE, "r", encoding="utf-8") as f:
    mapping = json.load(f)

def find_context(query, top_k=3, threshold=0.45):
    # Prefixo recomendado pelo BGE
    query_text = (
        f"Represent this sentence for searching relevant passages: {query}"
    )

    query_embedding = model.encode(query_text)

    query_embedding = np.array([query_embedding]).astype("float32")

    faiss.normalize_L2(query_embedding)

    # Busca
    distances, indices = index.search(query_embedding, top_k)

    context_texts = []

    print(f"Searching for context for query: {query}")

    for score, idx in zip(distances[0], indices[0]):

        if idx == -1:
            continue

        if score < threshold:
            continue
        
        print(f"Score: {score}, Index: {idx}")
        mapped_data = mapping.get(str(idx))


        if not mapped_data:
            continue

        title = mapped_data.get("title", "")
        content = mapped_data.get("content", "")

        context_texts.append(title + "\n" + content)

    return "\n\n".join(context_texts)