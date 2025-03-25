import hashlib
import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from unittest.mock import MagicMock
from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel
from src.repository import users

@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock(spec=Session)

@pytest.fixture
def user_data():
    """Provide sample user data."""
    return UserModel(username="testuser", email="test@example.com", password="password123")

@pytest.mark.asyncio
async def test_get_user_by_email(mock_db):
    """Test getting a user by email."""
    user = User(id=1, username="testuser", email="test@example.com")
    mock_db.query.return_value.filter.return_value.first.return_value = user

    result = await users.get_user_by_email("test@example.com", mock_db)
    assert result == user

def get_gravatar_url(email: str):
    email_hash = hashlib.md5(email.lower().encode('utf-8')).hexdigest()
    return f"https://www.gravatar.com/avatar/{email_hash}"

@pytest.mark.asyncio
async def test_create_user(mock_db, user_data):
    expected_avatar_url = get_gravatar_url(user_data.email)
    with patch('libgravatar.Gravatar') as MockGravatar:
        mock_gravatar_instance = MockGravatar.return_value
        mock_gravatar_instance.get_image.return_value = "http://example.com/avatar.jpg"

        new_user = await users.create_user(user_data, mock_db)

        assert new_user.username == user_data.username
        assert new_user.email == user_data.email
        assert new_user.avatar == expected_avatar_url
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_is_reset_token_expired():
    """Test checking if a reset token is expired."""
    expired_time = datetime.now(timezone.utc) - timedelta(days=1)
    assert await users.is_reset_token_expired(expired_time) is True
    assert await users.is_reset_token_expired(None) is False

@pytest.mark.asyncio
async def test_update_token(mock_db):
    """Test updating a user's refresh token."""
    user = User(id=1, username="testuser", email="test@example.com")
    mock_db.query.return_value.filter.return_value.first.return_value = user

    await users.update_token(user, "new_refresh_token", mock_db)

    assert user.refresh_token == "new_refresh_token"
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_confirmed_email(mock_db):
    """Test confirming a user's email."""
    user = User(id=1, username="testuser", email="test@example.com", confirmed=False)
    mock_db.query.return_value.filter.return_value.first.return_value = user

    await users.confirmed_email("test@example.com", mock_db)

    assert user.confirmed is True
    mock_db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_update_avatar(mock_db):
    """Test updating a user's avatar."""
    user = User(id=1, username="testuser", email="test@example.com", avatar=None)
    mock_db.query.return_value.filter.return_value.first.return_value = user

    updated_user = await users.update_avatar("test@example.com", "http://example.com/new_avatar.jpg", mock_db)

    assert updated_user.avatar == "http://example.com/new_avatar.jpg"
    mock_db.commit.assert_called_once()
    