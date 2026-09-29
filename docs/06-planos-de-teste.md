# 6. Planos de Teste e Desempenho

Os planos de teste validam as Regras de Negócio (RN01 a RN08) e os Requisitos Não Funcionais, com foco em precisão matemática (RNF03), desempenho (RNF02) e integridade dos dados (RNF05).

O motor de cálculo em Python deve produzir **exatamente** os números abaixo. Os Casos A e B vêm da planilha e da tela do PI3 (o Caso A é a captura da Figura 4, na seção 7); os demais foram calculados a partir das mesmas fórmulas (seção 3). Eles devem virar testes automáticos em `tests/test_calculo.py`.

## 6.1. Cenários do Plano Original

**Cenário 1: Carteira Equilibrada.** Com todos os ativos exatamente no valor alvo e aporte igual a zero, o sistema mostra "NÃO APORTAR" para todos. Com aporte maior que zero, o aporte é distribuído proporcionalmente aos percentuais alvo (Caso C).

**Cenário 2: Carteira Desequilibrada.** Com ativos acima e abaixo do alvo, o algoritmo prioriza os ativos de maior defasagem e não recomenda nenhuma venda (Casos A e B).

**Cenário 3: Aporte Insuficiente.** Quando o aporte é menor que a defasagem total, o sistema aloca o valor começando pelo ativo prioritário, respeitando a priorização (Casos B e B2).

## 6.2. Casos de Teste com Resultados Esperados

### Caso A: carteira completa do PI3, aporte de R$ 100.000,00

| Ticker | Tipo | Qtd. | Preço | % Alvo |
|---|---|---|---|---|
| ITUB4 | Ação | 200 | R$ 32,00 | 25% |
| HGLG11 | FII | 50 | R$ 160,00 | 25% |
| IVVB11 | ETF | 30 | R$ 280,00 | 20% |
| CDB Banco X | Renda Fixa | 1 | R$ 5.000,00 | 20% |
| BTC | Cripto | 0,01 | R$ 350.000,00 | 10% |

Total atual: R$ 31.300,00. Total pós-aporte: R$ 131.300,00.

| Rank | Ticker | Defasagem = Aporte Recomendado | Qtd. a comprar | Valor investido |
|---|---|---|---|---|
| 1 | ITUB4 | R$ 26.425,00 | 825 | R$ 26.400,00 |
| 2 | HGLG11 | R$ 24.825,00 | 155 | R$ 24.800,00 |
| 3 | CDB Banco X | R$ 21.260,00 | (saldo passa a R$ 26.260,00) | R$ 21.260,00 |
| 4 | IVVB11 | R$ 17.860,00 | 63 | R$ 17.640,00 |
| 5 | BTC | R$ 9.630,00 | 0,02751429 | R$ 9.630,00 |

Todos com status "APORTAR". Soma dos Aportes Recomendados: R$ 100.000,00. Total investido: R$ 99.730,00. Não investido por arredondamento: R$ 270,00.

### Caso B: tela da Figura 2, aporte de R$ 1.600,00 (aporte insuficiente)

| Ticker | Tipo | Qtd. | Preço | % Alvo |
|---|---|---|---|---|
| ITSA4 | Ação | 200 | R$ 9,50 | 10% |
| VALE3 | Ação | 50 | R$ 62,00 | 15% |
| WEGE3 | Ação | 100 | R$ 40,00 | 20% |
| MGLU3 | Ação | 1.000 | R$ 2,00 | 5% |
| MXRF11 | FII | 300 | R$ 10,50 | 15% |
| KNCR11 | FII | 20 | R$ 102,50 | 10% |
| IVVB11 | ETF | 50 | R$ 76,00 | 25% |

Total atual: R$ 20.000,00. Total pós-aporte: R$ 21.600,00.

| Ticker | Valor Atual | % Atual | Valor Alvo (Pós-Aporte) | Necessidade de Aporte | Status |
|---|---|---|---|---|---|
| ITSA4 | R$ 1.900,00 | 9,50% | R$ 2.160,00 | R$ 260,00 | APORTAR |
| VALE3 | R$ 3.100,00 | 15,50% | R$ 3.240,00 | R$ 140,00 | APORTAR |
| WEGE3 | R$ 4.000,00 | 20,00% | R$ 4.320,00 | R$ 320,00 | APORTAR |
| MGLU3 | R$ 2.000,00 | 10,00% | R$ 1.080,00 | nenhuma (defasagem negativa de R$ 920,00) | NÃO APORTAR |
| MXRF11 | R$ 3.150,00 | 15,75% | R$ 3.240,00 | R$ 90,00 | APORTAR |
| KNCR11 | R$ 2.050,00 | 10,25% | R$ 2.160,00 | R$ 110,00 | APORTAR |
| IVVB11 | R$ 3.800,00 | 19,00% | R$ 5.400,00 | R$ 1.600,00 | APORTAR |

