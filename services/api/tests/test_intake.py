"""Tests for requirement intake extraction endpoint."""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.models import RequirementType
from app.main import app


@pytest.mark.asyncio
async def test_extract_persists_requirements(project, persona_id: uuid.UUID) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.post(
            "/v1/intake/extract",
            json={
                "project_id": project.id,
                "persona_id": str(persona_id),
                "text": "Enable offline access\nSupport automatic backups",
            },
        )

    assert response.status_code == 201
    payload = response.json()
    assert isinstance(payload, list)
    assert len(payload) == 2

    for requirement in payload:
        assert requirement["project_id"] == project.id
        assert requirement["persona_id"] == str(persona_id)
        assert requirement["type"] == RequirementType.FEATURE.value
        assert requirement["text"] in {
            "Enable offline access",
            "Support automatic backups",
        }

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        list_response = await client.get(
            f"/v1/requirements?project_id={project.id}&persona_id={persona_id}"
        )

    assert list_response.status_code == 200
    items = list_response.json()
    assert len(items) == 2
    assert {item["persona_id"] for item in items} == {str(persona_id)}