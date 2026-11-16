"""QA09 - Contrato e validacoes HTTP do BE13."""

def obter_rota(openapi_schema):
    sufixo = "/analise-temporal/escolas/{co_entidade}/comparacao-municipio"
    rotas = [
        path for path in openapi_schema["paths"]
        if path.endswith(sufixo)
    ]
    assert len(rotas) == 1, f"Rota BE13 nao encontrada: {sufixo}"
    return rotas[0]


def test_be13_endpoint_documentado(openapi_schema):
    rota = obter_rota(openapi_schema)
    operacao = openapi_schema["paths"][rota]["get"]

    assert "200" in operacao["responses"]
    assert "422" in operacao["responses"]

    parametros = {p["name"] for p in operacao.get("parameters", [])}
    assert {"co_entidade", "ano_inicio", "ano_fim"} <= parametros


def test_be13_rejeita_intervalo_menor_que_tres_anos(api_client, openapi_schema):
    rota = obter_rota(openapi_schema).replace(
        "{co_entidade}", "15014020"
    )

    resposta = api_client.get(
        rota,
        params={"ano_inicio": 2022, "ano_fim": 2023},
    )

    assert resposta.status_code == 422


def test_be13_rejeita_codigo_escola_invalido(api_client, openapi_schema):
    rota = obter_rota(openapi_schema).replace(
        "{co_entidade}", "123"
    )

    resposta = api_client.get(
        rota,
        params={"ano_inicio": 2022, "ano_fim": 2025},
    )

    assert resposta.status_code == 422
