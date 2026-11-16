"""QA09 - Testes funcionais independentes do dominio BE13."""

import pytest

from app.domain.infraestrutura import (
    InfraestruturaRegistroBruto,
    calcular_indice_infraestrutura,
    calcular_comparacao_infraestrutura_ano,
    calcular_serie_comparacao_infraestrutura,
)

INDICADORES = ("in_agua_potavel", "in_biblioteca")


def registro(codigo, valores, *, ano=2024, municipio=1501402):
    return InfraestruturaRegistroBruto(
        co_entidade=codigo,
        no_entidade=f"Escola {codigo}",
        co_municipio=municipio,
        no_municipio="Belem",
        nu_ano_censo=ano,
        indicadores=dict(zip(INDICADORES, valores, strict=True)),
    )


def test_be13_indice_distingue_zero_um_e_ausencia():
    resultado = calcular_indice_infraestrutura(
        {"in_agua_potavel": 1, "in_biblioteca": 0},
        indicadores_esperados=INDICADORES,
    )

    assert resultado.presentes == 1
    assert resultado.validos == 2
    assert resultado.percentual == 50.0
    assert resultado.cobertura_indicadores_percentual == 100.0


def test_be13_none_nao_e_contabilizado_como_zero():
    resultado = calcular_indice_infraestrutura(
        {"in_agua_potavel": 1, "in_biblioteca": None},
        indicadores_esperados=INDICADORES,
    )

    assert resultado.presentes == 1
    assert resultado.validos == 1
    assert resultado.percentual == 100.0
    assert resultado.cobertura_indicadores_percentual == 50.0


def test_be13_calcula_media_simples_dos_pares_e_exclui_a_escola_alvo():
    escola = registro(100, [1, 0])
    referencias = [
        registro(100, [0, 0]),  # Mesmo codigo da escola alvo: deve ser excluida.
        registro(101, [1, 0]),  # Indice 50%.
        registro(102, [0, 0]),  # Indice 0%.
        registro(103, [1, 1], municipio=1509999),  # Outro municipio.
        registro(104, [1, 1], ano=2023),  # Outro ano.
    ]

    resultado = calcular_comparacao_infraestrutura_ano(
        escola,
        referencias,
        indicadores_esperados=INDICADORES,
    )

    assert resultado.situacao == "disponivel"
    assert resultado.indice_escola_percentual == 50.0
    assert resultado.denominador_pares == 2
    assert resultado.quantidade_pares_validos == 2
    assert resultado.media_municipal_percentual == 25.0
    assert resultado.diferenca_pontos_percentuais == 25.0


def test_be13_identifica_escola_sem_dados():
    escola = registro(100, [None, None])
    referencias = [registro(101, [1, 1])]

    resultado = calcular_comparacao_infraestrutura_ano(
        escola, referencias, indicadores_esperados=INDICADORES
    )

    assert resultado.situacao == "escola_sem_dados"
    assert resultado.indice_escola_percentual is None
    assert resultado.diferenca_pontos_percentuais is None


def test_be13_identifica_ausencia_de_pares_municipais():
    escola = registro(100, [1, 0])

    resultado = calcular_comparacao_infraestrutura_ano(
        escola, [], indicadores_esperados=INDICADORES
    )

    assert resultado.situacao == "sem_pares_municipio"
    assert resultado.indice_escola_percentual == 50.0
    assert resultado.denominador_pares == 0
    assert resultado.media_municipal_percentual is None


def test_be13_identifica_pares_sem_indice_valido():
    escola = registro(100, [1, 0])
    referencias = [
        registro(101, [None, None]),
        registro(102, [None, None]),
    ]

    resultado = calcular_comparacao_infraestrutura_ano(
        escola, referencias, indicadores_esperados=INDICADORES
    )

    assert resultado.situacao == "sem_pares_validos"
    assert resultado.denominador_pares == 2
    assert resultado.quantidade_pares_validos == 0
    assert resultado.media_municipal_percentual is None


def test_be13_serie_historica_e_ordenada_por_ano():
    registros = [
        registro(100, [1, 1], ano=2025),
        registro(100, [1, 0], ano=2022),
    ]

    resultado = calcular_serie_comparacao_infraestrutura(
        registros,
        [],
        indicadores_esperados=INDICADORES,
    )

    assert [p.ano for p in resultado] == [2022, 2025]


def test_be13_rejeita_registros_duplicados_da_escola_no_mesmo_ano():
    registros = [
        registro(100, [1, 0], ano=2024),
        registro(100, [0, 1], ano=2024),
    ]

    with pytest.raises(ValueError, match="mais de um registro"):
        calcular_serie_comparacao_infraestrutura(
            registros, [], indicadores_esperados=INDICADORES
        )
