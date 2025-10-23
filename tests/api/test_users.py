import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_users(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/users", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_users_unauthorized(client: AsyncClient):
    response = await client.get("/api/v1/users")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_user_by_id(client: AsyncClient, auth_headers, test_user):
    response = await client.get(f"/api/v1/users/{test_user.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_update_user_profile(client: AsyncClient, auth_headers):
    response = await client.patch(
        "/api/v1/users/me",
        headers=auth_headers,
        json={"first_name_ru": "Обновленное Имя"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["first_name_ru"] == "Обновленное Имя"

