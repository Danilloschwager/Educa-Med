"""
[Conceitos: Dicionários + Mapeamento de Arquivos]

Perfil do aluno (área, rotina e método de estudo) que a IA vai descobrindo
durante a conversa. Fica salvo em dados/perfil.json.
"""

from services.arquivos import ARQUIVO_PERFIL, ler_json, salvar_json

CAMPOS_PERFIL = ["area", "rotina", "metodo_estudo"]


def carregar_perfil():
    perfil = ler_json(ARQUIVO_PERFIL, {})
    for campo in CAMPOS_PERFIL:
        perfil.setdefault(campo, None)
    return perfil


def atualizar_perfil(dados_da_ia):
    """Só sobrescreve o que a IA realmente identificou (campos vazios são ignorados)."""
    perfil = carregar_perfil()
    for campo in CAMPOS_PERFIL:
        if dados_da_ia.get(campo):
            perfil[campo] = dados_da_ia[campo]
    salvar_json(ARQUIVO_PERFIL, perfil)
    return perfil
