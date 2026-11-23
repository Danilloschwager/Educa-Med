// =====================================================================
// Educa-Med — Camada de Apresentação
// Conversa com a API (main.py) via fetch e desenha a tela.
// =====================================================================

// ---------- Elementos da página ----------
const janelaMensagens = document.getElementById("janela-mensagens");
const formChat = document.getElementById("form-chat");
const campoMensagem = document.getElementById("campo-mensagem");
const botaoEnviar = document.getElementById("botao-enviar");
const sugestoes = document.getElementById("sugestoes");
const listaTarefas = document.getElementById("lista-tarefas");
const formTarefa = document.getElementById("form-tarefa");
const botaoRecomecar = document.getElementById("botao-recomecar");

let tarefaEmEdicao = null; // id da tarefa que está sendo editada

const BOAS_VINDAS =
  "Olá! Sou a Educa-Med, uma IA que ajuda a organizar seus estudos.\n\n" +
  "Me conte: qual área da medicina você quer estudar, quanto tempo tem por dia e como prefere estudar. " +
  "Com isso eu monto um cronograma — e você pode editar tudo ao lado.";


// ---------- Utilidades ----------
function escapeHtml(texto) {
  const div = document.createElement("div");
  div.textContent = texto ?? "";
  return div.innerHTML;
}

async function chamarApi(metodo, url, corpo) {
  const opcoes = { method: metodo, headers: { "Content-Type": "application/json" } };
  if (corpo) opcoes.body = JSON.stringify(corpo);

  const resposta = await fetch(url, opcoes);
  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.detail || "Algo deu errado no servidor.");
  }
  return resposta.status === 204 ? null : resposta.json();
}

function rolarParaBaixo() {
  janelaMensagens.scrollTop = janelaMensagens.scrollHeight;
}


// =====================================================================
// CHAT
// =====================================================================
function adicionarMensagem(tipo, texto) {
  const div = document.createElement("div");
  div.className = `message ${tipo}`;
  div.innerHTML = escapeHtml(texto).replace(/\n/g, "<br>");
  janelaMensagens.appendChild(div);
  rolarParaBaixo();
  return div;
}

function adicionarRespostaIA(registro) {
  const div = adicionarMensagem("ai", registro.resposta);
  adicionarRodapeChecagem(div, registro);
}

// Material de estudo: resumo + pontos-chave + questões com correção
function adicionarMaterialEstudo(registro) {
  const m = registro.material;
  const div = document.createElement("div");
  div.className = "message ai material";

  const pontos = m.pontos_chave.length
    ? `<h4>Pontos-chave</h4><ul>${m.pontos_chave.map((p) => `<li>${escapeHtml(p)}</li>`).join("")}</ul>`
    : "";

  const questoes = m.questoes.map((q, i) => `
    <div class="questao" data-correta="${q.correta}">
      <p><b>${i + 1}.</b> ${escapeHtml(q.pergunta)}</p>
      ${q.alternativas.map((alt, j) => `
        <button class="alternativa" data-indice="${j}">${"ABCDEFGH"[j]}) ${escapeHtml(alt)}</button>`).join("")}
      <div class="explicacao" hidden>${escapeHtml(q.explicacao)}</div>
    </div>`).join("");

  // No chat, a IA também manda uma mensagem antes do material
  const intro = registro.resposta && registro.resposta !== m.resumo
    ? `<p>${escapeHtml(registro.resposta).replace(/\n/g, "<br>")}</p>` : "";

  div.innerHTML = `
    ${intro}
    <div class="material-titulo">Material de estudo · gerado por IA</div>
    <p>${escapeHtml(m.resumo).replace(/\n/g, "<br>")}</p>
    ${pontos}
    ${m.questoes.length ? `<h4>Questões <span class="placar">0 de ${m.questoes.length} acertos</span></h4>${questoes}` : ""}
  `;

  // Corrige a questão quando o aluno clica numa alternativa
  let acertos = 0;
  div.querySelectorAll(".questao").forEach((questao) => {
    questao.querySelectorAll(".alternativa").forEach((botao) => {
      botao.addEventListener("click", () => {
        const correta = Number(questao.dataset.correta);
        const escolhida = Number(botao.dataset.indice);
        questao.querySelectorAll(".alternativa").forEach((b) => {
          b.disabled = true;
          if (Number(b.dataset.indice) === correta) b.classList.add("certa");
        });
        if (escolhida === correta) {
          acertos++;
        } else {
          botao.classList.add("errada");
        }
        questao.querySelector(".explicacao").hidden = false;
        div.querySelector(".placar").textContent = `${acertos} de ${m.questoes.length} acertos`;
      });
    });
  });

  janelaMensagens.appendChild(div);
  adicionarRodapeChecagem(div, { ...registro, onde_conferir: m.onde_conferir });
  div.scrollIntoView({ block: "start" }); // mostra o material desde o início
}

