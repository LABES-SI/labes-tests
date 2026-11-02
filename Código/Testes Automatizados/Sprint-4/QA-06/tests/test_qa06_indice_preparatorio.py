"""Testes preparatórios de domínio para QA06.

Estes testes exercitam a função de índice já existente no snapshot do backend.
Eles não validam o payload HTTP da composição detalhada BE09/BE10.
"""

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

from app.domain.infraestrutura import calcular_indice_infraestrutura

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


def calcular(valores):
    assert len(valores) == 17
    indicadores = dict(zip(INDICADORES_ESPERADOS, valores, strict=True))
    return calcular_indice_infraestrutura(
        indicadores,
        indicadores_esperados=INDICADORES_ESPERADOS,
        cobertura_minima_percentual=None,
    )


def test_composicao_conta_presentes_validos_sem_dados_e_percentual():
    """7 Sim, 5 Não e 5 NULL: 7/12 = 58,33%; 5 sem dados."""

    resultado = calcular([1] * 7 + [0] * 5 + [None] * 5)

    assert resultado.presentes == 7
    assert resultado.validos == 12
    assert resultado.total_indicadores == 17
    # O domínio atual não retorna um campo 'sem_dados' explícito.
    # A quantidade é derivada do total esperado menos os válidos.
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
    """Um Sim e dezesseis NULL devem resultar em 100%."""

    resultado = calcular([1] + [None] * 16)

    assert resultado.presentes == 1
    assert resultado.validos == 1
    assert resultado.total_indicadores == 17
    assert resultado.percentual == 100.0
    assert resultado.cobertura_indicadores_percentual == 5.88


def test_um_indicador_nao_e_demais_nulos():
    """Um Não e dezesseis NULL devem resultar em 0%."""

    resultado = calcular([0] + [None] * 16)

    assert resultado.presentes == 0
    assert resultado.validos == 1
    assert resultado.total_indicadores == 17
    assert resultado.percentual == 0.0
    assert resultado.cobertura_indicadores_percentual == 5.88


def test_um_indicador_nulo_e_demais_sim():
    """Um NULL e dezesseis Sim devem resultar em 100%."""

    resultado = calcular([None] + [1] * 16)

    assert resultado.presentes == 16
    assert resultado.validos == 16
    assert resultado.total_indicadores == 17
    assert resultado.percentual == 100.0
    assert resultado.cobertura_indicadores_percentual == 94.12
