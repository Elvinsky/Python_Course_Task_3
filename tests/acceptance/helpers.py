"""Helpers for the repository-level acceptance tests (static checks, no Docker or kubectl needed)."""

import re
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[2]
K8S_BASE = ROOT / "deploy" / "k8s" / "base"
K8S_OVERLAY = ROOT / "deploy" / "k8s" / "overlays" / "local"
SERVICES = ["auth", "core"]
Doc = dict[str, Any]


def load_docs(path: Path) -> list[Doc]:
    """All YAML documents of a file; an empty or comment-only file gives []."""
    if not path.is_file():
        return []
    return [d for d in yaml.safe_load_all(path.read_text()) if isinstance(d, dict)]


def kustomization(directory: Path) -> Doc:
    docs = load_docs(directory / "kustomization.yaml")
    assert docs, f"{directory.relative_to(ROOT)}/kustomization.yaml is missing or empty"
    return docs[0]


def base_manifests() -> list[Doc]:
    """Every document of every resource file listed in the base kustomization."""
    docs: list[Doc] = []
    for name in kustomization(K8S_BASE).get("resources", []):
        docs.extend(load_docs(K8S_BASE / str(name)))
    return docs


def of_kind(kind: str) -> list[Doc]:
    return [d for d in base_manifests() if d.get("kind") == kind]


def named(kind: str, name: str) -> Doc:
    for doc in of_kind(kind):
        if doc.get("metadata", {}).get("name") == name:
            return doc
    raise AssertionError(
        f"no {kind} named {name!r} in deploy/k8s/base (check the file is listed in kustomization.yaml)"
    )


def dockerfile_instructions(path: Path) -> list[tuple[str, str]]:
    """(INSTRUCTION, arguments) pairs: comments dropped, line continuations joined."""
    assert path.is_file(), f"{path.relative_to(ROOT)} is missing"
    text = re.sub(r"\\\s*\n", " ", path.read_text())
    result: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        keyword, _, rest = line.partition(" ")
        result.append((keyword.upper(), rest.strip()))
    return result
