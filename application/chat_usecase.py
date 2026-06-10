"""Chat use case - application layer orchestrator."""

from application.dto import ChatRequestDTO, ChatResponseDTO
from application.chat_service import ChatService


class ChatUseCase:
    """Use case for handling chat requests.
    
    Implements the business logic for:
    - Validating user input
    - Delegating to ChatService for processing
    - Building response DTO
    """

    def __init__(self, chat_service: ChatService):
        """Initialize chat use case.
        
        Args:
            chat_service: Service to handle chat workflow.
        """
        self.chat_service = chat_service

    def execute(self, request: ChatRequestDTO) -> ChatResponseDTO:
        """Execute chat use case.
        
        Args:
            request: Chat request DTO with question.
            
        Returns:
            Chat response DTO with answer and context.
            
        Raises:
            ValueError: If question is empty or invalid.
        """
        # Validate and sanitize input
        question = request.question.strip() if request.question else ""

        if not question:
            raise ValueError("Question cannot be empty")

        # Execute chat workflow
        answer, context = self.chat_service.execute(question)

        # Build response DTO
        return ChatResponseDTO(answer=answer, context=context)