function adicionarRodapeChecagem(div, registro) {
  if (registro.onde_conferir) {
    div.insertAdjacentHTML("beforeend",
      `<div class="onde-conferir"><b>Onde conferir:</b> ${escapeHtml(registro.onde_conferir)}</div>`);
  }

  // Rodapé de checagem: o aluno avalia a resposta da IA
  const checagem = document.createElement("div");
  checagem.className = "checagem";
  checagem.innerHTML = `
    <span>Você checou essa resposta?</span>
    <button data-status="conferida">✓ Conferi na fonte</button>
    <button data-status="com_erro">⚠ Achei um erro</button>
  `;
  checagem.querySelectorAll("button").forEach((botao) => {
    botao.addEventListener("click", () => marcarChecagem(registro.id, botao.dataset.status, checagem));
  });
  div.appendChild(checagem);
  pintarChecagem(checagem, registro.status);
  rolarParaBaixo();
}

function mostrarDigitando() {
  const div = document.createElement("div");
  div.className = "message ai digitando";
  div.setAttribute("aria-label", "Educa-Med está digitando");
  div.innerHTML = "<i></i><i></i><i></i>";
  janelaMensagens.appendChild(div);
  rolarParaBaixo();
  return div;
}

async function enviarMensagem(texto) {
  texto = texto.trim();
  if (!texto) return;

  sugestoes.hidden = true;
  adicionarMensagem("user", texto);
  campoMensagem.value = "";
  botaoEnviar.disabled = true;
  const digitando = mostrarDigitando();

  try {
    const dados = await chamarApi("POST", "/chat", { message: texto });
    digitando.remove();

    if (dados.bloqueada) {
      adicionarMensagem("bloqueada", dados.mensagem);
      return;
    }

    const registro = {
      id: dados.id_resposta,
      resposta: dados.mensagem || "Não entendi, pode reformular?",
      onde_conferir: dados.onde_conferir,
      status: "pendente",
      material: dados.material,
    };
    if (registro.material) adicionarMaterialEstudo(registro);
    else adicionarRespostaIA(registro);

    await carregarSensoCritico();
    if (dados.cronograma_atualizado) await carregarTarefas();
  } catch (erro) {
    digitando.remove();
    adicionarMensagem("erro", erro.message === "Failed to fetch"
      ? "Não consegui me conectar ao servidor. Verifique se o backend está rodando."
      : erro.message);
  } finally {
    botaoEnviar.disabled = false;
    campoMensagem.focus();
  }
}

formChat.addEventListener("submit", (e) => {
  e.preventDefault();
  enviarMensagem(campoMensagem.value);
});

campoMensagem.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    enviarMensagem(campoMensagem.value);
  }
});

sugestoes.querySelectorAll("button").forEach((botao) => {
  botao.addEventListener("click", () => enviarMensagem(botao.dataset.texto));
});


