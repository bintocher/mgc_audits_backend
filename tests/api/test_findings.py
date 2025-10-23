import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_findings(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/findings", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_findings_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/findings")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_findings_with_filters(client: AsyncClient, auth_headers):
    response = await client.get(
        "/api/v1/findings?skip=0&limit=10",
        headers=auth_headers
    )
    assert response.status_code == 200

