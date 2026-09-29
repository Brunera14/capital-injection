# Capital Injection (contexto para o Claude Code)

Projeto Integrador da faculdade (CEUB). Calculadora de aporte que rebalanceia uma carteira de investimentos pelo método "sem venda". Uso pessoal, 1 usuário, roda no computador, não é site publicado.

## Como trabalhar comigo
- Sou iniciante em código. Explique cada passo em português simples, sem jargão.
- Faça uma fase por vez, começando pelo plano. Só codifique depois que eu aprovar.
- Rode os testes você mesmo e me mostre só o resultado.
- Ao fim de cada fase: git commit com mensagem clara em português e git push.
- Nunca commitar o arquivo .env (token da brapi). O repositório é público.
- Não adicionar nada além do pedido: sem login, sem gráficos, sem enfeites.
- Não use o caractere travessão nos textos que escrever (README, comentários, mensagens de commit).

## Fonte de verdade: a pasta docs/
Leia antes de codar, nesta ordem:
1. docs/03-regras-de-negocio.md: regras RN01 a RN08 e todas as fórmulas.
2. docs/06-planos-de-teste.md: casos com números esperados. Eles viram testes em tests/test_calculo.py e o código só está pronto quando todos passam. Se algum número não bater com o que você calculou, pare e me avise; não ajuste o teste para passar.
3. docs/04-arquitetura.md: tecnologias, modelo de dados SQLite, estrutura de pastas e rotas.
4. docs/05-interface-prototipacao.md: o que a tela do MVP deve ter (seção 5.4).
5. docs/02-requisitos.md e docs/07-implementacao-mvp.md: requisitos e ordem de construção.

## Resumo das decisões (detalhes nos docs)
- Stack fechada: Python, Flask, HTML/CSS/JavaScript sem framework, SQLite (sqlite3), brapi.dev, pytest. Decisão registrada no ADR 001 (issue #88).
- Cálculos com decimal.Decimal, nunca float.
- calculo.py não conhece banco, API nem tela: só funções puras.
- Consolidar aporte é atômico (tudo ou nada) e grava o histórico.
- A API de cotações é chamada só pelo backend. Se falhar, usar o último preço salvo ou o preço manual.

## Ordem de construção (uma por vez)
1. Esqueleto do projeto (issue #82)
2. Motor de cálculo com testes (issue #83)
3. Banco SQLite, consolidar e histórico (issue #86)
4. Tela de uma página (issue #85)
5. Cotações via brapi com preço manual de reserva (issue #84)
