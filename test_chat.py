from ai.chat_service import responder

pergunta = "Como calcular juros simples?"
contexto = "A renda fixa, como o próprio nome já diz, é uma classe de investimentos em que a rentabilidade é determinada no momento da contratação. Por exemplo, se o investidor adquire um título com juros prefixados que paga 6% de rentabilidade ao ano, ao final do período, ou seja, na data de vencimento do contrato, ele irá receber a remuneração combinada. Por outro lado, se contrata um título pós-fixado atrelado ao CDI, IPCA ou Selic, não é possível saber exatamente quanto vai receber ao final do período, mas sabe que a taxa de rentabilidade está fixada no indicador."

print(responder(pergunta, contexto))