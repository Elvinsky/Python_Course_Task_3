"""AC 8 (repository part): ARCHITECTURE.md documents the boundaries, JWT claims and error format."""

import re

from tests.acceptance.helpers import ROOT

SECTIONS = ["Service boundaries", "JWT claims", "Error format", "Data ownership", "URL prefixes"]


def _sections() -> dict[str, str]:
    path = ROOT / "ARCHITECTURE.md"
    assert path.is_file(), "ARCHITECTURE.md is missing"
    parts = re.split(r"^## +", path.read_text(), flags=re.MULTILINE)[1:]
    sections: dict[str, str] = {}
    for part in parts:
        title, *body = part.splitlines()
        # a line that still contains a TODO marker is a placeholder, not documentation
        sections[title.strip()] = "\n".join(line for line in body if "TODO" not in line).strip()
    return sections


def test_no_todo_markers_remain() -> None:
    text = (ROOT / "ARCHITECTURE.md").read_text()
    assert "TODO" not in text, "replace every TODO in ARCHITECTURE.md with your decisions"


def test_every_required_section_is_written() -> None:
    sections = _sections()
    missing = [s for s in SECTIONS if s not in sections]
    assert not missing, f"missing sections: {missing}"
    too_short = [s for s in SECTIONS if len(sections[s]) < 60]
    assert not too_short, f"write at least a few sentences in: {too_short}"


def test_jwt_claims_are_documented() -> None:
    claims = _sections().get("JWT claims", "")
    for claim in ("sub", "role", "exp"):
        assert re.search(rf"\b{claim}\b", claims), f"document the `{claim}` claim"


def test_data_ownership_names_the_tables() -> None:
    ownership = _sections().get("Data ownership", "").lower()
    for table in ("users", "items", "orders"):
        assert table in ownership, f"say which service owns `{table}`"


def test_url_prefixes_are_documented() -> None:
    prefixes = _sections().get("URL prefixes", "")
    assert "/auth" in prefixes and "/api" in prefixes
