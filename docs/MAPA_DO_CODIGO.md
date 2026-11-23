# Mapa do código — roteiro para a apresentação

Onde cada conteúdo da disciplina aparece no Educa-Med. Use como roteiro: abra o arquivo, mostre a função, explique em uma frase.

## Conteúdos de Python

| Conteúdo | Arquivo → função | O que mostrar |
|---|---|---|
| **Variáveis e Operadores** | `services/texto.py` → `formatar_minutos` | `//` e `%` convertem 90 min em "1h30" |
| | `services/respostas.py` → `calcular_senso_critico` | `verificadas / total * 100` = taxa de checagem |
| **Estruturas Condicionais** | `services/seguranca.py` → `validar_mensagem` | `if / elif` para mensagem vazia ou longa demais |
| | `main.py` → `chat` | `if e_pedido_clinico(...)` bloqueia caso clínico antes de chegar na IA |
| **Estruturas de Repetição** | `services/seguranca.py` → `e_pedido_clinico` | `for` percorre a lista de termos proibidos |
| | `services/cronograma.py` → `gerar_novo_id` | `for` acha o maior id da lista |
| **Listas e Matrizes** | `services/cronograma.py` → `montar_resumo` | Matriz `[dia, tarefas, concluídas, minutos]`, uma linha por dia; o front desenha o cronograma a partir dela |
| **Strings** | `services/texto.py` → `normalizar_texto`, `converter_duracao_para_minutos` | `lower`, `strip`, `replace`, `split` e percorrer letra por letra |
| **Funções** | todos os `services/` | Cada função faz uma coisa só, com nome que explica o quê |
| **Mapeamento de Arquivos** | `services/arquivos.py` → `ler_json`, `salvar_json` | `open(...)` + `json` salvam tudo em `dados/` (sobrevive a reinício) |
| | `services/ia_service.py` → `padronizar_material` | `for` + `if` descartam questões mal formatadas pela IA |
| **Tratamento de Erros** | `services/arquivos.py` → `ler_json` | `FileNotFoundError` e `JSONDecodeError` |
| | `services/ia_service.py` → `gerar_resposta_ia` | IA fora do ar vira `RuntimeError` → `main.py` responde 503 sem quebrar |
| | `services/texto.py` → `converter_duracao_para_minutos` | `ValueError` quando a duração não é um número ("dia todo") |

## O artefato: CRUD

`services/cronograma.py` + rotas em `main.py`:

| Operação | Função | Rota |
|---|---|---|
| **C**reate | `criar_tarefa` | `POST /tarefas` |
| **R**ead | `buscar_tarefa` | `GET /tarefas/{id}` |
| **U**pdate | `atualizar_tarefa` | `PUT /tarefas/{id}` |
| **D**elete | `remover_tarefa` | `DELETE /tarefas/{id}` |
| **L**ist | `listar_tarefas` | `GET /tarefas` |

Teste ao vivo: **http://localhost:8000/docs** (o FastAPI gera essa tela para testar cada rota).

## Letramento em IA: onde está no código

| Princípio | Como o sistema aplica |
|---|---|
| **Compreender** (sabe que é IA e conhece seus limites) | Aviso fixo no chat + selo "IA" nas tarefas criadas pela IA (`origem: "ia"`) |
| **Criticar** (confere antes de confiar) | Questões geradas por IA também podem estar erradas: o material de estudo tem o mesmo botão *Achei um erro*.  Toda resposta traz "Onde conferir" e botões *Conferi na fonte* / *Achei um erro* (`services/respostas.py`). O painel "Seu senso crítico" mostra a % de respostas checadas |
| **Usar com apoio** (não substitui professor) | `services/seguranca.py` bloqueia caso clínico, diagnóstico e medicação antes de chamar a IA; o prompt reforça o limite |

## Roteiro de demo (4 min)

1. Clicar em **"Dificuldade em farmacologia"** → a IA monta o cronograma na coluna da direita.
2. Marcar uma tarefa como feita, editar outra e adicionar uma manualmente (o CRUD ao vivo).
3. Em uma tarefa, clicar em **"Estudar com IA →"** → resumo, pontos-chave e questões com correção. Mostrar que questão gerada por IA também pode errar: botão *Achei um erro*.
4. Clicar em **"Conferi na fonte"** em uma resposta → a % de senso crítico sobe.
5. Clicar em **"Testar limite: caso clínico"** → a mensagem é bloqueada antes de chegar na IA.
6. Reiniciar o servidor e recarregar a página → tudo continua lá (arquivos JSON).

> Sem internet ou sem `GROQ_API_KEY`, o sistema entra em **modo demonstração** e devolve um cronograma de exemplo.
