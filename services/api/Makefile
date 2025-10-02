.PHONY: dev migrate upgrade

MESSAGE ?=

dev:
	poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

migrate:
	@if [ -z "$(MESSAGE)" ]; then \
		echo "Please provide a migration message via MESSAGE=..."; \
		exit 1; \
	fi
	poetry run alembic revision --autogenerate -m "$(MESSAGE)"

upgrade:
	poetry run alembic upgrade head
