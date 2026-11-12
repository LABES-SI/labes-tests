
import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest


# ============================================================
# CONFIGURAÇÃO
# ============================================================

API_ROOT = os.getenv("LABES_API_URL", "http://localhost:8000").rstrip("/")

ESCOLA_INEP = "15010201"

ENDPOINT = (
    f"{API_ROOT}/infraestrutura/analise-temporal/"
    f"escolas/{ESCOLA_INEP}/comparacao-municipio"
)

ENDPOINT_INVALIDO = (
    f"{API_ROOT}/infraestrutura/analise-temporal/"
    "escolas/abc/comparacao-municipio"
)

ENDPOINT_INEXISTENTE = (
    f"{API_ROOT}/infraestrutura/analise-temporal/"
    "escolas/99999999/comparacao-municipio"
)

ANOS_ESPERADOS = [2022, 2023, 2024, 2025]

INDICADORES = [
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
]

COMPOSICAO_ESPERADA = {
    indicador: 0 for indicador in INDICADORES
}

COMPOSICAO_ESPERADA["in_banheiro"] = 1
COMPOSICAO_ESPERADA["in_cozinha"] = 1


# ============================================================
# DADOS DE REFERÊNCIA OBSERVADOS NO AMBIENTE LOCAL
# ============================================================

RESULTADOS_MUNICIPAIS = {
    2022: {
        "media": 20.32,
        "diferenca": -8.56,
        "pares_validos": 99,
        "denominador": 120,
        "cobertura": 82.50,
    },
    2023: {
        "media": 22.41,
        "diferenca": -10.65,
        "pares_validos": 100,
        "denominador": 103,
        "cobertura": 97.09,
    },
    2024: {
        "media": 24.58,
        "diferenca": -12.81,
        "pares_validos": 101,
        "denominador": 103,
        "cobertura": 98.06,
    },
    2025: {
        "media": 26.73,
        "diferenca": -14.97,
        "pares_validos": 101,
        "denominador": 104,
        "cobertura": 97.12,
    },
}


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def requisitar_api(url):
    request = Request(
        url,
        headers={"Accept": "application/json"},
        method="GET",
    )

    try:
        with urlopen(request, timeout=15) as response:
            return response.status, json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as error:
        corpo = error.read().decode("utf-8")

        try:
            corpo_json = json.loads(corpo)
        except (json.JSONDecodeError, ValueError):
            corpo_json = {"raw": corpo}

        return error.code, corpo_json


@pytest.fixture(scope="module")
def resposta_comparacao():
    status, corpo = requisitar_api(ENDPOINT)

    assert status == 200, (
        f"Esperado HTTP 200, recebido HTTP {status}. "
        f"Resposta: {corpo}"
    )

    return corpo


@pytest.fixture(scope="module")
def serie(resposta_comparacao):
    return resposta_comparacao["data"]["serie"]


# ============================================================
# TESTE 01 - CONTRATO HTTP E ESTRUTURA DA RESPOSTA
# ============================================================

def test_qa06_http_01_contrato_resposta(resposta_comparacao):

    assert resposta_comparacao["descricao"] == (
        "comparacao_infraestrutura_escola_municipio"
    )

    data = resposta_comparacao["data"]

    assert "escola" in data
    assert "municipio" in data
    assert "metodologia" in data
    assert "serie" in data

    assert data["escola"]["co_entidade"] == int(ESCOLA_INEP)
    assert data["escola"]["no_entidade"] == (
        "E M E F PRINCESA ISABEL"
    )

    assert data["municipio"]["co_municipio"] == 1505908
    assert data["municipio"]["no_municipio"] == "Porto de Moz"


# ============================================================
# TESTE 02 - SÉRIE HISTÓRICA DOS QUATRO ANOS
# ============================================================

def test_qa06_http_02_serie_historica(serie):

    anos_retornados = [item["ano"] for item in serie]

    assert anos_retornados == ANOS_ESPERADOS

    assert len(serie) == 4

    for item in serie:
        assert item["situacao"] == "disponivel"
        assert item["registro_historico_disponivel"] is True


