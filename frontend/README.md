# Frontend - Chatbot AGI

Interface web moderna para o Chatbot AGI.

## 📁 Estrutura

```
frontend/
└── index.html    # Interface do chatbot
```

## 🚀 Como usar

### Opção 1: Abrir diretamente no navegador
```
Abra o arquivo: frontend/index.html
```

### Opção 2: Usar um servidor local (recomendado)

**Com Python:**
```bash
cd frontend
python -m http.server 3000
```

**Com Node.js (http-server):**
```bash
cd frontend
npx http-server -p 3000
```

Depois acesse: `http://localhost:3000`

## ⚙️ Configuração

O frontend se conecta ao backend em `http://localhost:8000` por padrão.

Para mudar a URL do backend, edite a linha no `index.html`:
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

## ✨ Recursos

- 💬 Chat em tempo real
- 📚 Exibição de contexto das respostas
- 🟢 Status de conexão (Online/Offline)
- ⌨️ Suporte a Enter para enviar
- 📱 Responsivo (desktop e mobile)
- ✍️ Indicador de digitação
- 🎨 Interface moderna com gradientes e animações

## 🔄 Fluxo

1. Frontend envia pergunta para `POST /api/chat`
2. Backend processa com embedding e LLM
3. Resposta retorna com `answer` e `context`
4. Frontend exibe ambos para o usuário
