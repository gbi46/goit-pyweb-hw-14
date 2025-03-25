import pickle
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.repository import users as repository_users
from src.services.auth import auth_service
from src.schemas import ContactResponse, ContactUpdate
from unittest.mock import patch, AsyncMock

def test_read_contacts(client, get_token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        mock_user = User(id=1, username="neo", email="neo@example.com")

        # Pickle the user object
        pickled_user = pickle.dumps(mock_user)

        # Configure redis_mock.get to return the pickled user data
        redis_mock.get.return_value = pickled_user

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        monkeypatch.setattr(repository_users, "get_user_by_email", AsyncMock(return_value=mock_user))

        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=mock_user))

        # Mock repository_contacts.get_contacts to return a list of contacts
        mock_contacts = [
            ContactResponse(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", phone="1234567890", birthday="2000-01-01", user_id=1),
            ContactResponse(id=2, first_name="Jane", last_name="Smith", email="jane.smith@example.com", phone="9876543210", birthday="1995-05-15", user_id=1),
        ]
        monkeypatch.setattr("src.repository.contacts.get_contacts", AsyncMock(return_value=mock_contacts))

        token = get_token
        print(f"Token: {token}")
        headers = {"Authorization": f"Bearer {token}"}
        print(f"Headers: {headers}")

        response = client.get("/api/contacts/", headers=headers)

        print(f"Response Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 2 # verify the correct length of the returned list.
        assert ContactResponse(**response.json()[0]) # Verify the response model

def test_read_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        mock_user = User(id=1, username="neo", email="neo@example.com")

        # Pickle the user object
        pickled_user = pickle.dumps(mock_user)

        # Configure redis_mock.get to return the pickled user data
        redis_mock.get.return_value = pickled_user

        monkeypatch.setattr(repository_users, "get_user_by_email", AsyncMock(return_value=mock_user))
        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=mock_user))

        # Mock repository_contacts.get_contact with contact id
        mock_contact = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "birthday": "1990-01-01",
            "user_id": 1,
            "additional_info": "Some additional info"
        }

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        monkeypatch.setattr(repository_contacts, "get_contact", AsyncMock(return_value=mock_contact))

        token = get_token
        headers = {"Authorization": f"Bearer {token}"}

        response = client.get("/api/contacts/1", headers=headers)

        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert ContactResponse(**response.json()) # Verify the response model

# Test for creating a contact
def test_create_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        mock_contact = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "birthday": "1990-01-01",
            "user_id": 1,
            "additional_info": "Some additional info"
        }

        mock_user = User(id=1, username="neo", email="neo@example.com")

        monkeypatch.setattr(repository_users, "get_user_by_email", AsyncMock(return_value=mock_user))
        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=mock_user))

        # Pickle the user object
        pickled_user = pickle.dumps(mock_user)

        # Configure redis_mock.get to return the pickled user data
        redis_mock.get.return_value = pickled_user

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        monkeypatch.setattr(repository_contacts, "create_contact", AsyncMock(return_value=mock_contact))

        headers = {"Authorization": f"Bearer {get_token}"}
        response = client.post("/api/contacts/", json=mock_contact, headers=headers)

        assert response.status_code == 201
        assert response.json() == mock_contact

# Test for deleting a contact
def test_delete_contact(client, get_token, monkeypatch):
    with patch.object(auth_service, 'r') as redis_mock:
        mock_contact = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890",
            "birthday": "1990-01-01",
            "user_id": 1,
            "additional_info": "Some additional info"
        }

        mock_user = User(id=1, username="neo", email="neo@example.com")

        monkeypatch.setattr(repository_users, "get_user_by_email", AsyncMock(return_value=mock_user))
        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=mock_user))
        
        # Pickle the user object
        pickled_user = pickle.dumps(mock_user)

        # Configure redis_mock.get to return the pickled user data
        redis_mock.get.return_value = pickled_user

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        monkeypatch.setattr(repository_contacts, "remove_contact", AsyncMock(return_value=mock_contact))

        headers = {"Authorization": f"Bearer {get_token}"}
        response = client.delete("/api/contacts/delete/1", headers=headers)

        assert response.status_code == 200
        assert response.json() == mock_contact

