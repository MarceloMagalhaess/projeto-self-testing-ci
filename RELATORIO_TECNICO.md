# Wallet API --- Relatório Técnico

## Projeto Capstone: Microsserviço Financeiro com Self-Testing e CI

**Versão:** 1.0\
**Status:** Especificação inicial --- Fase 1\
**Linguagem:** Python 3.12+\
**Framework:** FastAPI\
**Testes:** Pytest\
**Banco de dados:** SQLite\
**Controle de versão:** Git e GitHub\
**Estratégia de branching:** Trunk-Based Development

------------------------------------------------------------------------

## 1. Visão geral

A Wallet API é uma API REST para gerenciamento simplificado de carteiras
digitais e conciliação de movimentações financeiras. O sistema permitirá
criar e consultar contas, transferir valores entre contas, consultar
extratos e integrar-se a um serviço externo fictício de análise
antifraude por webhook.

O projeto será desenvolvido com foco em qualidade de software, separação
de responsabilidades, integridade financeira, testabilidade e automação
de integração contínua.

### 1.1 Objetivo

Construir uma API demonstrável e testável que mantenha a consistência
dos saldos mesmo diante de solicitações repetidas ou concorrentes,
registrando as movimentações e verificando a integração externa por meio
de testes automatizados.

### 1.2 Escopo

Estão incluídos:

-   criação de contas digitais com saldo inicial;
-   consulta de contas e saldos;
-   transferência entre contas;
-   validação de saldo suficiente;
-   idempotência das solicitações de transferência;
-   proteção da consistência em operações concorrentes;
-   consulta de extrato com filtros;
-   notificação a um gateway antifraude fictício;
-   testes unitários, de integração e ponta a ponta;
-   pipeline de CI no GitHub Actions;
-   teste de carga com pelo menos 50 usuários virtuais concorrentes;
-   documentação técnica.

Não fazem parte do escopo inicial: integração com bancos reais,
movimentação de dinheiro real, autenticação bancária, liquidação
financeira externa ou análise antifraude baseada em inteligência
artificial.

------------------------------------------------------------------------

## 2. Requisitos de software

Os requisitos são identificados por códigos para facilitar
rastreabilidade, implementação e validação.

### 2.1 Requisitos funcionais (RF)

  -----------------------------------------------------------------------
  Código                  Descrição               Critério de aceitação
  ----------------------- ----------------------- -----------------------
  RF01                    O sistema deve criar    Uma solicitação válida
                          uma conta digital com   cria uma conta e
                          identificação e saldo   retorna seus dados.
                          inicial.                

  RF02                    O sistema deve          Uma conta existente
                          consultar uma conta     retorna seus dados e
                          pelo identificador.     saldo; uma inexistente
                                                  retorna HTTP 404.

  RF03                    O sistema deve          Uma transferência
                          transferir um valor de  válida debita a origem
                          uma conta de origem     e credita o destino
                          para uma conta de       pelo mesmo valor.
                          destino.                

  RF04                    O sistema deve impedir  A operação é recusada e
                          transferência com saldo os saldos permanecem
                          insuficiente.           inalterados.

  RF05                    O sistema deve oferecer Repetir uma solicitação
                          idempotência nas        com a mesma chave de
                          transferências.         idempotência não cria
                                                  uma segunda
                                                  movimentação.

  RF06                    O sistema deve proteger Operações simultâneas
                          a integridade das       não podem gerar saldo
                          transferências          negativo nem
                          concorrentes.           perda/criação de
                                                  valores.

  RF07                    O sistema deve          Cada transferência
                          registrar as            concluída gera
                          movimentações           registros de débito e
                          financeiras.            crédito associados.

  RF08                    O sistema deve          A resposta apresenta as
                          consultar o extrato de  movimentações
                          uma conta.              pertencentes à conta
                                                  solicitada.

  RF09                    O sistema deve filtrar  Os filtros de data
                          o extrato por período e inicial, data final e
                          tipo de movimentação.   tipo são aplicados
                                                  corretamente.

  RF10                    O sistema deve          A integração recebe os
                          notificar o gateway     dados definidos no
                          antifraude fictício     contrato de
                          sobre transferências.   notificação.

  RF11                    O sistema deve validar  Dados ausentes,
                          os dados recebidos nas  inválidos ou fora das
                          requisições.            regras são rejeitados
                                                  com resposta HTTP
                                                  apropriada.
  -----------------------------------------------------------------------

