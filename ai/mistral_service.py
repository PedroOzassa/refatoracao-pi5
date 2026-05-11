import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")

def chamar_mistral(prompt: str) -> str:
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "mistral:instruct",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]