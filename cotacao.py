import os
from datetime import datetime
from decimal import Decimal

import requests
from dotenv import load_dotenv

import banco

load_dotenv()

URL_BASE = "https://brapi.dev/api/quote/"
TIPOS_AUTOMATICOS = {"Acao", "FII", "ETF"}


def buscar_cotacao(ticker):
    token = os.getenv("BRAPI_TOKEN")
    headers = {"Authorization": "Bearer " + token} if token else {}

    resposta = requests.get(URL_BASE + ticker, headers=headers, timeout=10)
    resposta.raise_for_status()
    dados = resposta.json()

    resultados = dados.get("results") or []
    if not resultados:
        return None

    preco = resultados[0].get("regularMarketPrice")
    return Decimal(str(preco)) if preco is not None else None


def buscar_cotacoes(tickers):
    # O plano gratuito da brapi permite apenas 1 ativo por chamada,
    # por isso cada ticker e buscado em uma requisicao separada.
    precos = {}
    for ticker in tickers:
        try:
            preco = buscar_cotacao(ticker)
        except (requests.RequestException, ValueError):
            continue
        if preco is not None:
            precos[ticker] = preco
    return precos


def atualizar_cotacoes(conn):
    ativos = banco.listar_ativos(conn)
    alvo = [a for a in ativos if a["tipo"] in TIPOS_AUTOMATICOS]

    if not alvo:
        return {"atualizados": [], "falhas": [], "aviso": None}

    tickers = [a["ticker"] for a in alvo]
    precos = buscar_cotacoes(tickers)

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
    if falhas and not atualizados:
        aviso = (
            "A API de cotacoes esta indisponivel. Os ultimos precos salvos "
            "foram mantidos; informe o preco manualmente se precisar."
        )
    elif falhas:
        aviso = (
            "Nao foi possivel obter cotacao para: " + ", ".join(falhas)
            + ". O ultimo preco salvo foi mantido; informe o preco manualmente se precisar."
        )

    return {"atualizados": atualizados, "falhas": falhas, "aviso": aviso}
