# Three independent uv projects: the repository root (static checks), services/auth and services/core.
PROJECTS := . services/auth services/core
SERVICES := services/auth services/core
.DEFAULT_GOAL := check
.PHONY: setup lint typecheck test check fmt

setup:            ## create a virtual environment in each project and install everything
	uv python install 3.14
	@for d in $(PROJECTS); do echo "== uv sync in $$d"; (cd $$d && uv sync) || exit 1; done

lint:             ## style and static checks in every project
	@for d in $(PROJECTS); do echo "== lint $$d"; (cd $$d && uv run ruff check . && uv run ruff format --check .) || exit 1; done

typecheck:        ## strict type checks in every project
	@for d in $(PROJECTS); do echo "== mypy $$d"; (cd $$d && uv run mypy .) || exit 1; done

test:             ## acceptance tests + your own tests in every project (does not stop at the first failure)
	@status=0; for d in $(PROJECTS); do echo "== pytest $$d"; (cd $$d && uv run pytest -q) || status=1; done; exit $$status

check: lint typecheck test   ## everything: this is the definition of "green"

fmt:              ## auto-fix what can be fixed
	@for d in $(PROJECTS); do (cd $$d && uv run ruff check --fix . && uv run ruff format .); done
