"""
[Conceitos: Funções + Tratamento de Erros]

Camada de IA: é a ÚNICA parte do sistema que conversa com o modelo de
linguagem (Groq). Trocar de provedor no futuro só exige mexer aqui.
"""

import json
import os

from groq import Groq

MODELO_IA = "openai/gpt-oss-20b"

PROMPT_SISTEMA = """Você é a Educa-Med, assistente de IA que ajuda estudantes de medicina a ORGANIZAR os estudos.

O que você faz:
1. Descobre a área da medicina que o estudante quer estudar ou tem dificuldade.
2. Descobre a rotina: quanto tempo por dia/semana ele tem para estudar.
3. Descobre o método de estudo preferido (resumos, questões, vídeo-aulas, mapas mentais...).
4. Com informação suficiente, monta um cronograma simples e realista, dividido por dia.
5. Adapta o cronograma quando o estudante contar novas dificuldades ou mudanças.
6. ENSINA: se o estudante pedir explicação, resumo, revisão, questões ou exercícios de um tema,
   preencha o campo "material" com um resumo didático, pontos-chave e 3 a 5 questões de múltipla
   escolha (4 alternativas, só uma correta). Se ele só estiver falando da rotina, use "material": null.

Limites (obrigatórios):
- Uso EXCLUSIVAMENTE educacional. Nunca dê diagnóstico, conduta, prescrição ou opinião sobre casos clínicos reais.
- Nunca apresente sua resposta como verdade absoluta. Você é apoio, não substitui professores, livros-texto ou diretrizes oficiais.
- Incentive o estudante a conferir informações importantes em fontes confiáveis.

Responda SOMENTE em JSON, neste formato:
{
  "mensagem": "texto acolhedor, direto e motivador",
  "area": "área identificada ou vazio",
  "rotina": "tempo disponível informado ou vazio",
  "metodo_estudo": "método preferido informado ou vazio",
  "onde_conferir": "tipo de fonte confiável para checar o que você disse (ex: livro-texto de farmacologia, diretriz da sociedade médica) ou vazio",
  "cronograma": [{"dia": "Segunda", "atividade": "o que estudar", "duracao": "1h30"}],
  "material": {
    "resumo": "explicação didática do tema",
    "pontos_chave": ["ponto 1", "ponto 2"],
    "questoes": [{"pergunta": "...", "alternativas": ["A", "B", "C", "D"], "correta": 0, "explicacao": "..."}]
  }
}
"correta" é o índice (0 a 3) da alternativa certa.
Se ainda não houver informação suficiente para o cronograma, use "cronograma": [].
Só devolva o cronograma de novo se ele mudar; se o pedido for só ensinar, use "cronograma": []."""

CAMPOS_RESPOSTA = ["mensagem", "area", "rotina", "metodo_estudo", "onde_conferir"]

_cliente = None


def obter_cliente():
    """Cria o cliente da Groq só na primeira vez que for usado."""
    global _cliente
    if _cliente is None:
        _cliente = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _cliente


# Textos de exemplo que NÃO são uma chave de verdade (o primeiro é o do .env.example)
CHAVES_DE_EXEMPLO = ["", "cole_sua_chave_aqui", "coloque_sua_chave_aqui"]


def chave_configurada():
    """True só se a GROQ_API_KEY tiver uma chave real (e não o texto de exemplo)."""
    chave = os.getenv("GROQ_API_KEY", "").strip()
    return chave not in CHAVES_DE_EXEMPLO


def montar_contexto(mensagem, perfil, tarefas):
    """Junta o que já sabemos do aluno + a nova mensagem em um único texto para a IA."""
    cronograma_atual = []
    for tarefa in tarefas:
        cronograma_atual.append(f"{tarefa['dia']}: {tarefa['atividade']} ({tarefa['duracao']})")

    return (
        f"Perfil do estudante até agora: {json.dumps(perfil, ensure_ascii=False)}\n"
        f"Cronograma atual: {'; '.join(cronograma_atual) or 'nenhum'}\n"
        f"Nova mensagem do estudante: {mensagem}"
    )


def padronizar_resposta(dados):
    """Garante que a resposta sempre tenha as mesmas chaves, mesmo se a IA esquecer alguma."""
    for campo in CAMPOS_RESPOSTA:
        if not isinstance(dados.get(campo), str):
            dados[campo] = ""
    if not isinstance(dados.get("cronograma"), list):
        dados["cronograma"] = []

    # Material de estudo pedido no chat (resumo + questões): só fica se tiver conteúdo
    material = dados.get("material")
    if isinstance(material, dict):
        material.setdefault("onde_conferir", dados["onde_conferir"])
        material = padronizar_material(material)
        if not material["resumo"] and not material["questoes"]:
            material = None
    else:
        material = None
    dados["material"] = material
    return dados


def resposta_modo_demo():
    """Usada quando não há GROQ_API_KEY: permite mostrar o sistema funcionando sem internet."""
    return padronizar_resposta({
        "mensagem": (
            "[Modo demonstração — configure a GROQ_API_KEY para usar a IA de verdade]\n\n"
            "Montei um cronograma de exemplo para Anatomia, com 1h30 por dia e foco em resumos e questões. "
            "Lembre-se de conferir os conteúdos no seu livro-texto!"
        ),
        "area": "Anatomia",
        "rotina": "1h30 por dia",
        "metodo_estudo": "Resumos e questões",
        "onde_conferir": "Livro-texto de anatomia adotado pela sua faculdade",
        "cronograma": [
            {"dia": "Segunda", "atividade": "Membro superior: ossos e articulações", "duracao": "1h30"},
            {"dia": "Quarta", "atividade": "Membro superior: músculos (resumo)", "duracao": "1h30"},
            {"dia": "Sexta", "atividade": "Questões de revisão da semana", "duracao": "1h"},
        ],
    })