### 2.2 Requisitos não funcionais (RNF)

  -----------------------------------------------------------------------
  Código                  Descrição               Verificação
  ----------------------- ----------------------- -----------------------
  RNF01                   O código deve ser       Revisão da estrutura e
                          organizado em camadas   das dependências do
                          com responsabilidades   projeto.
                          separadas.              

  RNF02                   A cobertura de          Coverage.py no pipeline
                          linhas/statements deve  de CI.
                          ser de pelo menos 85%.  

  RNF03                   A cobertura de branches Coverage.py com medição
                          deve ser de pelo menos  de branches.
                          80%.                    

  RNF04                   Os testes devem ser     Execução do GitHub
                          executados              Actions.
                          automaticamente em push 
                          e pull request.         

  RNF05                   O teste de carga deve   Execução do Locust e
                          simular no mínimo 50    registro de métricas.
                          usuários virtuais       
                          concorrentes no         
                          endpoint de             
                          transferência.          

  RNF06                   As operações            Testes unitários,
                          financeiras devem       integração,
                          preservar a integridade concorrência e E2E.
                          dos saldos.             

  RNF07                   Valores monetários      Uso de `Decimal` na
                          devem utilizar          lógica de domínio e
                          representação decimal,  estratégia adequada de
                          sem aritmética          persistência.
                          financeira baseada em   
                          ponto flutuante         
                          binário.                

  RNF08                   A API deve fornecer     Testes dos códigos e
                          respostas HTTP e erros  formatos de resposta.
                          consistentes.           

  RNF09                   A configuração sensível Uso de variáveis de
                          e dependente do         ambiente e arquivo
                          ambiente não deve ser   `.env.example`.
                          versionada.             

  RNF10                   O projeto deve permitir Instruções e
                          execução local          dependências
                          reproduzível.           documentadas.
  -----------------------------------------------------------------------

**Observação sobre desempenho:** o requisito de 50 usuários virtuais é
uma condição do teste de carga, não uma promessa de 50 transferências
concluídas simultaneamente. A latência, taxa de falhas e limitações do
ambiente serão medidas e documentadas.

------------------------------------------------------------------------

## 3. Regras de negócio

1.  Uma conta deve possuir identificador único.
2.  O saldo inicial não pode ser negativo.
3.  O valor de uma transferência deve ser maior que zero.
4.  A conta de origem e a conta de destino devem existir.
5.  A conta de origem deve possuir saldo suficiente.
6.  Uma conta não pode transferir para ela mesma.
7.  Uma transferência concluída deve debitar a origem e creditar o
    destino pelo mesmo valor.
8.  Débito, crédito e registro da transferência devem ser persistidos de
    forma atômica: ou todos são confirmados, ou nenhum é.
9.  A chave de idempotência deve identificar uma solicitação lógica.
    Reutilizar a mesma chave com os mesmos dados deve retornar o
    resultado anterior; reutilizá-la com dados diferentes deve ser
    rejeitado.
10. O extrato deve distinguir movimentações de débito e crédito e
    permitir filtros por período.
11. A falha do serviço antifraude deve ter comportamento explicitamente
    definido. A primeira versão registrará a tentativa de notificação e
    tratará a integração como dependência externa; não deverá desfazer
    uma transferência já confirmada apenas porque a notificação falhou.
    O resultado da integração será testado e documentado.
12. Os valores monetários devem ser representados com precisão decimal.
    A persistência deverá evitar tipos de ponto flutuante.

------------------------------------------------------------------------

## 4. Arquitetura proposta

### 4.1 Estilo arquitetural

