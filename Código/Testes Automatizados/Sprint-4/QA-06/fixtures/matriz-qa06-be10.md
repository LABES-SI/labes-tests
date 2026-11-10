# Matriz QA06 — BE10: agregação municipal por indicador

## Escopo desta suíte

Os testes desta matriz exercitam diretamente a função de domínio `agregar_indicadores_municipais()` e o serviço `InfraestruturaAgregacaoMunicipalService.calcular_serie()` adicionados pela BE10.

A suíte é independente, utiliza registros artificiais e repositório falso. Não acessa o warehouse e não chama uma rota HTTP. Ela só poderá ser executada quando a cópia local do backend contiver os módulos da BE10:

- `app/domain/infraestrutura_agregacao_municipal.py`
- `app/services/infraestrutura_agregacao_municipal.py`

## Regras do agregado municipal

Para cada indicador e para as escolas de referência do mesmo município histórico e ano, excluindo a escola-alvo:

- presentes = quantidade de valores `1`;
- válidos = quantidade de valores `0` ou `1`;
- sem dados = quantidade de valores `None`;
- escolas de referência = total de outras escolas encontradas no município e ano;
- percentual de presença = `100 * presentes / válidos`; `None` quando válidos for zero;
- cobertura municipal do indicador = `100 * válidos / escolas de referência`; `None` quando não houver escolas de referência.

Invariantes:

- `presentes <= válidos`;
- `válidos + sem dados = escolas de referência`;
- escola selecionada excluída;
- apenas mesmo município histórico e mesmo ano entram na contagem;
- `None` não é convertido em zero.

## Cenários automatizados de domínio

| ID | Cenário | Evidência esperada |
|---|---|---|
| BE10-QA-01 | Contagens por indicador com `1`, `0` e `None`, exclusão da escola-alvo e filtros de município/ano | Contagens, percentuais e 17 chaves corretos |
| BE10-QA-02 | Município conhecido sem escolas de referência | Contagens zero; presença e cobertura `None` |
| BE10-QA-03 | Escolas de referência existentes, todas com indicador nulo | Sem dados igual ao total; presença `None`; cobertura 0% |
| BE10-QA-04 | Percentuais válidos de 0% e 100% | Zero não confundido com ausência de dados |
| BE10-QA-05 | Precisão na saída | 1/3 = 33,33%, sem arredondamento intermediário |
| BE10-QA-06 | Município histórico da escola ausente | Agregação retorna `None` |
| BE10-QA-07 | Escola de referência duplicada | Erro de integridade |
| BE10-QA-08 | Escola de referência sem identificador | Erro de integridade |
| BE10-QA-09 | Valores inválidos (`2`, `-1`, `True`, texto e float) | Erro de validação |
| BE10-QA-10 | Indicador esperado ausente no registro | Erro de integridade |
| BE10-QA-11 | Lista de indicadores vazia ou com duplicatas | Erro de validação |

## Cenários automatizados de serviço

| ID | Cenário | Evidência esperada |
|---|---|---|
| BE10-QA-12 | Escola muda de município entre 2022 e 2024 | Consulta de pares usa município do registro de cada ano |
| BE10-QA-13 | Escola inexistente versus existente sem histórico | `NotFoundError` versus série de quatro anos sem registro |
| BE10-QA-14 | Registro histórico com município nulo | Registro reconhecido; não consulta pares; composição municipal `None` |
| BE10-QA-15 | Município conhecido sem pares | 17 indicadores, contagens zero e percentuais `None` |
| BE10-QA-16 | Histórico duplicado | Erro antes de consultar pares |
| BE10-QA-17 | Histórico de outra escola ou ano fora de 2022–2025 | Erro de integridade |

## Limites: o que esta suíte não valida

- Não valida o alerta da escola selecionada no payload HTTP; o serviço BE10 do patch não retorna `cobertura_indicadores_reduzida` nem os metadados BE09.
- Não valida o endpoint/response HTTP v3.
- Não valida a composição individual da escola, que ainda precisa ser integrada ao serviço/contrato BE09.
- Não substitui a amostra manual da DAD06.
- A cobertura municipal por indicador não recebe alerta automaticamente; ela é informativa.

## Relação com os casos sintéticos DAD06

Os cenários de escola com cinco indicadores esperados (3/5 = 60%, 2/5 = 40%, 4/5 = 80% e denominador válido zero) ficam na suíte `test_qa06_indice_preparatorio.py` e exercitam `calcular_indice_infraestrutura()` com lista esperada sintética de cinco itens. Eles validam percentuais e disponibilidade do índice, mas não validam a apresentação do alerta na resposta HTTP.

A cobertura de `composicao_municipal` nesta matriz é outra métrica: `válidos / escolas de referência`. O contrato BE09 determina que a cobertura municipal por indicador não recebe classificação automática de baixa cobertura.
