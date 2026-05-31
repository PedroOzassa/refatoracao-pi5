# Chatbot-AGI

> Chatbot RAG (Retrieval-Augmented Generation) usando FAISS, embeddings por SentenceTransformers e geração via Mistral.

## Sobre o projeto

Este é um projeto acadêmico desenvolvido por alunos da PUC Campinas como parte do **Projeto Integrador 5**, em conjunto com a empresa **AgiBank**. O objetivo do projeto é construir um protótipo de chatbot de atendimento baseado em RAG (Retrieval-Augmented Generation) para demonstrar técnicas de NLP, recuperação vetorial e integração com LLMs.

Integrantes:

- Ana Julia Matozo Rodrigues
- Briann Oliveira Gomes
- Hugo Daniel Bosada Rodrigues
- Letícia Lima da Silva
- Lucas Presendo Canhete
- Otávio Rosa Zampolli
- Pedro Henrique Martins De Almeida Ozassa


## Visão Geral

Projeto de um chatbot de atendimento que responde perguntas consultando um conjunto de documentos (RAG). O pipeline principal é:

- Ingestão: documentos a partir de `documents.json` e scraping do site via `scraper/`.
- Persistência: documentos armazenados no MongoDB Atlas.
- Vetorização: embeddings gerados com `sentence-transformers` (modelo `BAAI/bge-m3`) e índice FAISS (`index.faiss`).
- Recuperação: busca vetorial no FAISS que monta o contexto relevante (top-k).
- Orquestração LLM: classificador de relevância + geração via endpoint Mistral.
- API: FastAPI expõe `/api/chat` para integração com frontend.

## Stack tecnológico

- Python 3.10+
- FastAPI
- MongoDB Atlas (`pymongo`)
- SentenceTransformers (`BAAI/bge-m3`)
- FAISS (`faiss-cpu` ou `faiss`) + NumPy
- Requests, python-dotenv
- BeautifulSoup4, pymupdf (`fitz`) para scraping / PDF
- Frontend: HTML + JavaScript (fetch)

## Estrutura principal de arquivos

- `app.py` — API FastAPI (endpoints `/health` e `/api/chat`).
- `llm/` — serviços LLM: `chat_service.py`, `mistral_service.py`, `llm_classifier.py`, `prompt_builder.py`.
- `embedding/` — geração e busca de embeddings: `load_embeddings.py`, `find_context.py`.
- `db/` — cliente MongoDB e modelagem (`mongodb_client.py`, `template.py`).
- `scraper/` — crawler, parser, PDF scraper e rotina de seed (`seed_db_documents.py`).
- `frontend/` — UI simples para chat (`index.html`, `config.js`).
- `index.faiss`, `mapping.json` — artefatos gerados pela rotina de embeddings.

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
MONGODB_URI="mongodb+srv://<user>:<pass>@cluster0.mongodb.net/?retryWrites=true&w=majority"
MISTRAL_HOST_URL="https://seu-endpoint-mistral.example/api/generate"
```

Observação: o repositório já contém `.env` de exemplo — revise antes de usar em produção.

### Nota sobre o serviço Mistral

O endpoint Mistral apontado em `MISTRAL_HOST_URL` refere-se a uma instância do modelo que está rodando em outra máquina (remota). Se você for executar este projeto localmente, certifique-se de ter o serviço Mistral disponível e acessível — ou provisionar e rodar uma instância do Mistral na sua própria máquina/servidor e apontar `MISTRAL_HOST_URL` para ela.

Em resumo:

- Se não houver um Mistral público/externo disponível, é necessário instalar/rodar o serviço Mistral localmente ou em um host acessível antes de usar `/api/chat`.
- Atualize a variável `MISTRAL_HOST_URL` no arquivo `.env` para o endereço correto do serviço.


## Requisitos (pré-instalação)

- Python 3.10 ou superior
- Rede ativa para baixar modelos e chamar endpoint Mistral
- Conta/URI do MongoDB Atlas
- Espaço em disco suficiente para o modelo de embeddings (podem ser grandes)

## Instalação local (passo a passo)

1. Crie e ative um ambiente virtual:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

Se preferir instalar manualmente:

```bash
pip install fastapi uvicorn python-dotenv pymongo sentence-transformers faiss-cpu numpy requests beautifulsoup4 pymupdf
```

3. Configure o `.env` na raiz com `MONGODB_URI` e `MISTRAL_HOST_URL`.

4. Popular o banco de dados (opcional, usa `documents.json` e scraping):

```bash
python -c "from scraper.seed_db_documents import seed_db_documents; seed_db_documents()"
```

5. Gerar embeddings e criar índice FAISS (gera `index.faiss` e `mapping.json`):

```bash
python -c "from embedding.load_embeddings import load_embeddings; load_embeddings()"
```

6. Rodar a API localmente:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

7. Servir o frontend (opcional, via servidor HTTP simples):

```bash
python -m http.server 8080 -d frontend
# então abra http://localhost:8080
```
