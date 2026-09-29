from decimal import Decimal

from calculo import calcular_aporte, APORTAR, NAO_APORTAR


def ativo(ticker, tipo, qtd, preco, pct_alvo):
    return {
        "ticker": ticker,
        "tipo": tipo,
        "qtd": Decimal(qtd),
        "preco": Decimal(preco),
        "pct_alvo": Decimal(pct_alvo),
    }


def por_ticker(resultados):
    return {r["ticker"]: r for r in resultados}


def test_caso_a_aporte_grande_carteira_completa():
    ativos = [
        ativo("ITUB4", "Acao", "200", "32.00", "0.25"),
        ativo("HGLG11", "FII", "50", "160.00", "0.25"),
        ativo("IVVB11", "ETF", "30", "280.00", "0.20"),
        ativo("CDB Banco X", "RendaFixa", "1", "5000.00", "0.20"),
        ativo("BTC", "Cripto", "0.01", "350000.00", "0.10"),
    ]

    resultados = calcular_aporte(ativos, Decimal("100000.00"))
    r = por_ticker(resultados)

    for ticker in r:
        assert r[ticker]["status"] == APORTAR

    assert r["ITUB4"]["aporte_recomendado"] == Decimal("26425.00")
    assert r["ITUB4"]["qtd_comprar"] == Decimal("825")
    assert r["ITUB4"]["valor_investido"] == Decimal("26400.00")

    assert r["HGLG11"]["aporte_recomendado"] == Decimal("24825.00")
    assert r["HGLG11"]["qtd_comprar"] == Decimal("155")
    assert r["HGLG11"]["valor_investido"] == Decimal("24800.00")

    assert r["CDB Banco X"]["aporte_recomendado"] == Decimal("21260.00")
    assert r["CDB Banco X"]["qtd_comprar"] == Decimal("1")
    assert r["CDB Banco X"]["valor_investido"] == Decimal("21260.00")

    assert r["IVVB11"]["aporte_recomendado"] == Decimal("17860.00")
    assert r["IVVB11"]["qtd_comprar"] == Decimal("63")
    assert r["IVVB11"]["valor_investido"] == Decimal("17640.00")

    assert r["BTC"]["aporte_recomendado"] == Decimal("9630.00")
    assert r["BTC"]["qtd_comprar"] == Decimal("0.02751429")
    assert r["BTC"]["valor_investido"] == Decimal("9630.00")

    total_investido = sum((res["valor_investido"] for res in resultados), Decimal("0"))
    assert total_investido == Decimal("99730.00")

    soma_aporte_recomendado = sum((res["aporte_recomendado"] for res in resultados), Decimal("0"))
    assert soma_aporte_recomendado == Decimal("100000.00")


def _carteira_caso_b():
    return [
        ativo("ITSA4", "Acao", "200", "9.50", "0.10"),
        ativo("VALE3", "Acao", "50", "62.00", "0.15"),
        ativo("WEGE3", "Acao", "100", "40.00", "0.20"),
        ativo("MGLU3", "Acao", "1000", "2.00", "0.05"),
        ativo("MXRF11", "FII", "300", "10.50", "0.15"),
        ativo("KNCR11", "FII", "20", "102.50", "0.10"),
        ativo("IVVB11", "ETF", "50", "76.00", "0.25"),
    ]


def test_caso_b_aporte_insuficiente():
    resultados = calcular_aporte(_carteira_caso_b(), Decimal("1600.00"))
    r = por_ticker(resultados)

    assert r["IVVB11"]["status"] == APORTAR
    assert r["IVVB11"]["aporte_recomendado"] == Decimal("1600.00")
    assert r["IVVB11"]["qtd_comprar"] == Decimal("21")
    assert r["IVVB11"]["valor_investido"] == Decimal("1596.00")

    assert r["MGLU3"]["status"] == NAO_APORTAR
    assert r["MGLU3"]["defasagem"] == Decimal("-920.00")
    assert r["MGLU3"]["aporte_recomendado"] == Decimal("0")

    for ticker in ("ITSA4", "VALE3", "WEGE3", "MXRF11", "KNCR11"):
        assert r[ticker]["aporte_recomendado"] == Decimal("0")

    total_investido = sum((res["valor_investido"] for res in resultados), Decimal("0"))
    assert total_investido == Decimal("1596.00")


