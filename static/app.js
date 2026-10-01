let carteira = [];

const APORTAR = "APORTAR";

function moeda(valorTexto) {
  if (valorTexto === undefined || valorTexto === null) return "-";
  return Number(valorTexto).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

// Converte a fracao guardada (0.28) em percentual para mostrar (28), sem sujeira de casas decimais.
function pctParaTela(fracaoTexto) {
  return Number((Number(fracaoTexto) * 100).toFixed(2));
}

function percentual(valorTexto) {
  if (valorTexto === undefined || valorTexto === null) return "-";
  const numero = Number(valorTexto) * 100;
  return numero.toFixed(1).replace(".", ",") + "%";
}

async function carregarCarteira() {
  const resp = await fetch("/api/carteira");
  carteira = await resp.json();
}

let historicoLinhas = [];

async function carregarHistorico() {
  const resp = await fetch("/api/historico");
  const dados = await resp.json();
  historicoLinhas = dados.linhas;
  document.getElementById("btn-desfazer").disabled = !dados.pode_desfazer;
  document.getElementById("btn-refazer").disabled = !dados.pode_refazer;
  renderHistorico();
}

function campoHistorico(campo, valor) {
  return "<td><input type=\"text\" data-campo=\"" + campo + "\" value=\"" + valor + "\"></td>";
}

function linhaEdicaoHistorico(h) {
  const linha = document.createElement("tr");
  linha.dataset.id = h ? h.id : "";
  linha.dataset.edicao = "1";
  linha.innerHTML =
    campoHistorico("data", h ? h.data : "") +
    campoHistorico("ticker", h ? h.ticker : "") +
    campoHistorico("qtd_comprada", h ? h.qtd_comprada : "") +
    campoHistorico("preco", h ? h.preco : "") +
    "<td class=\"vazio\">-</td>" +
    "<td class=\"col-acoes\"><button data-acao=\"salvar\">Salvar</button>" +
    "<button data-acao=\"cancelar\">Cancelar</button></td>";
  return linha;
}

function renderHistorico() {
  const corpo = document.getElementById("corpo-historico");
  corpo.innerHTML = "";

  // Linhas gravadas no mesmo momento pertencem ao mesmo aporte.
  const blocos = [];
  for (const h of historicoLinhas) {
    let bloco = blocos.find((b) => b.data === h.data);
    if (!bloco) {
      bloco = { data: h.data, linhas: [], total: 0 };
      blocos.push(bloco);
    }
    bloco.linhas.push(h);
    bloco.total += Number(h.valor_investido);
  }

  for (const b of blocos) {
    const cabecalho = document.createElement("tr");
    cabecalho.className = "cabecalho-bloco";
    cabecalho.dataset.data = b.data;
    cabecalho.innerHTML =
      "<td colspan=\"5\">Aporte de " + b.data + " (total " + moeda(b.total) + ")</td>" +
      "<td class=\"col-acoes\"><button data-acao=\"excluir-bloco\">Excluir bloco</button></td>";
    corpo.appendChild(cabecalho);

    for (const h of b.linhas) {
      const linha = document.createElement("tr");
      linha.dataset.id = h.id;
      linha.innerHTML =
        "<td>" + h.data + "</td>" +
        "<td>" + h.ticker + "</td>" +
        "<td>" + h.qtd_comprada + "</td>" +
        "<td>" + moeda(h.preco) + "</td>" +
        "<td>" + moeda(h.valor_investido) + "</td>" +
        "<td class=\"col-acoes\"><button data-acao=\"editar\">Editar</button>" +
        "<button data-acao=\"excluir\">Excluir</button></td>";
      corpo.appendChild(linha);
    }
  }
}

async function enviarHistorico(metodo, url, corpo) {
  const opcoes = { method: metodo };
  if (corpo) {
    opcoes.headers = { "Content-Type": "application/json" };
    opcoes.body = JSON.stringify(corpo);
  }
  const resp = await fetch(url, opcoes);
  const dados = await resp.json();
  if (!resp.ok) {
    document.getElementById("aviso-validacao").textContent = dados.erro;
    return false;
  }
  await carregarCarteira();
  await carregarHistorico();
  await recalcular();
  return true;
}

function lerLinhaEdicao(linha) {
  const valores = {};
  for (const entrada of linha.querySelectorAll("input")) {
    valores[entrada.dataset.campo] = entrada.value;
  }
  return valores;
}

async function acaoHistorico(evento) {
  const botao = evento.target;
  const acao = botao.dataset.acao;
  if (!acao) return;
  const linha = botao.closest("tr");
  const id = linha.dataset.id;

  if (acao === "excluir-bloco") {
    const data = linha.dataset.data;
    if (!confirm("Excluir o aporte inteiro de " + data + "? As quantidades serao tiradas da carteira.")) return;
    await enviarHistorico("POST", "/api/historico/excluir-bloco", { data: data });
    return;
  }

  if (acao === "editar") {
    const h = historicoLinhas.find((x) => String(x.id) === id);
    linha.replaceWith(linhaEdicaoHistorico(h));
  } else if (acao === "cancelar") {
    renderHistorico();
  } else if (acao === "salvar") {
    const valores = lerLinhaEdicao(linha);
    if (id) {
      await enviarHistorico("PUT", "/api/historico/" + id, valores);
    } else {
      await enviarHistorico("POST", "/api/historico", valores);
    }
  } else if (acao === "excluir") {
    if (!confirm("Excluir esta linha? A quantidade sera tirada da carteira.")) return;
    await enviarHistorico("DELETE", "/api/historico/" + id);
  }
}

function renderResultados(resultados) {
  const corpo = document.getElementById("corpo-resultados");
  corpo.innerHTML = "";
  if (!resultados) return;

  // Maior defasagem primeiro; quem nao vai receber aporte fica no fim.
  const ordenados = resultados.slice().sort(
    (a, b) => Number(b.defasagem) - Number(a.defasagem)
  );

  for (const r of ordenados) {
    const aporta = r.status === APORTAR && Number(r.aporte_recomendado) > 0;
    const linha = document.createElement("tr");
    linha.innerHTML =
      "<td>" + r.ticker + "</td>" +
      "<td>" + (aporta ? moeda(r.aporte_recomendado) : "-") + "</td>" +
      "<td>" + (aporta ? r.qtd_comprar : "-") + "</td>" +
      "<td>" + (aporta ? moeda(r.sobra) : "-") + "</td>";
    corpo.appendChild(linha);
  }
}

function renderTotais(totais) {
  document.getElementById("total-aporte-recomendado").textContent = moeda(totais.soma_aporte_recomendado);
  document.getElementById("total-sobra").textContent = moeda(totais.soma_sobra);
  document.getElementById("total-pct-atual").textContent = "100,0%";
}

function limparTotais() {
  document.getElementById("total-aporte-recomendado").textContent = "-";
  document.getElementById("total-sobra").textContent = "-";
  document.getElementById("total-pct-atual").textContent = "-";
}

function renderTotalPctAlvo() {
  const totalCarteira = carteira.reduce((acc, a) => acc + Number(a.qtd) * Number(a.preco_atual), 0);
  document.getElementById("total-valor-carteira").textContent = moeda(totalCarteira);
  const soma = carteira.reduce((acc, a) => acc + pctParaTela(a.pct_alvo), 0);
  const celula = document.getElementById("total-pct-alvo");
  celula.textContent = soma.toFixed(1).replace(".", ",") + "%";
  celula.classList.toggle("total-errado", Math.abs(soma - 100) > 0.001);
}

function renderCarteira(resultados) {
  const corpo = document.getElementById("corpo-carteira");
  corpo.innerHTML = "";

  for (const a of carteira) {
    const r = resultados ? resultados.find((x) => x.ticker === a.ticker) : null;
    const linha = document.createElement("tr");

    linha.innerHTML =
      "<td>" + a.ticker + "</td>" +
      "<td>" + moeda(a.preco_atual) + "</td>" +
      "<td class=\"col-qtd\"><input type=\"text\" data-ticker=\"" + a.ticker + "\" data-campo=\"qtd\" value=\"" + a.qtd + "\"></td>" +
      "<td>" + moeda(Number(a.qtd) * Number(a.preco_atual)) + "</td>" +
      "<td class=\"col-pct\"><input type=\"text\" data-ticker=\"" + a.ticker + "\" data-campo=\"pct_alvo\" value=\"" + pctParaTela(a.pct_alvo) + "\"></td>" +
      "<td>" + (r ? percentual(r.pct_atual) : "-") + "</td>" +
      "<td>" + (r && r.status === APORTAR ? moeda(r.defasagem) : "-") + "</td>" +
      "<td class=\"col-x\"><button class=\"btn-remover\" data-ticker=\"" + a.ticker + "\" title=\"Remover\">x</button></td>";

    corpo.appendChild(linha);
  }
  renderTotalPctAlvo();
}

async function recalcular() {
  const aporte = document.getElementById("input-aporte").value || "0";
  const resp = await fetch("/api/calcular", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ aporte: aporte }),
  });
  const dados = await resp.json();
  const aviso = document.getElementById("aviso-validacao");

  if (!resp.ok) {
    aviso.textContent = dados.erro;
    renderCarteira(null);
    renderResultados(null);
    limparTotais();
    return;
  }

  aviso.textContent = "";
  renderCarteira(dados.resultados);
  renderResultados(dados.resultados);
  renderTotais(dados.totais);
}

