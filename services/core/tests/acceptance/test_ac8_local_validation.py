"""AC 8 (service part): Core validates JWTs locally and never calls Auth.

Core must work with the Auth service switched off, so it must not contain any HTTP client.
"""

import ast
from pathlib import Path

APP = Path(__file__).resolve().parents[2] / "app"
HTTP_CLIENTS = {"httpx", "requests", "aiohttp", "urllib3", "urllib", "http", "grpc"}


def test_core_has_no_http_client_imports() -> None:
    offenders: list[str] = []
    for path in APP.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            offenders += [f"{path.name}: {n}" for n in names if n.split(".")[0] in HTTP_CLIENTS]
    assert not offenders, "Core must never call Auth over HTTP:\n" + "\n".join(offenders)


def test_core_does_not_know_an_auth_service_url() -> None:
    config = (APP / "config.py").read_text().lower()
    assert "auth_url" not in config and "auth_service" not in config
