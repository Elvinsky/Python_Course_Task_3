# TODO (AC 7): write a multi-stage Dockerfile for this service. Requirements (checked by
# tests/acceptance/test_ac7_containers.py at the repository root):
#
#   - at least two stages: a `builder` that installs dependencies with uv, and a slim runtime image
#   - base images with a pinned tag (for example python:3.14-slim); never `latest`
#   - install from the lockfile: `uv sync --frozen --no-dev`
#   - copy only the virtual environment and the app into the runtime stage
#   - run as a non-root user (USER ...)
#   - no secrets baked in (no ENV/ARG with passwords, keys or tokens)
#   - start with: uvicorn app.main:app --host 0.0.0.0 --port 8000
#
# Hint: uv's Docker guide shows the multi-stage pattern: https://docs.astral.sh/uv/guides/integration/docker/
