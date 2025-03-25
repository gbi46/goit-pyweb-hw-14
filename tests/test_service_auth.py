import pytest
from unittest.mock import patch, MagicMock
from jose import jwt, JWTError
from fastapi import HTTPException, status
from src.database.models import User
from src.services.auth import Auth, auth_service
from src.conf.config import settings
from datetime import datetime, timedelta
import pickle

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def mock_redis():
    mock_redis = MagicMock()
    with patch.object(auth_service, 'r', mock_redis):
        yield mock_redis

@pytest.fixture
def auth_instance():
    return Auth()

def test_verify_password(auth_instance):
    plain_password = "password123"
    hashed_password = auth_instance.get_password_hash(plain_password)
    assert auth_instance.verify_password(plain_password, hashed_password)
    assert not auth_instance.verify_password("wrong_password", hashed_password)

def test_get_password_hash(auth_instance):
    password = "password123"
    hashed_password = auth_instance.get_password_hash(password)
    assert isinstance(hashed_password, str)
    assert hashed_password != password

@pytest.mark.asyncio
async def test_create_access_token(auth_instance):
    data = {"sub": "test@example.com"}
    token = await auth_instance.create_access_token(data)
    decoded_token = jwt.decode(token, auth_instance.SECRET_KEY, auth_instance.ALGORITHM)
    assert decoded_token["sub"] == "test@example.com"
    assert decoded_token["scope"] == "access_token"

@pytest.mark.asyncio
async def test_create_refresh_token(auth_instance):
    data = {"sub": "test@example.com"}
    token = await auth_instance.create_refresh_token(data)
    decoded_token = jwt.decode(token, auth_instance.SECRET_KEY, auth_instance.ALGORITHM)
    assert decoded_token["sub"] == "test@example.com"
    assert decoded_token["scope"] == "refresh_token"

@pytest.mark.asyncio
async def test_decode_refresh_token_valid(auth_instance):
    data = {"sub": "test@example.com", "scope": "refresh_token"}
    token = jwt.encode(data, auth_instance.SECRET_KEY, auth_instance.ALGORITHM)
    email = await auth_instance.decode_refresh_token(token)
    assert email == "test@example.com"

@pytest.mark.asyncio
async def test_decode_refresh_token_invalid_scope(auth_instance):
    data = {"sub": "test@example.com", "scope": "access_token"}
    token = jwt.encode(data, auth_instance.SECRET_KEY, auth_instance.ALGORITHM)
    with pytest.raises(HTTPException) as excinfo:
        await auth_instance.decode_refresh_token(token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Invalid scope for token"

@pytest.mark.asyncio
async def test_decode_refresh_token_jwt_error(auth_instance):
    with pytest.raises(HTTPException) as excinfo:
        await auth_instance.decode_refresh_token("invalid_token")
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Could not validate credentials"

@pytest.mark.asyncio
async def test_get_current_user_invalid_scope(auth_instance, mock_db):
    data = {"sub": "test@example.com", "scope": "refresh_token"}
    token = jwt.encode(data, auth_instance.SECRET_KEY, auth_instance.ALGORITHM)
    with pytest.raises(HTTPException) as excinfo:
        await auth_instance.get_current_user(token, mock_db)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_get_current_user_jwt_error(auth_instance, mock_db):
    with pytest.raises(HTTPException) as excinfo:
        await auth_instance.get_current_user("invalid_token", mock_db)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_create_email_token(auth_instance):
    data = {"sub": "test@example.com"}
    token = await auth_instance.create_email_token(data)
    decoded_token = jwt.decode(token, auth_instance.SECRET_KEY, auth_instance.ALGORITHM)
    assert decoded_token["sub"] == "test@example.com"

@pytest.mark.asyncio
async def test_get_email_from_token_valid(auth_instance):
    data = {"sub": "test@example.com"}
    token = await auth_instance.create_email_token(data)
    email = await auth_instance.get_email_from_token(token)
    assert email == "test@example.com"

@pytest.mark.asyncio
async def test_get_email_from_token_jwt_error(auth_instance):
    with pytest.raises(HTTPException) as excinfo:
        await auth_instance.get_email_from_token("invalid_token")
    assert excinfo.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY