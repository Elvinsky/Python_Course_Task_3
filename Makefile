PROJECTS := services/auth services/core
.DEFAULT_GOAL := check
.PHONY: setup lint typecheck test check fmt

setup:
	uv python install 3.14
	@for d in $(PROJECTS); do echo "== uv sync in $$d"; (cd $$d && uv sync) || exit 1; done

lint:
	@for d in $(PROJECTS); do echo "== lint $$d"; (cd $$d && uv run ruff check . && uv run ruff format --check .) || exit 1; done

typecheck:
	@for d in $(PROJECTS); do echo "== mypy $$d"; (cd $$d && uv run mypy .) || exit 1; done

test:
	@status=0; for d in $(PROJECTS); do echo "== pytest $$d"; (cd $$d && uv run pytest -q) || status=1; done; exit $$status

check: lint typecheck test

fmt:
	@for d in $(PROJECTS); do (cd $$d && uv run ruff check --fix . && uv run ruff format .); done
