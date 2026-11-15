# Entrega do desafio Onfly

## Requisitos e arquitetura

O programa consolida reservas de hotel em um relatório JSON a partir de dois CSVs. A saída reúne um resumo geral, os totais por mês de check-in e um ranking de hotéis por valor em reais.

O comando `python -m onfly_report` recebe `--input` e `--rates` como argumentos obrigatórios. `--output` tem o padrão `output/report.json` e `--top` aceita inteiros a partir de 1, com padrão 5. O CLI imprime um resumo no terminal. Os códigos de saída são 0 para sucesso, 2 para entrada ou argumento inválido e 1 para erro inesperado.

A estrutura inicial divide o trabalho entre os seguintes componentes.

| Parte | Responsabilidade |
| --- | --- |
| `cli.py` | Interpreta os argumentos, aciona o processamento e grava o JSON. |
| `repositories/` | Lê os arquivos de reservas e taxas de câmbio. |
| `row_parser.py` | Converte os campos da reserva para os tipos usados no cálculo. |
| `status_policy.py`, `stay_calculator.py` e `currency_converter.py` | Aplicam as regras de status, noites de quarto e câmbio. |
| `report_builder.py` | Coordena o processamento, agrega os resultados e monta o relatório. |

O fluxo é ler os CSVs, converter os tipos, contar os status, selecionar as reservas confirmadas e agregar os resultados. O enunciado permite reorganizar o código interno. O comando, os argumentos e o contrato do JSON devem ser preservados, assim como os CSVs `data/reservas_hoteis.csv` e `data/taxas_cambio.csv` e os arquivos de teste fornecidos.

## Regras de negócio

- Todas as reservas entram no total e na contagem do próprio status. Somente `CONFIRMED` entra nas noites, nos valores, no agrupamento mensal e no ranking.
- As noites de quarto são a diferença entre as datas completas de check-out e check-in, em dias, multiplicada pela quantidade de quartos. Uma estadia de 28 de janeiro a 2 de fevereiro em dois quartos soma 10 noites de quarto.
- O valor em reais é o valor da reserva multiplicado pela taxa da moeda no CSV. Os cálculos usam `Decimal`, com arredondamento `ROUND_HALF_UP` apenas na serialização. Os valores monetários saem como texto com duas casas decimais.
- A média por noite é o total em reais dividido pelas noites de quarto. Quando não há noites, o valor é `"0.00"`.
- O agrupamento usa o mês do check-in e ordena os meses de forma crescente.
- O ranking ordena os hotéis pelo total em reais do maior para o menor. Em caso de empate, usa o `hotel_id` em ordem crescente. O limite de `--top` é aplicado depois da ordenação.
- O JSON mantém a versão `"1.0"` e o campo `generated_at` com offset fixo `-03:00`. O horário de geração fica fora da comparação do conteúdo.

## Investigação e correções

A investigação inicial comparou o comportamento descrito no README com os testes fornecidos e as funções responsáveis pelos cálculos. A execução inicial no Python 3.11.18 registrou 5 falhas.

| Área | Causa identificada | Estado |
| --- | --- | --- |
| Status | O filtro exclui apenas `CANCELLED`, então inclui reservas `NO_SHOW` nos cálculos. | Corrigido. Apenas `CONFIRMED` passa pelo filtro. O teste de status passou. |
| Noites | O cálculo subtrai apenas o dia do mês, produzindo resultados incorretos nas viradas de mês ou ano. | Corrigido. A diferença usa as datas completas e é multiplicada pela quantidade de quartos. O teste de noites passou. |
| Câmbio | A conversão divide pela taxa e passa por `float`, embora a taxa represente o fator de multiplicação para BRL. | Corrigido. O valor é multiplicado pela taxa usando `Decimal`, com arredondamento apenas na saída. |
| Ranking | A ordenação por valor é crescente, então os hotéis de menor gasto aparecem primeiro. | Corrigido. O ranking usa primeiro o maior valor em reais e depois o menor `hotel_id` em caso de empate. |
| Leitura do CSV | O leitor encerrava o processamento ao atingir 200 reservas. | Corrigido. O leitor percorre o CSV até o fim. |
| Taxa ausente | A busca por uma moeda ausente na tabela gerava um erro inesperado de chave. | Corrigido. O CLI informa a moeda e retorna código 2. |
| Codificação do CSV | A falha ao decodificar UTF-8 escapava do tratamento dos erros de entrada. | Corrigido. Os dois leitores informam o erro e o CLI retorna código 2. |
| Taxa de câmbio não finita | A comparação com zero acontecia sem verificar se a taxa era finita. | Corrigido. A tabela aceita apenas taxas finitas e positivas. |

