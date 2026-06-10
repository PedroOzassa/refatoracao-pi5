"""Chat service - orchestrates context retrieval and LLM response generation."""

import json
from typing import Tuple

from domain.repositories.llm_provider import LLMProvider
from domain.repositories.context_repository import ContextRepository


class ChatService:
    """Service that orchestrates chat workflow.
    
    Handles:
    1. Context retrieval from vector database
    2. Relevance classification
    3. Prompt building
    4. LLM response generation with fallback
    """

    # Message returned when context is not relevant
    NO_CONTEXT_MESSAGE = (
        "Desculpe, não encontrei informações suficientes para responder à sua pergunta. "
        "Por favor, reformule sua solicitação ou entre em contato pelo site: "
        "https://agibank.com.br/fale-conosco "
        "ou ligue para 3004 2221 (Capitais e regiões metropolitanas) "
        "ou 0800 602 0022 (Demais localidades)."
    )

    def __init__(
        self,
        llm_chain: LLMProvider,
        context_repository: ContextRepository,
        classifier_llm: LLMProvider = None,
    ):
        """Initialize chat service with dependencies.
        
        Args:
            llm_chain: LLM provider with fallback strategy (Mistral → GPT).
            context_repository: Repository to retrieve context from documents.
            classifier_llm: Optional LLM for classifying question relevance.
                           If None, uses same as llm_chain.
        """
        self.llm_chain = llm_chain
        self.context_repository = context_repository
        self.classifier_llm = classifier_llm or llm_chain

    def execute(self, question: str) -> Tuple[str, str]:
        """Execute chat workflow: retrieve context → classify → generate response.
        
        Args:
            question: User question to answer.
            
        Returns:
            Tuple of (answer, context) where:
            - answer: Generated response from LLM
            - context: Retrieved context from documents
            
        Raises:
            ValueError: If question is empty.
        """
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")

        question = question.strip()

        # Step 1: Retrieve context from vector database
        context = self.context_repository.find_context(
            query=question,
            top_k=3,
            threshold=0.45
        )

        # Step 2: Classify if question is relevant to context
        is_relevant = self._classify_relevance(question, context)

        # Step 3: Generate answer if relevant, else return default message
        if is_relevant:
            prompt = self._build_prompt(question, context)
            answer = self.llm_chain.generate(prompt)
        else:
            answer = self.NO_CONTEXT_MESSAGE

        return answer, context

    def _classify_relevance(self, question: str, context: str) -> bool:
        """Classify if question is relevant to the retrieved context.
        
        Uses LLM to determine if context has sufficient information to answer question.
        
        Args:
            question: User question.
            context: Retrieved context.
            
        Returns:
            True if relevant, False otherwise.
        """
        if not context or not context.strip():
            return False

        # Build classification prompt
        classification_prompt = self._build_classification_prompt(question, context)

        try:
            response = self.classifier_llm.generate(classification_prompt)
            return self._parse_classification_response(response)
        except Exception:
            # If classification fails, default to True (try to answer)
            return True

    def _parse_classification_response(self, response: str) -> bool:
        """Parse JSON response from classifier.
        
        Expected format: {"answer": "yes" | "no", "confidence": 0.0-1.0}
        
        Args:
            response: JSON string from classifier.
            
        Returns:
            True if answer is "yes" and confidence >= 0.5, False otherwise.
        """
        try:
            data = json.loads(response)
            answer = str(data.get("answer", "no")).strip().lower()
            confidence = float(data.get("confidence", 0.0))
        except (json.JSONDecodeError, TypeError, ValueError):
            # Try parsing as plain text
            answer = response.strip().lower()
            confidence = 0.0

        # Validate answer value
        if answer not in {"yes", "no"}:
            answer = "no"

        # Validate confidence range
        confidence = max(0.0, min(confidence, 1.0))

        # Return True only if yes with high confidence
        return answer == "yes" and confidence >= 0.5

    def _build_classification_prompt(self, question: str, context: str) -> str:
        """Build prompt for relevance classification.
        
        Args:
            question: User question.
            context: Retrieved context.
            
        Returns:
            Formatted classification prompt.
        """
        return f"""Você é um classificador de relevância para atendimento bancário.

Responda somente com JSON válido no formato:
{{"answer": "yes" ou "no", "confidence": número entre 0 e 1}}

Pergunta: {question}
Contexto: {context}

Com base no contexto fornecido, a pergunta pode ser respondida de forma adequada?"""

    def _build_prompt(self, question: str, context: str) -> str:
        """Build prompt for LLM response generation.
        
        Args:
            question: User question.
            context: Retrieved context.
            
        Returns:
            Formatted prompt for LLM.
        """
        return f"""Você é um assistente de atendimento ao cliente do AgiBank.
Use o contexto fornecido para responder a pergunta de forma clara, concisa e profissional.

Contexto:
{context}

Pergunta: {question}

Responda em português de forma objetiva."""
