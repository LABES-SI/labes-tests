"""Configuracao dos testes independentes de QA09."""

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

api_root_text = os.environ.get("LABES_API_ROOT")

if not api_root_text:
    raise RuntimeError("Defina LABES_API_ROOT com o caminho do worktree do backend.")

API_ROOT = Path(api_root_text).resolve()

if not (API_ROOT / "main.py").is_file():
    raise RuntimeError(f"Backend invalido: {API_ROOT}")

if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from main import app  # noqa: E402


@pytest.fixture(scope="session")
def api_app():
    return app


@pytest.fixture(scope="session")
def api_client():
    return TestClient(app)


@pytest.fixture(scope="session")
def openapi_schema():
    return app.openapi()
