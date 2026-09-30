# Capital Injection

**Calculadora de Aporte Inteligente**: rebalanceamento de carteira de investimentos pelo método *sem venda*.

Projeto Integrador IV, Ciência da Computação, CEUB

Bruno Rodrigues Barcelos de Oliveira

---

## Sobre o projeto

O investidor comum perde tempo e erra ao decidir manualmente onde alocar o aporte do mês.
O **Capital Injection** resolve isso: o usuário informa quanto tem disponível e quais ativos possui,
e o sistema devolve o **ranking de prioridade** e o **valor exato de compra por ativo**, equilibrando
a carteira sem nunca recomendar a venda de nenhuma posição.

## Arquitetura atual

A partir do PI4, o projeto migrou de uma solução low code (Excel e Power BI) para uma aplicação em código, rodando localmente no computador do usuário:

| Camada | Tecnologia |
|---|---|
| Motor de cálculo e backend | Python |
| Interface | HTML, CSS e JavaScript, servidos localmente |
| Persistência de dados | SQLite (arquivo local, sem servidor externo) |
| Cotações em tempo real | API brapi.dev |

O motivo da mudança de arquitetura, incluindo o que foi avaliado e descartado (Supabase, entre outros), está documentado no [ADR 001](https://github.com/Brunera14/capital-injection/issues/88).

## Arquitetura anterior (histórico)

Até o PI3, o projeto foi desenvolvido como solução low code:

| Camada | Tecnologia |
|---|---|
| Motor de cálculo | Microsoft Excel (fórmulas nativas) |
| Cotações em tempo real | Função nativa de dados financeiros do Excel |
| Visualização e dashboard | Power BI (DAX e Power Query M) |
| Prototipação de interface | Figma |

Protótipo interativo no Figma: [Design Screens for Capital Injection](https://www.figma.com/community/file/1629261141093957791/design-screens-for-capital-injection)

Essa fase não foi apagada, só encerrada. A pesquisa, as regras de negócio e as personas continuam valendo para a versão em código.

## Documentação

A documentação completa do projeto, incluindo a fase anterior em Excel e Power BI e a fase atual em código, está em [`/docs`](docs/):

| Seção | Conteúdo |
|---|---|
| [1. Introdução](docs/01-introducao.md) | Problema, solução e público-alvo |
| [2. Requisitos do Sistema](docs/02-requisitos.md) | RF, RNF e histórias de usuário |
| [3. Regras de Negócio](docs/03-regras-de-negocio.md) | RN01 a RN04 |
| [4. Arquitetura e Integrações](docs/04-arquitetura.md) | Tecnologias, integrações e ALM |
| [5. Interface e Prototipação](docs/05-interface-prototipacao.md) | Telas de alta fidelidade |
| [6. Planos de Teste](docs/06-planos-de-teste.md) | Cenários e matriz de teste |
| [7. Implementação (MVP)](docs/07-implementacao-mvp.md) | Motor de cálculo |
| [8. Pesquisa de Campo](docs/08-pesquisa-de-campo.md) | Análise dos dados coletados |
| [9. Personas](docs/09-personas.md) | Três perfis validados |
| [10. Gestão Ágil](docs/10-gestao-agil.md) | Seis sprints e retrospectiva |

As regras de negócio, a pesquisa de campo e as personas seguem válidas para a fase atual em código.

## Estado do projeto

**PI-I a PI-III (concluído, solução low code)**

| Entrega | Situação |
|---|---|
| Documentação do sistema completa (29 páginas) | Feita |
| Pesquisa de campo com respondentes reais e três personas validadas | Feita |
| Protótipos de alta fidelidade no Figma | Feita |
| Motor de cálculo funcional, com todos os cenários de teste aprovados | Feita |
| Integração de cotações automatizada | Feita |
| Seis sprints registradas, com Daily Scrum e retrospectiva | Feita |

**PI4 (em andamento, migração para código)**

| Entrega | Situação |
|---|---|
| Decisão de arquitetura documentada em ADR ([issue #88](https://github.com/Brunera14/capital-injection/issues/88)) | Feita |
| GitHub reorganizado, board e milestones reestruturados a partir da Sprint 09 | Feita |
| Esqueleto do projeto ([issue #82](https://github.com/Brunera14/capital-injection/issues/82)) | Feita |
| Motor de cálculo em Python, com todos os casos de teste aprovados ([issue #83](https://github.com/Brunera14/capital-injection/issues/83)) | Feita |
| Banco SQLite, cadastro de ativos, consolidação atômica e histórico ([issue #86](https://github.com/Brunera14/capital-injection/issues/86)) | Feita |
| Tela de uma página, ligada às rotas do backend ([issue #85](https://github.com/Brunera14/capital-injection/issues/85)) | Feita |
| Cotações via brapi.dev, com preço manual de reserva ([issue #84](https://github.com/Brunera14/capital-injection/issues/84)) | Feita |
| Testes completos e validação final ([issue #87](https://github.com/Brunera14/capital-injection/issues/87)) | A fazer |

## Roadmap do PI4

| Sprint | Foco | Vencimento |
|---|---|---|
| Sprint 09 | Reestruturação e GitHub | 29/09/2026 |
| Sprint 10 | Desenvolvimento (motor de cálculo e cotações) | 20/10/2026 |
| Sprint 11 | Final de desenvolvimento (interface e histórico) | 10/11/2026 |
| Sprint 12 | Finalização e apresentação | 03/12/2026 |

O acompanhamento das tarefas é feito no [GitHub Projects](https://github.com/users/Brunera14/projects/2).

## Como rodar

```
python -m venv .venv
.venv\Scripts\activate          (Windows)
pip install -r requirements.txt
copy .env.example .env          (depois preencha BRAPI_TOKEN)
python app.py                   (abra http://127.0.0.1:5000)
pytest                          (roda os testes)
```

O `BRAPI_TOKEN` é opcional para alguns ativos (PETR4, MGLU3, VALE3 e ITUB4 funcionam sem token no plano gratuito da brapi.dev). Sem token ou sem internet, o sistema mantém o último preço salvo e aceita preço manual.

## Estrutura do repositório

```
.
├── app.py               rotas do Flask
├── calculo.py           motor de cálculo (funções puras)
├── banco.py             acesso ao SQLite (ativos, histórico, consolidação)
├── cotacao.py            consulta à brapi.dev com preço manual de reserva
├── seed_exemplo.py       carrega uma carteira de exemplo no banco
├── templates/index.html  página única
├── static/               app.js e style.css
├── tests/                test_calculo.py, test_banco.py, test_cotacao.py
├── docs/                 documentação completa do projeto (Markdown)
│   └── img/              figuras e capturas de tela
├── requirements.txt
├── .env.example
└── .gitignore
```
