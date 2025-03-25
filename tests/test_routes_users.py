from src.database.models import User
from src.services.auth import auth_service
from unittest.mock import patch, AsyncMock
import pickle

def test_get_me(client, get_token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        mock_user = User(id=1, username="test@example.com", email="test@example.com")

        # Pickle the user object
        pickled_user = pickle.dumps(mock_user)

        # Configure redis_mock.get to return the pickled user data
        redis_mock.get.return_value = pickled_user
    
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=mock_user))

        token = get_token
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get("api/users/me", headers=headers)
        assert response.status_code == 200