async function salvarAtivo(ativo) {
  const resp = await fetch("/api/ativos", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(ativo),
  });
  const dados = await resp.json();
  if (!resp.ok) {
    document.getElementById("aviso-validacao").textContent = dados.erro;
    return false;
  }
  return true;
}

async function editarCampo(ticker, campo, valorTexto) {
  const ativo = carteira.find((a) => a.ticker === ticker);
  if (!ativo) return;

  const atualizado = Object.assign({}, ativo);
  if (campo === "pct_alvo") {
    atualizado.pct_alvo = String(Number(valorTexto) / 100);
  } else {
    atualizado[campo] = valorTexto;
  }

  const ok = await salvarAtivo(atualizado);
  if (!ok) {
    await carregarCarteira();
    await recalcular();
    return;
  }
  await carregarCarteira();
  await recalcular();
}

async function removerAtivo(ticker) {
  if (!confirm("Remover " + ticker + " da carteira?")) return;
  await fetch("/api/ativos/" + encodeURIComponent(ticker), { method: "DELETE" });
  await carregarCarteira();
  await recalcular();
}

async function adicionarAtivo(evento) {
  evento.preventDefault();
  const forma = evento.target;
  const dados = new FormData(forma);

  const ativo = {
    ticker: dados.get("ticker"),
    qtd: dados.get("qtd"),
    pct_alvo: String(Number(dados.get("pct_alvo")) / 100),
  };

  const ok = await salvarAtivo(ativo);
  if (ok) {
    forma.reset();
    await carregarCarteira();
    await recalcular();
  }
}

