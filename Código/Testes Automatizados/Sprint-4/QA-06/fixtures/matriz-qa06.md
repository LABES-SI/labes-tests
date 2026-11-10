# Matriz QA06 — índice preparatório, cobertura sintética e BE10

Esta matriz distingue três grupos de validação:

1. Testes preparatórios do índice individual e casos sintéticos DAD06, em `tests/test_qa06_indice_preparatorio.py`.
2. Testes independentes de domínio BE10, em `tests/test_qa06_be10_agregacao_municipal.py`.
3. Testes independentes de serviço BE10 com repositório falso, em `tests/test_qa06_be10_servico_agregacao.py`.

## A. Índice da escola e casos sintéticos pedidos por Dados/Backend

| ID | Entrada | Presentes | Válidos | Sem dados | Índice | Cobertura | Alerta conforme BE09 |
|---|---|---:|---:|---:|---:|---:|---|
| QA06-D01 | 7 Sim, 5 Não, 5 NULL (17 itens) | 7 | 12 | 5 | 58,33% | 70,59% | Não |
| QA06-D02 | 17 NULL | 0 | 0 | 17 | NULL | 0% | Sem registro não classifica; registro com 17 nulos tem cobertura reduzida |
| QA06-D03 | 5 Sim, 3 Não, 9 NULL (17 itens) | 5 | 8 | 9 | 62,50% | 47,06% | Sim, se campo BE09 integrado |
| QA06-D08 | 2 Sim, 1 Não, 2 NULL (5 itens sintéticos) | 2 | 3 | 2 | 66,67% | 60% | Não; fronteira exata, operador estritamente menor |
| QA06-D09 | 5 NULL (5 itens sintéticos) | 0 | 0 | 5 | NULL | 0% | Percentual NULL; não dividir por zero |
| QA06-D10 | 1 Sim, 1 Não, 3 NULL (5 itens sintéticos) | 1 | 2 | 3 | 50% | 40% | Sim, se campo BE09 integrado |
| QA06-D11 | 3 Sim, 1 Não, 1 NULL (5 itens sintéticos) | 3 | 4 | 1 | 75% | 80% | Não, se campo BE09 integrado |

**Limitação:** D08–D11 validam o cálculo da cobertura e o percentual na função de domínio. O teste não valida a presença/ausência real do campo `cobertura_indicadores_reduzida` na resposta HTTP, pois o serviço BE10 do patch ainda não publica a resposta BE09. O contrato BE09 define que o alerta aplica-se somente à cobertura da escola selecionada; cobertura municipal por indicador não recebe alerta automático.

## B. Agregação municipal BE10 — domínio

Para cada indicador e as escolas de referência do mesmo município histórico e ano, excluindo a escola-alvo:

- `quantidade_presentes`: respostas `1`;
- `quantidade_validos`: respostas `0` ou `1`;
- `quantidade_sem_dados`: respostas `None`;
- `quantidade_escolas_referencia`: total de outras escolas do município/ano;
- `percentual_presentes`: `100 * presentes / validos`, `None` se validos = 0;
- `cobertura_percentual`: `100 * validos / escolas_referencia`, `None` se não houver escolas.

| ID | Cenário | Resultado esperado |
|---|---|---|
| BE10-QA-01 | Contagens por indicador com 1/0/NULL; exclusão do alvo; filtros por município e ano | Contagens e percentuais corretos, exatamente 17 chaves |
| BE10-QA-02 | Nenhuma escola de referência | Contagens 0; percentual de presença e cobertura NULL |
| BE10-QA-03 | Escolas existem, mas todas têm NULL no indicador | Sem dados = total; percentual NULL; cobertura 0% |
| BE10-QA-04 | Respostas válidas somente 0 ou somente 1 | Percentual 0% ou 100%, cobertura 100% |
| BE10-QA-05 | Um presente em três válidos | Percentual 33,33%, sem arredondamento intermediário |
| BE10-QA-06 | Cobertura municipal do indicador com 3 válidos de 5 | Cobertura 60%; é informativa, não aciona alerta municipal |
| BE10-QA-07 | Município histórico da escola é NULL | Composição municipal indisponível (`None`) |
| BE10-QA-08 | Identificador de escola referência duplicado | ValueError de integridade |
| BE10-QA-09 | Identificador de referência ausente | ValueError de integridade |
| BE10-QA-10 | Valor 2, -1, True, string ou float | ValueError de valor inválido |
| BE10-QA-11 | Chave esperada ausente no registro | ValueError de integridade |
| BE10-QA-12 | Lista esperada vazia ou com duplicatas | ValueError de contrato |

## C. Serviço BE10 — histórico e orquestração

| ID | Cenário | Resultado esperado |
|---|---|---|
| BE10-QA-13 | Mesma escola em 2022 e 2024, com municípios diferentes | Consulta de pares utiliza o município histórico de cada ano |
| BE10-QA-14 | Escola inexistente versus escola existente sem histórico | NotFoundError versus série de quatro anos sem registro |
| BE10-QA-15 | Registro histórico com município NULL | Registro existente, sem município e sem composição municipal; não consulta pares |
| BE10-QA-16 | Município conhecido sem pares | 17 indicadores com contagens zero e percentuais NULL |
| BE10-QA-17 | Histórico duplicado no mesmo ano | ValueError antes das consultas de pares |
| BE10-QA-18 | Histórico de outra escola ou ano fora de 2022–2025 | ValueError de integridade |

## D. Limites da entrega QA

- Os testes BE10 exercitam domínio e serviço com dados artificiais e repositório falso; não acessam warehouse.
- O patch BE10 declara que ainda não cria rota nem envelope HTTP. Portanto, não são testes do endpoint BE09.
- A composição individual da escola, os metadados e `cobertura_indicadores_reduzida` precisam ser validados após integração BE09/BE10.
- A amostra manual DAD06 continua sendo responsabilidade da equipe de Dados. Estes testes sintéticos não a substituem.
