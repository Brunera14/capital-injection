# 3. Regras de Negócio

As regras de negócio definem as premissas e restrições lógicas que o sistema deve seguir para garantir a eficácia do método de investimento proposto pela calculadora. As regras RN01 a RN04 vêm do PI3 e continuam valendo; RN05 a RN08 formalizam o comportamento que já existia na planilha e as novidades do PI4.

## Regras do PI3 (mantidas)

**RN01: Aporte Exclusivo (Método Sem Venda)**
O sistema sob nenhuma circunstância recomendará a venda de um ativo para rebalancear a carteira. O rebalanceamento deve ser feito estritamente através da alocação inteligente do novo aporte financeiro mensal.

**RN02: Bloqueio de Aporte em Ativos no Alvo**
Ativos que, na comparação com o seu valor alvo, estiverem com uma alocação igual ou superior ao ideal receberão a indicação "NÃO APORTAR" no mês vigente.
*Esclarecimento (PI4):* a comparação é feita contra o **Valor Alvo pós-aporte** (definição na seção "Fórmulas"), e não contra o percentual da carteira antes do aporte. Na prática: se a **Defasagem** do ativo for menor ou igual a zero, o status é "NÃO APORTAR"; se for maior que zero, "APORTAR". É assim que a planilha do PI3 funciona (por exemplo, o HGLG11 tinha 25,6% contra alvo de 25%, mas seguia abaixo do seu valor alvo pós-aporte e recebia aporte).

**RN03: Somatório de Alocação**
A soma do "Percentual Alvo" definido pelo usuário para todos os ativos cadastrados na carteira deve corresponder obrigatoriamente a 100%. O sistema deve validar essa regra antes de gerar as recomendações e, se não bater, bloquear o cálculo e mostrar uma mensagem clara.

**RN04: Lógica de Priorização**
O algoritmo deve calcular a diferença financeira entre o valor ideal do ativo (baseado no percentual alvo) e o seu valor atual. O ativo com a maior defasagem financeira deve assumir o topo do ranking de prioridade para receber o aporte.

## Regras novas do PI4

**RN05: Distribuição do Aporte por Prioridade**
O aporte é distribuído percorrendo o ranking (RN04) do maior para o menor: cada ativo com status "APORTAR" recebe o menor valor entre a sua Defasagem e o que ainda resta do aporte, até o aporte acabar. Consequência: se o aporte for menor que a defasagem do primeiro colocado, ele recebe 100% do aporte. O valor recebido é o **Aporte Recomendado** do ativo. Como a soma das defasagens de todos os ativos é igual ao aporte, sempre existe defasagem positiva suficiente para alocar o aporte inteiro.

**RN06: Cotas Inteiras e Frações**
- **Ação, FII e ETF:** a quantidade a comprar é o Aporte Recomendado dividido pelo preço, **arredondado para baixo** (cota inteira). Nunca se gasta mais do que o Aporte Recomendado. Se ele não cobre o preço de uma cota, a quantidade a comprar é zero e nenhuma compra é sugerida para o ativo.
- **Renda Fixa:** a quantidade é sempre 1 e o "preço" é o saldo atual em Reais. O valor investido é exatamente o Aporte Recomendado, e o saldo aumenta nesse valor.
- **Cripto:** aceita quantidade fracionária (até 8 casas decimais). O valor investido é exatamente o Aporte Recomendado.
- O valor que sobra por causa do arredondamento de cotas inteiras fica como saldo não investido e **não** é redistribuído para outros ativos.

**RN07: Consolidação do Aporte**
Ao consolidar, o sistema, em uma única operação atômica (tudo ou nada): (1) soma a quantidade comprada à quantidade de cada ativo (Renda Fixa: soma o valor ao saldo); (2) grava uma linha no histórico para cada ativo que teve compra; (3) zera o valor do aporte. O próximo cálculo parte das quantidades novas, sem edição manual.

**RN08: Histórico Imutável**
Os registros do histórico só são inseridos, nunca editados ou apagados pela interface. Cada registro contém: data, ticker, quantidade comprada, preço e valor investido.

## Fórmulas

Para cada ativo *i*, com aporte *A*:

| Grandeza | Fórmula |
|---|---|
| Valor Atual | Quantidade × Preço Atual |
| Total Atual (T) | soma dos Valores Atuais de todos os ativos |
| % Atual | Valor Atual ÷ T |
| Total Pós-Aporte | T + A |
| Valor Alvo (Pós-Aporte) | % Alvo × (T + A) |
| Defasagem (Necessidade de Aporte) | Valor Alvo (Pós-Aporte) − Valor Atual |
| Status | "APORTAR" se Defasagem > 0; "NÃO APORTAR" caso contrário |
| Aporte Recomendado | preenchimento por prioridade (RN05) |
| Quantidade a comprar | conforme RN06 |
| Valor investido | Quantidade a comprar × Preço (Renda Fixa e Cripto: o próprio Aporte Recomendado) |

**Exemplo rápido:** carteira de R$ 20.000,00 e aporte de R$ 1.600,00. O IVVB11 vale R$ 3.800,00 e tem alvo de 25%. Valor Alvo pós-aporte = 25% × 21.600 = R$ 5.400,00. Defasagem = 5.400 − 3.800 = R$ 1.600,00. Como é a maior defasagem da carteira e é igual ao aporte, recebe o aporte inteiro (a R$ 76,00 por cota, são 21 cotas, R$ 1.596,00 investidos). Os casos completos com resultados esperados estão na seção 6.