Será adotada uma arquitetura em camadas, com separação entre domínio,
aplicação, entrada HTTP e persistência. A API será um serviço
independente, embora o projeto acadêmico possa ser executado como uma
única aplicação.

### 4.2 Responsabilidades

  -----------------------------------------------------------------------
  Camada                              Responsabilidade
  ----------------------------------- -----------------------------------
  `domain`                            Entidades, tipos e regras
                                      fundamentais do negócio.

  `services`                          Casos de uso e orquestração das
                                      regras de negócio.

  `repositories`                      Contratos e implementações de
                                      acesso aos dados.

  `controllers`                       Endpoints HTTP, validação de
                                      entrada e serialização de
                                      respostas.

  Integração antifraude               Comunicação com o gateway externo
                                      fictício por meio de uma abstração
                                      substituível em testes.
  -----------------------------------------------------------------------

### 4.3 Fluxo de transferência

1.  O cliente envia uma requisição HTTP para o endpoint de
    transferência.
2.  O controller valida o formato da entrada e encaminha o caso de uso.
3.  O serviço verifica a chave de idempotência.
4.  O serviço valida as contas, o valor e o saldo disponível.
5.  O repositório executa a atualização dos saldos e o registro das
    movimentações dentro de uma transação atômica.
6.  Após a confirmação da operação, o serviço solicita a notificação
    antifraude.
7.  O controller retorna o resultado da transferência.

A implementação deverá evitar que a chamada HTTP externa mantenha uma
transação de banco de dados aberta por tempo desnecessário. Para uma
solução mais robusta, pode ser adotado o padrão Outbox; sua
implementação será avaliada conforme o tempo disponível.

### 4.4 Concorrência e integridade

A transferência é uma operação crítica porque altera duas contas. A
implementação deverá usar transação de banco de dados e mecanismos de
proteção contra atualizações concorrentes.

Como SQLite possui limitações de concorrência de escrita, o projeto
deverá adotar transações adequadas, restrições e tratamento de
bloqueios. O teste de carga deverá registrar essas limitações. Não será
afirmado que o sistema oferece escalabilidade de produção sem validação
em um banco apropriado para esse cenário.

### 4.5 Idempotência

O endpoint de transferência receberá uma chave de idempotência,
preferencialmente pelo cabeçalho `Idempotency-Key`.

O sistema deverá persistir a chave associada aos dados relevantes da
solicitação e ao resultado. Uma chave já utilizada não poderá executar
novamente a movimentação. Se a mesma chave for enviada com parâmetros
diferentes, a API deverá retornar conflito.

------------------------------------------------------------------------

## 5. Contrato inicial da API

Os caminhos e formatos abaixo são a proposta inicial e poderão ser
refinados durante a implementação.

  Método   Endpoint                             Finalidade
  -------- ------------------------------------ -------------------------
  POST     `/accounts`                          Criar conta
  GET      `/accounts/{account_id}`             Consultar conta e saldo
  POST     `/transfers`                         Transferir valores
  GET      `/accounts/{account_id}/statement`   Consultar extrato

### 5.1 Exemplo --- criação de conta

Requisição:

``` http
POST /accounts
Content-Type: application/json
```

``` json
{
  "owner_name": "João",
  "initial_balance": "500.00"
}
```

A resposta deverá apresentar o identificador criado, o titular e o saldo
inicial.

### 5.2 Exemplo --- transferência

Requisição:

``` http
POST /transfers
Content-Type: application/json
Idempotency-Key: transfer-001
```

``` json
{
  "source_account_id": "uuid-da-conta-origem",
  "destination_account_id": "uuid-da-conta-destino",
  "amount": "100.00"
}
```

Os valores monetários serão enviados como strings decimais para evitar
ambiguidades de representação no JSON.

### 5.3 Exemplo --- consulta de extrato

``` http
GET /accounts/{account_id}/statement?start_date=2026-01-01&end_date=2026-12-31&type=debit
```

Os filtros de data e tipo serão opcionais. Os tipos previstos são
`debit` e `credit`.

