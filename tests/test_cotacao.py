from decimal import Decimal

import pytest
import requests

import banco
import cotacao


class RespostaFalsa:
    def __init__(self, dados, status_ok=True):
        self._dados = dados
        self._status_ok = status_ok

    def raise_for_status(self):
        if not self._status_ok:
            raise requests.HTTPError("erro simulado")

    def json(self):
        return self._dados


def ativo(ticker, tipo, qtd, preco, pct_alvo, preco_origem="api"):
    return {
        "ticker": ticker,
        "tipo": tipo,
        "qtd": Decimal(qtd),
        "preco_atual": Decimal(preco),
        "pct_alvo": Decimal(pct_alvo),
        "preco_origem": preco_origem,
        "atualizado_em": "2026-01-01 10:00:00",
    }


def banco_de_teste(tmp_path):
    return banco.conectar(str(tmp_path / "teste.db"))


def test_buscar_cotacoes_sucesso(monkeypatch):
    def get_falso(url, headers=None, timeout=None):
        assert "ITUB4" in url
        return RespostaFalsa({
            "results": [
                {"symbol": "ITUB4", "regularMarketPrice": 32.5},
                {"symbol": "VALE3", "regularMarketPrice": 62.0},
            ]
        })

    monkeypatch.setattr(requests, "get", get_falso)

    precos = cotacao.buscar_cotacoes(["ITUB4", "VALE3"])

    assert precos == {"ITUB4": Decimal("32.5"), "VALE3": Decimal("62.0")}


def test_buscar_cotacoes_lista_vazia_nao_chama_a_api(monkeypatch):
    def get_falso(*args, **kwargs):
        raise AssertionError("nao deveria chamar a API sem tickers")

    monkeypatch.setattr(requests, "get", get_falso)

    assert cotacao.buscar_cotacoes([]) == {}


def test_buscar_cotacoes_falha_de_rede(monkeypatch):
    def get_falso(url, headers=None, timeout=None):
        raise requests.ConnectionError("sem internet")

    monkeypatch.setattr(requests, "get", get_falso)

    with pytest.raises(cotacao.CotacaoIndisponivel):
        cotacao.buscar_cotacoes(["ITUB4"])


def test_buscar_cotacoes_status_de_erro(monkeypatch):
    def get_falso(url, headers=None, timeout=None):
        return RespostaFalsa({}, status_ok=False)

    monkeypatch.setattr(requests, "get", get_falso)

    with pytest.raises(cotacao.CotacaoIndisponivel):
        cotacao.buscar_cotacoes(["ITUB4"])


def test_atualizar_cotacoes_sucesso(tmp_path, monkeypatch):
    conn = banco_de_teste(tmp_path)
    banco.salvar_ativo(conn, ativo("ITUB4", "Acao", "200", "30.00", "1.0"))

    monkeypatch.setattr(cotacao, "buscar_cotacoes", lambda tickers: {"ITUB4": Decimal("33.00")})

    resultado = cotacao.atualizar_cotacoes(conn)

    assert resultado["atualizados"] == ["ITUB4"]
    assert resultado["falhas"] == []
    assert resultado["aviso"] is None

    atualizado = banco.buscar_ativo(conn, "ITUB4")
    assert atualizado["preco_atual"] == Decimal("33.00")
    assert atualizado["preco_origem"] == "api"

    conn.close()


def test_atualizar_cotacoes_ignora_renda_fixa_e_cripto(tmp_path, monkeypatch):
    conn = banco_de_teste(tmp_path)
    banco.salvar_ativo(conn, ativo("ITUB4", "Acao", "200", "30.00", "0.5"))
    banco.salvar_ativo(conn, ativo("CDB Banco X", "RendaFixa", "1", "5000.00", "0.3", preco_origem="manual"))
    banco.salvar_ativo(conn, ativo("BTC", "Cripto", "0.01", "350000.00", "0.2", preco_origem="manual"))

    tickers_chamados = []

    def buscar_falso(tickers):
        tickers_chamados.extend(tickers)
        return {"ITUB4": Decimal("31.00")}

    monkeypatch.setattr(cotacao, "buscar_cotacoes", buscar_falso)

    resultado = cotacao.atualizar_cotacoes(conn)

    assert tickers_chamados == ["ITUB4"]
    assert resultado["atualizados"] == ["ITUB4"]

    cdb = banco.buscar_ativo(conn, "CDB Banco X")
    assert cdb["preco_atual"] == Decimal("5000.00")
    assert cdb["preco_origem"] == "manual"

    btc = banco.buscar_ativo(conn, "BTC")
    assert btc["preco_atual"] == Decimal("350000.00")
    assert btc["preco_origem"] == "manual"

    conn.close()


def test_ct07_api_fora_do_ar_mantem_ultimo_preco_e_avisa(tmp_path, monkeypatch):
    conn = banco_de_teste(tmp_path)
    banco.salvar_ativo(conn, ativo("ITUB4", "Acao", "200", "30.00", "1.0"))

    def buscar_com_falha(tickers):
        raise cotacao.CotacaoIndisponivel("API fora do ar")

    monkeypatch.setattr(cotacao, "buscar_cotacoes", buscar_com_falha)

    resultado = cotacao.atualizar_cotacoes(conn)

    assert resultado["atualizados"] == []
    assert resultado["falhas"] == ["ITUB4"]
    assert resultado["aviso"] is not None
    assert "indisponivel" in resultado["aviso"].lower()

    mantido = banco.buscar_ativo(conn, "ITUB4")
    assert mantido["preco_atual"] == Decimal("30.00")
    assert mantido["preco_origem"] == "api"

    banco.salvar_ativo(conn, {**mantido, "preco_atual": Decimal("31.50"), "preco_origem": "manual"})
    manual = banco.buscar_ativo(conn, "ITUB4")
    assert manual["preco_atual"] == Decimal("31.50")
    assert manual["preco_origem"] == "manual"

    conn.close()


def test_atualizar_cotacoes_sem_ativos_automaticos(tmp_path, monkeypatch):
    conn = banco_de_teste(tmp_path)
    banco.salvar_ativo(conn, ativo("CDB Banco X", "RendaFixa", "1", "5000.00", "1.0", preco_origem="manual"))

    def get_falso(*args, **kwargs):
        raise AssertionError("nao deveria chamar a API")

    monkeypatch.setattr(requests, "get", get_falso)

    resultado = cotacao.atualizar_cotacoes(conn)

    assert resultado == {"atualizados": [], "falhas": [], "aviso": None}

    conn.close()
