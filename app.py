from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Flask, g, jsonify, render_template, request

import banco
import cotacao
from calculo import calcular_aporte, APORTAR

DB_PATH = "capital_injection.db"

app = Flask(__name__)

CAMPOS_DECIMAL_RESULTADO = {
    "preco", "valor_atual", "pct_atual", "valor_alvo",
    "defasagem", "aporte_recomendado", "qtd_comprar", "valor_investido", "sobra",
}

TIPO_PADRAO = "Acao"


def get_conn():
    if "conn" not in g:
        g.conn = banco.conectar(DB_PATH)
    return g.conn


@app.teardown_appcontext
def fechar_conn(exception=None):
    conn = g.pop("conn", None)
    if conn is not None:
        conn.close()


def ler_decimal(valor, nome):
    try:
        return Decimal(str(valor))
    except (InvalidOperation, TypeError):
        raise ValueError("Valor invalido para " + nome + ": " + str(valor))


def ativo_para_json(a):
    return {
        "ticker": a["ticker"],
        "tipo": a["tipo"],
        "qtd": str(a["qtd"]),
        "preco_atual": str(a["preco_atual"]),
        "pct_alvo": str(a["pct_alvo"]),
        "preco_origem": a["preco_origem"],
        "atualizado_em": a["atualizado_em"],
    }


def resultado_para_json(r):
    return {k: (str(v) if k in CAMPOS_DECIMAL_RESULTADO else v) for k, v in r.items()}


def montar_calculo(aporte_bruto):
    aporte = ler_decimal(aporte_bruto, "aporte")
    ativos = banco.listar_ativos(get_conn())
    ativos_calculo = [
        {
            "ticker": a["ticker"],
            "tipo": a["tipo"],
            "qtd": a["qtd"],
            "preco": a["preco_atual"],
            "pct_alvo": a["pct_alvo"],
        }
        for a in ativos
    ]
    resultados = calcular_aporte(ativos_calculo, aporte)

    total_atual = sum((r["valor_atual"] for r in resultados), Decimal("0"))
    total_pos = total_atual + aporte
    for r in resultados:
        r["pct_atual"] = (r["valor_atual"] / total_atual) if total_atual > 0 else Decimal("0")
        r["sobra"] = r["aporte_recomendado"] - r["valor_investido"]

    totais = {
        "total_atual": str(total_atual),
        "total_pos": str(total_pos),
        "soma_valor_atual": str(total_atual),
        "soma_valor_alvo": str(sum((r["valor_alvo"] for r in resultados), Decimal("0"))),
        "soma_aporte_recomendado": str(sum((r["aporte_recomendado"] for r in resultados), Decimal("0"))),
        "soma_valor_investido": str(sum((r["valor_investido"] for r in resultados), Decimal("0"))),
        "soma_sobra": str(sum((r["sobra"] for r in resultados), Decimal("0"))),
    }

    ranking = sorted(
        (r for r in resultados if r["status"] == APORTAR),
        key=lambda r: r["defasagem"],
        reverse=True,
    )

    return resultados, ranking, totais


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/carteira", methods=["GET"])
def api_carteira():
    ativos = banco.listar_ativos(get_conn())
    return jsonify([ativo_para_json(a) for a in ativos])