### 5.4 Códigos HTTP previstos

  Código   Uso
  -------- ----------------------------------------------------
  200      Consulta ou operação concluída
  201      Recurso criado
  400      Requisição inválida ou regra de negócio violada
  404      Conta ou recurso não encontrado
  409      Conflito de idempotência ou conflito de estado
  422      Erro de validação dos dados de entrada
  500      Erro interno inesperado
  503      Dependência externa indisponível, quando aplicável

Os códigos definitivos serão alinhados aos casos de uso e aos testes de
contrato.

------------------------------------------------------------------------

## 6. Estratégia de testes

Será utilizada a pirâmide de testes, priorizando testes unitários
rápidos, complementados por testes de integração e poucos testes E2E que
validem os principais fluxos.

### 6.1 Testes unitários

Local: `tests/unit/`

Validarão regras isoladas, sem depender de rede ou banco de dados real.

Casos previstos:

-   cálculo de saldo após débito e crédito;
-   rejeição de valor zero ou negativo;
-   rejeição de saldo insuficiente;
-   rejeição de transferência para a mesma conta;
-   comportamento da idempotência;
-   filtros e classificação de movimentações.

O desenvolvimento seguirá TDD, registrando evidências de
Red-Green-Refactor no histórico de commits.

### 6.2 Testes de integração

Local: `tests/integration/`

Validarão a colaboração entre serviços, repositórios, banco e integração
externa.

-   **Mocks:** verificar se o gateway antifraude foi chamado, quantas
    vezes e com quais parâmetros.
-   **Stubs:** fornecer respostas fixas e controladas para dependências
    de entrada, como validação cadastral ou cotação fictícia.
-   **Banco em memória:** testar persistência e transações sem utilizar
    a base de dados de desenvolvimento.

### 6.3 Testes E2E

Local: `tests/e2e/`

Utilizarão o `TestClient` do FastAPI para enviar requisições HTTP à
aplicação e validar fluxos completos.

Fluxo principal:

1.  Criar duas contas.
2.  Consultar os saldos.
3.  Transferir um valor.
4.  Consultar novamente os saldos.
5.  Consultar o extrato das duas contas.
6.  Verificar os registros de débito e crédito.

### 6.4 Cobertura

A ferramenta será Coverage.py, executada com medição de branches.

Metas obrigatórias:

-   linhas/statements: mínimo de 85%;
-   branches: mínimo de 80%.

O pipeline deverá falhar quando qualquer limite não for atingido.
Cobertura mede código executado, não substitui a qualidade das asserções
nem garante ausência de defeitos.

------------------------------------------------------------------------

## 7. Estratégia de branching e commits

### 7.1 Modelo escolhido: Trunk-Based Development

A branch `main` será a linha principal de desenvolvimento e deverá
permanecer em estado funcional. As funcionalidades serão implementadas
em branches curtas, integradas por Pull Requests.

Branches planejadas:

-   `feature/account-creation`
-   `feature/transfers`
-   `feature/statement`
-   `feature/anti-fraud`
-   `fix/transfer-validation`
-   `hotfix/...`

As branches são exemplos de nomenclatura; serão criadas conforme a
necessidade real do desenvolvimento.

### 7.2 Convenção de commits

Será adotado o padrão Conventional Commits:

  Prefixo       Uso
  ------------- -----------------------------------------------
  `feat:`       Nova funcionalidade
  `fix:`        Correção de defeito
  `test:`       Inclusão ou ajuste de testes
  `refactor:`   Refatoração sem mudança funcional intencional
  `docs:`       Documentação
  `ci:`         Configuração de integração contínua
  `build:`      Dependências e ferramentas de build

Exemplos:

``` text
feat: add account creation
test: cover insufficient balance
fix: prevent duplicate transfer processing
refactor: isolate transfer business rules
ci: add pytest and coverage workflow
docs: describe wallet api requirements
```

### 7.3 Pull Requests e proteção da branch principal

A branch `main` deverá ser protegida nas configurações do GitHub, quando
disponíveis, para exigir Pull Request e aprovação das verificações de CI
antes do merge.

