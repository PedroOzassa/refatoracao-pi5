# ADR-003: Escolha do FAISS como Banco de Armazenamento Vetorial

- **Status:** Aceito
- **Data:** 2026-06
- **Contexto do projeto:** Chatbot RAG de atendimento ao cliente — AgiBank / Projeto Integrador 5 (PUC Campinas)

---

## Contexto

O pipeline RAG do projeto exige um componente de busca vetorial para recuperar os trechos de documentos mais relevantes para cada pergunta do usuário. O fluxo é:

1. Os documentos são convertidos em vetores de embedding (usando `sentence-transformers` com o modelo `BAAI/bge-m3`).
2. Esses vetores são persistidos em um índice para consulta eficiente.
3. A cada pergunta recebida, o embedding da pergunta é comparado ao índice para recuperar os `top-k` documentos mais similares (por similaridade de cosseno).
4. Os documentos recuperados formam o contexto enviado ao LLM.

Os requisitos para o banco vetorial foram:
- Ser executável localmente, sem necessidade de serviço externo.
- Suportar busca por similaridade de cosseno eficiente.
- Ter boa integração com Python e NumPy.
- Ser adequado ao volume de dados do protótipo (alguns centenas de documentos).

---

## Decisão

Adotar o **FAISS** (`faiss-cpu`) da Meta AI como solução de indexação e busca vetorial, com o índice persistido nos arquivos `index.faiss` e `mapping.json`.

---

## Alternativas Consideradas

### Chroma
- Banco vetorial com API de alto nível, persistência automática e interface amigável para projetos RAG.
- Adiciona uma dependência de servidor ou processo separado na versão persistente.
- Possui overhead maior para o volume de dados do projeto.
- Seria uma escolha válida se o projeto exigisse gerenciamento mais elaborado de coleções e metadados.

### Pinecone / Weaviate / Qdrant (soluções cloud ou self-hosted)
- Soluções managed (Pinecone) ou self-hosted (Weaviate, Qdrant) de alto desempenho para produção.
- Adicionam dependência de serviço externo ou containers Docker, aumentando a complexidade operacional para um protótipo acadêmico.
- Pinecone tem custos associados fora do tier gratuito limitado.

### Busca exaustiva com NumPy (sem FAISS)
- Viável para volumes pequenos, mas não escalável.
- Exigiria implementação manual das operações de similaridade e normalização de vetores.
- O FAISS já abstrai isso de forma otimizada.

### pgvector (extensão do PostgreSQL)
- Requereria um banco PostgreSQL configurado, adicionando complexidade de infraestrutura.
- Não faz sentido dado que o banco de documentos já é MongoDB.

---

## Justificativa

O FAISS foi escolhido pelos seguintes motivos:

1. **Execução local e sem serviços externos:** O FAISS é uma biblioteca Python que roda inteiramente no processo da aplicação — não há servidor, daemon ou container adicional para gerenciar. O índice é carregado diretamente do arquivo `index.faiss`.
2. **Alta performance para o tamanho do dataset:** Para o volume do projeto (documentos do FAQ do AgiBank), o índice `IndexFlatIP` (produto interno, equivalente à similaridade de cosseno com vetores normalizados) oferece busca exata com latência desprezível.
3. **Integração direta com NumPy:** Os embeddings do `sentence-transformers` retornam arrays NumPy, e o FAISS os consome diretamente — sem camadas de conversão extras.
4. **Normalização L2 para similaridade de cosseno:** O projeto normaliza os vetores com `faiss.normalize_L2()` antes da indexação e busca, convertendo produto interno em similaridade de cosseno — abordagem padrão e eficiente.
5. **Portabilidade:** O índice é serializado em dois arquivos (`index.faiss` e `mapping.json`) que podem ser versionados junto ao repositório e carregados em qualquer ambiente com `faiss.read_index()`.
6. **Maturidade:** FAISS é mantido pela Meta AI e é amplamente utilizado em produção para sistemas RAG e busca semântica.

---

## Consequências

**Positivas:**
- Zero dependência de infraestrutura externa para a busca vetorial.
- Latência de busca muito baixa para o volume de documentos do projeto.
- Índice pode ser pré-computado e versionado no repositório (`index.faiss` já incluso).
- Implementação limpa com lazy-loading no `FAISSRepository`, evitando carregamento desnecessário do índice em inicializações.

**Negativas / Riscos:**
- O índice `IndexFlatIP` realiza busca exata (força bruta), o que não escala para milhões de vetores — seria necessário migrar para índices aproximados (HNSW, IVF) em produção.
- Não há suporte nativo a filtragem por metadados durante a busca vetorial; a filtragem é feita em pós-processamento no `mapping.json`.
- Se o corpus de documentos mudar com frequência, o índice precisa ser regerado por completo (`initialize_data.py`), o que pode ser custoso com o modelo `BAAI/bge-m3`.
