"""QA06: testes independentes da agregacao municipal da BE10.

Exercitam a funcao de dominio BE10 sem banco de dados e sem rota HTTP.
"""

import pytest

from app.domain.infraestrutura_agregacao_municipal import (
    agregar_indicadores_municipais,
)
from app.schemas.infraestrutura import INDICADORES_COMPARACAO_INFRAESTRUTURA

INDICADORES = INDICADORES_COMPARACAO_INFRAESTRUTURA
AGUA = "in_agua_potavel"
BIBLIOTECA = "in_biblioteca"


def valores(**sobrescritos):
    dados = {chave: None for chave in INDICADORES}
    dados.update(sobrescritos)
    return dados


def agregar(escola, referencias):
    return agregar_indicadores_municipais(
        escola,
        referencias,
        indicadores_esperados=INDICADORES,
    )


def test_agregacao_conta_presentes_validos_nulos_e_filtra_alvo_ano_municipio(
    qa06_registro_factory,
):
    """A agregacao usa somente outras escolas do mesmo municipio e ano."""
    escola_alvo = qa06_registro_factory(
        15012345,
        valores(**{AGUA: 1, BIBLIOTECA: 1}),
        ano=2024,
        co_municipio=1501402,
    )
    referencia_a = qa06_registro_factory(
        15010001,
        valores(**{AGUA: 1, BIBLIOTECA: 0}),
        ano=2024,
        co_municipio=1501402,
    )
    referencia_b = qa06_registro_factory(
        15010002,
        valores(**{AGUA: 0, BIBLIOTECA: 0}),
        ano=2024,
        co_municipio=1501402,
    )
    referencia_c = qa06_registro_factory(
        15010003,
        valores(**{AGUA: None, BIBLIOTECA: 1}),
        ano=2024,
        co_municipio=1501402,
    )
    outro_ano = qa06_registro_factory(
        15010004,
        valores(**{AGUA: 1, BIBLIOTECA: 1}),
        ano=2023,
        co_municipio=1501402,
    )
    outro_municipio = qa06_registro_factory(
        15010005,
        valores(**{AGUA: 1, BIBLIOTECA: 1}),
        ano=2024,
        co_municipio=1500800,
    )

    resultado = agregar(
        escola_alvo,
        [
            escola_alvo,  # deve ser excluida da propria referencia
            referencia_a,
            referencia_b,
            referencia_c,
            outro_ano,  # deve ser ignorada
            outro_municipio,  # deve ser ignorada
        ],
    )

    assert set(resultado) == set(INDICADORES)
    assert len(resultado) == 17

    agua = resultado[AGUA]
    assert agua.quantidade_presentes == 1
    assert agua.quantidade_validos == 2
    assert agua.quantidade_sem_dados == 1
    assert agua.quantidade_escolas_referencia == 3
    assert agua.percentual_presentes == 50.0
    assert agua.cobertura_percentual == 66.67

    biblioteca = resultado[BIBLIOTECA]
    assert biblioteca.quantidade_presentes == 1
    assert biblioteca.quantidade_validos == 3
    assert biblioteca.quantidade_sem_dados == 0
    assert biblioteca.quantidade_escolas_referencia == 3
    assert biblioteca.percentual_presentes == 33.33
    assert biblioteca.cobertura_percentual == 100.0


def test_sem_escolas_de_referencia_retorna_contagens_zero_e_percentuais_nulos(
    qa06_registro_factory,
):
    escola = qa06_registro_factory(15012345, valores(**{AGUA: 1}))

    resultado = agregar(escola, [])

    assert set(resultado) == set(INDICADORES)
    for agregado in resultado.values():
        assert agregado.quantidade_presentes == 0
        assert agregado.quantidade_validos == 0
        assert agregado.quantidade_sem_dados == 0
        assert agregado.quantidade_escolas_referencia == 0
        assert agregado.percentual_presentes is None
        assert agregado.cobertura_percentual is None


def test_referencias_existentes_com_todos_os_valores_nulos_nao_viram_zero(
    qa06_registro_factory,
):
    escola = qa06_registro_factory(15012345)
    referencias = [
        qa06_registro_factory(15010001),
        qa06_registro_factory(15010002),
        qa06_registro_factory(15010003),
    ]

    resultado = agregar(escola, referencias)
    agua = resultado[AGUA]

    assert agua.quantidade_presentes == 0
    assert agua.quantidade_validos == 0
    assert agua.quantidade_sem_dados == 3
    assert agua.quantidade_escolas_referencia == 3
    assert agua.percentual_presentes is None
    assert agua.cobertura_percentual == 0.0


