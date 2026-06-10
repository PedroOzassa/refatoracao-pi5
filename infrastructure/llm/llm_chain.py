"""LLM Chain - strategy pattern for fallback between multiple LLM providers."""

from typing import List

from domain.repositories.llm_provider import LLMProvider


class LLMChain(LLMProvider):
    """Chain of Language Model providers with automatic fallback.
    
    Implements the LLMProvider interface by trying multiple LLM providers in sequence.
    If the first provider fails, it automatically falls back to the next one.
    
    This pattern is useful for:
    - High availability (fallback from primary to secondary LLM)
    - Cost optimization (try cheaper model first, fallback to more expensive)
    - Feature testing (try new model first, fallback to stable one)
    """

    def __init__(self, providers: List[LLMProvider]):
        """Initialize LLM chain with a list of providers.
        
        Args:
            providers: List of LLMProvider instances in order of preference.
                      Will try each provider in order until one succeeds.
                      
        Raises:
            ValueError: If providers list is empty.
        """
        if not providers:
            raise ValueError("At least one LLM provider must be provided")

        self.providers = providers

    def generate(self, prompt: str) -> str:
        """Generate a response using the chain of providers.
        
        Attempts to generate a response from the first provider. If it fails,
        tries the next provider in the chain. Continues until a provider succeeds
        or all providers are exhausted.
        
        Args:
            prompt: The input prompt to send to the LLM providers.
            
        Returns:
            str: The generated response from the first successful provider.
            
        Raises:
            RuntimeError: If all providers in the chain fail.
            ValueError: If the prompt is invalid (checked before trying any provider).
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        errors = []

        for i, provider in enumerate(self.providers):
            try:
                response = provider.generate(prompt)
                return response

            except Exception as e:
                provider_name = provider.__class__.__name__
                error_msg = f"Provider {i + 1}/{len(self.providers)} ({provider_name}) failed: {str(e)}"
                errors.append(error_msg)
                # Continue to next provider
                continue

        # All providers failed
        error_summary = "\n".join(errors)
        raise RuntimeError(
            f"All {len(self.providers)} LLM provider(s) in the chain failed:\n{error_summary}"
        )
