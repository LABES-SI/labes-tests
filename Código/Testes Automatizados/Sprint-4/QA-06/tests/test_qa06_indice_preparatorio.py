"""Testes preparatórios QA06 para regras de cálculo e cobertura sintética.

Estes testes exercitam a função de domínio já existente no backend.
Eles NÃO validam o alerta no payload HTTP ou na interface: o snapshot
analisado ainda não contém implementação de composição/alerta BE09/BE10.
"""

import json
import os
import sys
from pathlib import Path

import pytest

API_ROOT_TEXT = os.environ.get("LABES_API_ROOT")
if not API_ROOT_TEXT:
    raise RuntimeError("Defina LABES_API_ROOT para a pasta do backend.")

API_ROOT = Path(API_ROOT_TEXT).resolve()
if not (API_ROOT / "app" / "domain" / "infraestrutura.py").is_file():
    raise RuntimeError(f"Backend não encontrado em: {API_ROOT}")

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.domain.infraestrutura import calcular_indice_infraestrutura  # noqa: E402

INDICADORES_ESPERADOS = (
    "in_agua_potavel",
    "in_energia_rede_publica",
    "in_esgoto_rede_publica",
    "in_lixo_servico_coleta",
    "in_banheiro",
    "in_banheiro_pne",
    "in_biblioteca",
    "in_sala_leitura",
    "in_laboratorio_ciencias",
    "in_laboratorio_informatica",
    "in_sala_multiuso",
    "in_sala_atendimento_especial",
    "in_cozinha",
    "in_refeitorio",
    "in_quadra_esportes",
    "in_patio_coberto",
    "in_auditorio",
)

assert len(INDICADORES_ESPERADOS) == 17

FIXTURE_PATH = (
    Path(__file__).resolve().parents[1]
    / "fixtures"
    / "cobertura-dad06.json"
)
with FIXTURE_PATH.open(encoding="utf-8") as arquivo:
    FIXTURE_COBERTURA = json.load(arquivo)

CASOS_COBERTURA = FIXTURE_COBERTURA["casos"]
INDICADORES_SINTETICOS_5 = INDICADORES_ESPERADOS[:5]


def calcular(
    valores: list[int | None],
    indicadores_esperados: tuple[str, ...] = INDICADORES_ESPERADOS,
):
    """Executa o cálculo sem impor cobertura mínima.

    O conjunto pode ter cinco indicadores nos casos sintéticos de fronteira;
    os casos gerais continuam utilizando os 17 indicadores do MVP.
    """
    if len(valores) != len(indicadores_esperados):
        raise ValueError(
            "A quantidade de valores deve corresponder aos indicadores esperados."
        )

    indicadores = dict(zip(indicadores_esperados, valores, strict=True))
    return calcular_indice_infraestrutura(
        indicadores,
        indicadores_esperados=indicadores_esperados,
        cobertura_minima_percentual=None,
    )


def executar_caso_sintetico(caso_id: str):
    caso = CASOS_COBERTURA[caso_id]
    resultado = calcular(caso["valores"], INDICADORES_SINTETICOS_5)
    return caso, resultado


# ---------------------------------------------------------------------------
# Sete cenários preparatórios já existentes: contrato geral de 17 indicadores
# ---------------------------------------------------------------------------


def test_composicao_conta_presentes_validos_sem_dados_e_percentual():
    """7 Sim, 5 Não e 5 NULL: 7/12 = 58,33%; 5 sem dados."""

    resultado = calcular([1] * 7 + [0] * 5 + [None] * 5)

    assert resultado.presentes == 7
    assert resultado.validos == 12
    assert resultado.total_indicadores == 17
    assert resultado.total_indicadores - resultado.validos == 5
    assert resultado.percentual == 58.33
    assert resultado.cobertura_indicadores_percentual == 70.59


def test_composicao_todos_nulos_nao_retorna_indice_zero():
    resultado = calcular([None] * 17)

    assert resultado.presentes == 0
    assert resultado.validos == 0
    assert resultado.total_indicadores == 17
    assert resultado.total_indicadores - resultado.validos == 17
    assert resultado.percentual is None
    assert resultado.cobertura_indicadores_percentual == 0.0


def test_indice_parcial_com_baixa_cobertura_nao_e_bloqueado_no_mvp():
    """5 Sim, 3 Não e 9 NULL: índice 62,5%, cobertura 47,06%."""

    resultado = calcular([1] * 5 + [0] * 3 + [None] * 9)

    assert resultado.presentes == 5
    assert resultado.validos == 8
    assert resultado.total_indicadores - resultado.validos == 9
    assert resultado.percentual == 62.5
    assert resultado.cobertura_indicadores_percentual == 47.06