Não serão feitos commits diretos de funcionalidades na `main`.

### 7.4 Correções emergenciais e merges documentados

A atividade exige pelo menos duas correções emergenciais ou merges
documentados. Essas evidências serão produzidas durante o
desenvolvimento, com problema, causa, solução, testes executados e
identificação do commit ou Pull Request.

Não serão inventados registros de correções que ainda não ocorreram. Os
eventos reais serão documentados nesta seção após sua execução.

------------------------------------------------------------------------

## 8. Pipeline de integração contínua

O workflow será criado em `.github/workflows/ci.yml`.

Eventos previstos:

-   `push` nas branches monitoradas;
-   `pull_request` direcionado à `main`.

Etapas previstas:

1.  Preparar ambiente Python.
2.  Instalar dependências.
3.  Executar Ruff para análise estática e lint.
4.  Executar testes unitários e de integração.
5.  Executar a suíte E2E.
6.  Medir cobertura de linhas e branches.
7.  Falhar se as metas mínimas não forem atingidas.
8.  Publicar relatórios e logs como artefatos.

A configuração de proteção da `main` no GitHub será necessária para que
a aprovação do workflow seja efetivamente exigida antes do merge.

------------------------------------------------------------------------

## 9. Teste de carga e desempenho

Será utilizado Locust para simular pelo menos 50 usuários virtuais
realizando requisições ao endpoint de transferência.

As métricas registradas serão:

-   quantidade de requisições;
-   quantidade e percentual de falhas;
-   latência média;
-   percentis de latência, quando disponíveis;
-   taxa de requisições por segundo;
-   comportamento diante de conflitos e contenção do banco.

O teste deverá utilizar contas e valores preparados para o cenário,
evitando que a falta de saldo invalide artificialmente toda a medição.
Os resultados reais, ambiente de execução, duração e limitações serão
registrados após a execução. Nenhum resultado de desempenho será
presumido neste documento.

------------------------------------------------------------------------

## 10. Estrutura planejada do repositório

``` text
projeto-self-testing-ci/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/
│   ├── domain/
│   ├── controllers/
│   ├── services/
│   └── repositories/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── .env.example
├── .gitignore
├── requirements.txt
├── Makefile
└── RELATORIO_TECNICO.md
```

Arquivos adicionais poderão ser criados conforme a necessidade técnica,
como `main.py`, configurações, modelos de persistência e módulos de
integração.

------------------------------------------------------------------------

