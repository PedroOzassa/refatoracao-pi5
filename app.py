from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from llm.chat_service import responder
from embedding.find_context import find_context

app = FastAPI(title="Chatbot Agi API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str
    context: str


@app.post("/api/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    context = find_context(question)
    answer = responder(question, context)

    return ChatResponse(answer=answer, context=context)
