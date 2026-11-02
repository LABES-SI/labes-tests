# QA06 — Contrato e composição detalhada (Sprint 4)

## Situação desta preparação

Este diretório contém a preparação independente de QA06: matriz de cenários, fixtures sintéticas e testes de domínio que já podem ser executados contra a função existente `calcular_indice_infraestrutura`.

**Importante:** o ZIP analisado da branch `feature/SIE-54-sprint4-infrastructure-composition` corresponde ao snapshot identificado pelo comentário do arquivo ZIP como `a41b64be4e5d2db76a573125ac8b94127537cea5`. Nesse snapshot não foram encontrados endpoint, schema Pydantic ou serviço específicos para a composição detalhada (BE09/BE10). Portanto, ainda não existem testes executáveis do contrato HTTP de composição, dos metadados nem do alerta da composição. Esses testes devem ser adicionados quando o contrato e a implementação correspondentes estiverem disponíveis.

## Escopo preparado

- valores `1`, `0` e `NULL`;
- contagem de presentes, válidos e sem dados;
- percentual do índice e cobertura;
- cálculo parcial sem bloqueio por cobertura mínima;
- valores inválidos;
- composição municipal por indicador, com dados sintéticos e resultados esperados;
- plano para metadados, alerta de baixa cobertura, escola não encontrada e escola existente sem histórico.

## O que não deve ser declarado como concluído ainda

- validação do schema HTTP de composição;
- validação dos nomes/tipos exatos dos campos de resposta;
- validação do alerta de baixa cobertura no payload;
- validação de 404 versus 200 sem histórico na nova rota de composição;
- teste integrado com o endpoint BE09/BE10.

## Execução dos testes de domínio preparatórios

Defina `LABES_API_ROOT` para a pasta do backend que contém `pyproject.toml` e `app/` e execute, na raiz do repositório `labes-tests`:

```powershell
uv run --project "$env:LABES_API_ROOT" python -m pytest "Código\Testes Automatizados\Sprint-4\QA-06\tests" -v
```

Esses testes exercitam apenas a função de domínio já existente. Eles não substituem os futuros testes de contrato e composição.

## Dependências para completar QA06

1. Contrato HTTP v3 completo (commit informado no planejamento: `f883ca2061ead757060a4fbf5dc0bae75d608742`).
2. Implementação BE09/BE10 presente na branch atualizada.
3. Confirmação da regra e do limiar do alerta de baixa cobertura, conciliando REQ-05, DAD-05 e o relatório de acompanhamento/DAD06.
