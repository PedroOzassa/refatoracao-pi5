from busca import search

query = "Gostaria de contratar um serviço de seguro pelo Agi"

results = search(query)
print(results)

for result in results:
    print(f"Score: {result['score']:.4f}")
    print(f"FAISS Index: {result['faiss_index']}")
    print(result["mapping"])
    print("-" * 50)