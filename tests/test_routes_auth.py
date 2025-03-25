from datetime import datetime, timedelta, timezone
from fastapi import status
from fastapi.testclient import TestClient
from main import app
from unittest.mock import ANY, AsyncMock, MagicMock, patch
from src.database.models import User
from src.repository.utils import logger
from src.services.auth import auth_service
from unittest.mock import patch
from src.database.db import get_db
import jwt
import pytest
import pytz
import uuid

def test_create_user(client: TestClient, user: dict, monkeypatch):
    mock_send_email = MagicMock()
    monkeypatch.setattr("src.routes.auth.send_email", mock_send_email)
    response = client.post(
        "/api/auth/signup",
        data={
            "username": user['username'],
            "email": user['email'],
            "password": user['password']
        }
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["user"]["email"] == user.get("email")
    assert "id" in data["user"]

def test_repeat_create_user(client, user):
    response = client.post(
        "/api/auth/signup",
        data={
            "username": user['username'],
            "email": user['email'],
            "password": user['password']
        }
    )
    assert response.status_code == 409, response.text
    data = response.json()
    assert data["detail"] == "Account already exists"

def test_login_user_not_confirmed(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Email not confirmed"

def test_login_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user.get('email')).first()
    current_user.confirmed = True
    session.commit()
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": user.get('password')},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user.get('email'), "password": 'password'},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid password"

def test_login_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": 'email', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text
    data = response.json()
    assert data["detail"] == "Invalid email"

@pytest.mark.asyncio
async def test_confirmed_email(client: TestClient):
    # User data to encode into the JWT
    email = "test@example.com"
    payload = {
        "sub": email
    }
    
    # Generate a real JWT token
    token = jwt.encode(payload, auth_service.SECRET_KEY, algorithm=auth_service.ALGORITHM)

    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db

    with patch("src.services.auth.auth_service.get_email_from_token", return_value=email), \
         patch("src.repository.users.get_user_by_email", new_callable=AsyncMock) as mock_get_user_by_email, \
         patch("src.repository.users.confirmed_email", new_callable=AsyncMock) as mock_confirmed_email: 
        
        # Mock the user object and its response
        mock_user = AsyncMock()
        mock_user.confirmed = False
        mock_get_user_by_email.return_value = mock_user
        
        response = client.get(f"/api/auth/confirmed_email/{token}")

        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response JSON: {response.json()}")

        # Assertions
        assert response.status_code == 200
        assert response.json() == {"message": "Email confirmed"}

        mock_get_user_by_email.assert_called_once_with(email, mock_db)
        mock_confirmed_email.assert_called_once_with(email, mock_db)

    app.dependency_overrides.clear()

def test_confirmed_email_already_confirmed(client):
    email = "test@example.com"

    payload = {
        "sub": email
    }
    
    token = jwt.encode(payload, auth_service.SECRET_KEY, algorithm=auth_service.ALGORITHM)

    mock_db = AsyncMock()

    async def override_get_db():
        yield mock_db

    app.dependency_overrides[get_db] = override_get_db
    
    with patch("src.services.auth.auth_service.get_email_from_token", return_value=email), \
         patch("src.repository.users.get_user_by_email", new_callable=AsyncMock) as mock_get_user_by_email, \
         patch("src.repository.users.confirmed_email", new_callable=AsyncMock) as mock_confirmed_email: 

        # Mock the user object and its response
        mock_user = AsyncMock()
        mock_user.confirmed = True
        mock_get_user_by_email.return_value = mock_user
        
        response = client.get(f"/api/auth/confirmed_email/{token}")

        # Assertions
        assert response.status_code == 200
        assert response.json() == {"message": "Your email is already confirmed"}

        mock_get_user_by_email.assert_called_once_with(email, mock_db)
        mock_confirmed_email.assert_not_called()

    app.dependency_overrides.clear()

def test_confirmed_email_invalid_token(client):
    email = "test@example.com"

    payload = {"sub": email}
    token = jwt.encode(payload, auth_service.SECRET_KEY, algorithm=auth_service.ALGORITHM)

    with patch("src.services.auth.auth_service.get_email_from_token", return_value=None) as mock_get_email_from_token:
        response = client.get(f"/api/auth/confirmed_email/{token}")

        # Assertions
        assert response.status_code == 400
        assert response.json() == {"detail": "Verification error"}

        mock_get_email_from_token.assert_called_once_with(token)

@pytest.mark.asyncio
async def test_refresh_token_success(client):
    """Test successful refresh token."""
    token = "valid_refresh_token"
    email = "test@example.com"
    
    # Mock user object
    user = MagicMock(email=email, refresh_token=token)

    mock_db = MagicMock()
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch('src.services.auth.Auth.decode_refresh_token', return_value=email), \
         patch('src.repository.users.get_user_by_email', return_value=user), \
         patch('src.services.auth.Auth.create_access_token', return_value="new_access_token"), \
         patch('src.services.auth.Auth.create_refresh_token', return_value="new_refresh_token"), \
         patch('src.repository.users.update_token') as mock_update_token:
        
        response = client.get("api/auth/refresh_token", headers={"Authorization": f"Bearer {token}"})

        logger.info(f"Response status code: {response.status_code}")
        logger.info(f"Response JSON: {response.json()}")
        
        assert response.status_code == 200
        assert response.json()["access_token"] == "new_access_token"
        assert response.json()["refresh_token"] == "new_refresh_token"
        assert response.json()["token_type"] == "bearer"

        logger.info("Update Token Call Arguments: %s", mock_update_token.call_args_list)

        mock_update_token.assert_called_once()
        call_args = mock_update_token.call_args[0]  # Get the positional arguments
        assert call_args[0] == user  # Check the user
        assert call_args[1] == "new_refresh_token"  # Check the token
        assert isinstance(call_args[2], MagicMock)

@pytest.mark.asyncio
async def test_refresh_token_invalid_token(client):
    """Test refresh token with an invalid token."""
    token = "invalid_refresh_token"
    
    with patch('src.services.auth.Auth.decode_refresh_token', side_effect=Exception("Invalid token")), \
         patch('src.repository.users.get_user_by_email') as mock_get_user:
        
        response = client.get("api/auth/refresh_token", headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid refresh token"
        mock_get_user.assert_not_called()

@pytest.mark.asyncio
async def test_refresh_token_user_not_found(client):
    """Test refresh token when user is not found."""
    token = "valid_refresh_token"
    email = "test@example.com"

    with patch('src.services.auth.Auth.decode_refresh_token', return_value=email), \
         patch('src.repository.users.get_user_by_email', return_value=None):
        
        response = client.get("api/auth/refresh_token", headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid refresh token"

@pytest.mark.asyncio
async def test_refresh_token_mismatched_token(client):
    """Test refresh token when the token does not match the user's stored token."""
    token = "valid_refresh_token"
    email = "test@example.com"
    
    # Mock user object with a different refresh token
    user = MagicMock(email=email, refresh_token="different_refresh_token")

    mock_db = MagicMock()

    # Override the get_db dependency to return the mock_db
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch('src.services.auth.auth_service.decode_refresh_token', return_value=email), \
         patch('src.repository.users.get_user_by_email', return_value=user), \
         patch('src.repository.users.update_token') as mock_update_token:
        
        response = client.get("api/auth/refresh_token", headers={"Authorization": f"Bearer {token}"})
        
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid refresh token"
        
        # Check that update_token was called with the correct parameters
        mock_update_token.assert_called_once_with(user, None, mock_db)

    # Clean up the dependency override
    app.dependency_overrides[get_db] = None

@pytest.mark.asyncio
async def test_password_reset_request(client: TestClient):
    # Mock data
    email = "test@example.com"
    username = "testuser"
    reset_token = str(uuid.uuid4())
    reset_token_expiry = datetime.now(timezone.utc).replace(tzinfo=pytz.UTC) + timedelta(hours=1)

    # Mock user object
    mock_user = AsyncMock()
    mock_user.email = email
    mock_user.username = username
    mock_user.reset_token = reset_token
    mock_user.reset_token_expired = reset_token_expiry

    # Mock database session
    mock_db = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db
    app.dependency_overrides[auth_service.get_current_user] = lambda: mock_user

    # Mock dependencies
    with patch("src.repository.users.get_user_by_email", return_value=mock_user) as mock_get_user_by_email, \
         patch("src.routes.auth.send_password_reset_email") as mock_send_password_reset_email:

        # Request payload
        payload = {"email": email}

        headers = {"Authorization": "Bearer test_token"}

        # Make request
        response = client.post("/api/auth/password-reset-request", json=payload, headers=headers)

        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Password reset email sent"}

        # Check function calls
        mock_get_user_by_email.assert_called_once_with(email, mock_db)
        mock_send_password_reset_email.assert_called_once_with(email, username, mock_user.reset_token, ANY)

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_password_reset_valid_token(client: TestClient):
    """Test successful password reset token verification"""
    reset_token = str(uuid.uuid4())

    # Mock user with a valid reset token
    mock_user = AsyncMock()
    mock_user.reset_token = reset_token
    mock_user.reset_token_expired = datetime.now(timezone.utc) + timedelta(hours=1)

    # Mock database session
    mock_db = AsyncMock()

    # Override dependency to use mock database
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("src.repository.users.get_user_by_reset_token", return_value=mock_user) as mock_get_user_by_reset_token, \
         patch("src.repository.users.is_reset_token_expired", return_value=False) as mock_is_reset_token_expired:

        response = client.get(f"/api/auth/password-reset?token={reset_token}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"reset-token": reset_token}

        mock_get_user_by_reset_token.assert_called_once_with(reset_token, mock_db)
        mock_is_reset_token_expired.assert_called_once_with(mock_user.reset_token_expired)

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_password_reset_invalid_token(client: TestClient):
    """Test password reset with an invalid token"""
    invalid_token = "invalid_token"

    # Mock database session
    mock_db = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("src.repository.users.get_user_by_reset_token", return_value=None) as mock_get_user_by_reset_token:
        response = client.get(f"/api/auth/password-reset?token={invalid_token}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Invalid reset token"}

        mock_get_user_by_reset_token.assert_called_once_with(invalid_token, mock_db)

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_password_reset_expired_token(client: TestClient):
    """Test password reset with an expired token"""
    reset_token = str(uuid.uuid4())

    # Mock user with an expired reset token
    mock_user = AsyncMock()
    mock_user.reset_token = reset_token
    mock_user.reset_token_expired = datetime.now(timezone.utc) - timedelta(hours=1)  # Expired

    # Mock database session
    mock_db = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("src.repository.users.get_user_by_reset_token", return_value=mock_user) as mock_get_user_by_reset_token, \
         patch("src.repository.users.is_reset_token_expired", return_value=True) as mock_is_reset_token_expired:

        response = client.get(f"/api/auth/password-reset?token={reset_token}")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Reset token expired"}

        mock_get_user_by_reset_token.assert_called_once_with(reset_token, mock_db)
        mock_is_reset_token_expired.assert_called_once_with(mock_user.reset_token_expired)

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_set_new_password_valid_token(client: TestClient):
    """Test successfully setting a new password with a valid token"""
    reset_token = str(uuid.uuid4())
    new_password = "NewSecurePassword123!"

    # Mock user with a valid reset token
    mock_user = AsyncMock()
    mock_user.reset_token = reset_token
    mock_user.reset_token_expired = None

    # Mock database session
    mock_db = AsyncMock()

    # Override dependency to use mock database
    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("src.repository.users.get_user_by_reset_token", return_value=mock_user) as mock_get_user_by_reset_token, \
         patch("src.repository.users.is_reset_token_expired", return_value=False) as mock_is_reset_token_expired, \
         patch("src.services.auth.auth_service.get_password_hash", return_value="hashed_password") as mock_get_password_hash:

        response = client.post(
            f"/api/auth/set-new-password?token={reset_token}&new_password={new_password}"
        )

        logger.info(f"Resp ln 417: {response.json()}")
        logger.info(f"Reset Token Expiry: {mock_user.reset_token_expired}")
        logger.info(f"Current time: {datetime.now(timezone.utc)}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Password updated successfully"}

        mock_get_user_by_reset_token.assert_called_once_with(reset_token, mock_db)
        mock_is_reset_token_expired.assert_called_once_with(mock_user.reset_token_expired)
        mock_get_password_hash.assert_called_once_with(new_password)

        mock_db.commit.assert_called_once()

    app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_set_new_password_invalid_token(client: TestClient):
    """Test setting a new password with an invalid token"""
    invalid_token = "invalid_token"
    new_password = "NewSecurePassword123!"

    # Mock database session
    mock_db = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("src.repository.users.get_user_by_reset_token", return_value=None) as mock_get_user_by_reset_token:
        response = client.post(
            f"/api/auth/set-new-password?token={invalid_token}&new_password={new_password}"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Invalid reset token"}

        mock_get_user_by_reset_token.assert_called_once_with(invalid_token, mock_db)

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_set_new_password_expired_token(client: TestClient):
    """Test setting a new password with an expired token"""
    reset_token = str(uuid.uuid4())
    new_password = "NewSecurePassword123!"

    # Mock user with an expired reset token
    mock_user = AsyncMock()
    mock_user.reset_token = reset_token
    mock_user.reset_token_expired = datetime.now(timezone.utc) - timedelta(hours=1)  # Expired

    # Mock database session
    mock_db = AsyncMock()

    app.dependency_overrides[get_db] = lambda: mock_db

    with patch("src.repository.users.get_user_by_reset_token", return_value=mock_user) as mock_get_user_by_reset_token, \
         patch("src.repository.users.is_reset_token_expired", return_value=True) as mock_is_reset_token_expired:

        response = client.post(
            f"/api/auth/set-new-password?token={reset_token}&new_password={new_password}"
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"detail": "Reset token expired"}

        mock_get_user_by_reset_token.assert_called_once_with(reset_token, mock_db)
        mock_is_reset_token_expired.assert_called_once_with(mock_user.reset_token_expired)

    app.dependency_overrides.clear()
