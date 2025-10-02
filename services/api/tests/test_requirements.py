"""Tests for requirement API endpoints."""

from __future__ import annotations

import uuid

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.models import RequirementType
from app.main import app


@pytest.mark.asyncio
async def test_create_and_list_requirements(project, persona_id: uuid.UUID) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_response = await client.post(
            "/v1/requirements",
            json={
                "project_id": project.id,
                "persona_id": str(persona_id),
                "text": "Export data to CSV",
                "type": RequirementType.FEATURE.value,
                "confidence": 0.8,
            },
        )
        assert create_response.status_code == 201
        created = create_response.json()
        assert created["project_id"] == project.id
        assert created["persona_id"] == str(persona_id)

        list_response = await client.get(f"/v1/requirements?project_id={project.id}")
        assert list_response.status_code == 200
        items = list_response.json()
        assert len(items) == 1
        assert items[0]["id"] == created["id"]

        filtered_response = await client.get(
            f"/v1/requirements?project_id={project.id}&persona_id={persona_id}"
        )
        assert filtered_response.status_code == 200
        filtered_items = filtered_response.json()
        assert len(filtered_items) == 1
        assert filtered_items[0]["id"] == created["id"]


@pytest.mark.asyncio
async def test_update_requirement(project, persona_id: uuid.UUID) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_response = await client.post(
            "/v1/requirements",
            json={
                "project_id": project.id,
                "persona_id": str(persona_id),
                "text": "Offline access",
                "type": RequirementType.IMPROVEMENT.value,
            },
        )
        requirement_id = create_response.json()["id"]

        update_response = await client.patch(
            f"/v1/requirements/{requirement_id}",
            json={"type": RequirementType.CONSTRAINT.value, "confidence": 0.55},
        )
        assert update_response.status_code == 200
        updated = update_response.json()
        assert updated["type"] == RequirementType.CONSTRAINT.value
        assert updated["confidence"] == 0.55

        clear_confidence = await client.patch(
            f"/v1/requirements/{requirement_id}",
            json={"confidence": None},
        )
        assert clear_confidence.status_code == 200
        assert clear_confidence.json()["confidence"] is None


@pytest.mark.asyncio
async def test_delete_requirement(project, persona_id: uuid.UUID) -> None:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        create_response = await client.post(
            "/v1/requirements",
            json={
                "project_id": project.id,
                "persona_id": str(persona_id),
                "text": "Realtime collaboration",
                "type": RequirementType.FEATURE.value,
            },
        )
        requirement_id = create_response.json()["id"]

        delete_response = await client.delete(f"/v1/requirements/{requirement_id}")
        assert delete_response.status_code == 204

        list_response = await client.get(f"/v1/requirements?project_id={project.id}")
        assert list_response.status_code == 200
        assert list_response.json() == []