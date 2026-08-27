import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root status endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "WellNexa" in data["app"]

@pytest.mark.asyncio
async def test_health_check_endpoint(client: AsyncClient):
    """Test /api/v1/health status endpoint."""
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "healthy"
    assert payload["data"]["database"] == "healthy"
    assert payload["data"]["version"] == "0.1.0"
