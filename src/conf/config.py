from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic.config import ConfigDict
import os

load_dotenv()

class Settings(BaseSettings):
    app_location: str = os.getenv('APP_LOCATION')
    cloudinary_api_key: str = os.getenv('CLOUDINARY_API_KEY')
    cloudinary_api_secret: str = os.getenv('CLOUDINARY_API_SECRET')
    cloudinary_name: str = os.getenv('CLOUDINARY_NAME')
    secret_key: str = os.getenv('SECRET_KEY')
    jwt_algorithm: str = os.getenv('JWT_ALGORITHM')
    mail_username: str = os.getenv('MAIL_USERNAME')
    mail_password: str = "!@yvafimq_9@S"
    mail_from: str = os.getenv('MAIL_FROM')
    mail_port: int = os.getenv('MAIL_PORT')
    mail_server: str = os.getenv('MAIL_SERVER')
    mail_server: str = "mail.your-server.de"
    redis_host: str = os.getenv("REDIS_HOST")
    redis_local_host: str = os.getenv("REDIS_LOCAL_HOST")
    redis_port: int = os.getenv("REDIS_PORT")
    postgres_db_protocol: str = os.getenv("POSTGRES_DB_PROTOCOL")
    postgres_db_user: str = os.getenv("POSTGRES_DB_USER")
    postgres_db_password: str = os.getenv("POSTGRES_DB_PASSWORD")
    postgres_db_host: str = os.getenv("POSTGRES_DB_HOST")
    postgres_db_port: int = os.getenv("POSTGRES_DB_PORT")
    postgres_db_name: str = os.getenv("POSTGRES_DB_NAME")
    redis_host: str = os.getenv("REDIS_HOST")
    redis_port: int = os.getenv("REDIS_PORT")
    sqlalchemy_database_url: str = "postgresql://contacts:567234@localhost:5432/contacts_db"

    model_config = ConfigDict(
        env_file="../../.env",
        env_file_encoding="utf-8"
    )

settings = Settings()
