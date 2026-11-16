"""QA09 - Testes funcionais independentes do servico BE15."""

import pytest

from app.core.exceptions import NotFoundError, SourceDataInconsistentError
from app.services.infraestrutura_service import (
    METRIC_FIELDS,
    InfraestruturaService,
)

MUNICIPIO = {
    "co_municipio": 1501402,
    "no_municipio": "Belem",
}


class RepositorioFake:
    def __init__(self, identificacao=MUNICIPIO, registros=None):
        self.identificacao = identificacao
        self.registros = registros or []
        self.chamadas = []

    async def find_identificacao_municipio(self, *, co_municipio):
        self.chamadas.append(("identificacao", co_municipio))
        return self.identificacao

    async def find_serie_temporal_municipio(self, **kwargs):
        self.chamadas.append(("serie", kwargs))
        return self.registros


def registro_ano(
    ano,
    *,
    escolas=2,
    com_informacao=1,
    media=50.0,
    presentes=1,
    validos=2,
    inconsistentes=0,
):
    return {
        "ano": ano,
        "quantidade_escolas": escolas,
        "quantidade_escolas_com_informacao": com_informacao,
        "cobertura_media_percentual": media,
        "quantidade_escolas_inconsistentes": inconsistentes,
        "in_agua_potavel__presentes": presentes,
        "in_agua_potavel__validos": validos,
    }


@pytest.mark.asyncio
async def test_be15_monta_serie_e_preserva_ano_sem_registros():
    repo = RepositorioFake(registros=[
        registro_ano(2023, escolas=2, com_informacao=1,
                     presentes=1, validos=2, media=50.0)
    ])

    resposta = await InfraestruturaService(repo).build_visao_temporal_municipio(
        co_municipio=1501402,
        ano_inicio=2023,
        ano_fim=2024,
        indicadores=["in_agua_potavel"],
    )

    serie = resposta["data"]["serie"]

    assert [p["ano"] for p in serie] == [2023, 2024]
    assert serie[0]["situacao"] == "com_dados"
    assert serie[0]["indicadores"]["in_agua_potavel"] == {
        "quantidade_presentes": 1,
        "quantidade_validos": 2,
        "quantidade_sem_dados": 0,
        "percentual_presentes": 50.0,
        "cobertura_percentual": 100.0,
    }

    assert serie[1]["situacao"] == "denominador_zero"
    assert serie[1]["quantidade_escolas"] == 0
    assert serie[1]["cobertura_media_percentual"] is None


@pytest.mark.asyncio
async def test_be15_distingue_zero_de_ausencia_de_informacao():
    repo = RepositorioFake(registros=[
        registro_ano(
            2024,
            escolas=2,
            com_informacao=1,
            media=0.0,
            presentes=0,
            validos=1,
        )
    ])

    resposta = await InfraestruturaService(repo).build_visao_temporal_municipio(
        co_municipio=1501402,
        ano_inicio=2023,
        ano_fim=2024,
        indicadores=["in_agua_potavel"],
    )

    ponto = resposta["data"]["serie"][1]
    agua = ponto["indicadores"]["in_agua_potavel"]

    assert ponto["situacao"] == "com_dados"
    assert ponto["quantidade_escolas_sem_dados"] == 1
    assert agua["quantidade_presentes"] == 0
    assert agua["quantidade_validos"] == 1
    assert agua["percentual_presentes"] == 0.0
    assert agua["cobertura_percentual"] == 50.0


@pytest.mark.asyncio
async def test_be15_usa_os_dezessete_indicadores_quando_nao_informados():
    repo = RepositorioFake(registros=[
        {
            "ano": 2024,
            "quantidade_escolas": 1,
            "quantidade_escolas_com_informacao": 0,
            "cobertura_media_percentual": None,
            "quantidade_escolas_inconsistentes": 0,
            **{
                f"{indicador}__{campo}": 0
                for indicador, _ in METRIC_FIELDS
                for campo in ("presentes", "validos")
            },
        }
    ])

    resposta = await InfraestruturaService(repo).build_visao_temporal_municipio(
        co_municipio=1501402,
        ano_inicio=2023,
        ano_fim=2024,
    )

    filtros = resposta["data"]["filtros"]
    assert len(filtros["indicadores"]) == 17
    assert len(resposta["data"]["serie"][0]["indicadores"]) == 17
    assert resposta["data"]["metodologia"]["homologada"] is False


@pytest.mark.asyncio
async def test_be15_aplica_filtro_de_rede_e_indicador():
    repo = RepositorioFake(registros=[registro_ano(2024)])

    await InfraestruturaService(repo).build_visao_temporal_municipio(
        co_municipio=1501402,
        ano_inicio=2023,
        ano_fim=2024,
        rede_ensino=["Municipal"],
        indicadores=["in_agua_potavel"],
    )

    chamada = repo.chamadas[1][1]
    assert chamada["rede_ensino"] == ["Municipal"]
    assert chamada["indicadores"] == ["in_agua_potavel"]


@pytest.mark.asyncio
async def test_be15_municipio_inexistente_nao_consulta_serie():
    repo = RepositorioFake(identificacao=None)

    with pytest.raises(NotFoundError):
        await InfraestruturaService(repo).build_visao_temporal_municipio(
            co_municipio=1501402,
            ano_inicio=2023,
            ano_fim=2024,
        )

    assert len(repo.chamadas) == 1
    assert repo.chamadas[0][0] == "identificacao"


@pytest.mark.asyncio
async def test_be15_rejeita_intervalo_invertido_antes_de_consultar_repositorio():
    repo = RepositorioFake()

    with pytest.raises(ValueError, match="ano inicial"):
        await InfraestruturaService(repo).build_visao_temporal_municipio(
            co_municipio=1501402,
            ano_inicio=2025,
            ano_fim=2023,
        )

    assert repo.chamadas == []


@pytest.mark.asyncio
async def test_be15_rejeita_intervalo_de_um_ano():
    repo = RepositorioFake()

    with pytest.raises(ValueError, match="dois anos"):
        await InfraestruturaService(repo).build_visao_temporal_municipio(
            co_municipio=1501402,
            ano_inicio=2024,
            ano_fim=2024,
        )

    assert repo.chamadas == []


@pytest.mark.asyncio
async def test_be15_rejeita_indicador_invalido_antes_de_consultar_repositorio():
    repo = RepositorioFake()

    with pytest.raises(ValueError, match="Indicadores invalidos"):
        await InfraestruturaService(repo).build_visao_temporal_municipio(
            co_municipio=1501402,
            ano_inicio=2023,
            ano_fim=2024,
            indicadores=["indicador_inexistente"],
        )

    assert repo.chamadas == []


@pytest.mark.asyncio
async def test_be15_bloqueia_publicacao_de_fonte_inconsistente():
    repo = RepositorioFake(registros=[
        registro_ano(2024, inconsistentes=1)
    ])

    with pytest.raises(SourceDataInconsistentError):
        await InfraestruturaService(repo).build_visao_temporal_municipio(
            co_municipio=1501402,
            ano_inicio=2023,
            ano_fim=2024,
            indicadores=["in_agua_potavel"],
        )
