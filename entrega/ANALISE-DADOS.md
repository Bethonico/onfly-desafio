# Análise das reservas de hotel

A base principal reúne **300 reservas** com check-in de 1º de dezembro de 2024 a 30 de junho de 2025. Das 300, **235 foram confirmadas**, 31 foram canceladas e 34 foram registradas como não comparecimento. As confirmadas somaram **1.347 noites de quarto** e **R$ 396.170,00**, com custo médio de **R$ 294,11 por noite de quarto**.

## Evolução mensal

| Mês do check-in | Confirmadas | Noites de quarto | Valor em reais | Valor por noite de quarto |
| --- | ---: | ---: | ---: | ---: |
| Dez/2024 | 35 | 174 | R$ 61.335,80 | R$ 352,50 |
| Jan/2025 | 37 | 235 | R$ 64.662,89 | R$ 275,16 |
| Fev/2025 | 26 | 138 | R$ 45.991,09 | R$ 333,27 |
| Mar/2025 | 39 | 215 | R$ 65.984,99 | R$ 306,91 |
| Abr/2025 | 21 | 146 | R$ 31.335,97 | R$ 214,63 |
| Mai/2025 | 39 | 196 | R$ 63.507,98 | R$ 324,02 |
| Jun/2025 | 38 | 243 | R$ 63.351,29 | R$ 260,70 |

- **Março teve o maior valor e junho teve o maior volume.** Junho registrou 28 noites de quarto a mais que março, com valor total menor. A média por noite de quarto foi de R$ 260,70 em junho e R$ 306,91 em março.
- **Abril teve a maior queda mensal.** Em relação a março, o valor caiu 52,5%. As noites de quarto caíram 32,1%, e o valor médio por noite caiu 30,1%.

## Status das reservas

Os cancelamentos e os não comparecimentos somaram **65 reservas**, ou **21,7% da base**. Dezembro teve a maior proporção desses dois status, com **18 de 53 reservas (34,0%)**. Foram 8 cancelamentos e 10 não comparecimentos entre as reservas com check-in previsto no mês.

## Hotéis e localização

Os cinco hotéis com maior valor nas reservas confirmadas concentraram **52,8% do total**. O **Hotel Salvador Centro** liderou em valor, com **R$ 45.165,46** em 160 noites de quarto. O **Hotel Miami Beach** teve o maior valor médio por noite entre os 12 hotéis da base, **R$ 392,90**.

Os hotéis fora do Brasil representaram **39,2% do valor total** das reservas confirmadas. A média por noite de quarto foi de **R$ 337,22** no exterior e **R$ 271,76** no Brasil, uma diferença de **24,1%** nesta base.

## Base e método

Usei a [base principal de reservas](../data/reservas_hoteis.csv) e a [tabela de câmbio do desafio](../data/taxas_cambio.csv). O mês é o do check-in. Duas noites em dois quartos contam como quatro noites de quarto. Para o total em reais e a média por noite, considerei as reservas confirmadas, converti os valores com a taxa da moeda e arredondei na apresentação. A média é o valor total convertido dividido pelas noites de quarto do mesmo grupo.

As comparações descrevem a base do desafio. Motivos de cancelamento e valores efetivamente cobrados exigiriam dados complementares.
