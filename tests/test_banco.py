from decimal import Decimal

import pytest

import banco
from calculo import calcular_aporte


def ativo(ticker, tipo, qtd, preco, pct_alvo):
    return {
        "ticker": ticker,
        "tipo": tipo,
        "qtd": Decimal(qtd),
        "preco_atual": Decimal(preco),
        "pct_alvo": Decimal(pct_alvo),
        "preco_origem": "manual",
        "atualizado_em": "2026-01-01 10:00:00",
    }


def carteira_caso_b():
    return [
        ativo("ITSA4", "Acao", "200", "9.50", "0.10"),
        ativo("VALE3", "Acao", "50", "62.00", "0.15"),
        ativo("WEGE3", "Acao", "100", "40.00", "0.20"),
        ativo("MGLU3", "Acao", "1000", "2.00", "0.05"),
        ativo("MXRF11", "FII", "300", "10.50", "0.15"),
        ativo("KNCR11", "FII", "20", "102.50", "0.10"),
        ativo("IVVB11", "ETF", "50", "76.00", "0.25"),
    ]


def cadastrar_carteira_caso_b(conn):
    for a in carteira_caso_b():
        banco.salvar_ativo(conn, a)


def resultados_caso_b(conn, aporte):
    ativos_calculo = [
        {
            "ticker": a["ticker"],
            "tipo": a["tipo"],
            "qtd": a["qtd"],
            "preco": a["preco_atual"],
            "pct_alvo": a["pct_alvo"],
        }
        for a in banco.listar_ativos(conn)
    ]
    return calcular_aporte(ativos_calculo, Decimal(aporte))


def test_ct04_consolidar_caso_b(tmp_path):
    caminho = str(tmp_path / "teste.db")
    conn = banco.conectar(caminho)
    cadastrar_carteira_caso_b(conn)

    resultados = resultados_caso_b(conn, "1600.00")
    banco.consolidar_aporte(conn, resultados, data="2026-01-15")

    ivvb11 = banco.buscar_ativo(conn, "IVVB11")
    assert ivvb11["qtd"] == Decimal("71")

    historico = banco.listar_historico(conn)
    assert len(historico) == 1
    assert historico[0]["ticker"] == "IVVB11"
    assert historico[0]["qtd_comprada"] == Decimal("21")
    assert historico[0]["preco"] == Decimal("76.00")
    assert historico[0]["valor_investido"] == Decimal("1596.00")

    conn.close()


def test_ct05_persistencia(tmp_path):
    caminho = str(tmp_path / "teste.db")

    conn = banco.conectar(caminho)
    cadastrar_carteira_caso_b(conn)
    resultados = resultados_caso_b(conn, "1600.00")
    banco.consolidar_aporte(conn, resultados, data="2026-01-15")
    conn.close()

    conn2 = banco.conectar(caminho)
    ivvb11 = banco.buscar_ativo(conn2, "IVVB11")
    assert ivvb11["qtd"] == Decimal("71")

    historico = banco.listar_historico(conn2)
    assert len(historico) == 1
    assert historico[0]["ticker"] == "IVVB11"
    assert historico[0]["valor_investido"] == Decimal("1596.00")
    conn2.close()


def test_ct06_atomicidade(tmp_path):
    caminho = str(tmp_path / "teste.db")
    conn = banco.conectar(caminho)
    cadastrar_carteira_caso_b(conn)

    resultados = resultados_caso_b(conn, "1600.00")
    resultado_invalido = {
        "ticker": "NAO_EXISTE",
        "tipo": "Acao",
        "preco": Decimal("10.00"),
        "qtd_comprar": Decimal("1"),
        "valor_investido": Decimal("10.00"),
    }
    resultados_com_erro = resultados + [resultado_invalido]

    with pytest.raises(ValueError):
        banco.consolidar_aporte(conn, resultados_com_erro, data="2026-01-15")

    ivvb11 = banco.buscar_ativo(conn, "IVVB11")
    assert ivvb11["qtd"] == Decimal("50")

    assert banco.listar_historico(conn) == []

    conn.close()
