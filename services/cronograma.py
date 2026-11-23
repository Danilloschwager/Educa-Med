"""
[Conceitos: Listas e Matrizes + Estruturas de Repetição + Operadores + Funções]

O ARTEFATO: CRUD das tarefas do cronograma de estudos.
    C - criar_tarefa        R - buscar_tarefa      U - atualizar_tarefa
    D - remover_tarefa      L - listar_tarefas

Cada tarefa é um dicionário dentro de uma LISTA salva em dados/tarefas.json:
    {"id": 1, "dia": "Segunda", "atividade": "Anatomia: membro superior",
     "duracao": "1h30", "concluida": False, "origem": "ia"}
"""

from services.arquivos import ARQUIVO_TAREFAS, ler_json, salvar_json
from services.texto import converter_duracao_para_minutos, formatar_minutos

CAMPOS_EDITAVEIS = ["dia", "atividade", "duracao", "concluida"]


# ---------- L - Listar ----------
def listar_tarefas():
    return ler_json(ARQUIVO_TAREFAS, [])


def gerar_novo_id(tarefas):
    maior_id = 0
    for tarefa in tarefas:
        if tarefa["id"] > maior_id:
            maior_id = tarefa["id"]
    return maior_id + 1


def montar_tarefa(tarefas, dia, atividade, duracao, origem):
    return {
        "id": gerar_novo_id(tarefas),
        "dia": str(dia).strip() or "Sem dia",
        "atividade": str(atividade).strip(),
        "duracao": str(duracao).strip(),
        "concluida": False,
        "origem": origem,  # "ia" ou "aluno" -> transparência sobre quem criou
    }


# ---------- C - Criar ----------
def criar_tarefa(dia, atividade, duracao, origem="aluno"):
    tarefas = listar_tarefas()
    nova = montar_tarefa(tarefas, dia, atividade, duracao, origem)
    tarefas.append(nova)
    salvar_json(ARQUIVO_TAREFAS, tarefas)
    return nova


# ---------- R - Ler ----------
def buscar_tarefa(id_tarefa):
    for tarefa in listar_tarefas():
        if tarefa["id"] == id_tarefa:
            return tarefa
    raise KeyError(f"Tarefa {id_tarefa} não encontrada.")


# ---------- U - Atualizar ----------
def atualizar_tarefa(id_tarefa, novos_dados):
    tarefas = listar_tarefas()
    for tarefa in tarefas:
        if tarefa["id"] == id_tarefa:
            for campo in CAMPOS_EDITAVEIS:
                if novos_dados.get(campo) is not None:
                    tarefa[campo] = novos_dados[campo]
            salvar_json(ARQUIVO_TAREFAS, tarefas)
            return tarefa
    raise KeyError(f"Tarefa {id_tarefa} não encontrada.")


# ---------- D - Deletar ----------
def remover_tarefa(id_tarefa):
    tarefas = listar_tarefas()
    restantes = []
    for tarefa in tarefas:
        if tarefa["id"] != id_tarefa:
            restantes.append(tarefa)

    if len(restantes) == len(tarefas):
        raise KeyError(f"Tarefa {id_tarefa} não encontrada.")
    salvar_json(ARQUIVO_TAREFAS, restantes)


def substituir_tarefas_da_ia(cronograma_ia):
    """
    Quando a IA monta um cronograma novo, troca só as tarefas que vieram
    dela. As tarefas que o próprio aluno criou continuam lá.
    """
    tarefas = []
    for tarefa in listar_tarefas():
        if tarefa["origem"] != "ia":
            tarefas.append(tarefa)

    for item in cronograma_ia:
        if not isinstance(item, dict) or not item.get("atividade"):
            continue  # ignora itens mal formatados pela IA
        nova = montar_tarefa(tarefas, item.get("dia", ""), item["atividade"],
                             item.get("duracao", ""), origem="ia")
        tarefas.append(nova)

    salvar_json(ARQUIVO_TAREFAS, tarefas)


def montar_resumo(tarefas):
    """
    Monta uma MATRIZ (lista de listas) com uma linha por dia:
        [dia, total_de_tarefas, tarefas_concluidas, minutos_planejados]
    Ex.: [["Segunda", 2, 1, 150], ["Terça", 1, 0, 60]]
    """
    matriz = []
    for tarefa in tarefas:
        # Procura a linha do dia; se não existir, cria
        linha_do_dia = None
        for linha in matriz:
            if linha[0] == tarefa["dia"]:
                linha_do_dia = linha
        if linha_do_dia is None:
            linha_do_dia = [tarefa["dia"], 0, 0, 0]
            matriz.append(linha_do_dia)

        linha_do_dia[1] += 1
        if tarefa["concluida"]:
            linha_do_dia[2] += 1
        linha_do_dia[3] += converter_duracao_para_minutos(tarefa["duracao"])

    total_tarefas = 0
    total_concluidas = 0
    total_minutos = 0
    for linha in matriz:
        total_tarefas += linha[1]
        total_concluidas += linha[2]
        total_minutos += linha[3]

    progresso = round(total_concluidas / total_tarefas * 100) if total_tarefas > 0 else 0

    # Converte os minutos de cada dia para texto ("1h30") antes de enviar ao front
    por_dia = []
    for dia, qtd, concluidas, minutos in matriz:
        por_dia.append([dia, qtd, concluidas, formatar_minutos(minutos)])

    return {
        "por_dia": por_dia,
        "total_tarefas": total_tarefas,
        "total_concluidas": total_concluidas,
        "tempo_total": formatar_minutos(total_minutos),
        "progresso": progresso,
    }
