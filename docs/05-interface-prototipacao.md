# 5. Interface e Prototipação

Esta seção apresenta os protótipos de alta fidelidade do Capital Injection, feitos no Figma no PI3, e define o que entra na primeira versão em código (MVP). As telas foram concebidas com foco na Usabilidade (RNF01): interface limpa, mínimo de campos e saída clara.

Protótipo interativo no Figma: [Design Screens for Capital Injection](https://www.figma.com/community/file/1629261141093957791/design-screens-for-capital-injection)

## 5.1. Tela Inicial (Home)

![Tela inicial do aplicativo Capital Injection](img/home.png)

*Figura 1: Tela inicial, com apresentação da proposta de valor e acesso rápido às funcionalidades.*

## 5.2. Tela de Aporte (Planilha de Rebalanceamento)

![Tela de aporte com a planilha de rebalanceamento](img/aporte.png)

*Figura 2: Tela principal de aporte, onde o usuário insere o valor mensal e visualiza a planilha de rebalanceamento com a necessidade de aporte calculada por ativo.*

Esta é a tela que define o MVP. Os números da Figura 2 (aporte de R$ 1.600,00 sobre uma carteira de R$ 20.000,00) são usados como caso de teste na seção 6 (Caso B).

## 5.3. Tela de Perfil

![Tela de perfil do usuário](img/perfil.png)

*Figura 3: Tela de perfil do usuário, com configurações de investimento, preferências e resumo da carteira.*

## 5.4. Escopo da Interface em Código (MVP)

A primeira versão em código implementa **uma única página**, baseada na Figura 2. Home, Dashboard, Sobre e Perfil ficam para depois e não fazem parte da entrega mínima.

**Elementos da página:**

| Elemento | Comportamento |
|---|---|
| Valor do aporte este mês | Campo numérico em R$ (RF01) |
| Patrimônio atual e patrimônio após o aporte | Calculados e exibidos ao lado do campo |
| Tabela da carteira | Colunas: Ativo, Ticker, Tipo, Sua Qtd., % Alvo, Preço Atual, Valor Atual, % Atual, Valor Alvo (Pós-Aporte), Necessidade de Aporte, Aporte Recomendado, Qtd. a comprar, Status |
| Células editáveis | Sua Qtd., % Alvo e Preço Atual (destacadas, como na Figura 2) |
| Linha de totais | Soma dos valores e dos percentuais |
| Validação da soma de % Alvo | Aviso visível quando a soma não é 100% (RN03), com o cálculo bloqueado |
| Botão "Calcular" | Gera o ranking sem gravar nada |
| Botão "Consolidar Aporte" | Confirma o aporte, atualiza quantidades e grava o histórico (RN07) |
| Botão "Atualizar cotações" | Busca os preços na API (seção 4.4) |
| Ranking de prioridade | Lista ordenada por defasagem com o valor recomendado de cada ativo (RF08) |
| Histórico de aportes | Tabela com data, ticker, quantidade, preço e valor investido (RF12) |
| Ativos "NÃO APORTAR" | Mostrados com a necessidade de aporte vazia, como na Figura 2 (MGLU3) |

**Fora do escopo do MVP:** login, gráficos, tema claro, telas de Home, Dashboard, Sobre e Perfil, importação de arquivos.
