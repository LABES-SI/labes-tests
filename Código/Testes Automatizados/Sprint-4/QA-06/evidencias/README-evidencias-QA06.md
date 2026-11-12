# Evidências de Testes — QA-06 | Sprint 4

## 1. Identificação

- **Projeto:** LABES — Sistema de Indicadores Educacionais (SIE)
- **Sprint:** 4
- **Atividade:** QA-06 — Testes de composição e comparação municipal
- **Repositório:** `LABES-SI/labes-tests`
- **Branch:** `test/qa06-sprint4-composicao`
- **Pull Request dos testes:** [PR #3](https://github.com/LABES-SI/labes-tests/pull/3)
- **Pull Request relacionado ao backend:** BE10 — PR #15

## 2. Resultado consolidado

Foram executados **40 cenários de teste distintos**, distribuídos em duas etapas de validação.

| Etapa | Quantidade | Aprovados | Falhas | Erros |
|---|---:|---:|---:|---:|
| Testes preparatórios, agregação municipal e serviço BE10 | 33 | 33 | 0 | 0 |
| Testes de integração HTTP | 7 | 7 | 0 | 0 |
| **Total** | **40** | **40** | **0** | **0** |

Todos os cenários executados foram aprovados, sem falhas, erros ou testes ignorados nos relatórios principais.

## 3. Primeira execução — testes preparatórios e BE10

**Data:** 02/11/2026  
**Python:** 3.12.2  
**Pytest:** 9.1.1  
**Duração:** 0,71 segundo

### Resultado

- Total: 33 testes
- Aprovados: 33
- Falhas: 0
- Erros: 0
- Ignorados: 0

### Distribuição dos testes

| Arquivo | Quantidade | Objetivo |
|---|---:|---|
| `test_qa06_indice_preparatorio.py` | 11 | Validar os cenários preparatórios do índice e da cobertura. |
| `test_qa06_be10_agregacao_municipal.py` | 16 | Validar a agregação municipal e as regras de composição. |
| `test_qa06_be10_servico_agregacao.py` | 6 | Validar o comportamento do serviço de agregação. |
| **Total** | **33** | |

### Evidências

- `qa06-20261102-215058.xml` — relatório JUnit da execução.
- `qa06-20261102-215058.log` — registro textual da execução.

O log registra a coleta e aprovação dos 33 testes, com resultado final de `33 passed in 0.71s`.

## 4. Segunda execução — integração HTTP

**Data:** 12/11/2026  
**Python:** 3.12.2  
**Pytest:** 9.1.1  
**Duração:** 0,19 segundo

### Resultado

- Total: 7 testes
- Aprovados: 7
- Falhas: 0
- Erros: 0
- Ignorados: 0

### Endpoint validado

`GET /infraestrutura/analise-temporal/escolas/{co_entidade}/comparacao-municipio`

Foi utilizada a escola:

- **Código INEP:** `15010201`
- **Nome:** E M E F PRINCESA ISABEL
- **Município:** Porto de Moz
- **Código do município:** `1505908`

### Cenários cobertos

1. Validação do contrato da resposta, identificação da escola e município.
2. Validação da série histórica de 2022 a 2025.
3. Validação dos indicadores e do índice da escola.
4. Validação da comparação entre o resultado da escola e a média municipal.
5. Validação da metodologia e da composição municipal.
6. Validação da resposta HTTP 422 para código INEP inválido.
7. Validação da resposta HTTP 404 para escola inexistente.

### Evidências

- `qa06-http-20261112-113204.xml` — relatório JUnit da execução HTTP.
- `qa06-http-20261112-113204.log` — registro textual da execução.

O log registra o resultado final de `7 passed in 0.19s`.

A execução foi realizada contra a API local, utilizando banco PostgreSQL populado.

## 5. Arquivos de evidência

| Arquivo | Descrição |
|---|---|
| `qa06-20261102-215058.xml` | Relatório JUnit dos 33 testes preparatórios e BE10. |
| `qa06-20261102-215058.log` | Log dos 33 testes preparatórios e BE10. |
| `qa06-http-20261112-113204.xml` | Relatório JUnit dos 7 testes de integração HTTP. |
| `qa06-http-20261112-113204.log` | Log dos 7 testes de integração HTTP. |
| `README.md` | Índice das evidências desta pasta. |
| `README-evidencias-QA06.md` | Documentação detalhada dos resultados e limitações. |

### Registros de execuções anteriores

Os arquivos `qa06-junit.xml` e `execucao-qa06.txt` correspondem a uma execução preparatória anterior, com 7 testes.

Esses registros foram mantidos como histórico, mas **não são somados novamente ao resultado consolidado de 40 testes**, pois seus cenários já estão contemplados na execução posterior de 33 testes.

## 6. Limitações e pendências identificadas

Apesar da aprovação dos 40 cenários executados, algumas validações permanecem fora do escopo efetivamente comprovado:

1. **Amostra manual DAD06:** a validação manual da amostra permanece sob responsabilidade da equipe de Dados.
2. **Códigos HTTP 500 e 503:** os cenários de erro interno e indisponibilidade do serviço não foram contemplados nesta execução HTTP.
3. **Base integrada completa:** a validação foi realizada com os dados disponíveis no ambiente utilizado, não representando uma homologação de toda a base histórica integrada.
4. **Metodologia:** a metodologia utilizada permanece provisória, sem aprovação definitiva registrada.

A execução HTTP utilizou uma escola específica e sua série histórica de 2022 a 2025. Portanto, os resultados comprovam os cenários testados, mas não devem ser interpretados como validação exaustiva de todas as escolas e municípios.

## 7. Publicação e rastreabilidade

- **Repositório de testes:** `LABES-SI/labes-tests`
- **Pull Request dos testes:** [PR #3](https://github.com/LABES-SI/labes-tests/pull/3)
- **Branch:** `test/qa06-sprint4-composicao`
- **Referência do backend:** BE10 — PR #15

O hash exato do commit do backend utilizado na execução de 33 testes não foi registrado nas evidências disponíveis. Por esse motivo, não é atribuído um hash específico a essa execução.

## 8. Conclusão

A automação QA-06 possui **40 cenários distintos aprovados**, distribuídos entre testes preparatórios, testes de agregação municipal, testes de serviço e testes de integração HTTP.

Os relatórios JUnit e os logs correspondentes comprovam a aprovação de todos os cenários executados, sem falhas ou erros.

Assim, a entrega de automação e das evidências dos cenários implementados pode ser considerada concluída. As limitações e validações externas descritas neste documento devem permanecer registradas para acompanhamento pela equipe responsável, sem serem confundidas com falhas nos testes executados.