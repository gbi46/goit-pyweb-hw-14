import pytest
from unittest.mock import AsyncMock, Mock, patch
from fastapi_mail import FastMail, MessageSchema
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr
from src.services.auth import auth_service
from src.services.email import send_email, send_password_reset_email

@pytest.mark.asyncio
async def test_send_email():
    email: EmailStr = "test@example.com"
    username = "testuser"
    host = "http://localhost"

    mock_send_token = "mock_send_token"
    
    mock_message = AsyncMock()
    mock_message.subject = "Confirm your email "
    mock_message.recipients = [email]
    mock_message.template_body = {
        "host": host,
        "username": username,
    }
    
    # Mock `create_email_token`
    with patch.object(auth_service, "create_email_token", return_value=mock_send_token), \
         patch.object(FastMail, "send_message", new_callable=AsyncMock) as mock_send:
        
        mock_send.return_value = mock_message
        
        await send_email(email, username, host)

        mock_send.assert_called_once()
        
        # Verify the message contents
        args, kwargs = mock_send.call_args
        message: MessageSchema = args[0]

        print(f"Message: {message}")

        assert message.subject == "Confirm your email "
        assert message.recipients == [email]
        assert message.template_body["host"] == host
        assert message.template_body["username"] == username

@pytest.mark.asyncio
async def test_send_password_reset_email():
    email: EmailStr = "test@example.com"
    username = "testuser"
    reset_token = "mock_reset_token"
    host = "http://localhost"

    with patch.object(FastMail, "send_message", new_callable=AsyncMock) as mock_send:
        await send_password_reset_email(email, username, reset_token, host)

        # Ensure `send_message` was called once
        mock_send.assert_called_once()
        
        # Verify the message contents
        args, kwargs = mock_send.call_args
        message: MessageSchema = args[0]  # Extract the message object

        assert message.subject == "Reset your password "
        assert message.recipients == [email]
        assert message.template_body["host"] == host
        assert message.template_body["username"] == username
        assert message.template_body["reset_token"] == reset_token

@pytest.mark.asyncio
async def test_send_email_connection_error():
    email: EmailStr = "test@example.com"
    username = "testuser"
    host = "http://localhost"

    mock_token = "mock_token"

    with patch.object(auth_service, "create_email_token", return_value=mock_token), \
         patch.object(FastMail, "send_message", new_callable=AsyncMock) as mock_send:
        
        # Simulate a connection error
        mock_send.side_effect = ConnectionErrors("SMTP server unavailable")

        await send_email(email, username, host)

        mock_send.assert_called_once()

@pytest.mark.asyncio
async def test_send_password_reset_email_connection_error():
    email: EmailStr = "test@example.com"
    username = "testuser"
    reset_token = "mock_reset_token"
    host = "http://localhost"

    with patch.object(FastMail, "send_message", new_callable=AsyncMock) as mock_send:
        
        # Simulate a connection error
        mock_send.side_effect = ConnectionErrors("SMTP server unavailable")

        await send_password_reset_email(email, username, reset_token, host)

        mock_send.assert_called_once()
