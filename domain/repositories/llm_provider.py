"""LLM Provider interface - contract for language model implementations."""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for Language Model providers.
    
    Implementations (e.g., MistralAdapter, GPTAdapter) should inherit from this
    and implement the generate() method to integrate with different LLM services.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate a response from the language model.
        
        Args:
            prompt: The input prompt to send to the LLM.
            
        Returns:
            str: The generated response from the LLM.
            
        Raises:
            RuntimeError: If the LLM service is unavailable or misconfigured.
            ValueError: If the prompt is invalid or response cannot be parsed.
        """
        pass
