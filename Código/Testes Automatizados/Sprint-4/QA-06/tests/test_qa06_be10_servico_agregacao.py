"""QA06: testes independentes do servico BE10 com repositorio falso."""

import pytest

from app.core.exceptions import NotFoundError
from app.schemas.infraestrutura import (
    ANOS_COMPARACAO_INFRAESTRUTURA,
    INDICADORES_COMPARACAO_INFRAESTRUTURA,
)
from app.services.infraestrutura_agregacao_municipal import (
    InfraestruturaAgregacaoMunicipalService,
)

INDICADORES = INDICADORES_COMPARACAO_INFRAESTRUTURA
AGUA = "in_agua_potavel"
BIBLIOTECA = "in_biblioteca"


def valores(**sobrescritos):
    dados = {chave: None for chave in INDICADORES}
    dados.update(sobrescritos)
    return dados


def identificacao(co_entidade=15012345):
    return {
        "co_entidade": co_entidade,
        "no_entidade": f"Escola {co_entidade}",
        "co_municipio": 1501402,
        "no_municipio": "Belem",
    }


class RepositorioFake:
    def __init__(self, *, historico=(), pares=None, escola_existe=True):
        self.historico = list(historico)
        self.pares = pares or {}
        self.escola_existe = escola_existe
        self.chamadas_pares = []
        self.anos_solicitados = None

    async def find_identificacao_escola(self, *, co_entidade):
        if not self.escola_existe:
            return None
        return identificacao(co_entidade)

    async def find_historico_escola(self, *, co_entidade, anos_comparaveis):
        self.anos_solicitados = tuple(anos_comparaveis)
        return self.historico

    async def find_pares_municipais(
        self, *, co_entidade_excluida, co_municipio, ano
    ):
        self.chamadas_pares.append((co_entidade_excluida, co_municipio, ano))
        return self.pares.get((co_municipio, ano), [])


@pytest.mark.asyncio
async def test_servico_usa_municipio_historico_de_cada_ano_e_preserva_lacunas(
    qa06_registro_factory,
):
    escola_2022 = qa06_registro_factory(
        15012345,
        valores(**{AGUA: 1, BIBLIOTECA: 0}),
        ano=2022,
        co_municipio=1501402,
        no_municipio="Belem",
    )
    escola_2024 = qa06_registro_factory(
        15012345,
        valores(**{AGUA: None, BIBLIOTECA: 1}),
        ano=2024,
        co_municipio=1500800,
        no_municipio="Ananindeua",
    )

    pares_2022 = [
        qa06_registro_factory(15010001, valores(**{AGUA: 1}), ano=2022, co_municipio=1501402),
        qa06_registro_factory(15010002, valores(**{AGUA: 0}), ano=2022, co_municipio=1501402),
    ]
    pares_2024 = [
        qa06_registro_factory(15010003, valores(**{AGUA: 0}), ano=2024, co_municipio=1500800),
        qa06_registro_factory(15010004, valores(**{AGUA: None}), ano=2024, co_municipio=1500800),
    ]

    repo = RepositorioFake(
        historico=[escola_2024, escola_2022],
        pares={
            (1501402, 2022): pares_2022,
            (1500800, 2024): pares_2024,
        },
    )

    serie = await InfraestruturaAgregacaoMunicipalService(repo).calcular_serie(
        co_entidade=15012345
    )

    assert repo.anos_solicitados == ANOS_COMPARACAO_INFRAESTRUTURA
    assert [ponto["ano"] for ponto in serie] == [2022, 2023, 2024, 2025]
    assert serie[0]["municipio_referencia"] == {
        "co_municipio": 1501402,
        "no_municipio": "Belem",
    }
    assert serie[2]["municipio_referencia"] == {
        "co_municipio": 1500800,
        "no_municipio": "Ananindeua",
    }

    assert serie[0]["composicao_municipal"][AGUA] == {
        "quantidade_presentes": 1,
        "quantidade_validos": 2,
        "quantidade_sem_dados": 0,
        "quantidade_escolas_referencia": 2,
        "percentual_presentes": 50.0,
        "cobertura_percentual": 100.0,
    }
    assert serie[2]["composicao_municipal"][AGUA] == {
        "quantidade_presentes": 0,
        "quantidade_validos": 1,
        "quantidade_sem_dados": 1,
        "quantidade_escolas_referencia": 2,
        "percentual_presentes": 0.0,
        "cobertura_percentual": 50.0,
    }

    assert serie[1]["registro_historico_disponivel"] is False
    assert serie[1]["municipio_referencia"] is None
    assert serie[1]["composicao_municipal"] is None
    assert serie[3]["registro_historico_disponivel"] is False
    assert serie[3]["composicao_municipal"] is None

    assert set(repo.chamadas_pares) == {
        (15012345, 1501402, 2022),
        (15012345, 1500800, 2024),
    }


