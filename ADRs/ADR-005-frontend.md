# ADR-005: Escolha de Frontend Simples e Puro (sem Frameworks)

- **Status:** Aceito
- **Data:** 2026-06
- **Contexto do projeto:** Chatbot RAG de atendimento ao cliente — AgiBank / Projeto Integrador 5 (PUC Campinas)

---

## Contexto

O projeto necessita de uma interface de usuário para que seja possível interagir com o chatbot de forma visual. Essa interface precisa:

- Exibir uma janela de chat flutuante (estilo widget de suporte).
- Permitir que o usuário envie perguntas e receba respostas em tempo real.
- Consumir a API REST do backend (`POST /api/chat`).
- Ser fácil de iniciar — qualquer integrante deve conseguir rodar o frontend sem instalação de dependências de Node.js, npm ou ferramentas de build.
- Ter identidade visual minimamente alinhada ao contexto bancário/AgiBank.

O frontend não é o foco central do projeto — o núcleo acadêmico está no pipeline RAG (embeddings, busca vetorial, integração com LLM). A interface é apenas o meio de demonstração.

---

## Decisão

Adotar um **frontend simples com HTML, CSS e JavaScript puros**, sem frameworks ou ferramentas de build. O frontend consiste em dois arquivos:

- `frontend/index.html` — estrutura, estilos e lógica de interação do chat.
- `frontend/config.js` — configuração do endpoint da API (URL do backend), separada para facilitar a mudança sem editar o HTML principal.

O frontend é servido via servidor HTTP simples do Python:

```bash
python -m http.server 8080 -d frontend
```

---

## Alternativas Consideradas

### React (com Create React App ou Vite)
- Framework robusto com componentização, estado gerenciado e ecossistema rico.
- Exigiria instalação de Node.js, npm/yarn e processo de build (`npm run build`) para gerar os arquivos estáticos.
- Adicionaria complexidade de configuração desnecessária para uma interface de chat com funcionalidade simples.
- A curva de entrada para integrantes sem experiência prévia em React seria um obstáculo.

### Vue.js / Angular
- Mesmas considerações do React: overhead de setup e build pipeline para uma interface de baixa complexidade.

### Svelte
- Mais leve que React/Vue, mas ainda exige Node.js e compilação.

### Streamlit (Python)
- Muito utilizado em projetos de ML para criar interfaces rapidamente em Python puro.
- Não oferece controle fino sobre o layout e a aparência — difícil de estilizar para parecer um widget de chat flutuante.
- A interface resultante tem aparência genérica de dashboard científico, inadequada para um protótipo de atendimento ao cliente.

---

## Justificativa

O frontend puro (vanilla HTML/CSS/JS) foi escolhido pelos seguintes motivos:

1. **Zero dependências de ferramentas externas:** Qualquer navegador moderno executa o frontend. Não há Node.js, npm, build steps ou bundlers envolvidos. O comando `python -m http.server` (já disponível em qualquer instalação Python) é suficiente para servir os arquivos.

2. **Foco no backend e no pipeline RAG:** O objetivo acadêmico do projeto é demonstrar a arquitetura RAG — embeddings, busca vetorial, integração com LLM. O frontend é instrumentação para essa demonstração, e investir tempo em setup de frameworks reduziria o tempo disponível para o que realmente importa.

3. **Facilidade de contribuição:** Todos os integrantes, independentemente de experiência com frameworks JavaScript, conseguem ler, entender e modificar um arquivo HTML com JavaScript inline.

4. **Funcionalidade suficiente com código simples:** A interface de chat foi implementada com `fetch()` nativo para consumir a API, manipulação direta do DOM e CSS com variáveis customizadas (CSS Variables). O resultado é um widget de chat flutuante funcional, responsivo e com identidade visual adequada — sem necessidade de bibliotecas externas.

5. **Separação de configuração:** O arquivo `config.js` externaliza a URL do backend, permitindo que diferentes integrantes apontem para endereços diferentes (localhost, IP do integrante com o Mistral, etc.) sem alterar o HTML principal.

---

## Consequências

**Positivas:**
- Onboarding instantâneo: qualquer pessoa pode abrir `index.html` em um servidor local sem instalação adicional.
- Nenhuma etapa de build necessária — o código-fonte é o produto final.
- Fácil de inspecionar pelo avaliador do projeto sem ferramentas especializadas.
- Manutenção simples: mudanças de layout ou comportamento são feitas diretamente no arquivo HTML.

**Negativas / Riscos:**
- Não é escalável para uma interface de maior complexidade: adicionar novas páginas, rotas ou componentes reutilizáveis seria trabalhoso sem um framework.
- Sem gerenciamento de estado centralizado — o estado da conversa é mantido diretamente no DOM e em variáveis JavaScript locais.
- Para uma versão de produção real do produto AgiBank, seria necessário migrar para uma stack com componentização, acessibilidade aprimorada (ARIA) e internacionalização.
- Não há testes automatizados de interface (testes de componente, E2E) — aceitável para protótipo acadêmico.
