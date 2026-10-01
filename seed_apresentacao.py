from datetime import datetime
from decimal import Decimal

import banco

# Cenario da apresentacao: 4 ativos, perto do ideal, precos reais de hoje.
CARTEIRA_APRESENTACAO = [
    ("ITSA4", "Acao", "350", "14.60", "0.25"),
    ("VALE3", "Acao", "70", "69.90", "0.25"),
    ("WEGE3", "Acao", "100", "49.50", "0.25"),
    ("MXRF11", "Acao", "500", "9.20", "0.25"),
]


def main():
    conn = banco.conectar()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Apaga a carteira e o historico atuais para o cenario comecar do zero.
    conn.execute("DELETE FROM ativos")
    conn.execute("DELETE FROM historico")
    conn.execute("DELETE FROM operacoes")
    conn.commit()

    for ticker, tipo, qtd, preco, pct_alvo in CARTEIRA_APRESENTACAO:
        banco.salvar_ativo(conn, {
            "ticker": ticker,
            "tipo": tipo,
            "qtd": Decimal(qtd),
            "preco_atual": Decimal(preco),
            "pct_alvo": Decimal(pct_alvo),
            "preco_origem": "manual",
            "atualizado_em": agora,
        })

    conn.close()
    print("Cenario da apresentacao carregado em " + banco.NOME_BD_PADRAO + ".")


if __name__ == "__main__":
    main()
