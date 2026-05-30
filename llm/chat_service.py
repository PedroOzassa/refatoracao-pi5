from llm.mistral_service import chamar_mistral
from llm.prompt_builder import montar_prompt

def responder(pergunta: str, contexto: str) -> str:
    if not contexto or contexto.strip() == "":
        resposta = "Desculpe, não encontrei informações suficientes para responder" \
        " à sua pergunta. Por favor, reformule sua solicitação ou entre em" \
        " contato com nossa central de atendimento para obter suporte especializado."
    else:
        prompt = montar_prompt(pergunta, contexto)
        resposta = chamar_mistral(prompt)
        
    return resposta