## Como validar

Na raiz do projeto, em um PowerShell com o ambiente Python 3.11 ativo e as dependências de `requirements-dev.txt` instaladas, execute os comandos abaixo.

```powershell
python --version
python -m pytest -q

$env:PYTHONPATH = "src"
python -m onfly_report --input data/exemplo-validacao.csv --rates data/taxas_cambio.csv --output output/exemplo.json
python -m onfly_report --input data/reservas_hoteis.csv --rates data/taxas_cambio.csv --output output/report.json
```

Compare `output/exemplo.json` com a amostra do README. O resumo esperado tem 12 reservas, 9 confirmadas, 2 canceladas, 1 não comparecimento, 28 noites de quarto, total de `"7566.00"` e média de `"270.21"`. Confira também os meses e a ordem dos hotéis.

**Resultado inicial do pytest** — 5 falhas no Python 3.11.18.

**Após corrigir o status** — 1 teste passou e 4 falharam no Python 3.11.18. A suíte ainda aponta falhas de câmbio, noites, ranking e regressão.

**Após corrigir as noites** — 2 testes passaram e 3 falharam no Python 3.11.18. As falhas restantes são de câmbio, ranking e regressão. A checagem de 30/12 a 02/01 com dois quartos retornou 6 noites de quarto.

**Após corrigir o câmbio** — 4 testes passaram e 1 falhou no Python 3.11.18. Os testes de câmbio e regressão passaram. Resta a falha de ranking. Na checagem de precisão, duas conversões de `0.0542` foram somadas e só então formatadas como `"0.11"`.

**Após corrigir o ranking** — os 5 testes fornecidos passaram no Python 3.11.18. A checagem adicional confirmou que, com dois hotéis de mesmo valor e `--top 1`, o menor `hotel_id` aparece no relatório.

A execução na amostra confirmou o resumo, os totais mensais e os cinco hotéis esperados no README.

**Após corrigir a leitura do CSV** — 6 testes passaram no Python 3.11.18, incluindo os 5 fornecidos. O teste novo reproduziu o corte antes da correção e agora confirma que as 201 reservas contribuem para as contagens, as noites e o valor total. Na base principal, o CLI contou 300 reservas, sendo 235 confirmadas, 31 canceladas e 34 não comparecimentos. O relatório registrou 1.347 noites de quarto, total de `"396170.00"` e média de `"294.11"` por noite de quarto.

**Após tratar a taxa ausente** — 7 testes passaram no Python 3.11.18, incluindo os 5 fornecidos. O teste novo confirmou o código de saída 2, a identificação da moeda sem taxa e a ausência de JSON de saída. A base principal voltou a produzir o relatório com as 300 reservas.

**Após corrigir os CSVs inválidos** — 11 testes passaram no Python 3.11.18, incluindo os 5 fornecidos. Os quatro casos novos confirmaram o código 2 para UTF-8 inválido nos dois CSVs e para taxas `NaN` e `Infinity`. O Ruff passou, e os exemplos de execução do README geraram os relatórios da amostra e da base principal.

## Painel interativo (extra)

O script em scripts/gerar_painel.py usa o JSON consolidado para exibir indicadores, gasto mensal, ranking de hotéis e contagem por status. A dependência opcional do Plotly está em requirements-painel.txt. Veja os [comandos de geração do painel](../README.md#painel-interativo-extra).

O HTML foi aberto no Chrome em modo offline com a base principal, a amostra e um relatório sem reservas confirmadas. Indicadores e valores dos gráficos foram conferidos contra o JSON. A base principal foi verificada em larguras de 320, 390 e 1.280 pixels. A suíte do CLI passou com 11 testes no Python 3.11.18, e o Ruff passou incluindo o novo script.
