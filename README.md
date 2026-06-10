# Chatbot-AGI

> Chatbot de atendimento baseado em **RAG (Retrieval-Augmented Generation)** para o AgiBank, construído com arquitetura limpa (Clean Architecture + DDD), FAISS, SentenceTransformers e geração via Mistral com fallback para GPT.

---

## Sumário

- [Sobre o projeto](#sobre-o-projeto)
- [Arquitetura](#arquitetura)
- [Estrutura de diretórios](#estrutura-de-diretórios)
- [Pipeline RAG](#pipeline-rag)
- [Stack tecnológico](#stack-tecnológico)
- [Variáveis de ambiente](#variáveis-de-ambiente)
- [Pré-requisitos](#pré-requisitos)
- [Instalação e execução](#instalação-e-execução)
- [Inicialização dos dados](#inicialização-dos-dados)
- [API Reference](#api-reference)
- [Frontend](#frontend)
- [Módulos em detalhe](#módulos-em-detalhe)
- [Decisões de design](#decisões-de-design)
- [Integrantes](#integrantes)

---

## Sobre o projeto

Este projeto é um protótipo acadêmico desenvolvido por alunos da **PUC Campinas** como parte do **Projeto Integrador 5 (PI5)**, em parceria com a empresa **AgiBank**. O objetivo é demonstrar técnicas de NLP, recuperação vetorial e integração com LLMs em um chatbot de atendimento ao cliente.

A versão atual representa uma **refatoração completa** da base de código original, migrando de uma arquitetura monolítica para **Clean Architecture com Dependency Injection**, mantendo o mesmo comportamento funcional e melhorando a manutenibilidade, testabilidade e extensibilidade.

O chatbot responde perguntas dos clientes consultando uma base de conhecimento formada por **118 documentos de FAQ** extraídos do arquivo `faq.pdf` do AgiBank. Os tópicos cobertos incluem: Conta Corrente, Empréstimos, Cartão de Débito e Crédito, Seguros (Vida, Residencial, Auto, Proteção Urbana), Investimentos, Benefício INSS e informações gerais sobre o Agi.

---

## Arquitetura

O projeto segue **Clean Architecture** dividida em quatro camadas concêntricas com dependências sempre apontando para o interior:

```
┌──────────────────────────────────────────────┐
│              API (FastAPI)                   │  ← Camada externa: HTTP handlers
│  ┌────────────────────────────────────────┐  │
│  │         Application                   │  │  ← Casos de uso e serviços
│  │  ┌──────────────────────────────────┐ │  │
│  │  │           Domain                │ │  │  ← Entidades e interfaces (contratos)
│  │  └──────────────────────────────────┘ │  │
│  └────────────────────────────────────────┘  │
│              Infrastructure                  │  ← Adaptadores (MongoDB, FAISS, LLMs)
└──────────────────────────────────────────────┘
                       ↑
                DI Container (di/)             ← Composição das dependências
```

### Camadas

| Camada | Pacote | Responsabilidade |
|---|---|---|
| **API** | `api/` | Endpoints FastAPI, validação HTTP, serialização |
| **Application** | `application/` | Casos de uso, DTOs, orquestração do fluxo de negócio |
| **Domain** | `domain/` | Entidades de domínio, interfaces (contratos abstratos) |
| **Infrastructure** | `infrastructure/` | Implementações concretas: MongoDB, FAISS, Mistral, GPT |
| **DI** | `di/` | Container de injeção de dependência, composição de objetos |
| **Scraper** | `scraper/` | Extração de documentos (PDF e web) e seed do banco |
| **Scripts** | `scripts/` | Orquestração da inicialização completa dos dados |

---

## Estrutura de diretórios

```
refatoracao-pi5-main/
│
├── api/
│   ├── __init__.py               # Marca o módulo como pacote Python
│   └── handlers.py               # Endpoints FastAPI (/health, /api/chat)
│
├── application/
│   ├── __init__.py
│   ├── chat_service.py           # Orquestra: recuperação de contexto → classificação → LLM
│   ├── chat_usecase.py           # Caso de uso: valida entrada, delega ao ChatService, monta DTO
│   └── dto.py                    # ChatRequestDTO e ChatResponseDTO (dataclasses)
│
├── di/
│   ├── __init__.py
│   └── container.py              # DIContainer: fábrica lazy de todas as dependências
│
├── domain/
│   ├── __init__.py
│   ├── entities/
│   │   ├── __init__.py
│   │   └── document.py           # Entidade Document (título, conteúdo, fonte, tag, data)
│   └── repositories/
│       ├── __init__.py
│       ├── context_repository.py     # Interface: ContextRepository.find_context()
│       ├── document_repository.py    # Interface: DocumentRepository (CRUD)
│       ├── embedding_provider.py     # Interface: EmbeddingProvider.embed()
│       └── llm_provider.py           # Interface: LLMProvider.generate()
│
├── infrastructure/
│   ├── __init__.py
│   ├── config.py                 # Settings (dataclass + lru_cache), carregado do .env
│   ├── database/
│   │   ├── __init__.py
│   │   └── mongodb_adapter.py    # MongoDBDocumentRepository (implementa DocumentRepository)
│   ├── embedding/
│   │   ├── __init__.py
│   │   ├── faiss_embedding.py    # FAISSEmbedding (implementa EmbeddingProvider via SentenceTransformer)
│   │   └── faiss_repository.py   # FAISSRepository (implementa ContextRepository via FAISS index)
│   └── llm/
│       ├── __init__.py
│       ├── gpt_adapter.py        # GPTAdapter (implementa LLMProvider via OpenAI API)
│       ├── llm_chain.py          # LLMChain (fallback entre providers: Mistral → GPT)
│       └── mistral_adapter.py    # MistralAdapter (implementa LLMProvider via Ollama/endpoint HTTP)
│
├── scraper/
│   ├── __init__.py
│   ├── crawler.py                # Rastreia todas as URLs do domínio agibank.com.br (BFS)
│   ├── parser.py                 # Extrai seções (título + conteúdo) de páginas web via BeautifulSoup
│   ├── pdf_scraper.py            # Extrai pares pergunta-resposta do faq.pdf via PyMuPDF (fitz)
│   ├── seed_db_documents.py      # Entry point para seed: usa SeedService + DIContainer
│   └── seed_service.py           # Orquestra a ingestão: JSON → MongoDB ou PDF → JSON → MongoDB
│
├── scripts/
│   ├── __init__.py
│   └── initialize_data.py        # Script CLI de inicialização completa (PDF → JSON → MongoDB → FAISS)
│
├── frontend/
│   ├── index.html                # Interface web do chatbot (HTML + CSS + JS puros)
│   ├── config.js                 # Configuração do frontend (URL da API, timeouts, UI settings)
│   ├── image.png                 # Imagem de fundo da interface
│   └── README.md                 # Documentação específica do frontend
│
├── main.py                       # Wrapper do scripts/initialize_data.py (entry point padrão)
├── faq.pdf                       # Base de conhecimento: FAQ oficial do AgiBank
├── faq_documents.json            # Documentos extraídos do faq.pdf (118 registros, gerado pelo scraper)
├── index.faiss                   # Índice vetorial FAISS (gerado pela rotina de embeddings)
├── mapping.json                  # Mapeamento índice FAISS → metadados do documento
├── requirements.txt              # Dependências Python com versões fixas
└── .gitignore                    # Padrão Python + .env
```

---

## Pipeline RAG

O fluxo completo, da ingestão à resposta, é:

```
                        ┌────────────────────────────────┐
                        │        INGESTÃO (offline)      │
                        └────────────────────────────────┘
                                       │
           ┌───────────────────────────┼───────────────────────────┐
           ▼                           ▼                           ▼
     faq.pdf (PDF)         faq_documents.json (JSON)       agibank.com.br (web)
           │                           │                           │
    pdf_scraper.py              seed_service.py              crawler.py + parser.py
    (PyMuPDF + regex)          (carrega JSON)                (BFS + BeautifulSoup)
           │                           │                           │
           └───────────────────────────┴───────────────────────────┘
                                       │
                                       ▼
                              MongoDB Atlas
                          (collection: rag_documents)
                                       │
                                       ▼
                            SentenceTransformer
                             (BAAI/bge-m3 model)
                              gera embeddings
                                       │
                                       ▼
                            FAISS IndexFlatIP
                          (index.faiss + mapping.json)

                        ┌────────────────────────────────┐
                        │        INFERÊNCIA (online)     │
                        └────────────────────────────────┘
                                       │
                               Pergunta do usuário
                                       │
                                       ▼
                            embed query (BAAI/bge-m3)
                            + prefixo BGE de recuperação
                                       │
                                       ▼
                          FAISS.search(top_k=3, threshold=0.45)
                                       │
                               ┌───────┴────────┐
                          sem contexto       com contexto
                               │                   │
                         resposta padrão    montar prompt
                         (sem informação)   com contexto
                                                   │
                                                   ▼
                                         LLMChain.generate()
                                          Mistral → GPT fallback
                                                   │
                                                   ▼
                                     resposta em português
```

### Detalhes do pipeline de recuperação

**Embedding**: O modelo `BAAI/bge-m3` da HuggingFace é utilizado via `sentence-transformers`. Na busca, o texto da query recebe o prefixo especial `"Represent this sentence for searching relevant passages: "` antes de ser embutido, conforme recomendado pelo modelo BGE para tarefas de recuperação.

**Indexação FAISS**: O índice `IndexFlatIP` realiza busca por produto interno (Inner Product). Os vetores são normalizados com `faiss.normalize_L2` antes da busca, tornando o produto interno equivalente à similaridade de cosseno.

**Threshold**: Apenas resultados com score ≥ 0.45 são incluídos no contexto. Resultados com `idx == -1` (FAISS sem resultado suficiente) são descartados.

**Contexto**: Os documentos recuperados são concatenados no formato `título\nconteúdo`, separados por `\n\n`, e inseridos no prompt do LLM.

**Fallback de LLM**: O `LLMChain` tenta o Mistral primeiro; se qualquer exceção ocorrer (timeout, erro de conexão, HTTP error), passa automaticamente para o GPT-4o-mini. Se todos os providers falharem, levanta `RuntimeError` com o resumo de todos os erros.

---

## Stack tecnológico

| Componente | Tecnologia | Versão |
|---|---|---|
| **Web Framework** | FastAPI | 0.136.1 |
| **ASGI Server** | Uvicorn | 0.46.0 |
| **Banco de dados** | MongoDB Atlas (pymongo) | 4.17.0 |
| **Embeddings** | sentence-transformers (BAAI/bge-m3) | 5.4.1 |
| **Deep Learning** | PyTorch | 2.11.0 |
| **Índice vetorial** | faiss-cpu | 1.13.2 |
| **Álgebra linear** | NumPy | 2.4.4 |
| **LLM primário** | Mistral 7B (via HTTP/Ollama) | — |
| **LLM fallback** | OpenAI GPT-4o-mini | — |
| **HTTP Client** | Requests | 2.33.1 |
| **Web Scraping** | BeautifulSoup4 | 4.14.3 |
| **PDF Parsing** | PyMuPDF (fitz) | 1.27.2.3 |
| **Configuração** | python-dotenv | 1.2.2 |
| **Validação** | Pydantic | 2.13.4 |
| **Frontend** | HTML + CSS + JavaScript (vanilla) | — |

---

## Variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto. O arquivo `.env` está listado no `.gitignore` e nunca deve ser versionado.

```dotenv
# ── Banco de dados ────────────────────────────────────────────────
MONGODB_URI=mongodb+srv://<user>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority
MONGODB_DATABASE=chatbot-data          # opcional, padrão: chatbot-data
MONGODB_COLLECTION=rag_documents       # opcional, padrão: rag_documents

# ── LLM: Mistral (provider primário) ────────────────────────────
MISTRAL_HOST_URL=http://<host>:<porta>/api/generate
MISTRAL_MODEL=mistral:7b               # opcional, padrão: mistral:7b
MISTRAL_TIMEOUT=10                     # opcional, padrão: 10 segundos

# ── LLM: OpenAI/GPT (fallback) ──────────────────────────────────
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini               # opcional, padrão: gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1  # opcional
OPENAI_TIMEOUT=60                      # opcional, padrão: 60 segundos

# ── Embeddings / FAISS ──────────────────────────────────────────
EMBEDDING_MODEL=BAAI/bge-m3            # opcional, padrão: BAAI/bge-m3
INDEX_FILE=index.faiss                 # opcional, padrão: index.faiss
MAPPING_FILE=mapping.json             # opcional, padrão: mapping.json
FAISS_TOP_K=3                          # opcional, padrão: 3
FAISS_THRESHOLD=0.45                   # opcional, padrão: 0.45

# ── API ─────────────────────────────────────────────────────────
API_HOST=0.0.0.0                       # opcional, padrão: 0.0.0.0
API_PORT=8000                          # opcional, padrão: 8000
API_RELOAD=true                        # opcional, padrão: true
```

### Observações sobre as variáveis obrigatórias

**`MONGODB_URI`** é a única variável verdadeiramente obrigatória — a aplicação levanta `ValueError` ao iniciar se estiver ausente ou vazia.

**`MISTRAL_HOST_URL`** é necessário para usar o Mistral como provider primário. O endpoint aponta para uma instância do modelo rodando remotamente (ou localmente via Ollama). Se não configurado, o sistema pula o Mistral e usa apenas o GPT como provider.

**`OPENAI_API_KEY`** é necessário para usar o GPT como fallback (ou como único provider, caso o Mistral não esteja configurado).

**Pelo menos um dos dois LLM providers deve estar configurado.** Se nenhum estiver disponível, o `DIContainer` levanta `RuntimeError` ao tentar obter o `LLMChain`.

### Nota sobre o serviço Mistral

O `MISTRAL_HOST_URL` aponta para uma instância Ollama ou servidor compatível rodando o modelo Mistral 7B. O endpoint esperado é `/api/generate` (formato Ollama). Para rodar localmente:

```bash
# Instalar Ollama (https://ollama.ai)
ollama pull mistral:7b
ollama serve
# Endpoint ficará disponível em http://localhost:11434/api/generate
```

---

## Pré-requisitos

- Python **3.10** ou superior
- Rede ativa para baixar o modelo de embeddings `BAAI/bge-m3` no primeiro uso (~2 GB)
- Conta no **MongoDB Atlas** com a URI de conexão disponível
- Pelo menos um LLM provider configurado (Mistral e/ou OpenAI)
- Espaço em disco suficiente para o modelo de embeddings e os artefatos FAISS

---

## Instalação e execução

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd refatoracao-pi5-main
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

> O `requirements.txt` contém todas as dependências com versões fixas. O arquivo está em UTF-16-LE. Se houver problema ao instalar, use:
> ```bash
> pip install fastapi uvicorn pymongo sentence-transformers faiss-cpu numpy \
>             requests python-dotenv beautifulsoup4 pymupdf pydantic torch
> ```

### 4. Configurar o `.env`

```bash
cp .env.example .env   # se existir, ou criar manualmente
# editar com os valores corretos
```

### 5. Inicializar os dados (banco + embeddings)

Veja a seção [Inicialização dos dados](#inicialização-dos-dados) abaixo.

### 6. Rodar a API

```bash
uvicorn api.handlers:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em `http://localhost:8000`.

Documentação interativa (Swagger UI): `http://localhost:8000/docs`

### 7. Servir o frontend (opcional)

```bash
# Com Python
python -m http.server 3000 -d frontend
# Então acesse: http://localhost:3000

# Com Node.js
cd frontend && npx http-server -p 3000
```

---

## Inicialização dos dados

A inicialização é necessária **uma única vez** para popular o MongoDB e construir o índice FAISS. Há três formas equivalentes de fazer isso.

### Opção A — Script CLI completo (recomendado)

```bash
python scripts/initialize_data.py
```

Com argumentos opcionais:

```bash
python scripts/initialize_data.py \
  --pdf faq.pdf \
  --json faq_documents.json \
  --force-rebuild     # força reextração do PDF mesmo se JSON já existir
```

Este script executa sequencialmente:

1. Inicializa o `DIContainer`
2. Obtém o `DocumentRepository` (MongoDB)
3. Cria o `SeedService`
4. Se `faq_documents.json` existir e `--force-rebuild` não for passado: carrega do JSON. Caso contrário: extrai do `faq.pdf` e salva o JSON.
5. Insere os documentos no MongoDB
6. Verifica o `EmbeddingProvider` (lazy-load confirmado)

### Opção B — Via `main.py`

```bash
python main.py
```

Equivalente ao script acima com os parâmetros padrão (`faq.pdf`, `faq_documents.json`, `force_rebuild=False`).

### Opção C — Passo a passo via Python

```python
# Seed apenas o banco de dados
from scraper.seed_db_documents import seed_db_documents
seed_db_documents()

# Extrair documentos do PDF manualmente
from scraper.pdf_scraper import build_documents, save_documents_to_json
docs = build_documents("faq.pdf")
save_documents_to_json(docs, "faq_documents.json")
```

### Sobre o `faq_documents.json` incluído no repositório

O arquivo `faq_documents.json` já vem pré-gerado no repositório com **118 documentos** extraídos do `faq.pdf`. Os documentos cobrem 11 categorias temáticas:

| Categoria | Exemplos de perguntas cobertas |
|---|---|
| Sobre o Agi | O que é o Agi? Quais produtos oferece? |
| Conta Corrente | Como abrir conta? Qual o limite de transferência? |
| Empréstimos | Quais os tipos de empréstimo? Como simular? |
| Cartão de Débito e Crédito | Como solicitar? Qual o limite? |
| Seguros | Quais seguros estão disponíveis? |
| Seguro de Vida | Coberturas, valores, contratação |
| Seguro Residencial | O que cobre? Como acionar? |
| Seguro Auto | Quais veículos? Assistência 24h? |
| Proteção Urbana | O que é? Como funciona? |
| Investimentos | CDB, rendimentos, resgate |
| Benefício INSS | Antecipação, crédito consignado |

### Sobre os artefatos FAISS (`index.faiss` e `mapping.json`)

Os artefatos `index.faiss` e `mapping.json` também estão incluídos no repositório (pré-gerados). Eles são carregados automaticamente com **lazy loading** na primeira requisição ao endpoint `/api/chat`.

Se quiser regenerar os artefatos (por exemplo, após adicionar novos documentos ao banco), é necessário implementar ou chamar manualmente a rotina de geração de embeddings que lê os documentos do MongoDB, gera embeddings e grava o novo índice FAISS.

---

## API Reference

A API é servida pelo FastAPI em `http://localhost:8000`. A documentação interativa completa está disponível em `/docs` (Swagger UI) e `/redoc`.

### `GET /health`

Verifica se o serviço está rodando.

**Request:** sem parâmetros

**Response `200 OK`:**
```json
{
  "status": "ok"
}
```

---

### `POST /api/chat`

Recebe uma pergunta do usuário e retorna uma resposta gerada via RAG.

**Headers:**
```
Content-Type: application/json
```

**Request body:**
```json
{
  "question": "Quais são os horários de atendimento?"
}
```

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `question` | `string` | Sim | A pergunta do usuário. Não pode ser vazia ou apenas espaços. |

**Response `200 OK`:**
```json
{
  "answer": "Estamos disponíveis de segunda a sexta, das 8h às 20h.",
  "context": "Horários de atendimento\nSeg-sex: 8h às 20h. Sáb: 9h às 13h..."
}
```

| Campo | Tipo | Descrição |
|---|---|---|
| `answer` | `string` | Resposta gerada pelo LLM (Mistral ou GPT). Se nenhum contexto relevante for encontrado, retorna a mensagem padrão de fallback com os canais de suporte do AgiBank. |
| `context` | `string` | Trechos dos documentos recuperados pelo FAISS que foram usados para gerar a resposta. Pode ser vazio se nenhum documento atingiu o threshold de similaridade. |

**Response `400 Bad Request`** — pergunta vazia:
```json
{
  "detail": "Question is required and cannot be empty"
}
```

**Response `500 Internal Server Error`** — falha interna:
```json
{
  "detail": "Internal server error: <mensagem de erro>"
}
```

**Mensagem de fallback** (quando nenhum contexto relevante é encontrado):
```
Desculpe, não encontrei informações suficientes para responder à sua pergunta.
Por favor, reformule sua solicitação ou entre em contato pelo site:
https://agibank.com.br/fale-conosco
ou ligue para 3004 2221 (Capitais e regiões metropolitanas)
ou 0800 602 0022 (Demais localidades).
```

### Fluxo interno do endpoint `/api/chat`

```
POST /api/chat
      │
      ▼
Validar payload (Pydantic)
      │
      ▼
get_di_container() → DIContainer (singleton lazy)
      │
      ▼
container.get_llm_chain()        → LLMChain(MistralAdapter, GPTAdapter)
container.get_context_repository() → FAISSRepository
      │
      ▼
ChatService(llm_chain, context_repository)
      │
      ▼
ChatUseCase(chat_service).execute(ChatRequestDTO)
      │
      ├── context_repository.find_context(query, top_k=3, threshold=0.45)
      │         └── embed(query) → FAISS.search → filtrar por threshold → concatenar
      │
      ├── se contexto vazio → retorna NO_CONTEXT_MESSAGE
      │
      └── se contexto existe → llm_chain.generate(prompt) → resposta
                                    └── tenta Mistral → fallback GPT
```

---

## Frontend

O frontend é uma **single-page application** em HTML/CSS/JavaScript puro, sem frameworks ou dependências externas. Ele se comunica com o backend via `fetch` (API REST).

### Recursos

- **Chat flutuante**: widget de chat posicionado no canto inferior direito, abre/fecha com botão circular
- **Indicador de conexão**: bolinha verde/vermelha mostrando se a API está acessível (health check a cada 10 segundos)
- **Exibição de contexto**: cada resposta do bot exibe um colapsável com os trechos de documentos recuperados pelo FAISS
- **Indicador de digitação**: animação enquanto aguarda resposta do backend
- **Suporte a Enter**: pressionar Enter envia a mensagem
- **Responsivo**: adapta para desktop e mobile (largura máxima de 380px)
- **Limite de mensagens**: mantém no máximo 100 mensagens no histórico visual

### Configuração (`frontend/config.js`)

```javascript
const CONFIG = {
  API_BASE_URL: 'http://localhost:8000',   // URL do backend
  HEALTH_CHECK_INTERVAL: 10000,           // intervalo do health check (ms)
  REQUEST_TIMEOUT: 30000,                 // timeout das requisições (ms)
  UI: {
    maxMessages: 100,
    autoScroll: true,
    typingIndicatorDuration: 500,
  }
};
```

Para apontar para um backend em outro host/porta, edite `API_BASE_URL` no `config.js`.

---

## Módulos em detalhe

### `domain/entities/document.py` — Entidade Document

Representa um documento no sistema. É uma `dataclass` com os campos:

| Campo | Tipo | Descrição |
|---|---|---|
| `title` | `str` | Título ou pergunta do documento |
| `content` | `str` | Conteúdo ou resposta |
| `source` | `str` | Origem: caminho do PDF (`faq.pdf`) ou URL |
| `date` | `datetime` | Data de criação/extração (default: `datetime.now()`) |
| `tag` | `Optional[str]` | Categoria temática (ex: `"conta corrente"`) |
| `_id` | `Optional[str]` | ID do MongoDB (None se ainda não persistido) |

Métodos: `to_dict()` (para persistência) e `from_dict()` (para desserialização).

---

### `domain/repositories/` — Interfaces (contratos)

Todas as interfaces são classes abstratas Python (`ABC`). A camada de domínio nunca importa nada de fora de si mesma.

| Interface | Método principal | Implementação concreta |
|---|---|---|
| `LLMProvider` | `generate(prompt: str) → str` | `MistralAdapter`, `GPTAdapter`, `LLMChain` |
| `EmbeddingProvider` | `embed(text: str) → list[float]` | `FAISSEmbedding` |
| `ContextRepository` | `find_context(query, top_k, threshold) → str` | `FAISSRepository` |
| `DocumentRepository` | `insert_one`, `insert_many`, `find_by_source`, `find_all`, `search_title` | `MongoDBDocumentRepository` |

---

### `infrastructure/config.py` — Configuração centralizada

A classe `Settings` é um dataclass carregado do `.env` via `python-dotenv`. A função `get_settings()` usa `@lru_cache(maxsize=1)` garantindo que as variáveis de ambiente sejam lidas apenas uma vez durante o ciclo de vida da aplicação.

---

### `infrastructure/llm/llm_chain.py` — Chain de LLMs

Implementa o padrão **Chain of Responsibility** para LLMs. Tenta cada provider na ordem fornecida e retorna a primeira resposta bem-sucedida. Todos os erros são coletados e, se nenhum provider funcionar, um `RuntimeError` com o resumo é levantado.

```python
chain = LLMChain([MistralAdapter(...), GPTAdapter(...)])
response = chain.generate(prompt)
# Tenta Mistral → se falhar, tenta GPT → se ambos falharem, RuntimeError
```

---

### `infrastructure/embedding/faiss_repository.py` — Busca vetorial

Implementa `ContextRepository` com FAISS. Principais características:

- **Lazy loading**: o índice FAISS e o mapping JSON são carregados apenas na primeira chamada a `find_context()`
- **Prefixo BGE**: adiciona `"Represent this sentence for searching relevant passages: "` à query antes de embutir, otimizando a recuperação com o modelo `BAAI/bge-m3`
- **Normalização L2**: vetores normalizados antes da busca, tornando `IndexFlatIP` equivalente à similaridade de cosseno
- **Filtro por threshold**: apenas resultados com score ≥ `FAISS_THRESHOLD` (padrão: 0.45) são incluídos

---

### `di/container.py` — Container de Injeção de Dependência

O `DIContainer` é responsável por criar, configurar e cachear todas as dependências da aplicação. Segue o padrão **Service Locator** com inicialização lazy e singleton por instância.

```python
container = DIContainer()

# Cada chamada abaixo retorna o mesmo objeto (singleton por container)
llm = container.get_llm_chain()
embedding = container.get_embedding_provider()
context_repo = container.get_context_repository()
doc_repo = container.get_document_repository()

# Suporta uso como context manager
with DIContainer() as container:
    repo = container.get_document_repository()
# container.close() é chamado automaticamente

# Singleton global (usado pela API)
container = get_container()
reset_container()  # útil em testes
```

---

### `scraper/pdf_scraper.py` — Extração do FAQ em PDF

Extrai pares pergunta-resposta do `faq.pdf` usando PyMuPDF (`fitz`). O fluxo é:

1. Extrai texto bruto de todas as páginas do PDF
2. Normaliza espaçamento e quebras de linha
3. Divide o texto em tópicos usando os cabeçalhos predefinidos em `TOPIC_HEADERS` (ex: "Conta Corrente", "Empréstimos")
4. Dentro de cada tópico, identifica perguntas (linhas terminadas em `?`) e as respostas subsequentes
5. Cada par Q&A vira um `Document` com `title=pergunta`, `content=resposta`, `tag=tópico`

---

### `scraper/crawler.py` — Web Crawler

Realiza um rastreamento BFS (busca em largura) a partir de uma URL inicial, restrito ao mesmo domínio. Retorna o conjunto de URLs acessadas com sucesso. Útil para criar uma base de documentos a partir do site do AgiBank além do FAQ em PDF.

---

## Decisões de design

### Por que Clean Architecture?

A refatoração migrou de um monólito para Clean Architecture para:

- **Testabilidade**: as interfaces de domínio permitem substituir implementações reais por mocks em testes unitários
- **Extensibilidade**: adicionar um novo provider de LLM (ex: Claude, Gemini) requer apenas uma nova classe que implementa `LLMProvider`, sem tocar na camada de aplicação
- **Separação de responsabilidades**: cada camada tem um propósito único e bem definido
- **Inversão de dependência**: a lógica de negócio não depende de detalhes de infraestrutura

### Por que FAISS com `IndexFlatIP` e normalização L2?

O `IndexFlatIP` realiza busca por produto interno exato (força bruta). Combinado com normalização L2, o produto interno se torna equivalente à similaridade de cosseno, que é mais apropriada para embeddings de texto do que a distância euclidiana. Para o volume de documentos atual (~118), a busca exata é eficiente o suficiente sem necessidade de índices aproximados.

### Por que o prefixo BGE na query?

O modelo `BAAI/bge-m3` foi treinado com instruções diferentes para documentos (durante a indexação) e queries (durante a busca). O prefixo `"Represent this sentence for searching relevant passages: "` é a instrução recomendada pelo modelo para queries de recuperação, melhorando significativamente a qualidade dos resultados.

### Por que lazy loading no FAISS e no MongoDB?

Tanto o `FAISSRepository` quanto o `MongoDBDocumentRepository` usam conexões/carregamentos lazy para evitar penalizar o tempo de startup da API. O modelo de embeddings (~2GB) e o índice FAISS são carregados apenas quando a primeira requisição chega.

### Por que o classificador de relevância foi desativado?

O `ChatService` contém um método `_classify_relevance()` que usava um LLM para verificar se o contexto recuperado era suficiente para responder a pergunta. Esse passo foi removido do fluxo principal porque um classificador frágil poderia bloquear respostas válidas. Atualmente, se houver qualquer contexto acima do threshold do FAISS, o LLM é chamado diretamente. A mensagem de fallback é retornada apenas quando o FAISS não encontra nenhum contexto.

---

## Integrantes

Projeto desenvolvido por alunos da **PUC Campinas** — Projeto Integrador 5 (PI5), em parceria com o **AgiBank**:

- Ana Julia Matozo Rodrigues
- Briann Oliveira Gomes
- Hugo Daniel Bosada Rodrigues
- Letícia Lima da Silva
- Lucas Presendo Canhete
- Otávio Rosa Zampolli
- Pedro Henrique Martins De Almeida Ozassa