@pytest.mark.asyncio
async def test_escola_inexistente_e_diferente_de_escola_sem_historico():
    servico_inexistente = InfraestruturaAgregacaoMunicipalService(
        RepositorioFake(escola_existe=False)
    )
    with pytest.raises(NotFoundError):
        await servico_inexistente.calcular_serie(co_entidade=15012345)

    repo_sem_historico = RepositorioFake(historico=[])
    serie = await InfraestruturaAgregacaoMunicipalService(
        repo_sem_historico
    ).calcular_serie(co_entidade=15012345)

    assert [ponto["ano"] for ponto in serie] == [2022, 2023, 2024, 2025]
    assert all(ponto["registro_historico_disponivel"] is False for ponto in serie)
    assert all(ponto["municipio_referencia"] is None for ponto in serie)
    assert all(ponto["composicao_municipal"] is None for ponto in serie)
    assert repo_sem_historico.chamadas_pares == []


@pytest.mark.asyncio
async def test_registro_com_municipio_historico_nulo_nao_consulta_pares(
    qa06_registro_factory,
):
    escola = qa06_registro_factory(
        15012345,
        valores(**{AGUA: 1}),
        ano=2024,
        co_municipio=None,
        no_municipio=None,
    )
    repo = RepositorioFake(historico=[escola])

    serie = await InfraestruturaAgregacaoMunicipalService(repo).calcular_serie(
        co_entidade=15012345
    )

    ponto = serie[2]
    assert ponto["registro_historico_disponivel"] is True
    assert ponto["municipio_referencia"] is None
    assert ponto["composicao_municipal"] is None
    assert repo.chamadas_pares == []


@pytest.mark.asyncio
async def test_municipio_conhecido_sem_pares_retorna_17_indicadores_com_contagens_zero(
    qa06_registro_factory,
):
    escola = qa06_registro_factory(
        15012345,
        valores(**{AGUA: 1}),
        ano=2025,
        co_municipio=1501402,
    )
    repo = RepositorioFake(historico=[escola], pares={})

    serie = await InfraestruturaAgregacaoMunicipalService(repo).calcular_serie(
        co_entidade=15012345
    )

    composicao = serie[3]["composicao_municipal"]
    assert set(composicao) == set(INDICADORES)
    assert len(composicao) == 17
    for indicador in composicao.values():
        assert indicador["quantidade_presentes"] == 0
        assert indicador["quantidade_validos"] == 0
        assert indicador["quantidade_sem_dados"] == 0
        assert indicador["quantidade_escolas_referencia"] == 0
        assert indicador["percentual_presentes"] is None
        assert indicador["cobertura_percentual"] is None


@pytest.mark.asyncio
async def test_historico_duplicado_e_rejeitado_antes_da_consulta_de_pares(
    qa06_registro_factory,
):
    escola_2024_a = qa06_registro_factory(15012345, ano=2024)
    escola_2024_b = qa06_registro_factory(15012345, ano=2024)
    repo = RepositorioFake(historico=[escola_2024_a, escola_2024_b])

    with pytest.raises(ValueError, match="duplicados"):
        await InfraestruturaAgregacaoMunicipalService(repo).calcular_serie(
            co_entidade=15012345
        )

    assert repo.chamadas_pares == []


@pytest.mark.asyncio
async def test_historico_de_outra_escola_ou_ano_fora_do_recorte_e_rejeitado(
    qa06_registro_factory,
):
    registro_outra_escola = qa06_registro_factory(15099999, ano=2024)
    repo_outra_escola = RepositorioFake(historico=[registro_outra_escola])
    with pytest.raises(ValueError, match="outra escola"):
        await InfraestruturaAgregacaoMunicipalService(repo_outra_escola).calcular_serie(
            co_entidade=15012345
        )

    registro_ano_2026 = qa06_registro_factory(15012345, ano=2026)
    repo_ano_fora = RepositorioFake(historico=[registro_ano_2026])
    with pytest.raises(ValueError, match="fora do recorte"):
        await InfraestruturaAgregacaoMunicipalService(repo_ano_fora).calcular_serie(
            co_entidade=15012345
        )
