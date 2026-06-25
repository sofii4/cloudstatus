import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_get_all_services_status_empty():
    """Test status endpoint when no services are monitored."""
    with patch("app.database.get_db") as mock_get_db, \
         patch("app.services.cache.get_all_statuses") as mock_get_all_statuses:
        
        # Mock database to return empty list of services
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalars().all.return_value = []
        mock_db.execute.return_value = mock_result
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        # Mock cache to return empty dict
        mock_get_all_statuses.return_value = {}
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/status")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0


@pytest.mark.asyncio
async def test_get_all_services_status_with_data():
    """Test status endpoint with monitored services."""
    with patch("app.database.get_db") as mock_get_db, \
         patch("app.services.cache.get_all_statuses") as mock_get_all_statuses:
        
        # Mock database to return sample services
        mock_db = AsyncMock()
        mock_result = AsyncMock()
        mock_result.scalars().all.return_value = [
            type('Service', (), {'id': 1, 'name': 'Test Service', 'url': 'https://example.com', 'is_active': True})(),
            type('Service', (), {'id': 2, 'name': 'Another Service', 'url': 'https://another.com', 'is_active': True})()
        ]
        mock_db.execute.return_value = mock_result
        mock_get_db.return_value.__aenter__.return_value = mock_db
        
        # Mock cache to return status data
        mock_get_all_statuses.return_value = {
            "1": {"is_up": True, "response_ms": 150.5, "status_code": 200, "error_detail": None},
            "2": {"is_up": False, "response_ms": None, "status_code": None, "error_detail": "Connection timeout"}
        }
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/status")
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2
            
            # Check first service
            assert data[0]["id"] == 1
            assert data[0]["name"] == "Test Service"
            assert data[0]["url"] == "https://example.com"
            assert data[0]["current_status"]["is_up"] == True
            assert data[0]["current_status"]["response_ms"] == 150.5
            
            # Check second service
            assert data[1]["id"] == 2
            assert data[1]["name"] == "Another Service"
            assert data[1]["url"] == "https://another.com"
            assert data[1]["current_status"]["is_up"] == False
            assert data[1]["current_status"]["response_ms"] is None