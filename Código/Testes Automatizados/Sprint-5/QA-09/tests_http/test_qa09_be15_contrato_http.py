"""QA09 - Contrato e validacoes HTTP do BE15."""

def obter_rota(openapi_schema):
    sufixo = "/analise-temporal/municipios/{co_municipio}"
    rotas = [
        path for path in openapi_schema["paths"]
        if path.endswith(sufixo)
    ]
    assert len(rotas) == 1, f"Rota BE15 nao encontrada: {sufixo}"
    return rotas[0]


def test_be15_endpoint_documentado(openapi_schema):
    rota = obter_rota(openapi_schema)
    operacao = openapi_schema["paths"][rota]["get"]

    assert "200" in operacao["responses"]
    assert "422" in operacao["responses"]

    parametros = {p["name"] for p in operacao.get("parameters", [])}
    assert {
        "co_municipio",
        "ano_inicio",
        "ano_fim",
        "rede_ensino",
        "indicadores",
    } <= parametros


def test_be15_rejeita_intervalo_de_um_unico_ano(api_client, openapi_schema):
    rota = obter_rota(openapi_schema).replace(
        "{co_municipio}", "1501402"
    )

    resposta = api_client.get(
        rota,
        params={"ano_inicio": 2024, "ano_fim": 2024},
    )

    assert resposta.status_code == 422


def test_be15_rejeita_ano_inicial_posterior_ao_final(api_client, openapi_schema):
    rota = obter_rota(openapi_schema).replace(
        "{co_municipio}", "1501402"
    )

    resposta = api_client.get(
        rota,
        params={"ano_inicio": 2025, "ano_fim": 2023},
    )

    assert resposta.status_code == 422


def test_be15_rejeita_codigo_municipio_invalido(api_client, openapi_schema):
    rota = obter_rota(openapi_schema).replace(
        "{co_municipio}", "123"
    )

    resposta = api_client.get(
        rota,
        params={"ano_inicio": 2022, "ano_fim": 2025},
    )

    assert resposta.status_code == 422
