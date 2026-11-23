<h1>Educa-Med</h1>

Assistente de estudos com IA para **estudantes de Medicina**: monta cronogramas personalizados (rotina, dificuldades, método de estudo) e incentiva o uso **crítico, seguro e responsável** da IA.

> Evolução do *Humanizy Med*, que originalmente era um chatbot de orientação inicial em saúde.

---

## 🧩 O desafio

Estudantes de Medicina têm rotina intensa e muito conteúdo, e usam cada vez mais IA nos estudos. A facilidade de obter respostas rápidas leva muitos a aceitar o que a IA diz sem verificar fontes ou entender suas limitações — o que, na Medicina, é especialmente arriscado.

O desafio é usar a IA como **apoio** ao aprendizado, e não como substituta do próprio conhecimento.

## 💡 A solução

- **Organiza:** cria e adapta um cronograma de estudos por dia, que o aluno pode editar (CRUD).
- **Ensina:** em cada tarefa, "Estudar com IA" gera resumo, pontos-chave e questões de múltipla escolha com correção.
- **Limita:** uso exclusivamente educacional. Casos clínicos reais, diagnósticos e medicações são bloqueados antes de chegar na IA.
- **Ensina a checar:** cada resposta mostra *onde conferir* e o aluno marca se conferiu ou se achou erro. Um painel mostra a % de respostas checadas.
- **É transparente:** tarefas sugeridas pela IA ficam marcadas com o selo "IA".

---

## 🏗️ Arquitetura em 3 camadas

```
┌──────────────────────────────┐
│ 1. Apresentação               │  frontend/  (index.html, estilo.css, app.js)
└──────────────┬───────────────┘
               │ HTTP (fetch)
┌──────────────▼───────────────┐
│ 2. Aplicação (rotas da API)   │  main.py  (FastAPI)
└──────────────┬───────────────┘
               │ chamada de função
┌──────────────▼───────────────┐
│ 3. Regras, dados e IA         │  services/
│   seguranca · cronograma ·    │  dados/*.json
│   respostas · perfil · IA     │  Groq API
└──────────────────────────────┘
```

Cada arquivo de `services/` tem uma responsabilidade só — e cada um destaca um conteúdo de Python. Veja **[`docs/MAPA_DO_CODIGO.md`](docs/MAPA_DO_CODIGO.md)** para o mapa conteúdo → arquivo → função e o roteiro da demo.

## 📁 Estrutura de pastas

```
Educa-Med/
├── main.py                  # Rotas da API (chat + CRUD + checagem)
├── services/
│   ├── arquivos.py          # Ler/salvar JSON          (Arquivos, Erros)
│   ├── texto.py             # Tratar textos e durações (Strings, Operadores)
│   ├── seguranca.py         # Limites de uso           (Condicionais, Repetição)
│   ├── cronograma.py        # CRUD das tarefas         (Listas, Matrizes)
│   ├── respostas.py         # Checagem das respostas   (Letramento em IA)
│   ├── perfil.py            # Perfil do aluno
│   └── ia_service.py        # Integração com a Groq    (Funções, Erros)
├── frontend/
│   ├── index.html
│   ├── estilo.css
│   └── app.js
├── dados/                   # Criada automaticamente ao rodar
├── docs/
│   ├── MAPA_DO_CODIGO.md
│   └── DEPENDENCIAS.md
├── requirements.txt
└── .env.example
```

## 🔌 Rotas da API

| Método | Rota | Função |
|---|---|---|
| POST | `/chat` | Conversa com a IA |
| GET / POST | `/tarefas` | Listar / criar tarefas |
| GET / PUT / DELETE | `/tarefas/{id}` | Ler / editar / remover tarefa |
| POST | `/tarefas/{id}/estudar` | Gera resumo, pontos-chave e questões da tarefa |
| GET | `/respostas` | Histórico + painel de senso crítico |
| PUT | `/respostas/{id}` | Marcar resposta como `conferida`, `com_erro` ou `pendente` |
| DELETE | `/sessao` | Apagar tudo e recomeçar |

Documentação interativa: **http://localhost:8000/docs**

---

## 🚀 Tecnologias

Python 3.11+ · FastAPI · Uvicorn · Groq API (`openai/gpt-oss-20b`) · python-dotenv · HTML, CSS e JavaScript puros

## 📦 Como rodar

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env          # cole sua GROQ_API_KEY (grátis em https://console.groq.com)

uvicorn main:app --reload
```

Acesse **http://localhost:8000**. Sem `GROQ_API_KEY` o sistema roda em **modo demonstração**, com um cronograma de exemplo.

Detalhes da IA e erros comuns: [`docs/DEPENDENCIAS.md`](docs/DEPENDENCIAS.md).

---

## 📄 Licença

MIT.
