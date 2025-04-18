from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pathlib import Path
from pydantic import EmailStr, TypeAdapter
from src.conf.config import settings
from src.repository.utils import logger
from src.services.auth import auth_service

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=TypeAdapter(EmailStr).validate_python(settings.mail_from),
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Email rom fast api and hetzner",
    MAIL_DEBUG=1,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)

async def send_email(email: EmailStr, username: str, host: str):
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        logger.info(f"before send message: {email}")
        await fm.send_message(message, template_name="email_template.html")
        logger.info(f"email sent to: {email}")
    except ConnectionErrors as err:
        print(err)

async def send_password_reset_email(email: EmailStr, username: str, token: str, host: str):
    try:
        message = MessageSchema(
            subject="Reset your password ",
            recipients=[email],
            template_body={"host": host, "username": username, "reset_token": token},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="reset-password-email-template.html")
    except ConnectionErrors as err:
        print(err)
