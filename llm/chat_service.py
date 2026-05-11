from llm.mistral_service import chamar_mistral
from llm.prompt_builder import montar_prompt

def responder(pergunta: str, contexto: str) -> str:
    prompt = montar_prompt(pergunta, contexto)
    resposta = chamar_mistral(prompt)
    return resposta