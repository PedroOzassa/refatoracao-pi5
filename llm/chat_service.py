from llm.llm_classifier import is_question_valid
from llm.mistral_service import chamar_mistral
from llm.prompt_builder import montar_prompt

def responder(pergunta: str, contexto: str) -> str:
    classificacao = is_question_valid(pergunta, contexto)
    if classificacao:
        prompt = montar_prompt(pergunta, contexto)
        resposta = chamar_mistral(prompt)  
    else:
        resposta = (
    "Desculpe, não encontrei informações suficientes para responder à sua pergunta. "
    "Por favor, reformule sua solicitação ou entre em contato pelo site:"
    "https://agibank.com.br/fale-conosco"
    "ou ligue para 3004 2221 (Capitais e regiões metropolitanas) "
    "ou 0800 602 0022 (Demais localidades)."
    )   
    return resposta