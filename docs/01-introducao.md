# 1. Introdução

## 1.1. O Problema e as Dores do Usuário

O processo de investir mensalmente exige disciplina e análise. A principal "dor" do investidor comum é a perda de tempo e a complexidade matemática na hora de decidir onde alocar o novo dinheiro. Fazer o cálculo manual de rebalanceamento da carteira todos os meses gera dúvidas, estresse e aumenta a chance de erros (como vender ativos na baixa ou aportar em ativos que já estão acima do percentual ideal).

## 1.2. A Solução e o Resultado Esperado

Para solucionar esse problema, o **Capital Injection** propõe uma calculadora automatizada de aporte. O motivo do desenvolvimento é abstrair a complexidade analítica do mercado de capitais. O resultado esperado é que o usuário apenas informe quanto dinheiro tem disponível no mês e quais ativos possui; o sistema entregará, de forma imediata, uma lista de prioridades e os valores exatos de compra para cada ativo, garantindo o equilíbrio da carteira através do "rebalanceamento sem vendas".

Além de calcular, o sistema **lembra a carteira** entre um mês e outro: ao consolidar um aporte, as quantidades de cada ativo são atualizadas automaticamente e a compra fica registrada em um histórico. No mês seguinte, o usuário não precisa digitar tudo de novo.

**Evolução da solução:** no PI3, a solução foi construída em Microsoft Excel e Power BI (arquitetura low code). No PI4, o motor de cálculo e a interface foram reescritos em código (Python, SQLite e HTML/CSS/JavaScript), mantendo as mesmas regras de negócio. O motivo da mudança está documentado no ADR 001 (issue #88 do repositório) e resumido na seção 4.

## 1.3. Público-Alvo

O sistema é destinado a investidores pessoas físicas (PF), englobando desde indivíduos iniciantes, que buscam criar o hábito de investir com disciplina e clareza sem precisarem ser especialistas no mercado financeiro, até investidores experientes, que desejam otimizar seu tempo e evitar o desgaste de calcular o rebalanceamento de múltiplos ativos (CDB, Tesouro Direto, Ações, FIIs, ETFs) mensalmente.
