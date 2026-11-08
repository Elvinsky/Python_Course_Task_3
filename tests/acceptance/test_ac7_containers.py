"""AC 7: multi-stage, non-root Dockerfiles; `docker compose up --build` starts everything."""

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.acceptance.helpers import ROOT, SERVICES, dockerfile_instructions

SECRET_WORDS = re.compile(r"SECRET|PASSWORD|TOKEN|PRIVATE_KEY|API_KEY", re.IGNORECASE)


def _image_ref(args: str) -> str:
    """`python:3.14-slim AS builder` -> `python:3.14-slim`."""
    return args.split()[0]


@pytest.mark.parametrize("service", SERVICES)
class TestDockerfile:
    def test_has_at_least_two_stages(self, service: str) -> None:
        stages = [
            a
            for k, a in dockerfile_instructions(ROOT / "services" / service / "Dockerfile")
            if k == "FROM"
        ]
        assert len(stages) >= 2, "use a multi-stage build: a builder stage and a slim runtime stage"

    def test_base_images_are_pinned(self, service: str) -> None:
        instructions = dockerfile_instructions(ROOT / "services" / service / "Dockerfile")
        aliases: set[str] = set()
        for keyword, args in instructions:
            if keyword != "FROM":
                continue
            image = _image_ref(args)
            if image in aliases:
                continue  # `FROM builder` reuses an earlier stage
            tail = image.rsplit("/", 1)[-1]
            assert "@sha256:" in image or (":" in tail and not tail.endswith(":latest")), (
                f"pin the base image tag, got {image!r} (never `latest`, never untagged)"
            )
            parts = args.split()
            if len(parts) >= 3 and parts[1].upper() == "AS":
                aliases.add(parts[2])

    def test_installs_from_the_lockfile_without_dev_dependencies(self, service: str) -> None:
        runs = [
            a
            for k, a in dockerfile_instructions(ROOT / "services" / service / "Dockerfile")
            if k == "RUN"
        ]
        sync = [r for r in runs if "uv sync" in r]
        assert sync, "install dependencies with `uv sync`"
        assert any(("--frozen" in r or "--locked" in r) and "--no-dev" in r for r in sync), (
            "use `uv sync --frozen --no-dev` (or --locked)"
        )

    def test_runtime_stage_copies_from_the_builder(self, service: str) -> None:
        copies = [
            a
            for k, a in dockerfile_instructions(ROOT / "services" / service / "Dockerfile")
            if k == "COPY"
        ]
        assert any("--from=" in c for c in copies), (
            "copy the virtual environment out of the builder stage"
        )

    def test_runs_as_a_non_root_user(self, service: str) -> None:
        users = [
            a
            for k, a in dockerfile_instructions(ROOT / "services" / service / "Dockerfile")
            if k == "USER"
        ]
        assert users, "add a USER instruction to the runtime stage"
        assert users[-1].split(":")[0] not in {"root", "0"}, "the last USER must not be root"

    def test_bakes_in_no_secrets(self, service: str) -> None:
        offenders = [
            f"{k} {a}"
            for k, a in dockerfile_instructions(ROOT / "services" / service / "Dockerfile")
            if k in {"ENV", "ARG"} and SECRET_WORDS.search(a)
        ]
        assert not offenders, f"no secrets in the image: {offenders}"

    def test_starts_uvicorn_with_the_app(self, service: str) -> None:
        commands = [
            a
            for k, a in dockerfile_instructions(ROOT / "services" / service / "Dockerfile")
            if k in {"CMD", "ENTRYPOINT"}
        ]
        assert any("uvicorn" in c and "app.main:app" in c for c in commands), (
            "start `uvicorn app.main:app`"
        )


def _compose() -> dict[str, Any]:
    path = ROOT / "compose.yaml"
    assert path.is_file(), "compose.yaml is missing"
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict) and isinstance(data.get("services"), dict), (
        "compose.yaml needs `services:`"
    )
    services: dict[str, Any] = data["services"]
    return services


def _env(service: dict[str, Any]) -> dict[str, str]:
    env = service.get("environment", {})
    if isinstance(env, list):
        return {str(item).split("=", 1)[0]: str(item).split("=", 1)[-1] for item in env}
    return {str(k): str(v) for k, v in env.items()}


def _depends_on(service: dict[str, Any]) -> dict[str, str]:
    deps = service.get("depends_on", {})
    if isinstance(deps, list):
        return {str(name): "service_started" for name in deps}
    return {str(name): str(cfg.get("condition", "service_started")) for name, cfg in deps.items()}


def _build_context(service: dict[str, Any]) -> Path:
    build = service.get("build")
    assert build, "add a `build:` entry"
    context = build if isinstance(build, str) else build.get("context", ".")
    return (ROOT / context).resolve()


def test_compose_defines_all_services() -> None:
    missing = {"auth", "core", "auth-db", "core-db", "redis"} - set(_compose())
    assert not missing, f"compose.yaml is missing the services: {sorted(missing)}"


@pytest.mark.parametrize("service", SERVICES)
def test_compose_builds_each_service_from_its_directory(service: str) -> None:
    assert _build_context(_compose()[service]) == (ROOT / "services" / service).resolve()


@pytest.mark.parametrize(("service", "database"), [("auth", "auth-db"), ("core", "core-db")])
def test_compose_waits_for_a_healthy_database(service: str, database: str) -> None:
    compose = _compose()
    assert "healthcheck" in compose[database], f"{database} needs a healthcheck"
    assert _depends_on(compose[service]).get(database) == "service_healthy"


def test_auth_depends_on_redis() -> None:
    assert "redis" in _depends_on(_compose()["auth"])


def test_services_are_configured_through_the_environment() -> None:
    compose = _compose()
    auth, core = _env(compose["auth"]), _env(compose["core"])
    assert {"DATABASE_URL", "REDIS_URL", "JWT_SECRET"} <= set(auth)
    assert {"DATABASE_URL", "JWT_SECRET"} <= set(core)
    assert "auth-db" in auth["DATABASE_URL"] and "core-db" in core["DATABASE_URL"], (
        "each service connects to its OWN database host"
    )
    assert auth["JWT_SECRET"] == core["JWT_SECRET"], "Core must verify with the key Auth signs with"
