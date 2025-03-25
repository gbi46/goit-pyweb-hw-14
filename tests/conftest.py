import pytest
import pytest_asyncio
import warnings
from fastapi.testclient import TestClient
from main import app
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.models import Base
from src.database.db import get_db
from src.services.auth import auth_service

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def pytest_configure(config):
    warnings.filterwarnings("ignore", category=DeprecationWarning, message=".*crypt.*")

@pytest.fixture(scope="module")
def client(session):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

test_user = {"username": "neo", "email": "neo@example.com", "password": "123456789"}

@pytest.fixture(scope="module")
def user():
    return {"username": "deadpool", "email": "deadpool@example.com", "password": "123456789"}

@pytest.fixture
def mock_contact():
    """Fixture to provide a mock contact dictionary."""
    return {
        "id": 1,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone": "987-654-3210",
        "birthday": "1990-01-01",
        "user_id": 1,
        "additional_info": "Some additional info"
    }

@pytest_asyncio.fixture()
async def get_token():
    user_data = {"sub": test_user["email"]}
    print(f"User Data: {user_data}")

    token = await auth_service.create_access_token(data=user_data)

    print(f"token from get token: {token}")

    return token