def chamar_ia(prompt_sistema, texto_usuario):
    """Faz a chamada à Groq e devolve a resposta já convertida de JSON para dicionário."""
    try:
        resposta = obter_cliente().chat.completions.create(
            model=MODELO_IA,
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": texto_usuario},
            ],
            temperature=0.4,
            response_format={"type": "json_object"},
        )
    except Exception as erro:
        # Sem internet, chave inválida, modelo inexistente, Groq fora do ar...
        print(f"[erro IA] {erro}")
        raise RuntimeError("Não consegui falar com a IA agora. Verifique a internet e a GROQ_API_KEY.")

    texto = resposta.choices[0].message.content

    try:
        dados = json.loads(texto)
    except (json.JSONDecodeError, TypeError):
        # A IA respondeu fora do formato: aproveitamos o texto como mensagem
        dados = {"mensagem": texto or ""}

    if not isinstance(dados, dict):
        dados = {"mensagem": str(dados)}
    return dados


def gerar_resposta_ia(mensagem, perfil, tarefas):
    """Conversa do chat: devolve mensagem, perfil identificado e cronograma."""
    if not chave_configurada():
        return resposta_modo_demo()
    dados = chamar_ia(PROMPT_SISTEMA, montar_contexto(mensagem, perfil, tarefas))
    return padronizar_resposta(dados)


# =====================================================================
# MATERIAL DE ESTUDO: resumo + pontos-chave + questões de uma tarefa
# =====================================================================
PROMPT_ESTUDO = """Você é a Educa-Med, assistente de estudos para estudantes de medicina.
Crie um material de estudo curto sobre o tema pedido, no nível de graduação em medicina.

Regras:
- Conteúdo conceitual e educacional. Não faça condutas para pacientes reais nem prescrições.
- Questões de múltipla escolha estilo prova, com 4 alternativas e apenas UMA correta.
- Seja preciso. Se houver controvérsia, diga isso no resumo.
- Lembre o estudante de conferir o conteúdo em fontes confiáveis.

Responda SOMENTE em JSON, neste formato:
{
  "resumo": "explicação didática do tema em 1 a 3 parágrafos curtos",
  "pontos_chave": ["ponto 1", "ponto 2", "ponto 3"],
  "questoes": [
    {"pergunta": "...", "alternativas": ["A", "B", "C", "D"], "correta": 0, "explicacao": "por que essa é a correta"}
  ],
  "onde_conferir": "tipo de fonte confiável para checar esse conteúdo"
}
O campo "correta" é o índice (0 a 3) da alternativa certa. Gere de 3 a 5 questões."""


def padronizar_material(dados):
    """Confere o material da IA e descarta questões mal formatadas."""
    material = {
        "resumo": dados.get("resumo") if isinstance(dados.get("resumo"), str) else dados.get("mensagem", ""),
        "onde_conferir": dados.get("onde_conferir") if isinstance(dados.get("onde_conferir"), str) else "",
        "pontos_chave": [],
        "questoes": [],
    }

    for ponto in dados.get("pontos_chave") or []:
        if isinstance(ponto, str) and ponto.strip():
            material["pontos_chave"].append(ponto.strip())

    for questao in dados.get("questoes") or []:
        if not isinstance(questao, dict):
            continue
        alternativas = questao.get("alternativas")
        correta = questao.get("correta")
        if (isinstance(questao.get("pergunta"), str)
                and isinstance(alternativas, list) and len(alternativas) >= 2
                and isinstance(correta, int) and 0 <= correta < len(alternativas)):
            material["questoes"].append({
                "pergunta": questao["pergunta"],
                "alternativas": [str(a) for a in alternativas],
                "correta": correta,
                "explicacao": str(questao.get("explicacao", "")),
            })

    return material


def material_modo_demo(atividade):
    return padronizar_material({
        "resumo": (
            f"[Modo demonstração] Aqui viria um resumo sobre \"{atividade}\" gerado pela IA. "
            "Configure a GROQ_API_KEY para gerar o conteúdo de verdade."
        ),
        "pontos_chave": ["Exemplo de ponto-chave 1", "Exemplo de ponto-chave 2"],
        "questoes": [{
            "pergunta": "Qual é a atitude correta diante de uma resposta gerada por IA?",
            "alternativas": [
                "Aceitar, porque IA não erra",
                "Conferir em livro-texto, aula ou diretriz oficial",
                "Ignorar qualquer resposta de IA",
                "Perguntar de novo até a IA concordar comigo",
            ],
            "correta": 1,
            "explicacao": "A IA é apoio: ela pode errar, então a informação deve ser checada em fontes confiáveis.",
        }],
        "onde_conferir": "Livro-texto da disciplina",
    })


def gerar_material_estudo(atividade, perfil):
    """Gera resumo, pontos-chave e questões para uma tarefa do cronograma."""
    if not chave_configurada():
        return material_modo_demo(atividade)

    texto_usuario = (
        f"Tema da tarefa: {atividade}\n"
        f"Área do estudante: {perfil.get('area') or 'não informada'}\n"
        f"Método de estudo preferido: {perfil.get('metodo_estudo') or 'não informado'}"
    )
    return padronizar_material(chamar_ia(PROMPT_ESTUDO, texto_usuario))
