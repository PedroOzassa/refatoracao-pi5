# ADR-002: Escolha do FastAPI para o Backend

- **Status:** Aceito
- **Data:** 2026-06
- **Contexto do projeto:** Chatbot RAG de atendimento ao cliente — AgiBank / Projeto Integrador 5 (PUC Campinas)

---

## Contexto

O projeto necessita de uma camada de API HTTP para expor o pipeline RAG ao frontend. Essa API precisa:

- Receber perguntas do usuário via requisição HTTP POST.
- Orquestrar a recuperação de contexto (FAISS) e a geração de resposta (LLM).
- Retornar a resposta e o contexto recuperado em formato JSON.
- Ser implementada em Python, linguagem já adotada para todo o pipeline de ML/NLP do projeto.
- Ser simples de iniciar e desenvolver em um contexto acadêmico com prazo limitado.

---

## Decisão

Adotar o **FastAPI** como framework web para o backend, servido via `uvicorn`.

---

## Alternativas Consideradas

### Flask
- Framework Python leve e amplamente conhecido.
- Não possui suporte nativo a tipagem com Pydantic, o que exigiria validação manual dos payloads.
- Não gera documentação OpenAPI (Swagger) automaticamente.
- Suporte a async é mais limitado e requer extensões adicionais.

### Django / Django REST Framework
- Framework robusto com muitos recursos, mas excessivamente pesado para uma API simples de um único endpoint.
- Curva de aprendizado mais íngreme e configuração mais verbosa para o escopo do projeto.
- ORM do Django não seria utilizado (banco é MongoDB, não relacional).

### FastAPI com Starlette puro
- Starlette é a base do FastAPI e poderia ser usado diretamente, mas sem as abstrações de roteamento e validação que o FastAPI oferece sobre ele.

---

## Justificativa

O FastAPI foi escolhido pelos seguintes motivos:

1. **Integração nativa com Pydantic:** Os modelos de request (`ChatRequestModel`) e response (`ChatResponseModel`) são declarados com tipagem Python padrão, e a validação ocorre automaticamente — sem código boilerplate.
2. **Documentação automática:** O FastAPI gera automaticamente a interface Swagger UI em `/docs` e o schema OpenAPI, útil tanto para desenvolvimento quanto para apresentação do projeto.
3. **Performance:** Por ser baseado em ASGI (via Starlette e uvicorn), o FastAPI tem desempenho significativamente superior ao Flask/WSGI para cargas concorrentes.
4. **Simplicidade e produtividade:** A definição de endpoints é concisa. O endpoint principal `/api/chat` foi implementado com poucas linhas, incluindo injeção de dependências e tratamento de erros.
5. **Compatibilidade com o ecossistema:** FastAPI é amplamente adotado em projetos de ML/NLP em Python, sendo familiar para a equipe e bem integrado com as demais bibliotecas do projeto.
6. **Middleware de CORS:** O suporte nativo a `CORSMiddleware` simplificou a configuração de CORS necessária para que o frontend (servido separadamente) consumisse a API.

---

## Consequências

**Positivas:**
- Desenvolvimento rápido: o backend funcional foi criado com poucos arquivos e linhas de código.
- Validação de entrada automática com respostas de erro padronizadas (HTTP 400/500).
- Documentação interativa gerada automaticamente, útil para demonstrações do projeto.
- Fácil de iniciar localmente: `uvicorn api.handlers:app --reload`.

**Negativas / Riscos:**
- Para um projeto de escala maior, seria necessário adicionar autenticação, rate limiting e outras camadas de segurança que não foram implementadas neste protótipo.
- O uso de `allow_origins=["*"]` no CORS é adequado para desenvolvimento, mas não para produção.
