# QA06 — Testes automatizados de índice, cobertura e composição municipal (BE10)

## Resultado atual

**33 testes aprovados na execução local informada pela QA em 02/11/2026.** A duração, o código de saída e o XML JUnit da execução ainda precisam ser registrados a partir do terminal, caso não tenham sido salvos.

| Arquivo | Casos coletados | Camada |
|---|---:|---|
| `tests/test_qa06_indice_preparatorio.py` | 11 | Cálculo individual e cenários sintéticos de cobertura |
| `tests/test_qa06_be10_agregacao_municipal.py` | 16 | Domínio: agregação municipal por indicador |
| `tests/test_qa06_be10_servico_agregacao.py` | 6 | Serviço: orquestração e município histórico com repositório falso |
| **Total** | **33** | |

## Dependências

A variável `LABES_API_ROOT` deve apontar para uma cópia do `labes-api` que contenha:

- `app/domain/infraestrutura_agregacao_municipal.py`
- `app/services/infraestrutura_agregacao_municipal.py`

Esses módulos foram introduzidos pela BE10 (PR #15). Não copiar o backend para dentro do repositório `labes-tests`.

## O que a suíte valida

- Cálculo individual com valores `1`, `0` e `NULL`.
- Índice sem denominador válido e cenários sintéticos de cobertura.
- Contagens municipais de presentes, válidos, sem dados e escolas de referência.
- Percentual de presença e cobertura por indicador, incluindo denominador zero.
- Exclusão da escola-alvo da referência municipal.
- Rejeição de chaves, identificadores e valores inválidos ou duplicados.
- Uso do município histórico por ano e lacunas no período 2022–2025.
- Distinção entre escola inexistente, sem histórico e histórico sem município.

## Limites atuais

Os 33 testes **não** validam ainda:

- A resposta HTTP completa do contrato v3 da BE09.
- `composicao_escola` e todos os metadados v3 no payload.
- `cobertura_indicadores_reduzida` e os avisos na resposta HTTP.
- Os corpos reais dos erros HTTP `404`, `422`, `500` e `503` do contrato v3.
- Integração com warehouse real, frontend ou fluxo ponta a ponta.
- A amostra manual DAD06, que é responsabilidade da equipe de Dados.

A cobertura municipal por indicador é informativa e não recebe automaticamente o alerta de 60%. Para a escola, o alerta é estritamente abaixo de 60% e não bloqueia o cálculo, conforme a especificação BE09.

## Execução

Veja `INSTRUCOES.md` na raiz do pacote recebido e `evidencias/README-evidencias-QA06.md` para o registro do resultado e a geração dos artefatos de execução.
