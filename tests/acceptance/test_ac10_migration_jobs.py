"""AC 10: migrations run as Kubernetes Jobs; the Kustomize files are consistent."""

from pathlib import Path

import pytest

from tests.acceptance.helpers import (
    K8S_BASE,
    K8S_OVERLAY,
    ROOT,
    SERVICES,
    Doc,
    kustomization,
    of_kind,
)


def _job(service: str) -> Doc:
    jobs = [j for j in of_kind("Job") if service in j["metadata"]["name"]]
    assert jobs, f"add a Job for {service} (for example `{service}-migrate`) to migrate-job.yaml"
    return jobs[0]


@pytest.mark.parametrize("service", SERVICES)
def test_job_runs_alembic_upgrade_head(service: str) -> None:
    container = _job(service)["spec"]["template"]["spec"]["containers"][0]
    command = " ".join(
        str(part) for part in [*container.get("command", []), *container.get("args", [])]
    )
    assert "alembic upgrade head" in command, f"the {service} Job must run `alembic upgrade head`"


@pytest.mark.parametrize("service", SERVICES)
def test_job_uses_the_service_image_and_configuration(service: str) -> None:
    pod = _job(service)["spec"]["template"]["spec"]
    container = pod["containers"][0]
    assert str(container["image"]).startswith(f"kickstart/{service}:")
    assert {"secretRef": {"name": f"{service}-secrets"}} in container.get("envFrom", [])
    assert pod["restartPolicy"] in {"OnFailure", "Never"}


def test_jobs_are_part_of_the_base_kustomization() -> None:
    assert "migrate-job.yaml" in kustomization(K8S_BASE)["resources"]


@pytest.mark.parametrize("directory", [K8S_BASE, K8S_OVERLAY])
def test_kustomization_references_existing_files(directory: Path) -> None:
    for entry in kustomization(directory).get("resources", []):
        assert (directory / str(entry)).exists(), (
            f"{directory.relative_to(ROOT)}: {entry} does not exist"
        )


def test_overlay_builds_on_the_base() -> None:
    assert "../../base" in kustomization(K8S_OVERLAY)["resources"]


def test_every_base_manifest_is_listed() -> None:
    listed = set(kustomization(K8S_BASE)["resources"])
    present = {p.name for p in K8S_BASE.glob("*.yaml")} - {
        "kustomization.yaml",
        "secret.example.yaml",
    }
    assert present <= listed, f"not listed in kustomization.yaml: {sorted(present - listed)}"
