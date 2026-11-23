"""
[Conceitos: Strings + Variáveis e Operadores]

Funções que tratam os textos digitados pelo aluno ou devolvidos pela IA.
"""

ACENTOS = {
    "á": "a", "à": "a", "â": "a", "ã": "a",
    "é": "e", "ê": "e",
    "í": "i",
    "ó": "o", "ô": "o", "õ": "o",
    "ú": "u",
    "ç": "c",
}


def normalizar_texto(texto):
    """'  Estou com DOR ' -> 'estou com dor' (minúsculo, sem acento e sem espaços nas pontas)."""
    texto = texto.lower().strip()
    resultado = ""
    for letra in texto:
        resultado += ACENTOS.get(letra, letra)
    return resultado


def converter_duracao_para_minutos(duracao):
    """
    Transforma a duração escrita em texto em minutos:
        "1h30" -> 90    "45min" -> 45    "2 horas" -> 120    "1,5h" -> 90
    Se não der para entender o texto, devolve 0.
    """
    texto = normalizar_texto(str(duracao))
    texto = texto.replace(" e ", "").replace(" ", "")
    texto = texto.replace("minutos", "min").replace("horas", "h").replace("hora", "h")

    try:
        if "h" in texto:
            parte_horas, parte_minutos = texto.split("h", 1)
            horas = float(parte_horas.replace(",", ".")) if parte_horas else 0
            parte_minutos = parte_minutos.replace("min", "")
            minutos = int(parte_minutos) if parte_minutos else 0
        else:
            horas = 0
            minutos = int(texto.replace("min", ""))
    except ValueError:
        return 0

    return int(horas * 60) + minutos


def formatar_minutos(total_minutos):
    """90 -> '1h30'   120 -> '2h'   45 -> '45min'  (usa os operadores // e %)."""
    horas = total_minutos // 60      # divisão inteira
    minutos = total_minutos % 60     # resto da divisão

    if horas == 0:
        return f"{minutos}min"
    elif minutos == 0:
        return f"{horas}h"
    else:
        return f"{horas}h{minutos:02d}"