async function consolidar() {
  if (!confirm("Consolidar o aporte? As quantidades da carteira serao atualizadas.")) return;
  const aporte = document.getElementById("input-aporte").value || "0";
  const resp = await fetch("/api/consolidar", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ aporte: aporte }),
  });
  const dados = await resp.json();
  if (!resp.ok) {
    document.getElementById("aviso-validacao").textContent = dados.erro;
    return;
  }

  alert(dados.mensagem);
  document.getElementById("input-aporte").value = "0";
  await carregarCarteira();
  await carregarHistorico();
  await recalcular();
}

async function atualizarCotacoes() {
  const botao = document.getElementById("btn-atualizar-cotacoes");
  const aviso = document.getElementById("aviso-cotacao");
  botao.disabled = true;
  aviso.textContent = "Buscando cotacoes...";

  const resp = await fetch("/api/cotacoes/atualizar", { method: "POST" });
  const dados = await resp.json();
  botao.disabled = false;

  aviso.textContent = dados.aviso || "";
  if (dados.atualizados && dados.atualizados.length > 0) {
    aviso.textContent += (aviso.textContent ? " " : "") + "Atualizados: " + dados.atualizados.join(", ") + ".";
  }

  await carregarCarteira();
  await recalcular();
}

document.getElementById("corpo-historico").addEventListener("click", acaoHistorico);
document.getElementById("btn-desfazer").addEventListener("click", () => enviarHistorico("POST", "/api/historico/desfazer"));
document.getElementById("btn-refazer").addEventListener("click", () => enviarHistorico("POST", "/api/historico/refazer"));
document.getElementById("btn-adicionar-historico").addEventListener("click", () => {
  const corpo = document.getElementById("corpo-historico");
  if (corpo.querySelector("tr[data-edicao]")) return;
  corpo.appendChild(linhaEdicaoHistorico(null));
});
document.getElementById("btn-calcular").addEventListener("click", recalcular);
document.getElementById("btn-consolidar").addEventListener("click", consolidar);
document.getElementById("btn-atualizar-cotacoes").addEventListener("click", atualizarCotacoes);
document.getElementById("form-ativo").addEventListener("submit", adicionarAtivo);
document.getElementById("input-aporte").addEventListener("change", recalcular);

document.getElementById("corpo-carteira").addEventListener("change", (evento) => {
  const alvo = evento.target;
  if (alvo.tagName === "INPUT") {
    editarCampo(alvo.dataset.ticker, alvo.dataset.campo, alvo.value);
  }
});

document.getElementById("corpo-carteira").addEventListener("click", (evento) => {
  const alvo = evento.target;
  if (alvo.classList.contains("btn-remover")) {
    removerAtivo(alvo.dataset.ticker);
  }
});

(async function iniciar() {
  await carregarCarteira();
  await carregarHistorico();
  await recalcular();
})();
