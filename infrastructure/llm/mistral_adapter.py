"""Mistral LLM Provider Adapter."""

import requests

from domain.repositories.llm_provider import LLMProvider
from infrastructure.config import get_settings


class MistralAdapter(LLMProvider):
    """Adapter for Mistral LLM service.
    
    Implements the LLMProvider interface by making HTTP requests to a Mistral
    endpoint (typically running via Ollama or similar locally).
    """

    def __init__(self, host_url: str = None, model: str = None, timeout: int = None):
        """Initialize Mistral adapter.
        
        Args:
            host_url: Mistral endpoint URL (defaults to settings.MISTRAL_HOST_URL)
            model: Model name (defaults to settings.MISTRAL_MODEL)
            timeout: Request timeout in seconds (defaults to settings.MISTRAL_TIMEOUT)
        """
        settings = get_settings()
        self.host_url = host_url or settings.MISTRAL_HOST_URL
        self.model = model or settings.MISTRAL_MODEL
        self.timeout = timeout or settings.MISTRAL_TIMEOUT

        if not self.host_url:
            raise RuntimeError(
                "MISTRAL_HOST_URL is not configured. "
                "Set it in environment variables or pass it to the constructor."
            )

    def generate(self, prompt: str) -> str:
        """Generate a response from Mistral LLM.
        
        Args:
            prompt: The input prompt to send to the LLM.
            
        Returns:
            str: The generated response from Mistral.
            
        Raises:
            RuntimeError: If the Mistral service is unavailable or returns an error.
            requests.RequestException: If there's a network error.
            ValueError: If the response cannot be parsed.
            KeyError: If the response JSON structure is unexpected.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            response = requests.post(
                self.host_url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()
            
            if "response" not in data:
                raise KeyError(
                    f"Unexpected response structure. Expected 'response' key, got: {list(data.keys())}"
                )

            return data["response"]

        except requests.exceptions.Timeout as e:
            raise RuntimeError(f"Mistral request timed out after {self.timeout}s: {e}") from e
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"Failed to connect to Mistral at {self.host_url}: {e}") from e
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"Mistral returned HTTP error: {e.response.status_code} - {e}") from e