def test_valor_fora_do_contrato_e_rejeitado():
    valores = [1] * 16 + [2]
    with pytest.raises(ValueError, match="devem ser 0, 1 ou None"):
        calcular(valores)


def test_um_indicador_sim_e_demais_nulos():
    resultado = calcular([1] + [None] * 16)
    assert resultado.presentes == 1
    assert resultado.validos == 1
    assert resultado.total_indicadores == 17
    assert resultado.percentual == 100.0
    assert resultado.cobertura_indicadores_percentual == 5.88


def test_um_indicador_nao_e_demais_nulos():
    resultado = calcular([0] + [None] * 16)
    assert resultado.presentes == 0
    assert resultado.validos == 1
    assert resultado.total_indicadores == 17
    assert resultado.percentual == 0.0
    assert resultado.cobertura_indicadores_percentual == 5.88


def test_um_indicador_nulo_e_demais_sim():
    resultado = calcular([None] + [1] * 16)
    assert resultado.presentes == 16
    assert resultado.validos == 16
    assert resultado.total_indicadores == 17
    assert resultado.percentual == 100.0
    assert resultado.cobertura_indicadores_percentual == 94.12


# ---------------------------------------------------------------------------
# Quatro cenários sintéticos solicitados por Backend/Dados
# ---------------------------------------------------------------------------


def test_cobertura_exatamente_60_por_cento_sem_aviso_esperado():
    """3 válidos de 5 = 60%; índice disponível e sem alerta esperado.

    A função de domínio não gera o campo de alerta. A expectativa de não
    exibir aviso em exatamente 60% está documentada no JSON/matriz e será
    assertada no contrato/serviço quando BE09/BE10 disponibilizar o campo.
    """
    caso, resultado = executar_caso_sintetico("QA06-D08")
    esperado = caso["esperado"]

    assert resultado.presentes == esperado["presentes"] == 2
    assert resultado.validos == esperado["validos"] == 3
    assert resultado.total_indicadores == esperado["total"] == 5
    assert resultado.total_indicadores - resultado.validos == esperado["sem_dados"] == 2
    assert resultado.percentual == esperado["percentual"] == 66.67
    assert resultado.cobertura_indicadores_percentual == esperado["cobertura_percentual"] == 60.0
    assert caso["alerta_esperado"] == "nao_exibir"


def test_denominador_zero_retorna_percentual_nulo_sem_divisao_por_zero():
    """Nenhum valor válido: percentual NULL, nunca 0%, sem exceção."""
    caso, resultado = executar_caso_sintetico("QA06-D09")
    esperado = caso["esperado"]

    assert resultado.presentes == esperado["presentes"] == 0
    assert resultado.validos == esperado["validos"] == 0
    assert resultado.total_indicadores == esperado["total"] == 5
    assert resultado.total_indicadores - resultado.validos == esperado["sem_dados"] == 5
    assert resultado.percentual is esperado["percentual"] is None
    assert resultado.cobertura_indicadores_percentual == esperado["cobertura_percentual"] == 0.0


def test_cobertura_40_por_cento_mantem_calculo_e_prepara_alerta():
    """2 válidos de 5 = 40%; cálculo disponível; alerta esperado fica pendente.

    Esta camada confirma os cálculos. A presença real do alerta no payload
    ainda depende do contrato/serviço BE09/BE10.
    """
    caso, resultado = executar_caso_sintetico("QA06-D10")
    esperado = caso["esperado"]

    assert resultado.presentes == esperado["presentes"] == 1
    assert resultado.validos == esperado["validos"] == 2
    assert resultado.total_indicadores == esperado["total"] == 5
    assert resultado.total_indicadores - resultado.validos == esperado["sem_dados"] == 3
    assert resultado.percentual == esperado["percentual"] == 50.0
    assert resultado.cobertura_indicadores_percentual == esperado["cobertura_percentual"] == 40.0
    assert caso["alerta_esperado"] == "exibir"


def test_cobertura_80_por_cento_mantem_calculo_sem_alerta_esperado():
    """4 válidos de 5 = 80%; cálculo disponível; sem alerta esperado.

    Esta camada confirma os cálculos. A ausência real do alerta no payload
    ainda depende do contrato/serviço BE09/BE10.
    """
    caso, resultado = executar_caso_sintetico("QA06-D11")
    esperado = caso["esperado"]

    assert resultado.presentes == esperado["presentes"] == 3
    assert resultado.validos == esperado["validos"] == 4
    assert resultado.total_indicadores == esperado["total"] == 5
    assert resultado.total_indicadores - resultado.validos == esperado["sem_dados"] == 1
    assert resultado.percentual == esperado["percentual"] == 75.0
    assert resultado.cobertura_indicadores_percentual == esperado["cobertura_percentual"] == 80.0
    assert caso["alerta_esperado"] == "nao_exibir"
