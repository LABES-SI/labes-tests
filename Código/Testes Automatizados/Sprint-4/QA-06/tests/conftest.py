"""Configuracao dos testes independentes de QA06 para a BE10."""

import os
import sys
from pathlib import Path

import pytest


api_root_text = os.environ.get("LABES_API_ROOT")
if not api_root_text:
    raise RuntimeError(
        "Defina LABES_API_ROOT com o caminho da copia local do labes-api "
        "que contenha os modulos da BE10."
    )

API_ROOT = Path(api_root_text).resolve()
if not (API_ROOT / "app" / "domain" / "infraestrutura_agregacao_municipal.py").is_file():
    raise RuntimeError(
        "O backend apontado por LABES_API_ROOT ainda nao contem "
        "app/domain/infraestrutura_agregacao_municipal.py. "
        "Atualize para a versao que inclui a BE10 (PR #15)."
    )

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))


from app.domain.infraestrutura import InfraestruturaRegistroBruto  # noqa: E402
from app.schemas.infraestrutura import INDICADORES_COMPARACAO_INFRAESTRUTURA  # noqa: E402


@pytest.fixture
def qa06_registro_factory():
    """Cria registros artificiais de infraestrutura para os testes QA06.

    - Lista/tupla: exige os 17 valores na ordem do contrato.
    - Dicionario: preserva apenas as chaves informadas, permitindo testar
      explicitamente o comportamento de indicador ausente.
    - valores=None: cria os 17 indicadores com valor None.
    """

    def criar(
        co_entidade,
        valores=None,
        *,
        ano=2024,
        co_municipio=1501402,
        no_entidade=None,
        no_municipio="Belem",
    ):
        if valores is None:
            indicadores = {chave: None for chave in INDICADORES_COMPARACAO_INFRAESTRUTURA}
        elif isinstance(valores, dict):
            indicadores = dict(valores)
        else:
            lista = list(valores)
            if len(lista) != len(INDICADORES_COMPARACAO_INFRAESTRUTURA):
                raise ValueError("A lista deve conter exatamente 17 valores.")
            indicadores = dict(
                zip(INDICADORES_COMPARACAO_INFRAESTRUTURA, lista, strict=True)
            )

        return InfraestruturaRegistroBruto(
            co_entidade=co_entidade,
            no_entidade=no_entidade or f"Escola {co_entidade}",
            co_municipio=co_municipio,
            no_municipio=no_municipio,
            nu_ano_censo=ano,
            indicadores=indicadores,
        )

    return criar
