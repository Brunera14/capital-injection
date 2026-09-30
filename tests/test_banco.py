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


def conn_com_carteira(tmp_path):
    conn = banco.conectar(str(tmp_path / "teste.db"))
    cadastrar_carteira_caso_b(conn)
    return conn


def qtd_de(conn, ticker):
    return banco.buscar_ativo(conn, ticker)["qtd"]


def test_adicionar_historico_ajusta_carteira_e_desfaz(tmp_path):
    conn = conn_com_carteira(tmp_path)

    banco.adicionar_historico(conn, "2026-02-01", "VALE3", Decimal("4"), Decimal("60.00"))
    assert qtd_de(conn, "VALE3") == Decimal("54")
    linha = banco.listar_historico(conn)[0]
    assert linha["valor_investido"] == Decimal("240.00")

    banco.desfazer(conn)
    assert qtd_de(conn, "VALE3") == Decimal("50")
    assert banco.listar_historico(conn) == []

    banco.refazer(conn)
    assert qtd_de(conn, "VALE3") == Decimal("54")
    assert len(banco.listar_historico(conn)) == 1
    conn.close()


def test_editar_historico_ajusta_diferenca_e_desfaz(tmp_path):
    conn = conn_com_carteira(tmp_path)
    banco.adicionar_historico(conn, "2026-02-01", "VALE3", Decimal("3"), Decimal("60.00"))
    id_linha = banco.listar_historico(conn)[0]["id"]

    banco.editar_historico(conn, id_linha, "2026-02-02", "VALE3", Decimal("5"), Decimal("61.00"))
    assert qtd_de(conn, "VALE3") == Decimal("55")
    linha = banco.listar_historico(conn)[0]
    assert linha["qtd_comprada"] == Decimal("5")
    assert linha["valor_investido"] == Decimal("305.00")

    banco.desfazer(conn)
    assert qtd_de(conn, "VALE3") == Decimal("53")
    assert banco.listar_historico(conn)[0]["qtd_comprada"] == Decimal("3")
    conn.close()


def test_editar_trocando_ticker_move_quantidade(tmp_path):
    conn = conn_com_carteira(tmp_path)
    banco.adicionar_historico(conn, "2026-02-01", "VALE3", Decimal("3"), Decimal("60.00"))
    id_linha = banco.listar_historico(conn)[0]["id"]

    banco.editar_historico(conn, id_linha, "2026-02-01", "WEGE3", Decimal("3"), Decimal("40.00"))
    assert qtd_de(conn, "VALE3") == Decimal("50")
    assert qtd_de(conn, "WEGE3") == Decimal("103")
    conn.close()


def test_excluir_historico_tira_da_carteira_e_desfaz(tmp_path):
    conn = conn_com_carteira(tmp_path)
    banco.adicionar_historico(conn, "2026-02-01", "VALE3", Decimal("3"), Decimal("60.00"))
    id_linha = banco.listar_historico(conn)[0]["id"]

    banco.excluir_historico(conn, id_linha)
    assert qtd_de(conn, "VALE3") == Decimal("50")
    assert banco.listar_historico(conn) == []

    banco.desfazer(conn)
    assert qtd_de(conn, "VALE3") == Decimal("53")
    assert banco.listar_historico(conn)[0]["id"] == id_linha
    conn.close()


def test_desfazer_consolidar(tmp_path):
    conn = conn_com_carteira(tmp_path)
    banco.consolidar_aporte(conn, resultados_caso_b(conn, "1600.00"), data="2026-01-15")
    assert qtd_de(conn, "IVVB11") == Decimal("71")

    banco.desfazer(conn)
    assert qtd_de(conn, "IVVB11") == Decimal("50")
    assert banco.listar_historico(conn) == []
    conn.close()


