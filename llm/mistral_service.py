import os
import requests
from dotenv import load_dotenv

load_dotenv()

MISTRAL_HOST = os.getenv("MISTRAL_HOST_URL")

def chamar_mistral(prompt: str) -> str:
    response = requests.post(
        MISTRAL_HOST,
        json={
            "model": "mistral:7b",
            "prompt": prompt,
            "stream": False
        }
    )


    return response.json()["response"]