def test_zero_e_cem_por_cento_sao_percentuais_validos(qa06_registro_factory):
    escola = qa06_registro_factory(15012345)
    referencia_zero = qa06_registro_factory(
        15010001, valores(**{AGUA: 0})
    )
    referencia_um = qa06_registro_factory(
        15010002, valores(**{AGUA: 1})
    )

    resultado_zero = agregar(escola, [referencia_zero])[AGUA]
    resultado_cem = agregar(escola, [referencia_um])[AGUA]

    assert resultado_zero.percentual_presentes == 0.0
    assert resultado_zero.cobertura_percentual == 100.0
    assert resultado_cem.percentual_presentes == 100.0
    assert resultado_cem.cobertura_percentual == 100.0


def test_percentual_e_cobertura_sao_arredondados_apenas_na_saida(
    qa06_registro_factory,
):
    escola = qa06_registro_factory(15012345)
    referencias = [
        qa06_registro_factory(15010001, valores(**{AGUA: 1})),
        qa06_registro_factory(15010002, valores(**{AGUA: 0})),
        qa06_registro_factory(15010003, valores(**{AGUA: 0})),
    ]

    agua = agregar(escola, referencias)[AGUA]

    assert agua.quantidade_presentes == 1
    assert agua.quantidade_validos == 3
    assert agua.quantidade_sem_dados == 0
    assert agua.percentual_presentes == 33.33
    assert agua.cobertura_percentual == 100.0


def test_cobertura_municipal_por_indicador_exatamente_60_por_cento(
    qa06_registro_factory,
):
    """3 respostas validas em 5 escolas = cobertura municipal de 60%.

    Esta e cobertura municipal do indicador, nao o alerta da escola-alvo.
    O BE09 determina que a cobertura municipal e informativa e nao recebe
    automaticamente classificacao de baixa cobertura.
    """
    escola = qa06_registro_factory(15012345)
    referencias = [
        qa06_registro_factory(15010001, valores(**{AGUA: 1})),
        qa06_registro_factory(15010002, valores(**{AGUA: 1})),
        qa06_registro_factory(15010003, valores(**{AGUA: 0})),
        qa06_registro_factory(15010004, valores(**{AGUA: None})),
        qa06_registro_factory(15010005, valores(**{AGUA: None})),
    ]

    agua = agregar(escola, referencias)[AGUA]

    assert agua.quantidade_presentes == 2
    assert agua.quantidade_validos == 3
    assert agua.quantidade_sem_dados == 2
    assert agua.quantidade_escolas_referencia == 5
    assert agua.percentual_presentes == 66.67
    assert agua.cobertura_percentual == 60.0


def test_municipio_historico_ausente_deixa_composicao_indisponivel(
    qa06_registro_factory,
):
    escola = qa06_registro_factory(15012345, co_municipio=None)
    referencia = qa06_registro_factory(15010001)

    assert agregar(escola, [referencia]) is None


def test_duplicidade_de_escola_referencia_e_rejeitada(qa06_registro_factory):
    escola = qa06_registro_factory(15012345)
    duplicada_a = qa06_registro_factory(15010001, valores(**{AGUA: 1}))
    duplicada_b = qa06_registro_factory(15010001, valores(**{AGUA: 0}))

    with pytest.raises(ValueError, match="duplicadas"):
        agregar(escola, [duplicada_a, duplicada_b])


def test_escola_referencia_sem_identificador_e_rejeitada(qa06_registro_factory):
    escola = qa06_registro_factory(15012345)
    sem_codigo = qa06_registro_factory(None, valores(**{AGUA: 1}))

    with pytest.raises(ValueError, match="sem identificador"):
        agregar(escola, [sem_codigo])


@pytest.mark.parametrize("valor_invalido", [2, -1, True, "1", 1.0])
def test_valores_fora_de_zero_um_e_null_sao_rejeitados(
    qa06_registro_factory, valor_invalido
):
    escola = qa06_registro_factory(15012345)
    referencia = qa06_registro_factory(
        15010001, valores(**{AGUA: valor_invalido})
    )

    with pytest.raises(ValueError, match="Valor inválido"):
        agregar(escola, [referencia])


def test_chave_de_indicador_ausente_no_registro_e_rejeitada(
    qa06_registro_factory,
):
    escola = qa06_registro_factory(15012345)
    referencia = qa06_registro_factory(15010001, {AGUA: 1})

    with pytest.raises(ValueError, match="Indicador ausente"):
        agregar(escola, [referencia])


def test_lista_de_indicadores_vazia_ou_com_duplicatas_e_rejeitada(
    qa06_registro_factory,
):
    escola = qa06_registro_factory(15012345)

    with pytest.raises(ValueError, match="não vazia"):
        agregar_indicadores_municipais(escola, [], indicadores_esperados=())

    with pytest.raises(ValueError, match="duplicatas"):
        agregar_indicadores_municipais(
            escola,
            [],
            indicadores_esperados=(AGUA, AGUA),
        )
