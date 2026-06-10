"""FastAPI handlers - API endpoints with dependency injection."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from di.container import get_container
from application.dto import ChatRequestDTO, ChatResponseDTO
from application.chat_service import ChatService
from application.chat_usecase import ChatUseCase


# Initialize FastAPI app
app = FastAPI(title="Chatbot Agi API", version="0.1.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get DI container once (shared across all requests)
_container = None


def get_di_container():
    """Get or initialize the DI container.
    
    Uses lazy initialization on first request.
    In production, initialize in FastAPI startup event.
    
    Returns:
        DIContainer singleton.
    """
    global _container
    if _container is None:
        _container = get_container()
    return _container


# Pydantic models for OpenAPI documentation
class ChatRequestModel(BaseModel):
    """Chat request model for API documentation."""
    question: str

    class Config:
        json_schema_extra = {
            "example": {
                "question": "Quais são os horários de atendimento?"
            }
        }


class ChatResponseModel(BaseModel):
    """Chat response model for API documentation."""
    answer: str
    context: str

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "Estamos disponíveis de segunda a sexta, das 8h às 20h.",
                "context": "Horários de atendimento: seg-sex 8h-20h..."
            }
        }


@app.get("/health")
def health() -> dict:
    """Health check endpoint.
    
    Returns:
        dict: Status of the service.
    """
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponseModel)
def chat(payload: ChatRequestModel) -> ChatResponseModel:
    """Chat endpoint - answer user questions using RAG.
    
    Workflow:
    1. Retrieve relevant context from vector database
    2. Classify if context is relevant
    3. Generate answer using LLM (Mistral with GPT fallback)
    
    Args:
        payload: Chat request with question.
        
    Returns:
        ChatResponseModel with answer and retrieved context.
        
    Raises:
        HTTPException: 400 if question is empty.
        HTTPException: 500 for internal errors.
    """
    try:
        # Validate input
        question = payload.question.strip() if payload.question else ""
        if not question:
            raise HTTPException(
                status_code=400,
                detail="Question is required and cannot be empty"
            )

        # Get DI container
        container = get_di_container()

        # Build chat service with injected dependencies
        llm_chain = container.get_llm_chain()
        context_repository = container.get_context_repository()
        chat_service = ChatService(
            llm_chain=llm_chain,
            context_repository=context_repository,
            classifier_llm=llm_chain  # Use same chain for classification
        )

        # Build and execute use case
        use_case = ChatUseCase(chat_service=chat_service)
        request_dto = ChatRequestDTO(question=question)
        response_dto = use_case.execute(request_dto)

        # Return response
        return ChatResponseModel(
            answer=response_dto.answer,
            context=response_dto.context
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@app.on_event("shutdown")
def shutdown_event():
    """Clean up resources on shutdown.
    
    Closes database connections and other resources.
    """
    global _container
    if _container is not None:
        _container.close()
        _container = None
