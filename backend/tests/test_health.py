import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "checks" in data
        assert isinstance(data["checks"], dict)
        assert "api" in data["checks"]
        assert "db" in data["checks"]
        assert "redis" in data["checks"]
