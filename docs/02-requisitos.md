# 2. Requisitos do Sistema

Nesta seção estão descritos os Requisitos Funcionais (RF) e Não Funcionais (RNF) do Capital Injection. Itens marcados como **(PI4)** são novos ou foram alterados na migração para código.

## 2.1. Requisitos Funcionais (RF)

Os requisitos funcionais descrevem o que o sistema deve fazer.

| ID | Nome | Descrição |
|---|---|---|
| **RF01** | Entrada de Valor do Aporte | O sistema deve permitir que o usuário insira o valor financeiro total (em Reais) disponível para o aporte do mês. |
| **RF02** | Cadastro de Ativos na Carteira | O sistema deve permitir que o usuário cadastre os ativos que possui em carteira, informando o Ticker (código do ativo) e o **Tipo** (Ação, FII, ETF, Renda Fixa ou Cripto). **(PI4)** |
| **RF03** | Quantidade e Preço Atual | Para cada ativo cadastrado, o sistema deve permitir a entrada da quantidade possuída ("Sua Qtd.") e do preço de mercado atual ("Preço Atual"). O preço de Ações, FIIs e ETFs é obtido automaticamente pela API brapi.dev; para Renda Fixa e Cripto, e como reserva quando a API falhar, o preço (ou saldo) é informado manualmente. **(PI4)** |
| **RF04** | Definição de Percentual Alvo (% Alvo) | O sistema deve permitir que o usuário defina o percentual ideal que cada ativo deve representar na carteira total. A soma de todos os percentuais alvo deve ser obrigatoriamente 100%. |
| **RF05** | Cálculo do Valor Atual da Posição | O sistema deve calcular automaticamente o valor atual de cada posição (Sua Qtd. × Preço Atual). |
| **RF06** | Cálculo do Percentual Atual (% Atual) | O sistema deve calcular o percentual que cada ativo representa na carteira atual, em relação ao valor total investido. |
| **RF07** | Cálculo de Rebalanceamento | O sistema deve calcular a "Necessidade de Aporte" comparando o Valor Alvo (Pós-Aporte) com o Valor Atual. O algoritmo deve distribuir o valor do "Aporte este mês" (RF01) priorizando os ativos mais distantes do seu percentual alvo. |
| **RF08** | Geração de Ranking de Prioridade | O sistema deve gerar e exibir uma tabela ("Ranking de Prioridade de Aporte") indicando exatamente quais ativos devem receber aporte e qual o valor financeiro recomendado para cada um. |
| **RF09** | Restrição de Vendas (Método Sem Venda) | O algoritmo não deve, em nenhuma hipótese, recomendar a venda de ativos que ultrapassaram o percentual alvo, focando o rebalanceamento exclusivamente na injeção de novo capital (compras). |
| **RF10** | Persistência da Carteira **(PI4)** | O sistema deve salvar a carteira (ativos, quantidades, percentuais alvo e últimos preços) e restaurá-la ao ser aberto novamente, sem que o usuário precise redigitar os dados. |
| **RF11** | Consolidar Aporte **(PI4)** | O sistema deve oferecer a ação "Consolidar Aporte", que atualiza automaticamente a quantidade de cada ativo com o que foi comprado, zera o valor do aporte e deixa a carteira pronta para o próximo mês, sem edição manual. |
| **RF12** | Histórico de Aportes **(PI4)** | A cada consolidação, o sistema deve registrar em um histórico consultável: data, ticker, quantidade comprada, preço e valor investido. |

## 2.2. Requisitos Não Funcionais (RNF)

Os requisitos não funcionais descrevem como o sistema deve operar, focando em atributos de qualidade, desempenho e restrições.

| ID | Nome | Descrição |
|---|---|---|
| **RNF01** | Usabilidade (Interface Intuitiva) | A interface deve ser simples e clara, permitindo que usuários iniciantes no mercado financeiro utilizem a ferramenta sem curva de aprendizado complexa. |
| **RNF02** | Desempenho (Cálculo em Tempo Real) | Os cálculos de rebalanceamento, atualização de percentuais e montagem do ranking devem ocorrer quase instantaneamente após a inserção ou alteração de qualquer dado de entrada (meta: menos de 1 segundo para carteiras de até 20 ativos). |
| **RNF03** | Precisão Matemática | O sistema deve garantir a precisão dos cálculos financeiros (duas casas decimais), evitando erros de arredondamento que prejudiquem a indicação de aporte. Valores monetários devem ser tratados com tipo decimal, nunca com ponto flutuante binário. |
| **RNF04** | Disponibilidade **(PI4, alterado)** | O sistema roda localmente no computador do usuário e deve abrir e funcionar a qualquer momento, sem depender de servidor externo. Se a API de cotações estiver indisponível, o sistema continua operando com o último preço salvo ou com preço manual. |
| **RNF05** | Integridade dos Dados **(PI4)** | Gravações no banco devem ser atômicas: uma consolidação de aporte é concluída por inteiro ou não acontece, nunca fica pela metade. |
| **RNF06** | Segurança do Token **(PI4)** | O token da API de cotações deve ficar em um arquivo `.env` fora do controle de versão (o repositório é público) e nunca deve ser enviado ao navegador. |
