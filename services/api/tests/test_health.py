import pytest
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_healthz() -> None:
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_ping() -> None:
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        response = await client.get("/v1/ping")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
