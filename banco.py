import sqlite3
from datetime import datetime
from decimal import Decimal

NOME_BD_PADRAO = "capital_injection.db"


def conectar(caminho_bd=NOME_BD_PADRAO):
    conn = sqlite3.connect(caminho_bd)
    conn.row_factory = sqlite3.Row
    criar_tabelas(conn)
    return conn


def criar_tabelas(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ativos (
            ticker TEXT PRIMARY KEY,
            tipo TEXT NOT NULL,
            qtd TEXT NOT NULL,
            preco_atual TEXT NOT NULL,
            pct_alvo TEXT NOT NULL,
            preco_origem TEXT NOT NULL,
            atualizado_em TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            ticker TEXT NOT NULL,
            qtd_comprada TEXT NOT NULL,
            preco TEXT NOT NULL,
            valor_investido TEXT NOT NULL
        )
        """
    )
    conn.commit()


def _ativo_da_linha(linha):
    return {
        "ticker": linha["ticker"],
        "tipo": linha["tipo"],
        "qtd": Decimal(linha["qtd"]),
        "preco_atual": Decimal(linha["preco_atual"]),
        "pct_alvo": Decimal(linha["pct_alvo"]),
        "preco_origem": linha["preco_origem"],
        "atualizado_em": linha["atualizado_em"],
    }


def _historico_da_linha(linha):
    return {
        "id": linha["id"],
        "data": linha["data"],
        "ticker": linha["ticker"],
        "qtd_comprada": Decimal(linha["qtd_comprada"]),
        "preco": Decimal(linha["preco"]),
        "valor_investido": Decimal(linha["valor_investido"]),
    }


def salvar_ativo(conn, ativo):
    conn.execute(
        """
        INSERT INTO ativos (ticker, tipo, qtd, preco_atual, pct_alvo, preco_origem, atualizado_em)
        VALUES (:ticker, :tipo, :qtd, :preco_atual, :pct_alvo, :preco_origem, :atualizado_em)
        ON CONFLICT(ticker) DO UPDATE SET
            tipo = excluded.tipo,
            qtd = excluded.qtd,
            preco_atual = excluded.preco_atual,
            pct_alvo = excluded.pct_alvo,
            preco_origem = excluded.preco_origem,
            atualizado_em = excluded.atualizado_em
        """,
        {
            "ticker": ativo["ticker"],
            "tipo": ativo["tipo"],
            "qtd": str(ativo["qtd"]),
            "preco_atual": str(ativo["preco_atual"]),
            "pct_alvo": str(ativo["pct_alvo"]),
            "preco_origem": ativo["preco_origem"],
            "atualizado_em": ativo["atualizado_em"],
        },
    )
    conn.commit()


def listar_ativos(conn):
    linhas = conn.execute("SELECT * FROM ativos ORDER BY ticker").fetchall()
    return [_ativo_da_linha(linha) for linha in linhas]


def buscar_ativo(conn, ticker):
    linha = conn.execute("SELECT * FROM ativos WHERE ticker = ?", (ticker,)).fetchone()
    return _ativo_da_linha(linha) if linha else None


def remover_ativo(conn, ticker):
    conn.execute("DELETE FROM ativos WHERE ticker = ?", (ticker,))
    conn.commit()


def listar_historico(conn):
    linhas = conn.execute("SELECT * FROM historico ORDER BY id").fetchall()
    return [_historico_da_linha(linha) for linha in linhas]


def consolidar_aporte(conn, resultados, data=None):
    if data is None:
        data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    compras = [r for r in resultados if r["valor_investido"] > 0]

    try:
        for r in compras:
            ticker = r["ticker"]
            linha = conn.execute(
                "SELECT tipo, qtd, preco_atual FROM ativos WHERE ticker = ?", (ticker,)
            ).fetchone()
            if linha is None:
                raise ValueError("Ativo nao encontrado no banco: " + str(ticker))

            if linha["tipo"] == "RendaFixa":
                novo_saldo = Decimal(linha["preco_atual"]) + r["valor_investido"]
                conn.execute(
                    "UPDATE ativos SET preco_atual = ?, atualizado_em = ? WHERE ticker = ?",
                    (str(novo_saldo), data, ticker),
                )
            else:
                nova_qtd = Decimal(linha["qtd"]) + r["qtd_comprar"]
                conn.execute(
                    "UPDATE ativos SET qtd = ?, atualizado_em = ? WHERE ticker = ?",
                    (str(nova_qtd), data, ticker),
                )

            conn.execute(
                """
                INSERT INTO historico (data, ticker, qtd_comprada, preco, valor_investido)
                VALUES (?, ?, ?, ?, ?)
                """,
                (data, ticker, str(r["qtd_comprar"]), str(r["preco"]), str(r["valor_investido"])),
            )
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
