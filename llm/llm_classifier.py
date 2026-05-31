import json
from llm.mistral_service import chamar_mistral

def parse_classification(response: str):
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


def is_question_valid(pergunta: str, contexto: str):
    if not contexto or contexto.strip() == "":
        return {"answer": "no", "confidence": 1.0}

    prompt = f"""
Você é um classificador de relevância para atendimento bancário.

Responda somente com JSON válido no formato:
{{"answer":"yes"|"no","confidence":0.0-1.0}}

Regras:
- Responda "yes" se o contexto for suficiente para responder a pergunta com segurança.
- Responda "no" se o contexto for insuficiente, incompleto ou não relacionado.
- A confidence deve refletir sua certeza.

CONTEXTO:
{contexto}

PERGUNTA:
{pergunta}
""".strip()

    raw_response = chamar_mistral(prompt)
    return parse_classification(raw_response)