@app.route("/api/ativos", methods=["POST"])
def api_salvar_ativo():
    dados = request.get_json(force=True)
    try:
        ticker = str(dados["ticker"]).strip().upper()
        if not ticker:
            raise ValueError("Informe o ticker do ativo.")

        preco_origem = dados.get("preco_origem", "manual")
        atualizado_em = dados.get("atualizado_em")
        if dados.get("preco_atual") in (None, ""):
            # Ativo novo: o preco vem da brapi. Sem cotacao, o ativo nao e salvo.
            try:
                preco = cotacao.buscar_cotacao(ticker)
            except Exception:
                preco = None
            if preco is None:
                raise ValueError("Ticker nao encontrado na brapi: " + ticker + ". Confira se digitou certo.")
            preco_origem = "api"
            atualizado_em = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            preco = ler_decimal(dados["preco_atual"], "Preco Atual")

        ativo = {
            "ticker": ticker,
            "tipo": dados.get("tipo", TIPO_PADRAO),
            "qtd": ler_decimal(dados["qtd"], "Sua Qtd."),
            "preco_atual": preco,
            "pct_alvo": ler_decimal(dados["pct_alvo"], "% Alvo"),
            "preco_origem": preco_origem,
            "atualizado_em": atualizado_em or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
    except (KeyError, ValueError) as erro:
        return jsonify({"erro": str(erro)}), 400

    banco.salvar_ativo(get_conn(), ativo)
    return jsonify(ativo_para_json(ativo))


@app.route("/api/ativos/<ticker>", methods=["DELETE"])
def api_remover_ativo(ticker):
    banco.remover_ativo(get_conn(), ticker)
    return jsonify({"ok": True})


@app.route("/api/calcular", methods=["POST"])
def api_calcular():
    dados = request.get_json(force=True)
    try:
        resultados, ranking, totais = montar_calculo(dados.get("aporte", "0"))
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    return jsonify({
        "resultados": [resultado_para_json(r) for r in resultados],
        "ranking": [resultado_para_json(r) for r in ranking],
        "totais": totais,
    })


@app.route("/api/consolidar", methods=["POST"])
def api_consolidar():
    dados = request.get_json(force=True)
    try:
        resultados, ranking, totais = montar_calculo(dados.get("aporte", "0"))
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400

    try:
        banco.consolidar_aporte(get_conn(), resultados)
    except Exception as erro:
        return jsonify({"erro": "Falha ao consolidar o aporte: " + str(erro)}), 500

    return jsonify({"mensagem": "Aporte consolidado com sucesso."})


@app.route("/api/cotacoes/atualizar", methods=["POST"])
def api_atualizar_cotacoes():
    resultado = cotacao.atualizar_cotacoes(get_conn())
    return jsonify(resultado)


def ler_data(valor):
    texto = str(valor or "").strip()
    if not texto:
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatos = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y")
    for formato in formatos:
        try:
            return datetime.strptime(texto, formato).strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
    raise ValueError("Data invalida. Use dia/mes/ano, por exemplo 15/01/2026.")


def ler_linha_historico(dados):
    ticker = str(dados.get("ticker", "")).strip().upper()
    if not ticker:
        raise ValueError("Informe o ticker.")
    qtd = ler_decimal(dados.get("qtd_comprada"), "Qtd. Comprada")
    preco = ler_decimal(dados.get("preco"), "Preco")
    if qtd <= 0 or preco <= 0:
        raise ValueError("Quantidade e preco precisam ser maiores que zero.")
    return ler_data(dados.get("data")), ticker, qtd, preco


def alterar_historico(funcao, *args):
    try:
        funcao(get_conn(), *args)
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400
    return jsonify({"ok": True})


@app.route("/api/historico", methods=["GET"])
def api_historico():
    historico = banco.listar_historico(get_conn())
    return jsonify({
        "linhas": [
            {
                "id": h["id"],
                "data": h["data"],
                "ticker": h["ticker"],
                "qtd_comprada": str(h["qtd_comprada"]),
                "preco": str(h["preco"]),
                "valor_investido": str(h["valor_investido"]),
            }
            for h in historico
        ],
        **banco.estado_desfazer(get_conn()),
    })


@app.route("/api/historico", methods=["POST"])
def api_adicionar_historico():
    try:
        campos = ler_linha_historico(request.get_json(force=True))
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400
    return alterar_historico(banco.adicionar_historico, *campos)


@app.route("/api/historico/<int:id_linha>", methods=["PUT"])
def api_editar_historico(id_linha):
    try:
        campos = ler_linha_historico(request.get_json(force=True))
    except ValueError as erro:
        return jsonify({"erro": str(erro)}), 400
    return alterar_historico(banco.editar_historico, id_linha, *campos)


@app.route("/api/historico/<int:id_linha>", methods=["DELETE"])
def api_excluir_historico(id_linha):
    return alterar_historico(banco.excluir_historico, id_linha)


@app.route("/api/historico/excluir-bloco", methods=["POST"])
def api_excluir_bloco_historico():
    dados = request.get_json(force=True)
    return alterar_historico(banco.excluir_bloco_historico, str(dados.get("data", "")))


@app.route("/api/historico/desfazer", methods=["POST"])
def api_desfazer_historico():
    return alterar_historico(banco.desfazer)


@app.route("/api/historico/refazer", methods=["POST"])
def api_refazer_historico():
    return alterar_historico(banco.refazer)


if __name__ == "__main__":
    app.run(debug=True)
