"""
[Conceitos: Mapeamento de Arquivos + Tratamento de Erros]

Guarda os dados do Educa-Med em arquivos JSON dentro da pasta "dados/".
Assim o cronograma e o histórico não somem quando o servidor reinicia.
"""

import json
from pathlib import Path

# Variáveis com o caminho de cada arquivo usado pelo sistema
PASTA_DADOS = Path(__file__).resolve().parent.parent / "dados"
ARQUIVO_TAREFAS = PASTA_DADOS / "tarefas.json"
ARQUIVO_RESPOSTAS = PASTA_DADOS / "respostas_ia.json"
ARQUIVO_PERFIL = PASTA_DADOS / "perfil.json"


def ler_json(caminho, valor_padrao):
    """Lê um arquivo JSON. Se ele não existir ou estiver quebrado, devolve o valor padrão."""
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        # Primeira execução: o arquivo ainda não foi criado
        return valor_padrao
    except json.JSONDecodeError:
        print(f"[aviso] {caminho.name} estava corrompido — começando do zero.")
        return valor_padrao


def salvar_json(caminho, dados):
    """Grava os dados no arquivo (cria a pasta 'dados/' se precisar)."""
    PASTA_DADOS.mkdir(exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)


def limpar_todos_os_dados():
    """Zera tarefas, respostas e perfil (botão 'Recomeçar' da interface)."""
    salvar_json(ARQUIVO_TAREFAS, [])
    salvar_json(ARQUIVO_RESPOSTAS, [])
    salvar_json(ARQUIVO_PERFIL, {})
