"""
[Conceitos: Listas + Condicionais + Operadores] — LETRAMENTO EM IA

Toda resposta da IA fica registrada com um status de checagem.
O próprio aluno marca se conferiu a informação em uma fonte confiável ou
se encontrou um erro. Isso transforma o "senso crítico" em algo medível.
"""

from services.arquivos import ARQUIVO_RESPOSTAS, ler_json, salvar_json

STATUS_VALIDOS = ["pendente", "conferida", "com_erro"]


def listar_respostas():
    return ler_json(ARQUIVO_RESPOSTAS, [])


def gerar_novo_id(respostas):
    """Maior id + 1 (não repete id mesmo se algum registro for apagado do arquivo)."""
    maior_id = 0
    for registro in respostas:
        if registro["id"] > maior_id:
            maior_id = registro["id"]
    return maior_id + 1


def registrar_resposta(pergunta, resposta, onde_conferir, material=None):
    respostas = listar_respostas()
    registro = {
        "id": gerar_novo_id(respostas),
        "pergunta": pergunta,
        "resposta": resposta,
        "onde_conferir": onde_conferir,
        "status": "pendente",
        "material": material,  # resumo + questões, quando for um material de estudo
    }
    respostas.append(registro)
    salvar_json(ARQUIVO_RESPOSTAS, respostas)
    return registro


def atualizar_status(id_resposta, novo_status):
    if novo_status not in STATUS_VALIDOS:
        raise ValueError(f"Status inválido. Use um destes: {', '.join(STATUS_VALIDOS)}")

    respostas = listar_respostas()
    for registro in respostas:
        if registro["id"] == id_resposta:
            registro["status"] = novo_status
            salvar_json(ARQUIVO_RESPOSTAS, respostas)
            return registro
    raise KeyError(f"Resposta {id_resposta} não encontrada.")


def calcular_senso_critico(respostas):
    """Conta quantas respostas o aluno checou e calcula a taxa de verificação (%)."""
    conferidas = 0
    com_erro = 0
    for registro in respostas:
        if registro["status"] == "conferida":
            conferidas += 1
        elif registro["status"] == "com_erro":
            com_erro += 1

    total = len(respostas)
    verificadas = conferidas + com_erro
    taxa = round(verificadas / total * 100) if total > 0 else 0

    return {
        "total": total,
        "conferidas": conferidas,
        "com_erro": com_erro,
        "pendentes": total - verificadas,
        "taxa_verificacao": taxa,
    }
