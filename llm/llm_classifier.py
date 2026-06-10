import json
from llm.gpt_service import chamar_gpt
from llm.mistral_service import chamar_mistral
import requests

def parse_classification(response: str) -> bool:
    try:
        data = json.loads(response)
        answer = str(data.get("answer", "no")).strip().lower()
        confidence = float(data.get("confidence", 0.0))
    except (json.JSONDecodeError, TypeError, ValueError):
        answer = response.strip().lower()
        confidence = 0.0

    if answer not in {"yes", "no"}:
        answer = "no"

    confidence = max(0.0, min(confidence, 1.0))

    if answer != "yes" or confidence < 0.5:
        return False
    
    return True


def is_question_valid(pergunta: str, contexto: str) -> bool:
    prompt = f"""
Você é um classificador de relevância para atendimento bancário.

Responda somente com JSON válido no formato:
{{"answer":"yes"|"no","confidence":0.0-1.0}}

Regras:

Responda "yes" somente se:
- a PERGUNTA for algo que um chatbot de um banco deveria responder, e;
- o CONTEXTO possuir informação suficiente para respondê-la.

Responda "no" somente se: 
- o CONTEXTO for insuficiente, incompleto ou não relacionado.

A confidence deve refletir sua certeza sobre a sua resposta.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}
""".strip()
    try:
        raw_response = chamar_mistral(prompt)
    except (RuntimeError, requests.RequestException, ValueError, KeyError, IndexError):
        raw_response = chamar_gpt(prompt)
    return parse_classification(raw_response)