// =====================================================================
// LETRAMENTO EM IA: checagem das respostas + painel de senso crítico
// =====================================================================
function pintarChecagem(checagem, status) {
  checagem.querySelectorAll("button").forEach((botao) => {
    const ativo = botao.dataset.status === status;
    botao.className = ativo ? `ativo-${status}` : "";
    botao.setAttribute("aria-pressed", ativo);
  });
}

async function marcarChecagem(idResposta, status, checagem) {
  // Clicar de novo no botão ativo volta para "pendente"
  const atual = checagem.querySelector("[aria-pressed='true']");
  const novoStatus = atual && atual.dataset.status === status ? "pendente" : status;

  try {
    await chamarApi("PUT", `/respostas/${idResposta}`, { status: novoStatus });
    pintarChecagem(checagem, novoStatus);
    await carregarSensoCritico();
  } catch (erro) {
    adicionarMensagem("erro", erro.message);
  }
}

async function carregarSensoCritico() {
  const dados = await chamarApi("GET", "/respostas");
  const s = dados.senso_critico;
  document.getElementById("taxa-verificacao").textContent = `${s.taxa_verificacao}%`;
  document.getElementById("num-conferidas").textContent = s.conferidas;
  document.getElementById("num-erros").textContent = s.com_erro;
  document.getElementById("num-pendentes").textContent = s.pendentes;
  return dados.respostas;
}


// =====================================================================
// CRONOGRAMA (CRUD)
// =====================================================================
async function carregarTarefas() {
  const dados = await chamarApi("GET", "/tarefas");
  desenharTarefas(dados);
}

function desenharTarefas({ area, tarefas, resumo }) {
  document.getElementById("area-atual").textContent = area || "";

  const blocoProgresso = document.getElementById("bloco-progresso");
  blocoProgresso.hidden = tarefas.length === 0;
  document.getElementById("texto-progresso").textContent =
    `${resumo.total_concluidas} de ${resumo.total_tarefas} tarefas · ${resumo.progresso}%`;
  document.getElementById("tempo-total").textContent = `${resumo.tempo_total} no total`;
  document.getElementById("barra-progresso").style.width = `${resumo.progresso}%`;

  if (tarefas.length === 0) {
    listaTarefas.innerHTML = `<p class="vazio">Converse com a Educa-Med ou adicione tarefas abaixo — seu cronograma aparece aqui.</p>`;
    return;
  }

  // resumo.por_dia é a MATRIZ do backend: [dia, total, concluidas, tempo]
  listaTarefas.innerHTML = resumo.por_dia.map(([dia, , , tempo]) => {
    const tarefasDoDia = tarefas.filter((t) => t.dia === dia);
    return `
      <div class="grupo-dia">
        <div class="grupo-dia-titulo">${escapeHtml(dia)} <small>${escapeHtml(tempo)}</small></div>
        ${tarefasDoDia.map(desenharTarefa).join("")}
      </div>`;
  }).join("");
}

function desenharTarefa(t) {
  if (t.id === tarefaEmEdicao) {
    return `
      <div class="tarefa" data-id="${t.id}">
        <div class="tarefa-edicao">
          <input name="atividade" value="${escapeHtml(t.atividade)}" aria-label="Atividade">
          <div class="linha-form">
            <input name="dia" value="${escapeHtml(t.dia)}" list="dias-semana" aria-label="Dia">
            <input name="duracao" value="${escapeHtml(t.duracao)}" aria-label="Duração">
          </div>
          <div class="tarefa-acoes">
            <button data-acao="cancelar">Cancelar</button>
            <button data-acao="salvar">Salvar</button>
          </div>
        </div>
      </div>`;
  }

  return `
    <div class="tarefa ${t.concluida ? "feita" : ""}" data-id="${t.id}">
      <input type="checkbox" data-acao="concluir" ${t.concluida ? "checked" : ""} aria-label="Marcar como concluída">
      <div class="tarefa-texto">
        <span class="tarefa-nome">${escapeHtml(t.atividade)}</span>
        ${t.origem === "ia" ? `<span class="origem-ia" title="Sugerida pela IA">IA</span>` : ""}
        <small>${escapeHtml(t.duracao)} · <button class="link-estudar" data-acao="estudar">Estudar com IA →</button></small>
      </div>
      <div class="tarefa-acoes">
        <button data-acao="editar" aria-label="Editar">Editar</button>
        <button data-acao="remover" aria-label="Remover">✕</button>
      </div>
    </div>`;
}