def test_caso_b2_aporte_intermediario():
    resultados = calcular_aporte(_carteira_caso_b(), Decimal("3000.00"))
    r = por_ticker(resultados)

    assert r["IVVB11"]["aporte_recomendado"] == Decimal("1950.00")
    assert r["IVVB11"]["qtd_comprar"] == Decimal("25")
    assert r["IVVB11"]["valor_investido"] == Decimal("1900.00")

    assert r["WEGE3"]["aporte_recomendado"] == Decimal("600.00")
    assert r["WEGE3"]["qtd_comprar"] == Decimal("15")
    assert r["WEGE3"]["valor_investido"] == Decimal("600.00")

    assert r["ITSA4"]["aporte_recomendado"] == Decimal("400.00")
    assert r["ITSA4"]["qtd_comprar"] == Decimal("42")
    assert r["ITSA4"]["valor_investido"] == Decimal("399.00")

    assert r["VALE3"]["aporte_recomendado"] == Decimal("50.00")
    assert r["VALE3"]["qtd_comprar"] == Decimal("0")
    assert r["VALE3"]["valor_investido"] == Decimal("0")

    assert r["MXRF11"]["aporte_recomendado"] == Decimal("0")
    assert r["KNCR11"]["aporte_recomendado"] == Decimal("0")
    assert r["MGLU3"]["status"] == NAO_APORTAR

    total_investido = sum((res["valor_investido"] for res in resultados), Decimal("0"))
    assert total_investido == Decimal("2899.00")


def _carteira_caso_c():
    return [
        ativo("AAA3", "Acao", "100", "10.00", "0.50"),
        ativo("BBB4", "Acao", "50", "20.00", "0.50"),
    ]


def test_caso_c_carteira_equilibrada_sem_aporte():
    resultados = calcular_aporte(_carteira_caso_c(), Decimal("0"))
    r = por_ticker(resultados)

    assert r["AAA3"]["status"] == NAO_APORTAR
    assert r["BBB4"]["status"] == NAO_APORTAR
    assert r["AAA3"]["aporte_recomendado"] == Decimal("0")
    assert r["BBB4"]["aporte_recomendado"] == Decimal("0")


def test_caso_c_carteira_equilibrada_com_aporte():
    resultados = calcular_aporte(_carteira_caso_c(), Decimal("1000.00"))
    r = por_ticker(resultados)

    assert r["AAA3"]["aporte_recomendado"] == Decimal("500.00")
    assert r["AAA3"]["qtd_comprar"] == Decimal("50")

    assert r["BBB4"]["aporte_recomendado"] == Decimal("500.00")
    assert r["BBB4"]["qtd_comprar"] == Decimal("25")


def test_caso_d_aporte_nao_cobre_uma_cota():
    resultados = calcular_aporte(_carteira_caso_b(), Decimal("5.00"))
    r = por_ticker(resultados)

    assert r["IVVB11"]["status"] == APORTAR
    assert r["IVVB11"]["aporte_recomendado"] == Decimal("5.00")
    assert r["IVVB11"]["qtd_comprar"] == Decimal("0")
    assert r["IVVB11"]["valor_investido"] == Decimal("0")


def test_caso_f_aporte_encadeado_apos_consolidar():
    ativos = [
        ativo("ITSA4", "Acao", "200", "9.50", "0.10"),
        ativo("VALE3", "Acao", "50", "62.00", "0.15"),
        ativo("WEGE3", "Acao", "100", "40.00", "0.20"),
        ativo("MGLU3", "Acao", "1000", "2.00", "0.05"),
        ativo("MXRF11", "FII", "300", "10.50", "0.15"),
        ativo("KNCR11", "FII", "20", "102.50", "0.10"),
        ativo("IVVB11", "ETF", "71", "76.00", "0.25"),
    ]

    resultados = calcular_aporte(ativos, Decimal("1000.00"))
    r = por_ticker(resultados)

    assert r["WEGE3"]["aporte_recomendado"] == Decimal("519.20")
    assert r["WEGE3"]["qtd_comprar"] == Decimal("12")
    assert r["WEGE3"]["valor_investido"] == Decimal("480.00")

    assert r["ITSA4"]["aporte_recomendado"] == Decimal("359.60")
    assert r["ITSA4"]["qtd_comprar"] == Decimal("37")
    assert r["ITSA4"]["valor_investido"] == Decimal("351.50")

    assert r["VALE3"]["aporte_recomendado"] == Decimal("121.20")
    assert r["VALE3"]["qtd_comprar"] == Decimal("1")
    assert r["VALE3"]["valor_investido"] == Decimal("62.00")

    assert r["MGLU3"]["status"] == NAO_APORTAR

    for ticker in ("IVVB11", "MXRF11", "KNCR11"):
        assert r[ticker]["aporte_recomendado"] == Decimal("0")