# Test for updating a contact
def test_update_contact(client, monkeypatch, user, get_token):
    with patch.object(auth_service, 'r') as redis_mock:
        mock_contact_update = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "phone": "987-654-3210",
            "birthday": "2012-01-13",
            "done": True
        }
            
        mock_contact = {
            "id": 1,
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "phone": "987-654-3210",
            "birthday": "1990-01-01",
            "user_id": 1,
            "additional_info": "Some additional info"
        }

        mock_user = User(id=1, username="neo", email="neo@example.com")

        monkeypatch.setattr(repository_users, "get_user_by_email", AsyncMock(return_value=mock_user))
        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=mock_user))
        
        # Pickle the user object
        pickled_user = pickle.dumps(mock_user)

        # Configure redis_mock.get to return the pickled user data
        redis_mock.get.return_value = pickled_user

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        monkeypatch.setattr(repository_contacts, "update_contact", AsyncMock(return_value=mock_contact))

        print(f"Mocked update_contact return value: {mock_contact}")
        headers = {"Authorization": f"Bearer {get_token}"}
        response = client.put("/api/contacts/update/1", json=mock_contact_update, headers=headers)

        print(f"Response json: {response.json()}")
        assert response.status_code == 200
        assert response.json() == mock_contact

# Test for reading a contact by first name
def test_read_contact_by_first_name(client, monkeypatch, user, get_token, mock_contact):
    with patch.object(auth_service, 'r') as redis_mock:
        mock_user = User(id=1, username="neo", email="neo@example.com")

        monkeypatch.setattr(repository_users, "get_user_by_email", AsyncMock(return_value=mock_user))
        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=mock_user))
        
        # Pickle the user object
        pickled_user = pickle.dumps(mock_user)

        # Configure redis_mock.get to return the pickled user data
        redis_mock.get.return_value = pickled_user

        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=user))
        monkeypatch.setattr(repository_contacts, "get_contact_by_first_name", AsyncMock(return_value=mock_contact))

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        
        headers = {"Authorization": f"Bearer {get_token}"}
        response = client.get(f"/api/contacts/contact_by_first_name/{mock_contact['first_name']}", headers=headers)

        assert response.status_code == 200
        assert response.json() == mock_contact

# Test for reading a contact by last name
def test_read_contact_by_last_name(client, monkeypatch, user, get_token, mock_contact):
    with patch.object(auth_service, 'r') as redis_mock:
        mock_user = User(id=1, username="neo", email="neo@example.com")

        monkeypatch.setattr(repository_users, "get_user_by_email", AsyncMock(return_value=mock_user))
        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=mock_user))
        
        # Pickle the user object
        pickled_user = pickle.dumps(mock_user)

        # Configure redis_mock.get to return the pickled user data
        redis_mock.get.return_value = pickled_user

        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=user))
        monkeypatch.setattr(repository_contacts, "get_contact_by_last_name", AsyncMock(return_value=mock_contact))

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        
        headers = {"Authorization": f"Bearer {get_token}"}
        response = client.get(f"/api/contacts/contact_by_last_name/{mock_contact['last_name']}", headers=headers)

        assert response.status_code == 200
        assert response.json() == mock_contact

# Test for reading a contact by email
def test_read_contact_by_email(client, monkeypatch, user, get_token, mock_contact):
    with patch.object(auth_service, 'r') as redis_mock:
        mock_user = User(id=1, username="neo", email="neo@example.com")

        monkeypatch.setattr(repository_users, "get_user_by_email", AsyncMock(return_value=mock_user))
        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=mock_user))
        
        # Pickle the user object
        pickled_user = pickle.dumps(mock_user)

        # Configure redis_mock.get to return the pickled user data
        redis_mock.get.return_value = pickled_user
        
        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=user))
        monkeypatch.setattr(repository_contacts, "get_contact_by_email", AsyncMock(return_value=mock_contact))

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())
        
        headers = {"Authorization": f"Bearer {get_token}"}
        response = client.get(f"/api/contacts/contact_by_email/{mock_contact['email']}", headers=headers)

        assert response.status_code == 200
        assert response.json() == mock_contact

# Test for getting upcoming birthdays
def test_get_upcoming_birthdays(client, monkeypatch, user, get_token, mock_contact):
    with patch.object(auth_service, 'r') as redis_mock:
        mock_user = User(id=1, username="neo", email="neo@example.com")

        monkeypatch.setattr(repository_users, "get_user_by_email", AsyncMock(return_value=mock_user))
        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=mock_user))
        
        # Pickle the user object
        pickled_user = pickle.dumps(mock_user)

        # Configure redis_mock.get to return the pickled user data
        redis_mock.get.return_value = pickled_user
        
        mock_contacts = [mock_contact]  # Assuming the function returns a list of contacts
        monkeypatch.setattr(auth_service, "get_current_user", AsyncMock(return_value=user))
        monkeypatch.setattr(repository_contacts, "get_upcoming_birthdays", AsyncMock(return_value=mock_contacts))

        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.redis", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.identifier", AsyncMock())
        monkeypatch.setattr("fastapi_limiter.FastAPILimiter.http_callback", AsyncMock())

        headers = {"Authorization": f"Bearer {get_token}"}
        response = client.get("/api/contacts/upcoming_birthdays/", headers=headers)

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1  # Assuming we expect one contact
        assert response.json()[0] == mock_contact
