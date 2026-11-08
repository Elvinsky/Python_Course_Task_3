"""AC 5 (part 1): the OTP tests you wrote with fakeredis cover the required scenarios."""

import ast
import re
from pathlib import Path

TEST_FILE = Path(__file__).resolve().parents[1] / "test_otp.py"
REQUIRED = {
    "success": r"success|valid|correct",
    "wrong code": r"wrong|invalid",
    "expiry": r"expir|ttl",
    "single use": r"single|reuse|twice|once",
}


def _test_names() -> list[str]:
    tree = ast.parse(TEST_FILE.read_text())
    return [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        and node.name.startswith("test_")
    ]


def test_at_least_four_otp_tests_exist() -> None:
    names = _test_names()
    assert len(names) >= 4, f"tests/test_otp.py has {len(names)} tests; write at least 4"


def test_required_scenarios_are_covered() -> None:
    names = _test_names()
    missing = [
        label
        for label, pattern in REQUIRED.items()
        if not any(re.search(pattern, n) for n in names)
    ]
    assert not missing, f"no test name covers: {missing}. Test names found: {names}"


def test_otp_tests_use_the_fakeredis_fixture() -> None:
    assert "redis_client" in TEST_FILE.read_text(), "use the redis_client (fakeredis) fixture"
