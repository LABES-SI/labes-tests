# Matriz de cenários — QA06: contrato e composição detalhada

## 1. Convenções e fonte de regra

- `1`: recurso presente (Sim).
- `0`: recurso ausente (Não), mas resposta válida.
- `NULL`: sem informação; não entra no denominador.
- Contrato de referência: 17 indicadores do conjunto utilizado no MVP, sujeito à homologação semântica documentada.
- Em cálculo escolar: `índice = 100 × presentes / válidos`, quando há ao menos um indicador válido.
- `cobertura = 100 × válidos / 17`.
- Para composição municipal por indicador: `percentual = 100 × escolas com valor 1 / escolas com valor 0 ou 1`.
- `sem_dados = total de registros - válidos`.

Os nomes exatos dos campos HTTP de composição devem ser copiados do contrato v3/BE09-10 quando disponíveis; não inferir nomes a partir desta matriz.

## 2. Cenários de domínio já executáveis no snapshot analisado

### QA06-D01 — Um indicador igual a 1

Entrada escolar: primeiro indicador `1`, demais 16 `NULL`.

Esperado: presentes = 1; válidos = 1; sem dados = 16; total = 17; índice = 100%; cobertura = 5,88%.

### QA06-D02 — Um indicador igual a 0

Entrada escolar: primeiro indicador `0`, demais 16 `NULL`.

Esperado: presentes = 0; válidos = 1; sem dados = 16; total = 17; índice = 0%; cobertura = 5,88%.

### QA06-D03 — Um indicador NULL

Entrada escolar: primeiro indicador `NULL`, demais 16 `1`.

Esperado: presentes = 16; válidos = 16; sem dados = 1; total = 17; índice = 100%; cobertura = 94,12%.

### QA06-D04 — Composição escolar mista

Entrada: 7 valores `1`, 5 valores `0` e 5 valores `NULL`.

Esperado: presentes = 7; válidos = 12; sem dados = 5; total = 17; índice = 58,33%; cobertura = 70,59%.

### QA06-D05 — Todos os indicadores NULL

Entrada: 17 valores `NULL`.

Esperado: presentes = 0; válidos = 0; sem dados = 17; total = 17; índice = NULL; cobertura = 0%.

### QA06-D06 — Baixa cobertura sem bloqueio do cálculo

Entrada: 5 valores `1`, 3 valores `0` e 9 valores `NULL`.

Esperado: presentes = 5; válidos = 8; sem dados = 9; índice = 62,50%; cobertura = 47,06%. O índice permanece calculável no MVP, pois o corte mínimo sistêmico é nulo.

**Alerta:** o teste do campo/estado do aviso depende do schema de composição BE09/BE10 e da confirmação do limiar. Não marcar alerta como validado usando apenas o teste de domínio.

### QA06-D07 — Valor inválido

Entrada contendo `2` em um indicador.

Esperado no domínio atual: `ValueError`; não converter o valor inválido silenciosamente em `0`, `1` ou `NULL`.

## 3. Cenário sintético de composição municipal por indicador (fixture para BE10)

Município: código fictício de teste `1501402`; ano: 2024; quatro escolas no mesmo recorte.

| Indicador | Valores nas quatro escolas | Presentes | Válidos | Sem dados | Percentual esperado |
|---|---|---:|---:|---:|---:|
| `in_agua_potavel` | `1, 0, NULL, 1` | 2 | 3 | 1 | 66,67% |
| `in_energia_rede_publica` | `0, 0, 1, NULL` | 1 | 3 | 1 | 33,33% |
| `in_esgoto_rede_publica` | `NULL, NULL, NULL, NULL` | 0 | 0 | 4 | NULL |
| Demais 14 indicadores | `1, 1, 0, 0` | 2 | 4 | 0 | 50,00% |

O futuro teste de contrato/serviço deverá confirmar que BE10 devolve os quatro elementos acima para cada indicador, usando os nomes e a estrutura exatos do contrato HTTP.

## 4. Cenários de contrato/serviço pendentes de BE09/BE10

### QA06-C01 — Metadados da composição

Validar presença, tipo, nulabilidade e consistência dos metadados definidos no contrato v3. A lista exata de campos deve vir do commit `f883ca2`/schema BE09; não inventar propriedades.

### QA06-C02 — Aviso de baixa cobertura

Validar o estado informativo do aviso e confirmar que os resultados continuam disponíveis. O limiar deve ser confirmado pela decisão DAD06/PO antes de fixar asserções de fronteira.

### QA06-C03 — Escola inexistente

A escola não existe na fonte consultada. Validar o status HTTP e o corpo de erro especificados no contrato BE09/BE10.

### QA06-C04 — Escola existente sem histórico no período

A escola é identificada, mas não possui registros no recorte de análise. Validar a resposta de sucesso/estado vazio/metadados conforme contrato, distinguindo-a de C03.

### QA06-C05 — Precisão: diferença

Índice da escola = `2/3`; referência = `1/3`. Resultado público esperado: `33,33` pontos percentuais, arredondado apenas na saída.

### QA06-C06 — Precisão: média municipal

Índices das comparadoras = `0` e `2/3`. Média exata = `1/3`; resultado público esperado: `33,33%`, arredondado apenas na saída.

### QA06-C07 — Exclusão da escola selecionada

A escola selecionada aparece propositalmente na massa de referências; deve ser excluída do cálculo municipal.

### QA06-C08 — Município histórico por ano

Para cada registro anual da escola, o município associado àquele registro deve ser usado na consulta/composição daquele ano. Não propagar o município mais recente para anos anteriores.

## 5. Observações de rastreabilidade

- A matriz separa testes executáveis no snapshot atual de testes pendentes de contrato/implementação.
- Não usar dump nem chamar a rota real para os testes unitários de domínio.
- Testes de contrato podem validar Pydantic/OpenAPI/payload com dados sintéticos e dependências substituídas, sem banco real, quando BE09/BE10 estiverem implementadas.
- Não tratar decisões metodológicas provisórias como homologação semântica dos 17 indicadores.
