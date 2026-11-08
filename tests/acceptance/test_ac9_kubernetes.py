"""AC 9: local Kubernetes (k3d) manifests: Deployments, Services, config, probes and one Ingress."""

from typing import Any

import pytest
import yaml

from tests.acceptance.helpers import K8S_BASE, ROOT, SERVICES, Doc, base_manifests, named, of_kind


def _container(deployment: Doc) -> dict[str, Any]:
    containers: list[dict[str, Any]] = deployment["spec"]["template"]["spec"]["containers"]
    assert containers, "the Deployment needs a container"
    return containers[0]


def test_namespace_is_defined() -> None:
    assert named("Namespace", "kickstart")


def test_every_namespaced_resource_lives_in_the_kickstart_namespace() -> None:
    wrong = [
        f"{d['kind']}/{d['metadata']['name']}"
        for d in base_manifests()
        if d.get("kind") != "Namespace" and d.get("metadata", {}).get("namespace") != "kickstart"
    ]
    assert not wrong, f"set `namespace: kickstart` on: {wrong}"


@pytest.mark.parametrize("service", SERVICES)
class TestService:
    def test_deployment_has_two_replicas(self, service: str) -> None:
        assert named("Deployment", service)["spec"]["replicas"] == 2

    def test_image_tag_is_pinned(self, service: str) -> None:
        image = str(_container(named("Deployment", service))["image"])
        assert image.startswith(f"kickstart/{service}:"), (
            f"image should be kickstart/{service}:<version>"
        )
        assert not image.endswith(":latest")

    def test_configuration_comes_from_a_configmap_and_a_secret(self, service: str) -> None:
        env_from = _container(named("Deployment", service)).get("envFrom", [])
        assert {"configMapRef": {"name": f"{service}-config"}} in env_from
        assert {"secretRef": {"name": f"{service}-secrets"}} in env_from
        assert named("ConfigMap", f"{service}-config")

    def test_readiness_and_liveness_probes(self, service: str) -> None:
        container = _container(named("Deployment", service))
        assert container["readinessProbe"]["httpGet"]["path"] == "/ready"
        assert container["livenessProbe"]["httpGet"]["path"] == "/health"

    def test_resource_requests_are_set(self, service: str) -> None:
        requests = _container(named("Deployment", service))["resources"]["requests"]
        assert "cpu" in requests and "memory" in requests

    def test_clusterip_service_selects_the_pods(self, service: str) -> None:
        svc = named("Service", service)
        assert svc["spec"].get("type", "ClusterIP") == "ClusterIP"
        pod_labels = named("Deployment", service)["spec"]["template"]["metadata"]["labels"]
        assert svc["spec"]["selector"].items() <= pod_labels.items()
        assert svc["spec"]["ports"][0]["port"] == 80


def test_exactly_one_ingress_routes_auth_and_api() -> None:
    ingresses = of_kind("Ingress")
    assert len(ingresses) == 1, f"expected exactly one Ingress, found {len(ingresses)}"
    spec = ingresses[0]["spec"]
    assert spec.get("ingressClassName") == "traefik"
    routes = {
        p["path"]: p["backend"]["service"]["name"]
        for rule in spec["rules"]
        for p in rule["http"]["paths"]
        if p.get("pathType", "Prefix") == "Prefix"
    }
    assert routes.get("/auth") == "auth" and routes.get("/api") == "core", f"routes: {routes}"


def test_ingress_nginx_is_not_used() -> None:
    text = "\n".join(
        line
        for path in (ROOT / "deploy").rglob("*.yaml")
        for line in path.read_text().splitlines()
        if not line.lstrip().startswith("#")
    ).lower()
    assert "ingress-nginx" not in text and "ingressclassname: nginx" not in text


def test_no_image_uses_the_latest_tag() -> None:
    images = [
        str(c["image"])
        for d in base_manifests()
        if d.get("kind") in {"Deployment", "Job"}
        for c in d["spec"].get("template", {}).get("spec", {}).get("containers", [])
    ]
    assert images, "no workloads found"
    assert not [i for i in images if ":" not in i or i.endswith(":latest")]


def test_secrets_are_documented_but_never_committed() -> None:
    committed = [
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "deploy").rglob("*.yaml")
        if path.name != "secret.example.yaml"
        and any(
            isinstance(d, dict) and d.get("kind") == "Secret"
            for d in yaml.safe_load_all(path.read_text())
        )
    ]
    assert not committed, f"real Secrets must not be committed: {committed}"

    docs = [
        d
        for d in yaml.safe_load_all((K8S_BASE / "secret.example.yaml").read_text())
        if isinstance(d, dict)
    ]
    names = {d["metadata"]["name"]: d for d in docs if d.get("kind") == "Secret"}
    assert {"auth-secrets", "core-secrets"} <= set(names), (
        "secret.example.yaml must show auth-secrets and core-secrets"
    )
    for secret in names.values():
        for key in ("DATABASE_URL", "JWT_SECRET"):
            value = str(secret.get("stringData", {}).get(key, ""))
            assert key in secret.get("stringData", {}), f"{secret['metadata']['name']} needs {key}"
            assert any(w in value.lower() for w in ("change", "example", "placeholder", "<")), (
                f"use a placeholder for {key}, never a real value"
            )
