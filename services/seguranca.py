"""
[Conceitos: Estruturas Condicionais + Estruturas de Repetição]

Limites de uso do Educa-Med. Antes de qualquer mensagem chegar na IA, ela
passa por aqui. O assistente é EXCLUSIVAMENTE educacional: não responde
casos clínicos reais, diagnósticos ou pedidos de medicação.
"""

from services.texto import normalizar_texto

TAMANHO_MAXIMO = 1000

# Frases que indicam um caso real / pedido clínico (já sem acento)
TERMOS_CLINICOS = [
    "meu paciente", "minha paciente", "caso real",
    "estou sentindo", "to sentindo", "estou com dor", "tenho dor",
    "posso tomar", "devo tomar", "que remedio tomar", "qual remedio tomar",
    "me diagnostica", "o que eu tenho", "prescrever para",
]

RESPOSTA_BLOQUEIO = (
    "Não posso ajudar com casos clínicos reais, diagnósticos ou indicação de "
    "medicamentos — o Educa-Med é só para organizar seus estudos.\n\n"
    "Se for uma situação real, procure um professor, preceptor ou um serviço "
    "de saúde. Se for uma dúvida de estudo, reformule como tema "
    "(ex.: \"quero revisar dor torácica em clínica médica\")."
)


def validar_mensagem(mensagem):
    """Devolve um texto de erro se a mensagem for inválida, ou None se estiver tudo certo."""
    if len(mensagem) == 0:
        return "Escreva uma mensagem antes de enviar."
    elif len(mensagem) > TAMANHO_MAXIMO:
        return f"Mensagem muito longa: use no máximo {TAMANHO_MAXIMO} caracteres."
    return None


def e_pedido_clinico(mensagem):
    """True se a mensagem parecer um caso clínico real."""
    texto = normalizar_texto(mensagem)
    for termo in TERMOS_CLINICOS:
        if termo in texto:
            return True
    return False
