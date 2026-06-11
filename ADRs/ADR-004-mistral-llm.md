# ADR-004: Escolha do Mistral 7B como Modelo LLM (com Histórico de Mudanças)

- **Status:** Aceito (com revisões)
- **Data inicial:** início do projeto
- **Última revisão:** fase final do desenvolvimento
- **Contexto do projeto:** Chatbot RAG de atendimento ao cliente — AgiBank / Projeto Integrador 5 (PUC Campinas)

---

## Contexto

O projeto necessita de um LLM (Large Language Model) para duas funções:

1. **Classificação de relevância:** determinar se o contexto recuperado pelo FAISS é suficiente para responder à pergunta do usuário.
2. **Geração de resposta:** produzir uma resposta em português, clara e objetiva, com base no contexto e na pergunta.

Os requisitos iniciais foram:
- Modelo open-source, sem custo de API por requisição.
- Capaz de seguir instruções em português.
- Executável sem dependências de serviços externos pagos.
- Qualidade de geração adequada para atendimento bancário.

---

## Decisão e Evolução

A escolha e o modo de execução do LLM passaram por **três fases distintas** ao longo do desenvolvimento do projeto.

---

### Fase 1 — Execução local via Ollama (configuração inicial)

**Decisão:** Executar o **Mistral 7B** localmente nas máquinas dos integrantes via **Ollama**, acessado pela API REST em `http://localhost:11434/api/generate`.

**Justificativa:**
- Mistral 7B é um modelo open-source de alta qualidade para seu tamanho, superando modelos maiores em benchmarks de raciocínio e instrução.
- Ollama oferece uma interface simples para servir modelos localmente, com suporte a GPU e CPU.
- Não há custo de API; o modelo roda inteiramente na máquina do desenvolvedor.
- O endpoint do Ollama é compatível com a interface esperada pelo `MistralAdapter` (`POST /api/generate` com campo `response` no retorno).

**Problema encontrado:**
- A execução local do Mistral 7B exige hardware significativo (idealmente GPU com VRAM suficiente). Nem todos os integrantes da equipe possuíam máquinas com capacidade adequada.
- Isso criava inconsistências no ambiente de desenvolvimento: o chatbot funcionava bem na máquina de alguns integrantes e ficava lento ou inacessível nas demais.
- Compartilhar o ambiente de desenvolvimento tornou-se inviável com o modelo rodando localmente em cada máquina individualmente.

---

### Fase 2 — Modelo hospedado na máquina de um integrante (servidor compartilhado)

**Decisão:** Centralizar a execução do Mistral 7B na máquina de **um dos integrantes da equipe** com hardware mais adequado, expondo o endpoint via rede local ou endereço acessível.

**Como funciona:** A variável de ambiente `MISTRAL_HOST_URL` no arquivo `.env` passou a apontar para o endereço remoto da máquina do integrante (ex.: `http://<ip-do-integrante>:11434/api/generate`). O `MistralAdapter` faz requisições HTTP para esse endpoint, sem saber que o modelo está em outra máquina — a interface é idêntica.

**Justificativa:**
- Eliminou a necessidade de cada integrante ter o modelo rodando localmente.
- A equipe inteira passou a usar o mesmo endpoint, garantindo consistência nas respostas durante o desenvolvimento e nos testes.
- Nenhuma mudança de código foi necessária — apenas a atualização do `.env`.

**Problema encontrado:**
- A disponibilidade do serviço ficou atrelada à máquina e à conexão de internet de um único integrante.
- Em horários de uso intenso, testes de madrugada ou instabilidades de rede, o endpoint ficava inacessível.
- Isso expôs a necessidade de uma estratégia de fallback para garantir que o chatbot continuasse funcionando mesmo quando o Mistral estivesse indisponível.

---

### Fase 3 — Fallback para o ChatGPT (GPT-4o-mini via OpenAI API)

**Decisão:** Implementar um **padrão de chain com fallback automático** (`LLMChain`): o sistema tenta o Mistral primeiro e, em caso de falha, cai automaticamente para o **ChatGPT (GPT-4o-mini)** via API da OpenAI.

**Como funciona:**

```
LLMChain([MistralAdapter, GPTAdapter])
    ├── Tenta MistralAdapter → sucesso: retorna resposta
    └── MistralAdapter falha → tenta GPTAdapter → retorna resposta
```

O `LLMChain` itera sobre a lista de providers em ordem. Se qualquer exceção for lançada pelo provider atual, ele avança para o próximo. Se todos falharem, lança `RuntimeError` com o resumo de todos os erros.

**Justificativa:**
- Garante disponibilidade do chatbot mesmo quando o Mistral (hospedado na máquina de um integrante) está offline.
- GPT-4o-mini tem custo baixo por requisição e qualidade superior de geração em português — adequado como fallback.
- A abstração via interface `LLMProvider` tornou a implementação do chain trivial: nenhum código de lógica de negócio precisou ser alterado.
- A ordem de prioridade (Mistral → GPT) respeita a estratégia de custo: o modelo sem custo de API é sempre tentado primeiro.

**Configuração:** O fallback é ativado automaticamente se `OPENAI_API_KEY` estiver configurado no `.env`. Caso contrário, apenas o Mistral é utilizado.

---

## Alternativas Consideradas para o LLM Principal

### Llama 2 / Llama 3 (Meta)
- Qualidade comparável ao Mistral, mas com tamanhos de modelo maiores para performance equivalente.
- Exige aceitação de licença específica para uso comercial.
- Mistral 7B foi preferido por sua melhor relação qualidade/tamanho e licença Apache 2.0.

### Gemma (Google)
- Disponível em versões pequenas (2B, 7B), mas com desempenho inferior ao Mistral em benchmarks de instrução na época da decisão.

### GPT-4o / Claude como modelo principal
- Excelente qualidade, mas com custo por requisição — inviável como modelo primário para um projeto acadêmico sem orçamento.
- Adotado apenas como fallback de último caso.

---

## Consequências

**Positivas:**
- A progressão de local → hospedado → fallback cloud foi natural e guiada pelas necessidades reais do projeto.
- O padrão `LLMChain` com `LLMProvider` abstrato garante que novos modelos podem ser adicionados ou reordenados sem impacto no restante do código.
- O chatbot mantém disponibilidade mesmo em caso de falha do Mistral, o que é especialmente importante em demonstrações e apresentações.

**Negativas / Riscos:**
- A dependência do endpoint Mistral hospedado por um integrante é um ponto único de falha para o modelo primário — não adequado para produção.
- O fallback para GPT tem custo associado à API da OpenAI; requisições excessivas durante falhas prolongadas do Mistral podem gerar custos inesperados.
- Em produção, o ideal seria hospedar o Mistral em infraestrutura dedicada (ex.: instância GPU em cloud) ou adotar um modelo via API comercial como solução principal.
