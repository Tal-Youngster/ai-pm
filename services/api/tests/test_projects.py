"""Tests for project API endpoints."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.db.base import SessionLocal
from app.db.models import Client, Organization, PersonaRole, ProjectStatus, RequirementType
from app.main import app


def _create_organization_with_client() -> tuple[int, int]:
    """Helper to seed an organization and client for tests."""
    with SessionLocal() as session:
        organization = Organization(name="Projects Org")
        session.add(organization)
        session.flush()

        customer = Client(name="Acme Corp", organization_id=organization.id)
        session.add(customer)
        session.commit()
        return organization.id, customer.id


def _create_organization(name: str) -> int:
    with SessionLocal() as session:
        organization = Organization(name=name)
        session.add(organization)
        session.commit()
        return organization.id


@pytest.mark.asyncio
async def test_project_crud_flow() -> None:
    """End-to-end CRUD flow for projects including metadata handling."""
    organization_id, client_id = _create_organization_with_client()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        create_resp = await async_client.post(
            "/v1/projects",
            json={
                "name": "Discovery Project",
                "description": "First discovery engagement",
                "organization_id": organization_id,
                "client_id": client_id,
            },
        )
        assert create_resp.status_code == 201
        project_payload = create_resp.json()
        assert project_payload["name"] == "Discovery Project"
        assert project_payload["description"] == "First discovery engagement"
        assert project_payload["client_id"] == client_id
        assert project_payload["status"] == ProjectStatus.ACTIVE.value
        assert project_payload["personas"] == []
        assert project_payload["requirement_counts"] == {"total": 0, "by_type": {}}

        list_resp = await async_client.get(f"/v1/projects?organization_id={organization_id}")
        assert list_resp.status_code == 200
        projects = list_resp.json()
        assert len(projects) == 1
        assert projects[0]["id"] == project_payload["id"]
        assert projects[0]["persona_count"] == 0
        assert projects[0]["requirement_count"] == 0

        filtered_resp = await async_client.get(
            f"/v1/projects?organization_id={organization_id}&client_id={client_id}"
        )
        assert filtered_resp.status_code == 200
        assert filtered_resp.json()[0]["id"] == project_payload["id"]

        detail_resp = await async_client.get(f"/v1/projects/{project_payload['id']}")
        assert detail_resp.status_code == 200
        detail_payload = detail_resp.json()
        assert detail_payload["id"] == project_payload["id"]
        assert detail_payload["personas"] == []

        update_resp = await async_client.patch(
            f"/v1/projects/{project_payload['id']}",
            json={
                "name": "Updated Project",
                "status": ProjectStatus.PAUSED.value,
            },
        )
        assert update_resp.status_code == 200
        updated = update_resp.json()
        assert updated["name"] == "Updated Project"
        assert updated["status"] == ProjectStatus.PAUSED.value

        delete_resp = await async_client.delete(f"/v1/projects/{project_payload['id']}")
        assert delete_resp.status_code == 204

        final_list = await async_client.get(f"/v1/projects?organization_id={organization_id}")
        assert final_list.status_code == 200
        assert final_list.json() == []


@pytest.mark.asyncio
async def test_persona_requirement_flow_with_projects() -> None:
    """Ensure personas and requirements remain linked to projects after operations."""
    organization_id = _create_organization("Link Org")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        project_resp = await async_client.post(
            "/v1/projects",
            json={
                "name": "Lifecycle Project",
                "description": "Lifecycle work",
                "organization_id": organization_id,
            },
        )
        assert project_resp.status_code == 201
        project_payload = project_resp.json()
        project_id = project_payload["id"]

        persona_resp = await async_client.post(
            "/v1/personas",
            json={
                "project_id": project_id,
                "role": PersonaRole.CLIENT.value,
                "display_name": "Stakeholder",
            },
        )
        assert persona_resp.status_code == 201
        persona_payload = persona_resp.json()
        persona_id = persona_payload["id"]

        requirement_resp = await async_client.post(
            "/v1/requirements",
            json={
                "project_id": project_id,
                "persona_id": persona_id,
                "text": "Support offline mode",
                "type": RequirementType.FEATURE.value,
            },
        )
        assert requirement_resp.status_code == 201

        projects_resp = await async_client.get(f"/v1/projects?organization_id={organization_id}")
        assert projects_resp.status_code == 200
        listed_projects = projects_resp.json()
        assert len(listed_projects) == 1
        assert listed_projects[0]["id"] == project_id
        assert listed_projects[0]["persona_count"] == 1
        assert listed_projects[0]["requirement_count"] == 1

        detail_resp = await async_client.get(f"/v1/projects/{project_id}")
        assert detail_resp.status_code == 200
        detail_payload = detail_resp.json()
        assert detail_payload["requirement_counts"] == {
            "total": 1,
            "by_type": {RequirementType.FEATURE.value: 1},
        }
        assert detail_payload["personas"][0]["id"] == persona_id

        requirements_resp = await async_client.get(
            f"/v1/requirements?project_id={project_id}&persona_id={persona_id}"
        )
        assert requirements_resp.status_code == 200
        retrieved_requirements = requirements_resp.json()
        assert len(retrieved_requirements) == 1
        retrieved_requirement = retrieved_requirements[0]
        assert retrieved_requirement["persona_id"] == persona_id
        assert retrieved_requirement["project_id"] == project_id