Soma das necessidades positivas: R$ 2.520,00. **Resultado esperado:** o aporte inteiro (R$ 1.600,00) vai para o IVVB11, que compra 21 cotas (R$ 1.596,00). Os demais ativos têm Aporte Recomendado de R$ 0,00. Não investido: R$ 4,00.

### Caso B2: mesma carteira do Caso B, aporte de R$ 3.000,00

Ranking e alocação esperados:

| Rank | Ticker | Aporte Recomendado | Qtd. a comprar | Valor investido |
|---|---|---|---|---|
| 1 | IVVB11 | R$ 1.950,00 | 25 | R$ 1.900,00 |
| 2 | WEGE3 | R$ 600,00 | 15 | R$ 600,00 |
| 3 | ITSA4 | R$ 400,00 | 42 | R$ 399,00 |
| 4 | VALE3 | R$ 50,00 | 0 (não cobre uma cota de R$ 62,00) | R$ 0,00 |

MXRF11 e KNCR11 ficam com R$ 0,00 recomendados e MGLU3 continua "NÃO APORTAR". Total investido: R$ 2.899,00. Não investido: R$ 101,00.

### Caso C: carteira equilibrada

Ativos AAA3 (100 cotas a R$ 10,00, alvo 50%) e BBB4 (50 cotas a R$ 20,00, alvo 50%). Total atual: R$ 2.000,00.

- **Aporte R$ 0,00:** as duas defasagens são zero, os dois ativos ficam "NÃO APORTAR" (Cenário 1).
- **Aporte R$ 1.000,00:** cada ativo tem defasagem de R$ 500,00, e cada um recebe R$ 500,00 (AAA3: 50 cotas; BBB4: 25 cotas).

### Caso D: aporte que não cobre uma cota

Carteira do Caso B com aporte de R$ 5,00. O IVVB11 é o primeiro do ranking e recebe R$ 5,00 recomendados, mas a quantidade a comprar é 0 e o valor investido é R$ 0,00. O sistema não registra compra no histórico e mostra um aviso de que o aporte não cobre uma cota (RN06).

### Caso F: aporte encadeado depois de consolidar (feedback do professor)

Parte do Caso B consolidado: a quantidade de IVVB11 passa de 50 para 71. Novo aporte de R$ 1.000,00, com todos os outros dados iguais. Total atual: R$ 21.596,00.

| Ticker | Aporte Recomendado | Qtd. a comprar | Valor investido |
|---|---|---|---|
| WEGE3 | R$ 519,20 | 12 | R$ 480,00 |
| ITSA4 | R$ 359,60 | 37 | R$ 351,50 |
| VALE3 | R$ 121,20 | 1 | R$ 62,00 |

Os demais ativos ficam com R$ 0,00 e MGLU3 "NÃO APORTAR". Este caso prova o RF11: o segundo cálculo usou a quantidade nova, sem edição manual.

## 6.3. Testes de Comportamento

| ID | Teste | Resultado esperado |
|---|---|---|
| CT01 | Soma dos % Alvo diferente de 100% | Cálculo bloqueado com mensagem clara (RN03) |
| CT02 | Nenhuma venda recomendada em qualquer caso acima | Nenhum Aporte Recomendado negativo (RN01) |
| CT03 | Soma dos Aportes Recomendados | Igual ao valor do aporte, em todos os casos (RN05) |
| CT04 | Consolidar o Caso B | IVVB11 vai de 50 para 71; o histórico ganha 1 linha (data, IVVB11, 21, R$ 76,00, R$ 1.596,00); o campo de aporte zera (RN07, RF11, RF12) |
| CT05 | Persistência | Consolidar, fechar o programa, abrir de novo: quantidades e histórico continuam lá (RF10) |
| CT06 | Atomicidade | Se ocorrer erro no meio da consolidação, nenhuma quantidade muda e nada entra no histórico (RNF05) |
| CT07 | API fora do ar | O sistema avisa, usa o último preço salvo e aceita preço manual (RNF04) |
| CT08 | Token fora do repositório | `.env` está no `.gitignore` e não aparece em `git status` (RNF06) |
| CT09 | Histórico imutável | Não existe rota nem botão para editar ou apagar linhas do histórico (RN08) |

## 6.4. Desempenho

O desempenho é avaliado pelo tempo de resposta do cálculo (`POST /api/calcular`) com carteiras de até 20 ativos, com meta de execução inferior a 1 segundo (RNF02). O teste automático mede o tempo do motor de cálculo isolado com 20 ativos.