# ============================================================
# TESTE 03 - ÍNDICE, COBERTURA E COMPOSIÇÃO DA ESCOLA
# ============================================================

def test_qa06_http_03_indicadores_escola(serie):

    for item in serie:

        assert item["indice_escola_percentual"] == pytest.approx(
            11.76, abs=0.01
        )

        assert item["quantidade_indicadores_presentes"] == 2
        assert item["quantidade_indicadores_validos"] == 17
        assert item["total_indicadores"] == 17

        assert item["cobertura_indicadores_percentual"] == 100.0
        assert item["cobertura_indicadores_reduzida"] is False

        composicao = item["composicao_escola"]

        assert set(composicao.keys()) == set(INDICADORES)
        assert composicao == COMPOSICAO_ESPERADA


# ============================================================
# TESTE 04 - COMPARAÇÃO COM A MÉDIA MUNICIPAL
# ============================================================

def test_qa06_http_04_comparacao_municipal(serie):

    for item in serie:

        esperado = RESULTADOS_MUNICIPAIS[item["ano"]]

        assert item["municipio_referencia"]["co_municipio"] == 1505908
        assert item["municipio_referencia"]["no_municipio"] == (
            "Porto de Moz"
        )

        assert item["media_municipal_percentual"] == pytest.approx(
            esperado["media"], abs=0.01
        )

        assert item["diferenca_pontos_percentuais"] == pytest.approx(
            esperado["diferenca"], abs=0.01
        )

        assert item["quantidade_pares_validos"] == (
            esperado["pares_validos"]
        )

        assert item["denominador_pares"] == esperado["denominador"]

        assert item["cobertura_pares_percentual"] == pytest.approx(
            esperado["cobertura"], abs=0.01
        )


# ============================================================
# TESTE 05 - METODOLOGIA E COMPOSIÇÃO MUNICIPAL
# ============================================================

def test_qa06_http_05_metodologia_e_composicao(
    resposta_comparacao,
    serie,
):

    metodologia = resposta_comparacao["data"]["metodologia"]

    assert metodologia["versao"] == "infraestrutura-v3-provisoria"
    assert metodologia["homologada"] is False
    assert metodologia["anos"] == ANOS_ESPERADOS

    assert metodologia["total_indicadores"] == 17
    assert metodologia["indicadores"] == INDICADORES

    assert metodologia["cobertura_minima_percentual"] is None
    assert metodologia["limiar_alerta_cobertura_percentual"] == 60.0

    assert metodologia["limiar_alerta_cobertura_status"] == (
        "confirmado_req05"
    )

    assert metodologia["limiar_alerta_cobertura_escopo"] == (
        "escola_selecionada"
    )

    assert metodologia["bloqueia_resultado_por_cobertura"] is False

    for item in serie:

        composicao = item["composicao_municipal"]

        assert composicao is not None
        assert set(composicao.keys()) == set(INDICADORES)

        for indicador in INDICADORES:

            dados = composicao[indicador]

            assert dados["quantidade_presentes"] >= 0
            assert dados["quantidade_validos"] == (
                item["quantidade_pares_validos"]
            )

            assert dados["quantidade_sem_dados"] >= 0

            assert dados["quantidade_escolas_referencia"] == (
                item["denominador_pares"]
            )


# ============================================================
# TESTE 06 - VALIDAÇÃO DOS ERROS HTTP
# ============================================================

def test_qa06_http_06_erro_422_inep_invalido():

    status, corpo = requisitar_api(ENDPOINT_INVALIDO)

    assert status == 422

    assert "detail" in corpo


def test_qa06_http_07_erro_404_escola_inexistente():

    status, corpo = requisitar_api(ENDPOINT_INEXISTENTE)

    assert status == 404

    assert corpo["code"] == "not_found"
    assert "message" in corpo
