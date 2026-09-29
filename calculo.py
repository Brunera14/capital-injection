from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

APORTAR = "APORTAR"
NAO_APORTAR = "NAO_APORTAR"

TIPOS_COTA_INTEIRA = {"Acao", "FII", "ETF"}


def calcular_aporte(ativos, aporte):
    total_atual = sum((a["qtd"] * a["preco"] for a in ativos), Decimal("0"))
    total_pos = total_atual + aporte

    soma_pct_alvo = sum((a["pct_alvo"] for a in ativos), Decimal("0"))
    if soma_pct_alvo != Decimal("1"):
        raise ValueError(
            "A soma do percentual alvo dos ativos deve ser 100%, mas e "
            + str(soma_pct_alvo * 100) + "%."
        )

    resultados = []
    for a in ativos:
        valor_atual = a["qtd"] * a["preco"]
        valor_alvo = a["pct_alvo"] * total_pos
        defasagem = valor_alvo - valor_atual
        status = APORTAR if defasagem > 0 else NAO_APORTAR
        resultados.append({
            "ticker": a["ticker"],
            "tipo": a["tipo"],
            "preco": a["preco"],
            "valor_atual": valor_atual,
            "valor_alvo": valor_alvo,
            "defasagem": defasagem,
            "status": status,
            "aporte_recomendado": Decimal("0"),
        })

    ranking = sorted(
        (r for r in resultados if r["status"] == APORTAR),
        key=lambda r: r["defasagem"],
        reverse=True,
    )

    restante = aporte
    for r in ranking:
        valor = min(r["defasagem"], restante)
        r["aporte_recomendado"] = valor
        restante -= valor

    for r in resultados:
        tipo = r["tipo"]
        aporte_recomendado = r["aporte_recomendado"]
        if tipo in TIPOS_COTA_INTEIRA:
            if aporte_recomendado > 0:
                qtd_comprar = (aporte_recomendado / r["preco"]).to_integral_value(rounding=ROUND_DOWN)
            else:
                qtd_comprar = Decimal("0")
            valor_investido = qtd_comprar * r["preco"]
        elif tipo == "RendaFixa":
            qtd_comprar = Decimal("1")
            valor_investido = aporte_recomendado
        elif tipo == "Cripto":
            if aporte_recomendado > 0:
                qtd_comprar = (aporte_recomendado / r["preco"]).quantize(
                    Decimal("0.00000001"), rounding=ROUND_HALF_UP
                )
            else:
                qtd_comprar = Decimal("0")
            valor_investido = aporte_recomendado
        else:
            raise ValueError("Tipo de ativo desconhecido: " + str(tipo))

        r["qtd_comprar"] = qtd_comprar
        r["valor_investido"] = valor_investido

    return resultados
