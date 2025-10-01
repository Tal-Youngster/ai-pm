# syntax=docker/dockerfile:1.7
FROM python:3.11-slim AS base

ENV POETRY_VERSION=1.8.3 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /srv

# Copy dependency manifests and shared libraries first to leverage Docker layer caching
COPY services/worker/pyproject.toml ./services/worker/
COPY libs/py/common/pyproject.toml ./libs/py/common/
COPY libs/py/common ./libs/py/common

# Install runtime dependencies (no editable install of the service itself)
RUN poetry install --no-interaction --no-ansi --no-root --directory services/worker

# Copy application source code
COPY services/worker ./services/worker

ENV PYTHONPATH=/srv/services/worker

CMD ["poetry", "run", "--directory", "services/worker", "python", "run_worker.py"]
