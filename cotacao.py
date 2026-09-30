import os
from datetime import datetime
from decimal import Decimal

import requests
from dotenv import load_dotenv

import banco

load_dotenv()

URL_BASE = "https://brapi.dev/api/quote/"
TIPOS_AUTOMATICOS = {"Acao", "FII", "ETF"}


class CotacaoIndisponivel(Exception):
    pass


def buscar_cotacoes(tickers):
    if not tickers:
        return {}

    token = os.getenv("BRAPI_TOKEN")
    headers = {}
    if token:
        headers["Authorization"] = "Bearer " + token

    url = URL_BASE + ",".join(tickers)

    try:
        resposta = requests.get(url, headers=headers, timeout=10)
        resposta.raise_for_status()
        dados = resposta.json()
    except (requests.RequestException, ValueError) as erro:
        raise CotacaoIndisponivel("Nao foi possivel consultar a brapi: " + str(erro))

    precos = {}
    for item in dados.get("results", []):
        preco = item.get("regularMarketPrice")
        if preco is not None:
            precos[item["symbol"]] = Decimal(str(preco))
    return precos


def atualizar_cotacoes(conn):
    ativos = banco.listar_ativos(conn)
    alvo = [a for a in ativos if a["tipo"] in TIPOS_AUTOMATICOS]

    if not alvo:
        return {"atualizados": [], "falhas": [], "aviso": None}

    tickers = [a["ticker"] for a in alvo]

    try:
        precos = buscar_cotacoes(tickers)
    except CotacaoIndisponivel:
        return {
            "atualizados": [],
            "falhas": tickers,
            "aviso": (
                "A API de cotacoes esta indisponivel. Os ultimos precos salvos "
                "foram mantidos; informe o preco manualmente se precisar."
            ),
        }

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    atualizados = []
    falhas = []

    for a in alvo:
        preco = precos.get(a["ticker"])
        if preco is None:
            falhas.append(a["ticker"])
            continue
        novo_ativo = dict(a)
        novo_ativo["preco_atual"] = preco
        novo_ativo["preco_origem"] = "api"
        novo_ativo["atualizado_em"] = agora
        banco.salvar_ativo(conn, novo_ativo)
        atualizados.append(a["ticker"])

    aviso = None
    if falhas:
        aviso = (
            "Nao foi possivel obter cotacao para: " + ", ".join(falhas)
            + ". O ultimo preco salvo foi mantido; informe o preco manualmente se precisar."
        )

    return {"atualizados": atualizados, "falhas": falhas, "aviso": aviso}
