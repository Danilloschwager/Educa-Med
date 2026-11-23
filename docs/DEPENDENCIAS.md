# Dependências para usar a IA do Educa-Med

Este documento reúne tudo que é necessário para colocar a parte de
Inteligência Artificial do Educa-Med para funcionar — separado do
`README.md`, que cobre o projeto como um todo.

## 1. Chave de API da Groq

A IA do Educa-Med é servida pela **Groq**, que hospeda o modelo de
linguagem usado nas respostas.

- Crie uma conta gratuita em https://console.groq.com
- Gere uma chave de API (API Key) no painel da Groq
- Copie `.env.example` para `.env` e cole a chave na variável
  `GROQ_API_KEY`:
  ```
  GROQ_API_KEY=sua_chave_aqui
  ```
- Sem essa chave, o sistema roda em **modo demonstração**: devolve um
  cronograma de exemplo, sem chamar a IA.

## 2. Modelo de IA utilizado

- **Modelo:** `openai/gpt-oss-20b`, definido em
  `services/ia_service.py` na constante `MODELO_IA`.
- É um modelo rápido e leve, adequado para conversas em tempo real como
  a do chat. Para respostas mais elaboradas (ao custo de mais latência),
  essa constante pode ser trocada por outro modelo disponível na Groq.

## 3. Bibliotecas Python necessárias

Instale tudo de uma vez com:
```
pip install -r requirements.txt
```

| Biblioteca | Papel na parte de IA |
|---|---|
| `groq` | Cliente oficial usado em `services/ia_service.py` para enviar o prompt e receber a resposta do modelo |
| `python-dotenv` | Lê a `GROQ_API_KEY` do arquivo `.env` e a disponibiliza para o `os.getenv` |
| `fastapi` | Expõe a rota `/chat` que recebe a mensagem do estudante e aciona a IA |
| `pydantic` | Valida o formato da mensagem recebida antes de repassar para a IA |
| `uvicorn` | Servidor que mantém a API rodando |

## 4. Formato de resposta esperado da IA

O prompt do sistema (em `services/ia_service.py`) instrui o modelo a
responder **somente em JSON** (o modo `json_object` da Groq também é ativado), sempre com estas chaves:
```json
{
  "mensagem": "texto para o estudante",
  "area": "área da medicina identificada",
  "rotina": "tempo disponível informado",
  "metodo_estudo": "método de estudo preferido",
  "onde_conferir": "tipo de fonte confiável para checar a resposta",
  "cronograma": [
    {"dia": "Segunda-feira", "atividade": "...", "duracao": "1h"}
  ]
}
```
Se a IA responder algo fora desse formato (texto livre, por exemplo), o
código em `gerar_resposta_ia` trata o erro e devolve a mensagem mesmo
assim, com os outros campos vazios (`padronizar_resposta`) — a aplicação
não quebra por causa disso.

## 5. Erros comuns

| Sintoma | Causa provável |
|---|---|
| "Não consegui falar com a IA agora" (erro 503) | `GROQ_API_KEY` inválida, sem internet ou Groq fora do ar |
| Resposta começa com "[Modo demonstração]" | `GROQ_API_KEY` não configurada no `.env` |
| Cronograma nunca aparece | A IA ainda não recebeu informações suficientes (área, rotina e método de estudo) — continue a conversa |
