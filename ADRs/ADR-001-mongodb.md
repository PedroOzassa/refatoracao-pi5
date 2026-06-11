# ADR-001: Escolha do MongoDB como Banco de Dados do Projeto

- **Status:** Aceito
- **Data:** 2026-06
- **Contexto do projeto:** Chatbot RAG de atendimento ao cliente — AgiBank / Projeto Integrador 5 (PUC Campinas)

---

## Contexto

O projeto necessita de um mecanismo de persistência para armazenar os documentos de conhecimento utilizados pelo pipeline RAG (Retrieval-Augmented Generation). Esses documentos são extraídos via scraping do site do AgiBank e de PDFs de FAQ, e precisam ser persistidos de forma confiável para posterior geração de embeddings e indexação no FAISS.

Os requisitos considerados foram:

- Armazenar documentos com estrutura semi-estruturada (título, conteúdo, fonte, metadados variáveis).
- Suportar operações de busca por campo (ex.: busca por título, busca por source).
- Ser acessível remotamente por toda a equipe sem necessidade de infraestrutura local.
- Ter hospedagem gerenciada gratuita ou de baixo custo para um projeto acadêmico.
- Ser compatível com o ecossistema Python e de fácil integração.

---

## Decisão

Adotar o **MongoDB Atlas** (versão cloud gerenciada) como banco de dados principal para persistência dos documentos RAG, acessado via biblioteca `pymongo`.

---

## Alternativas Consideradas

### PostgreSQL / SQLite (bancos relacionais)
- Exigiriam a definição de um schema rígido para os documentos.
- Documentos possuem conteúdo de tamanho variável e metadados heterogêneos, o que tornaria o modelo relacional mais verboso e menos flexível.
- SQLite não oferece acesso remoto nativo, inviabilizando o uso compartilhado entre os integrantes.
- PostgreSQL exigiria provisionar e manter uma instância de servidor, adicionando complexidade operacional.

### Banco de dados exclusivamente em memória / arquivos JSON
- Não oferece persistência adequada entre reinicializações do serviço.
- Não escala para operações concorrentes.
- Considerado apenas como solução temporária de seed de dados (arquivo `faq_documents.json`), não como banco definitivo.

### Elasticsearch
- Possui capacidades de busca full-text avançadas, mas adiciona complexidade de setup significativa.
- A busca semântica já é tratada pelo FAISS; o banco de dados apenas precisa de persistência e busca simples.
- Infraestrutura mais pesada para um protótipo acadêmico.

---

## Justificativa

O MongoDB Atlas foi escolhido pelos seguintes motivos:

1. **Modelo de dados flexível:** O schema de documento (JSON/BSON) mapeia naturalmente para a entidade `Document` do projeto (campos `title`, `content`, `source`, `category`), sem necessidade de migrações ou reestruturações.
2. **Hospedagem gerenciada gratuita:** O tier gratuito do MongoDB Atlas (M0) é suficiente para o volume de dados do protótipo e elimina a necessidade de gerenciar infraestrutura de banco de dados.
3. **Acesso remoto centralizado:** Toda a equipe acessa o mesmo cluster, garantindo consistência dos dados durante o desenvolvimento distribuído.
4. **Integração simples com Python:** A biblioteca `pymongo` tem API madura, bem documentada e de fácil uso para as operações necessárias (insert, find, busca por regex).
5. **Separação de responsabilidades:** O MongoDB atua exclusivamente como camada de persistência de documentos. A busca semântica, que é o núcleo do RAG, é delegada ao FAISS — cada tecnologia cumpre seu papel específico.

---

## Consequências

**Positivas:**
- Setup inicial rápido e sem custo de infraestrutura.
- Flexibilidade para alterar a estrutura dos documentos sem migrações complexas.
- Operações CRUD implementadas de forma limpa no `MongoDBDocumentRepository`, seguindo a interface `DocumentRepository` do domínio.

**Negativas / Riscos:**
- Dependência de conexão com a internet para acessar o Atlas (não funciona em ambientes completamente offline).
- O tier gratuito do Atlas possui limitações de storage e IOPS — aceitável para protótipo, mas requereria upgrade em produção.
- Não fornece busca vetorial nativa; o índice FAISS é necessário em paralelo para a recuperação semântica.