def test_alteracao_nova_descarta_o_que_dava_para_refazer(tmp_path):
    conn = conn_com_carteira(tmp_path)
    banco.adicionar_historico(conn, "2026-02-01", "VALE3", Decimal("1"), Decimal("60.00"))
    banco.desfazer(conn)
    assert banco.estado_desfazer(conn)["pode_refazer"] is True

    banco.adicionar_historico(conn, "2026-02-02", "VALE3", Decimal("2"), Decimal("60.00"))
    assert banco.estado_desfazer(conn)["pode_refazer"] is False
    conn.close()


def test_edicao_que_deixa_carteira_negativa_e_recusada(tmp_path):
    conn = conn_com_carteira(tmp_path)
    banco.adicionar_historico(conn, "2026-02-01", "VALE3", Decimal("3"), Decimal("60.00"))
    id_linha = banco.listar_historico(conn)[0]["id"]

    with pytest.raises(ValueError):
        banco.editar_historico(conn, id_linha, "2026-02-01", "VALE3", Decimal("-100"), Decimal("60.00"))

    assert qtd_de(conn, "VALE3") == Decimal("53")
    assert banco.listar_historico(conn)[0]["qtd_comprada"] == Decimal("3")
    conn.close()


def test_desfazer_sem_nada_da_erro(tmp_path):
    conn = conn_com_carteira(tmp_path)
    with pytest.raises(ValueError):
        banco.desfazer(conn)
    with pytest.raises(ValueError):
        banco.refazer(conn)
    conn.close()


def test_excluir_historico_de_ativo_removido_da_carteira(tmp_path):
    conn = conn_com_carteira(tmp_path)
    banco.consolidar_aporte(conn, resultados_caso_b(conn, "1600.00"), data="2026-01-15")
    banco.remover_ativo(conn, "IVVB11")
    id_linha = banco.listar_historico(conn)[0]["id"]

    banco.excluir_historico(conn, id_linha)
    assert banco.listar_historico(conn) == []
    conn.close()


def test_excluir_bloco_remove_todas_as_linhas_e_desfaz_de_uma_vez(tmp_path):
    conn = conn_com_carteira(tmp_path)
    banco.adicionar_historico(conn, "2026-03-01 10:00:00", "VALE3", Decimal("2"), Decimal("60.00"))
    banco.adicionar_historico(conn, "2026-03-01 10:00:00", "WEGE3", Decimal("3"), Decimal("40.00"))
    banco.adicionar_historico(conn, "2026-04-01 10:00:00", "VALE3", Decimal("1"), Decimal("60.00"))

    banco.excluir_bloco_historico(conn, "2026-03-01 10:00:00")
    assert len(banco.listar_historico(conn)) == 1
    assert qtd_de(conn, "VALE3") == Decimal("51")
    assert qtd_de(conn, "WEGE3") == Decimal("100")

    banco.desfazer(conn)
    assert len(banco.listar_historico(conn)) == 3
    assert qtd_de(conn, "VALE3") == Decimal("53")
    assert qtd_de(conn, "WEGE3") == Decimal("103")
    conn.close()


def test_desfazer_exclusao_de_ativo_removido_restaura_so_o_historico(tmp_path):
    conn = conn_com_carteira(tmp_path)
    banco.consolidar_aporte(conn, resultados_caso_b(conn, "1600.00"), data="2026-01-15")
    banco.remover_ativo(conn, "IVVB11")
    id_linha = banco.listar_historico(conn)[0]["id"]
    banco.excluir_historico(conn, id_linha)

    banco.desfazer(conn)
    assert len(banco.listar_historico(conn)) == 1
    assert banco.buscar_ativo(conn, "IVVB11") is None
    conn.close()


def test_adicionar_historico_de_ticker_fora_da_carteira_e_recusado(tmp_path):
    conn = conn_com_carteira(tmp_path)
    with pytest.raises(ValueError):
        banco.adicionar_historico(conn, "2026-02-01", "XXXX3", Decimal("1"), Decimal("10"))
    assert banco.listar_historico(conn) == []
    conn.close()