// Um único "ouvinte" para todos os botões das tarefas (delegação de eventos)
listaTarefas.addEventListener("click", async (e) => {
  const acao = e.target.dataset.acao;
  if (!acao) return;
  const linha = e.target.closest(".tarefa");
  const id = Number(linha.dataset.id);

  try {
    if (acao === "concluir") {
      await chamarApi("PUT", `/tarefas/${id}`, { concluida: e.target.checked });
    } else if (acao === "editar") {
      tarefaEmEdicao = id;
    } else if (acao === "cancelar") {
      tarefaEmEdicao = null;
    } else if (acao === "salvar") {
      const campos = {};
      linha.querySelectorAll("input").forEach((input) => (campos[input.name] = input.value.trim()));
      await chamarApi("PUT", `/tarefas/${id}`, campos);
      tarefaEmEdicao = null;
    } else if (acao === "remover") {
      await chamarApi("DELETE", `/tarefas/${id}`);
    } else if (acao === "estudar") {
      await estudarTarefa(id, linha.querySelector(".tarefa-nome").textContent);
      return;
    }
    await carregarTarefas();
  } catch (erro) {
    adicionarMensagem("erro", erro.message);
  }
});

async function estudarTarefa(id, atividade) {
  sugestoes.hidden = true;
  adicionarMensagem("user", `Estudar: ${atividade}`);
  const digitando = mostrarDigitando();
  try {
    const dados = await chamarApi("POST", `/tarefas/${id}/estudar`);
    digitando.remove();
    adicionarMaterialEstudo({ id: dados.id_resposta, status: "pendente", material: dados });
    await carregarSensoCritico();
  } catch (erro) {
    digitando.remove();
    adicionarMensagem("erro", erro.message);
  }
}

formTarefa.addEventListener("submit", async (e) => {
  e.preventDefault();
  const atividade = document.getElementById("nova-atividade");
  const dia = document.getElementById("novo-dia");
  const duracao = document.getElementById("nova-duracao");

  try {
    await chamarApi("POST", "/tarefas", {
      atividade: atividade.value, dia: dia.value, duracao: duracao.value,
    });
    atividade.value = "";
    duracao.value = "";
    await carregarTarefas();
  } catch (erro) {
    adicionarMensagem("erro", erro.message);
  }
});


// =====================================================================
// RECOMEÇAR (pede um segundo clique para confirmar)
// =====================================================================
botaoRecomecar.addEventListener("click", async () => {
  if (!botaoRecomecar.classList.contains("confirmar")) {
    botaoRecomecar.classList.add("confirmar");
    botaoRecomecar.textContent = "Clique de novo para apagar tudo";
    setTimeout(() => {
      botaoRecomecar.classList.remove("confirmar");
      botaoRecomecar.textContent = "Recomeçar do zero";
    }, 3000);
    return;
  }

  await chamarApi("DELETE", "/sessao");
  location.reload();
});


// =====================================================================
// INÍCIO: carrega o que já estava salvo nos arquivos
// =====================================================================
async function iniciar() {
  adicionarMensagem("ai", BOAS_VINDAS);
  try {
    const historico = await carregarSensoCritico();
    historico.forEach((registro) => {
      adicionarMensagem("user", registro.pergunta);
      if (registro.material) adicionarMaterialEstudo(registro);
      else adicionarRespostaIA(registro);
    });
    sugestoes.hidden = historico.length > 0;
    await carregarTarefas();
  } catch (erro) {
    adicionarMensagem("erro", "Não consegui carregar seus dados. O backend está rodando?");
  }
}

iniciar();
