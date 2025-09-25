FROM python:3.12-slim

ENV POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONUNBUFFERED=1

RUN pip install --no-cache-dir "poetry==2.2.1"

WORKDIR /app

COPY pyproject.toml ./

RUN poetry install --only main --no-interaction --no-ansi

COPY worker ./worker
COPY run_worker.py ./

CMD ["poetry", "run", "python", "run_worker.py"]
