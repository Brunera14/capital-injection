import json
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
    # Cada alteracao do historico vira uma operacao, usada por desfazer e refazer.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS operacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dados TEXT NOT NULL,
            desfeita INTEGER NOT NULL DEFAULT 0
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
    operacao = {"historico": [], "ativos": {}}

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
                # Renda fixa (fora do MVP) nao entra no desfazer.
                operacao["ativos"][ticker] = str(r["qtd_comprar"])

            cursor = conn.execute(
                """
                INSERT INTO historico (data, ticker, qtd_comprada, preco, valor_investido)
                VALUES (?, ?, ?, ?, ?)
                """,
                (data, ticker, str(r["qtd_comprar"]), str(r["preco"]), str(r["valor_investido"])),
            )
            operacao["historico"].append({
                "id": cursor.lastrowid,
                "antes": None,
                "depois": {
                    "data": data,
                    "ticker": ticker,
                    "qtd_comprada": str(r["qtd_comprar"]),
                    "preco": str(r["preco"]),
                    "valor_investido": str(r["valor_investido"]),
                },
            })

        if operacao["historico"]:
            _registrar_operacao(conn, operacao)
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()


def _registrar_operacao(conn, operacao):
    # Uma alteracao nova descarta o que ainda podia ser refeito.
    conn.execute("DELETE FROM operacoes WHERE desfeita = 1")
    conn.execute("INSERT INTO operacoes (dados) VALUES (?)", (json.dumps(operacao),))


def _aplicar_ativos(conn, ativos, sinal):
    for ticker, delta in ativos.items():
        linha = conn.execute("SELECT qtd FROM ativos WHERE ticker = ?", (ticker,)).fetchone()
        ajuste = sinal * Decimal(delta)
        if linha is None:
            # Ativo ja removido da carteira: nao ha quantidade para ajustar.
            continue
        nova_qtd = Decimal(linha["qtd"]) + ajuste
        if nova_qtd < 0:
            raise ValueError("A quantidade de " + ticker + " ficaria negativa.")
        conn.execute("UPDATE ativos SET qtd = ? WHERE ticker = ?", (str(nova_qtd), ticker))


