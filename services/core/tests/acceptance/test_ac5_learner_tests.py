"""AC 5 (part 2): the guard-matrix tests you wrote cover 401, 403 and 200."""

import ast
import re
from pathlib import Path

TEST_FILE = Path(__file__).resolve().parents[1] / "test_guards.py"


def _tests() -> list[ast.AsyncFunctionDef | ast.FunctionDef]:
    tree = ast.parse(TEST_FILE.read_text())
    return [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef)
        and node.name.startswith("test_")
    ]


def test_at_least_four_guard_tests_exist() -> None:
    count = len(_tests())
    assert count >= 4, f"tests/test_guards.py has {count} tests; write at least 4"


def test_the_guard_matrix_covers_401_403_and_200() -> None:
    source = TEST_FILE.read_text()
    missing = [code for code in ("401", "403", "200") if not re.search(rf"\b{code}\b", source)]
    assert not missing, f"tests/test_guards.py never mentions the status codes {missing}"
