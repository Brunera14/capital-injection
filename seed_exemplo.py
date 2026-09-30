from datetime import datetime
from decimal import Decimal

import banco

CARTEIRA_CASO_B = [
    ("ITSA4", "Acao", "200", "9.50", "0.10"),
    ("VALE3", "Acao", "50", "62.00", "0.15"),
    ("WEGE3", "Acao", "100", "40.00", "0.20"),
    ("MGLU3", "Acao", "1000", "2.00", "0.05"),
    ("MXRF11", "FII", "300", "10.50", "0.15"),
    ("KNCR11", "FII", "20", "102.50", "0.10"),
    ("IVVB11", "ETF", "50", "76.00", "0.25"),
]


def main():
    conn = banco.conectar()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for ticker, tipo, qtd, preco, pct_alvo in CARTEIRA_CASO_B:
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
    print("Carteira de exemplo (Caso B) carregada em " + banco.NOME_BD_PADRAO + ".")


if __name__ == "__main__":
    main()
