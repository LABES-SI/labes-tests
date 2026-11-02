# Evidências — QA06

## Estado inicial

Ainda não há evidência de execução de testes de contrato da composição detalhada BE09/BE10, pois o snapshot do backend analisado não contém o respectivo endpoint/schema/serviço.

## Evidências preparatórias

- `fixtures/matriz-qa06.md`: cenários e oráculos esperados.
- `fixtures/composicao-municipal-2024.json`: registros sintéticos e resultado esperado por indicador.
- `tests/test_qa06_dominio_preparatorio.py`: testes de domínio que podem ser executados no snapshot atual.

Quando BE09/BE10 estiverem disponíveis, adicionar aqui:

- saída da suíte completa;
- XML JUnit;
- log em UTF-8;
- SHA exato do backend testado;
- referência ao commit do contrato BE09 e à implementação BE10.

Não registrar QA06 como concluído até os testes de contrato e composição serem executados contra a implementação correspondente.
