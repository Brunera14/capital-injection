# Capital Injection

**Calculadora de Aporte Inteligente** — rebalanceamento de carteira de investimentos pelo método *sem venda*.

Projeto Integrador IV — Ciência da Computação — CEUB
Bruno Rodrigues Barcelos de Oliveira

---

## Sobre o projeto

O investidor comum perde tempo e erra ao decidir manualmente onde alocar o aporte do mês.
O **Capital Injection** resolve isso: o usuário informa quanto tem disponível e quais ativos possui,
e o sistema devolve o **ranking de prioridade** e o **valor exato de compra por ativo** — equilibrando
a carteira sem nunca recomendar a venda de nenhuma posição.

## Arquitetura

Solução **low code**, por decisão de projeto:

| Camada | Tecnologia |
|---|---|
| Motor de cálculo | Microsoft Excel (fórmulas nativas) |
| Cotações em tempo real | Função nativa de dados financeiros do Excel |
| Visualização / dashboard | Power BI (DAX + Power Query M) |
| Prototipação de interface | Figma |
| Gestão do projeto | GitHub Projects (Kanban) |

Protótipo interativo no Figma: [Design Screens for Capital Injection](https://www.figma.com/community/file/1629261141093957791/design-screens-for-capital-injection)

## Documentação

A documentação completa do sistema está em [`/docs`](docs/):

| Seção | Conteúdo |
|---|---|
| [1. Introdução](docs/01-introducao.md) | Problema, solução e público-alvo |
| [2. Requisitos do Sistema](docs/02-requisitos.md) | RF, RNF e histórias de usuário |
| [3. Regras de Negócio](docs/03-regras-de-negocio.md) | RN01 a RN04 |
| [4. Arquitetura e Integrações](docs/04-arquitetura.md) | Tecnologias, integrações e ALM |
| [5. Interface e Prototipação](docs/05-interface-prototipacao.md) | Telas de alta fidelidade |
| [6. Planos de Teste](docs/06-planos-de-teste.md) | Cenários e matriz de teste |
| [7. Implementação — MVP](docs/07-implementacao-mvp.md) | Motor de cálculo |
| [8. Pesquisa de Campo](docs/08-pesquisa-de-campo.md) | Análise dos dados coletados |
| [9. Personas](docs/09-personas.md) | Três perfis validados |
| [10. Gestão Ágil](docs/10-gestao-agil.md) | Seis sprints e retrospectiva |

## Estado do projeto

Desenvolvido ao longo de PI-I, PI-II e PI-III, com as seguintes entregas já consolidadas:

- Documentação do sistema completa (29 páginas)
- Pesquisa de campo com respondentes reais e três personas validadas
- Protótipos de alta fidelidade no Figma
- Motor de cálculo funcional, com todos os cenários de teste aprovados
- Integração de cotações automatizada
- Seis sprints registradas, com Daily Scrum e retrospectiva

## Roadmap — PI4

- [ ] Migrar a documentação para este repositório
- [ ] Migrar backlog e sprints para o GitHub Projects
- [ ] Construir o dashboard em Power BI
- [ ] Plano de contingência
- [ ] Rodada final de testes
- [ ] Vídeo demonstrativo
- [ ] Apresentação final

## Estrutura do repositório

```
.
├── docs/          documentação do sistema (Markdown)
│   └── img/       figuras e capturas de tela
├── src/           motor de cálculo e camada de visualização
└── README.md
```
