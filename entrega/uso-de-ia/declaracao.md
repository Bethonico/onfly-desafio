# Declaração de uso de IA

Usei o **OpenAI Codex**, com o modelo `gpt-6.1-sol`, durante a resolução do teste técnico Onfly. O [registro consolidado da sessão](sessao.md) contém as solicitações e as respostas correspondentes.

## O que eu fiz

- Apresentei o material do desafio e defini, a cada etapa, quais correções e melhorias deveriam ser feitas.
- Preparei o ambiente Python 3.11 com `uv`, executei os testes e gerei os relatórios da amostra e da base principal no PowerShell.
- Criei as branches e fiz os commits das etapas do projeto. Pedi um painel com Plotly e, depois de ver a prévia interativa, solicitei o filtro mensal.

## O que o Codex fez

- Leu o enunciado, analisou a arquitetura e investigou as divergências entre o código, os testes e o relatório esperado.
- Editou a lógica de status, noites, câmbio e ranking. Corrigiu o limite de leitura do CSV e o tratamento de entradas inválidas. Criou testes de regressão em arquivos separados e executou os testes no Python 3.11.
- Implementou o painel opcional com Plotly e o filtro por mês de check-in a partir do JSON do CLI. Testou a geração e o uso offline no navegador.
- Atualizou as instruções de execução, registrou as causas dos defeitos e as validações no `README-ENTREGA.md` e preparou esta declaração e o registro consolidado.
