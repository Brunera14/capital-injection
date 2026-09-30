let carteira = [];

const APORTAR = "APORTAR";

function moeda(valorTexto) {
  if (valorTexto === undefined || valorTexto === null) return "-";
  const numero = Number(valorTexto);
  return "R$ " + numero.toFixed(2).replace(".", ",");
}

function percentual(valorTexto) {
  if (valorTexto === undefined || valorTexto === null) return "-";
  const numero = Number(valorTexto) * 100;
  return numero.toFixed(2).replace(".", ",") + "%";
}

async function carregarCarteira() {
  const resp = await fetch("/api/carteira");
  carteira = await resp.json();
}

async function carregarHistorico() {
  const resp = await fetch("/api/historico");
  const historico = await resp.json();
  renderHistorico(historico);
}

function renderHistorico(historico) {
  const corpo = document.getElementById("corpo-historico");
  corpo.innerHTML = "";
  for (const h of historico) {
    const linha = document.createElement("tr");
    linha.innerHTML =
      "<td>" + h.data + "</td>" +
      "<td>" + h.ticker + "</td>" +
      "<td>" + h.qtd_comprada + "</td>" +
      "<td>" + moeda(h.preco) + "</td>" +
      "<td>" + moeda(h.valor_investido) + "</td>";
    corpo.appendChild(linha);
  }
}

function renderRanking(ranking) {
  const lista = document.getElementById("lista-ranking");
  lista.innerHTML = "";
  if (ranking.length === 0) {
    lista.innerHTML = "<li>Nenhum ativo precisa de aporte no momento.</li>";
    return;
  }
  for (const r of ranking) {
    const item = document.createElement("li");
    item.textContent = r.ticker + ": " + moeda(r.aporte_recomendado);
    lista.appendChild(item);
  }
}

function renderTotais(totais) {
  document.getElementById("total-atual").textContent = moeda(totais.total_atual);
  document.getElementById("total-pos").textContent = moeda(totais.total_pos);
  document.getElementById("total-valor-atual").textContent = moeda(totais.soma_valor_atual);
  document.getElementById("total-pct-atual").textContent = "100,00%";
  document.getElementById("total-valor-alvo").textContent = moeda(totais.soma_valor_alvo);
  document.getElementById("total-necessidade").textContent = moeda(totais.soma_necessidade);
  document.getElementById("total-aporte-recomendado").textContent = moeda(totais.soma_aporte_recomendado);
}

function limparTotais() {
  document.getElementById("total-valor-atual").textContent = "-";
  document.getElementById("total-pct-atual").textContent = "-";
  document.getElementById("total-valor-alvo").textContent = "-";
  document.getElementById("total-necessidade").textContent = "-";
  document.getElementById("total-aporte-recomendado").textContent = "-";
}

function renderCarteira(resultados) {
  const corpo = document.getElementById("corpo-carteira");
  corpo.innerHTML = "";

  for (const a of carteira) {
    const r = resultados ? resultados.find((x) => x.ticker === a.ticker) : null;
    const linha = document.createElement("tr");

    const statusTexto = r ? (r.status === APORTAR ? "APORTAR" : "NAO APORTAR") : "-";
    const statusClasse = r ? (r.status === APORTAR ? "status-aportar" : "status-nao-aportar") : "";
    const necessidade = r && r.status === APORTAR ? moeda(r.defasagem) : (r ? "" : "-");

    linha.innerHTML =
      "<td>" + a.ticker + "</td>" +
      "<td>" + a.tipo + "</td>" +
      "<td><input type=\"text\" data-ticker=\"" + a.ticker + "\" data-campo=\"qtd\" value=\"" + a.qtd + "\"></td>" +
      "<td><input type=\"text\" data-ticker=\"" + a.ticker + "\" data-campo=\"pct_alvo\" value=\"" + (Number(a.pct_alvo) * 100) + "\"></td>" +
      "<td><input type=\"text\" data-ticker=\"" + a.ticker + "\" data-campo=\"preco_atual\" value=\"" + a.preco_atual + "\"></td>" +
      "<td>" + (r ? moeda(r.valor_atual) : "-") + "</td>" +
      "<td>" + (r ? percentual(r.pct_atual) : "-") + "</td>" +
      "<td>" + (r ? moeda(r.valor_alvo) : "-") + "</td>" +
      "<td>" + necessidade + "</td>" +
      "<td>" + (r ? moeda(r.aporte_recomendado) : "-") + "</td>" +
      "<td>" + (r ? r.qtd_comprar : "-") + "</td>" +
      "<td class=\"" + statusClasse + "\">" + statusTexto + "</td>" +
      "<td><button class=\"btn-remover\" data-ticker=\"" + a.ticker + "\">Remover</button></td>";

    corpo.appendChild(linha);
  }
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
    renderRanking([]);
    limparTotais();
    return;
  }

  aviso.textContent = "";
  renderCarteira(dados.resultados);
  renderRanking(dados.ranking);
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
    alert(dados.erro);
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
    tipo: dados.get("tipo"),
    qtd: dados.get("qtd"),
    preco_atual: dados.get("preco_atual"),
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

document.getElementById("btn-calcular").addEventListener("click", recalcular);
document.getElementById("btn-consolidar").addEventListener("click", consolidar);
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