## 11. Tecnologias e justificativas

  -----------------------------------------------------------------------
  Tecnologia              Finalidade              Justificativa
  ----------------------- ----------------------- -----------------------
  Python                  Linguagem               Produtividade e
                                                  ecossistema de testes.

  FastAPI                 API REST                Framework moderno com
                                                  validação e
                                                  documentação OpenAPI.

  Pytest                  Testes                  Organização de
                                                  fixtures,
                                                  parametrização e
                                                  asserções.

  HTTPX / TestClient      Testes HTTP             Validação dos endpoints
                                                  sem depender de
                                                  servidor externo.

  SQLite                  Persistência e testes   Banco leve e suporte a
                                                  banco em memória para
                                                  testes.

  Coverage.py             Cobertura               Medição de linhas e
                                                  branches.

  Ruff                    Qualidade estática      Lint e padronização de
                                                  código.

  Git / GitHub            Versionamento           Histórico, branches,
                                                  Pull Requests e
                                                  revisão.

  GitHub Actions          CI                      Automação de
                                                  verificações a cada
                                                  alteração.

  Locust                  Carga                   Simulação de usuários
                                                  concorrentes e coleta
                                                  de métricas.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 12. Riscos técnicos e medidas de mitigação

  -----------------------------------------------------------------------
  Risco                   Impacto                 Mitigação
  ----------------------- ----------------------- -----------------------
  Dupla execução de       Saldo incorreto         Chave de idempotência
  transferência                                   persistida e restrição
                                                  de unicidade.

  Concorrência entre      Atualização             Transações,
  transferências          inconsistente           bloqueios/controle de
                                                  escrita e testes
                                                  concorrentes.

  Falha do gateway        Notificação não enviada Isolamento da
  antifraude                                      integração, timeout,
                                                  tratamento de falha e
                                                  registro da tentativa.

  Cobertura abaixo da     Pipeline reprovado      Testes incrementais e
  meta                                            análise do relatório de
                                                  cobertura.

  Banco SQLite sob carga  Bloqueios e aumento de  Configuração e
                          latência                tratamento de
                                                  contenção; documentar
                                                  limites do ambiente.

  Integração frequente    Instabilidade da branch Branches curtas, Pull
  com defeitos            principal               Requests e CI
                                                  obrigatório.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 13. Critérios de conclusão e rastreabilidade

  -----------------------------------------------------------------------
  Entrega                             Evidência esperada
  ----------------------------------- -----------------------------------
  SRS                                 Este relatório técnico atualizado.

  Arquitetura                         Código organizado em camadas e
                                      responsabilidades identificáveis.

  Branching                           Histórico Git, branches, Pull
                                      Requests e merges documentados.

  TDD                                 Testes e commits que demonstrem
                                      Red-Green-Refactor.

  Testes unitários                    Suíte em `tests/unit/`.

  Mocks e Stubs                       Testes de integração com
                                      verificações de chamadas e dados
                                      controlados.

  Banco em memória                    Testes de integração isolados.

  E2E                                 Fluxo HTTP completo com TestClient.

  Cobertura                           Relatório Coverage.py atendendo aos
                                      limites.

  CI                                  Workflow executado e artefatos
                                      publicados.

  Carga                               Script Locust e relatório com
                                      métricas reais.
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 14. Plano de execução

  -----------------------------------------------------------------------
  Dia                     Atividade               Resultado esperado
  ----------------------- ----------------------- -----------------------
  1                       Requisitos, escopo,     Requisitos documentados
                          regras de negócio e SRS 

  2                       Arquitetura, estrutura, Base do projeto
                          Git e branching         organizada

  3                       TDD das regras          Testes unitários e
                          financeiras e           domínio
                          transferências          

  4                       Integração, Test        Suíte multinível
                          Doubles, persistência e 
                          E2E                     

  5                       GitHub Actions, Ruff e  CI automatizada
                          Coverage Gate           

  6                       Locust, concorrência e  Teste de carga e
                          resiliência             métricas

  7                       Revisão, histórico,     Entrega final
                          relatório e validação   
  -----------------------------------------------------------------------

------------------------------------------------------------------------

## 15. Histórico de validação do projeto

Esta seção deverá ser atualizada durante a execução. Os campos abaixo
não representam resultados já obtidos.

-   **Testes:** pendentes de implementação e execução.
-   **Cobertura de linhas:** pendente de medição.
-   **Cobertura de branches:** pendente de medição.
-   **Pipeline CI:** pendente de implementação e execução no GitHub.
-   **Teste de carga:** pendente de execução.
-   **Correções emergenciais/merges documentados:** pendentes de
    evidência no histórico Git.

### Registro de correções e merges

  Data          Commit/PR     Problema ou objetivo   Solução       Validação
  ------------- ------------- ---------------------- ------------- -------------
  A preencher   A preencher   A preencher            A preencher   A preencher
  A preencher   A preencher   A preencher            A preencher   A preencher

------------------------------------------------------------------------

## 16. Conclusão

A Wallet API será construída com foco em integridade financeira,
testabilidade e automação. A separação em camadas permitirá testar
regras de negócio independentemente da infraestrutura, enquanto os
testes de integração e E2E validarão a colaboração entre os componentes
e os fluxos HTTP.

O uso de TDD, Mocks, Stubs, banco em memória, cobertura automatizada,
GitHub Actions e teste de carga fornecerá evidências técnicas para os
critérios de avaliação do Capstone.

Este documento representa a especificação e o planejamento da Fase 1. Os
resultados de implementação, cobertura, CI, desempenho e histórico de
correções deverão ser preenchidos somente após sua execução e validação.
