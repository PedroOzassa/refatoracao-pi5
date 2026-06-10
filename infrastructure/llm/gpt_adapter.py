"""OpenAI/GPT LLM Provider Adapter."""

import requests

from domain.repositories.llm_provider import LLMProvider
from infrastructure.config import get_settings


class GPTAdapter(LLMProvider):
    """Adapter for OpenAI GPT LLM service.
    
    Implements the LLMProvider interface by making HTTP requests to the OpenAI API.
    Requires an OpenAI API key to be configured.
    """

    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        base_url: str = None,
        timeout: int = None,
    ):
        """Initialize GPT adapter.
        
        Args:
            api_key: OpenAI API key (defaults to settings.OPENAI_API_KEY)
            model: Model name (defaults to settings.OPENAI_MODEL)
            base_url: OpenAI API base URL (defaults to settings.OPENAI_BASE_URL)
            timeout: Request timeout in seconds (defaults to settings.OPENAI_TIMEOUT)
        """
        settings = get_settings()
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.base_url = (base_url or settings.OPENAI_BASE_URL).rstrip("/")
        self.timeout = timeout or settings.OPENAI_TIMEOUT

        if not self.api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not configured. "
                "Set it in environment variables or pass it to the constructor."
            )

    def generate(self, prompt: str) -> str:
        """Generate a response from OpenAI GPT.
        
        Args:
            prompt: The input prompt to send to the LLM.
            
        Returns:
            str: The generated response from GPT.
            
        Raises:
            RuntimeError: If the OpenAI service is unavailable or returns an error.
            requests.RequestException: If there's a network error.
            ValueError: If the response cannot be parsed.
            KeyError: If the response JSON structure is unexpected.
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0,
                },
                timeout=self.timeout,
            )

            response.raise_for_status()

            data = response.json()
            
            if "choices" not in data or len(data["choices"]) == 0:
                raise KeyError(
                    f"Unexpected response structure. Expected 'choices' array, got: {list(data.keys())}"
                )

            message = data["choices"][0].get("message", {}).get("content", "").strip()
            
            if not message:
                raise ValueError("Empty response message from GPT")

            return message

        except requests.exceptions.Timeout as e:
            raise RuntimeError(f"OpenAI request timed out after {self.timeout}s: {e}") from e
        except requests.exceptions.ConnectionError as e:
            raise RuntimeError(f"Failed to connect to OpenAI at {self.base_url}: {e}") from e
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(f"OpenAI returned HTTP error: {e.response.status_code} - {e}") from e
