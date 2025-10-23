import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_dashboard_stats(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/dashboard/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_audits" in data
    assert "total_findings" in data
    assert "active_findings" in data


@pytest.mark.asyncio
async def test_get_my_tasks(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/dashboard/my_tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "active_findings" in data
    assert "upcoming_audits" in data

