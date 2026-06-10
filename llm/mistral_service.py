import os
import requests
from dotenv import load_dotenv

load_dotenv()

MISTRAL_HOST = os.getenv("MISTRAL_HOST_URL")

def chamar_mistral(prompt: str) -> str:
    if not MISTRAL_HOST:
        raise RuntimeError("MISTRAL_HOST_URL não configurado")

    response = requests.post(
        MISTRAL_HOST,
        json={
            "model": "mistral:7b",
            "prompt": prompt,
            "stream": False,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()["response"]