def _aplicar_operacao(conn, operacao, inverso):
    _aplicar_ativos(conn, operacao["ativos"], -1 if inverso else 1)

    for mudanca in operacao["historico"]:
        antes, depois = mudanca["antes"], mudanca["depois"]
        if inverso:
            antes, depois = depois, antes
        if depois is None:
            conn.execute("DELETE FROM historico WHERE id = ?", (mudanca["id"],))
        elif antes is None:
            conn.execute(
                """
                INSERT INTO historico (id, data, ticker, qtd_comprada, preco, valor_investido)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (mudanca["id"], depois["data"], depois["ticker"], depois["qtd_comprada"],
                 depois["preco"], depois["valor_investido"]),
            )
        else:
            conn.execute(
                """
                UPDATE historico
                SET data = ?, ticker = ?, qtd_comprada = ?, preco = ?, valor_investido = ?
                WHERE id = ?
                """,
                (depois["data"], depois["ticker"], depois["qtd_comprada"],
                 depois["preco"], depois["valor_investido"], mudanca["id"]),
            )


def _linha_historico_texto(data, ticker, qtd, preco):
    return {
        "data": data,
        "ticker": ticker,
        "qtd_comprada": str(qtd),
        "preco": str(preco),
        "valor_investido": str(qtd * preco),
    }


def _exigir_ativo(conn, ticker):
    if conn.execute("SELECT 1 FROM ativos WHERE ticker = ?", (ticker,)).fetchone() is None:
        raise ValueError("O ativo " + ticker + " nao esta na carteira.")


def _somar_delta(ativos, ticker, delta):
    ativos[ticker] = str(Decimal(ativos.get(ticker, "0")) + delta)


def _executar_alteracao(conn, operacao):
    # Aplica e registra tudo em uma transacao so: ou vai tudo, ou nada.
    try:
        _aplicar_operacao(conn, operacao, inverso=False)
        _registrar_operacao(conn, operacao)
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()


def adicionar_historico(conn, data, ticker, qtd, preco):
    _exigir_ativo(conn, ticker)
    nova = _linha_historico_texto(data, ticker, qtd, preco)
    try:
        cursor = conn.execute(
            """
            INSERT INTO historico (data, ticker, qtd_comprada, preco, valor_investido)
            VALUES (?, ?, ?, ?, ?)
            """,
            (nova["data"], nova["ticker"], nova["qtd_comprada"], nova["preco"], nova["valor_investido"]),
        )
        id_novo = cursor.lastrowid
        ativos = {ticker: str(qtd)}
        _aplicar_ativos(conn, ativos, 1)
        _registrar_operacao(conn, {
            "historico": [{"id": id_novo, "antes": None, "depois": nova}],
            "ativos": ativos,
        })
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()
    return id_novo


def editar_historico(conn, id_linha, data, ticker, qtd, preco):
    antiga = conn.execute("SELECT * FROM historico WHERE id = ?", (id_linha,)).fetchone()
    if antiga is None:
        raise ValueError("Linha do historico nao encontrada.")

    _exigir_ativo(conn, ticker)
    antes = {k: antiga[k] for k in ("data", "ticker", "qtd_comprada", "preco", "valor_investido")}
    depois = _linha_historico_texto(data, ticker, qtd, preco)

    ativos = {}
    _somar_delta(ativos, antes["ticker"], -Decimal(antes["qtd_comprada"]))
    _somar_delta(ativos, ticker, qtd)
    ativos = {t: d for t, d in ativos.items() if Decimal(d) != 0}

    operacao = {
        "historico": [{"id": id_linha, "antes": antes, "depois": depois}],
        "ativos": ativos,
    }
    _executar_alteracao(conn, operacao)


def excluir_historico(conn, id_linha):
    antiga = conn.execute("SELECT * FROM historico WHERE id = ?", (id_linha,)).fetchone()
    if antiga is None:
        raise ValueError("Linha do historico nao encontrada.")

    antes = {k: antiga[k] for k in ("data", "ticker", "qtd_comprada", "preco", "valor_investido")}
    operacao = {
        "historico": [{"id": id_linha, "antes": antes, "depois": None}],
        "ativos": {antes["ticker"]: str(-Decimal(antes["qtd_comprada"]))},
    }
    _executar_alteracao(conn, operacao)


def desfazer(conn):
    linha = conn.execute(
        "SELECT id, dados FROM operacoes WHERE desfeita = 0 ORDER BY id DESC LIMIT 1"
    ).fetchone()
    if linha is None:
        raise ValueError("Nao ha nada para desfazer.")
    try:
        _aplicar_operacao(conn, json.loads(linha["dados"]), inverso=True)
        conn.execute("UPDATE operacoes SET desfeita = 1 WHERE id = ?", (linha["id"],))
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()


def refazer(conn):
    linha = conn.execute(
        "SELECT id, dados FROM operacoes WHERE desfeita = 1 ORDER BY id ASC LIMIT 1"
    ).fetchone()
    if linha is None:
        raise ValueError("Nao ha nada para refazer.")
    try:
        _aplicar_operacao(conn, json.loads(linha["dados"]), inverso=False)
        conn.execute("UPDATE operacoes SET desfeita = 0 WHERE id = ?", (linha["id"],))
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()


def estado_desfazer(conn):
    pode_desfazer = conn.execute("SELECT 1 FROM operacoes WHERE desfeita = 0 LIMIT 1").fetchone()
    pode_refazer = conn.execute("SELECT 1 FROM operacoes WHERE desfeita = 1 LIMIT 1").fetchone()
    return {"pode_desfazer": pode_desfazer is not None, "pode_refazer": pode_refazer is not None}


def excluir_bloco_historico(conn, data):
    linhas = conn.execute("SELECT * FROM historico WHERE data = ? ORDER BY id", (data,)).fetchall()
    if not linhas:
        raise ValueError("Bloco do historico nao encontrado.")

    mudancas = []
    ativos = {}
    for linha in linhas:
        antes = {k: linha[k] for k in ("data", "ticker", "qtd_comprada", "preco", "valor_investido")}
        mudancas.append({"id": linha["id"], "antes": antes, "depois": None})
        _somar_delta(ativos, antes["ticker"], -Decimal(antes["qtd_comprada"]))

    _executar_alteracao(conn, {"historico": mudancas, "ativos": ativos})
