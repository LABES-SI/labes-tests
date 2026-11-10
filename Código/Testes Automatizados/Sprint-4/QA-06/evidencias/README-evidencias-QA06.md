# Documento de evidências — QA06 | Sprint 4 | SIE V2

## 1. Identificação

- **Card:** QA06 — Automatizar testes do contrato e da composição.
- **Repositório de testes:** `LABES-SI/labes-tests`.
- **Branch de trabalho:** `test/qa06-sprint4-composicao` (confirmar branch local antes do push).
- **PR de referência:** [PR #3 — QA06](https://github.com/LABES-SI/labes-tests/pull/3). A PR foi aberta para a contribuição inicial; após o commit desta atualização, conferir se a PR mostra os novos arquivos e os 33 cenários.
- **Backend exercitado:** `rbecamend/labes-api`, implementação BE10/PR #15.
- **Data da execução informada:** 02/11/2026.
- **Resultado informado pela QA:** `33 passed`.
- **Duração / código de saída / SHA exato do backend:** não foram preservados na conversa. Preencher a partir do terminal e do `git rev-parse HEAD` do backend usado.

## 2. Escopo da suíte executada

| Arquivo | Casos | Resultado informado |
|---|---:|---|
| `tests/test_qa06_indice_preparatorio.py` | 11 | Aprovados |
| `tests/test_qa06_be10_agregacao_municipal.py` | 16 | Aprovados |
| `tests/test_qa06_be10_servico_agregacao.py` | 6 | Aprovados |
| **Total** | **33** | **33 aprovados** |

A contagem de 16 testes de domínio inclui variações parametrizadas de valores inválidos. Os 33 casos foram executados pela QA no ambiente local; esta documentação registra o resultado comunicado, sem inventar duração ou identificador de execução.

## 3. Principais cenários cobertos

### Índice individual e cobertura

- Preservação semântica de `1`, `0` e `NULL`.
- Exclusão de `NULL` do denominador válido.
- Índice indisponível quando não há respostas válidas.
- Casos sintéticos de cobertura abaixo, exatamente no e acima do limiar, além de denominador zero.
- Baixa cobertura não bloqueia o cálculo.

### Agregação municipal por indicador

- Quantidades de presentes, válidos, sem dados e escolas de referência.
- Percentual de presentes e cobertura por indicador.
- Nenhuma escola de referência e indicador sem valores válidos.
- Exclusão da escola selecionada.
- Precisão decimal e invariantes de contagem.
- Rejeição de identificadores duplicados/ausentes, valores inválidos e chaves ausentes.

### Serviço BE10

- Consulta de referência usando o município histórico de cada ano.
- Distinção entre escola inexistente e escola existente sem histórico.
- Histórico com município nulo.
- Município conhecido sem pares de referência.
- Rejeição de histórico duplicado ou inconsistente.

## 4. Evidências geradas

Para completar o registro auditável, executar novamente a suíte com o comando abaixo. Ele salvará o relatório JUnit e a saída do terminal dentro desta pasta:

```powershell
$repo = "C:/Users/karen/labes-tests"
Set-Location $repo
$qa = "Código\Testes Automatizados\Sprint-4\QA-06"
$evid = Join-Path $qa "evidencias"
New-Item -ItemType Directory -Path $evid -Force | Out-Null
$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$xml = Join-Path $evid "qa06-$stamp.xml"
$log = Join-Path $evid "qa06-$stamp.log"

$saida = & uv run --project "$env:LABES_API_ROOT" python -m pytest `
  (Join-Path $qa "tests") -v "--junitxml=$xml" 2>&1
$codigoSaida = $LASTEXITCODE
$saida | ForEach-Object { "$_" } | Set-Content -LiteralPath $log -Encoding utf8
$saida
Write-Host "Código de saída: $codigoSaida"
```

Preencher após essa execução:

- Backend SHA: `git -C "$env:LABES_API_ROOT" rev-parse HEAD`
- Backend branch: `git -C "$env:LABES_API_ROOT" branch --show-current`
- Data/hora e duração: copiar do resumo do pytest.
- Arquivo XML: nome gerado em `evidencias`.
- Arquivo de log: nome gerado em `evidencias`.
- Código de saída esperado: `0`.

**Não substituir a execução informada `33 passed` por uma duração ou SHA estimados.** Os dados acima devem vir de uma execução registrada.

## 5. Limitações e pendências conhecidas

A suíte usa dados artificiais e repositório falso para a camada de serviço. A execução aprovada comprova as regras cobertas nos testes, mas não é um aceite ponta a ponta.

Permanecem pendentes, quando a implementação integrada estiver disponível:

1. Testar a resposta HTTP v3 da BE09 contra o contrato versionado.
2. Conferir `composicao_escola`, `composicao_municipal`, `municipio_referencia` e `registro_historico_disponivel` no payload real.
3. Conferir `cobertura_indicadores_reduzida`, inclusive abaixo de 60%, exatamente 60% e acima de 60%, no payload HTTP.
4. Conferir metadados e avisos metodológicos.
5. Conferir os corpos reais de erro HTTP previstos no contrato.
6. Repetir os cenários relevantes com ambiente/warehouse integrado quando disponibilizado.

A validação da amostra manual e dos denominadores empíricos DAD06 permanece com a equipe de Dados; os fixtures sintéticos não substituem essa atividade.

## 6. Histórico de publicação no Git

- Branch prevista: `test/qa06-sprint4-composicao`.
- PR relacionado: [LABES-SI/labes-tests#3](https://github.com/LABES-SI/labes-tests/pull/3).
- Commit inicial citado na evidência anterior: `88a5c4b` — `test: add preparatory QA06 index tests`.
- **Commit de atualização dos 33 testes:** preencher depois do push.

## 7. Conclusão

A etapa automatizada de domínio e serviço BE10 da QA06 foi executada com **33 testes aprovados**, conforme resultado informado pela QA. A atividade deve permanecer em andamento/revisão até a validação do contrato HTTP v3 e das integrações previstas no escopo do card.
