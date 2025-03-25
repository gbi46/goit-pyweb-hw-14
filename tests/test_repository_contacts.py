import pytest
from datetime import date, datetime
from unittest.mock import AsyncMock, MagicMock
from src.services import contacts as contact_service
from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate

class TestContactsService:

    # Test create contact
    def test_create_contact(self):
        mock_user = User(id=1, username="neo", email="neo@example.com")
        mock_contact_data = {
            "first_name":"John", "last_name":"Doe", "email":"john.doe@example.com", 
            "phone":"1234567890", "birthday":"2000-01-01", "additional_info":"Info"
        }

        mock_contact = {
            "id": 1, "first_name":"John", "last_name":"Doe", "email":"john.doe@example.com", 
            "phone":"1234567890", "birthday":"2000-01-01", "additional_info":"Info"
        }

        mock_new_contact_data = ContactModel(
            first_name="John", 
            last_name="Doe", 
            email="john.doe@example.com", 
            phone="1234567890", 
            birthday="2000-01-01", 
            additional_info="Info"
        )
        
        # Mock Contact object to be returned from the DB (after creation)
        mock_new_contact = Contact(
            id=1, 
            first_name="John", 
            last_name="Doe", 
            email="john.doe@example.com", 
            phone="1234567890", 
            birthday="2000-01-01", 
            user_id=1, 
            additional_info="Info"
        )
        
        mock_db = AsyncMock()
        mock_db.add = AsyncMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock(return_value=mock_contact)

        # Test create contact
        result = contact_service.create_new_contact(mock_new_contact_data, mock_user, mock_db)

        # Compare attributes of the contact instead of the objects themselves
        assert result.first_name == mock_contact["first_name"]
        assert result.last_name == mock_contact["last_name"]
        assert result.email == mock_contact["email"]
        assert result.phone == mock_contact["phone"]
        assert result.birthday == datetime.strptime(mock_contact["birthday"], '%Y-%m-%d').date()
        assert result.additional_info == mock_contact["additional_info"]

        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_get_contact(self):
        mock_user = User(id=1, username="neo", email="neo@example.com")
        mock_contact = Contact(
            id=1, first_name="John", last_name="Doe", email="john.doe@example.com", 
            phone="1234567890", birthday="2000-01-01", user_id=1, additional_info="Info"
        )

        # Mock database session
        mock_db = MagicMock()
        
        # Mock `execute` to return a result object
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contact
        mock_db.execute.return_value = mock_result

        # Test get contact by ID
        result = contact_service.get_contact(1, mock_user, mock_db)

        assert result == mock_contact
        mock_db.execute.assert_called_once()

    # Test update contact
    def test_update_contact(self):
        # Create a mock user
        mock_user = User(id=1, username="neo", email="neo@example.com")
        
        # Create a mock Contact object
        mock_contact = Contact(
            id=1, first_name="John", last_name="Doe", email="john.doe@example.com", 
            phone="1234567890", birthday="2000-01-01", user_id=1, additional_info="Info"
        )
        
        # Create a mock ContactModel to simulate the update
        mock_contact_update = ContactModel(
            first_name="Jane", last_name="Doe", email="john.doe@example.com", 
            phone="1234567890", birthday="2000-01-01", additional_info="Info"
        )
        
        # Create a mock database session
        mock_db = MagicMock()

        # Mock the execute method to return a MagicMock object with scalar_one_or_none
        mock_execute = MagicMock()
        mock_execute.scalar_one_or_none.return_value = mock_contact  # Mock the method to return the mock_contact
        mock_db.execute = mock_execute  # Assign the mock execute to the db mock
        
        # Mock the commit method
        mock_db.commit = MagicMock()

        # Call the modify_contact function
        result = contact_service.modify_contact(1, mock_contact_update, mock_user, mock_db)

        # Assert that the result is the updated contact
        assert result.first_name == "Jane"
        assert result.last_name == "Doe"
        
        # Assert commit was called once
        mock_db.commit.assert_called_once()

    # Test delete contact
    def test_delete_contact(self):
        mock_user = User(id=1, username="neo", email="neo@example.com")
        mock_contact = Contact(
            id=1, first_name="John", last_name="Doe", email="john.doe@example.com", 
            phone="1234567890", birthday="2000-01-01", user_id=1, additional_info="Info"
        )
        
        mock_db = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contact
        mock_db.execute.return_value = mock_result

        mock_db.delete = MagicMock()
        mock_db.commit = MagicMock()

        # Test delete contact
        result = contact_service.delete_contact(1, mock_user, mock_db)

        print(f"Result ln 139: {result}")
        print(f"Mock contact ln 140: {mock_contact}")

        assert result == mock_contact
        mock_db.delete.assert_called_once()
        mock_db.commit.assert_called_once()

    # Test get contacts
    def test_get_contacts(self):
        mock_user = User(id=1, username="neo", email="neo@example.com")
        mock_contacts = [
            Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com", 
                    phone="1234567890", birthday="2000-01-01", user_id=1, additional_info="Info"),
            Contact(id=2, first_name="Jane", last_name="Smith", email="jane.smith@example.com", 
                    phone="9876543210", birthday="1995-05-15", user_id=1, additional_info="Info")
        ]
        
        mock_db = MagicMock()
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_contacts
        mock_db.execute.return_value = mock_result

        # Test get contacts
        result = contact_service.list_contacts(0, 10, mock_user, mock_db)

        assert len(result) == 2
        assert result == mock_contacts

    # Test get upcoming birthdays
    def test_get_upcoming_birthdays(self):
        mock_user = User(id=1, username="neo", email="neo@example.com")
        mock_contacts = [
            Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com",
                    phone="1234567890", birthday="2000-01-01", user_id=1, additional_info="Info")
        ]
        
        mock_db = MagicMock()
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_contacts
        mock_db.execute.return_value = mock_result

        result = contact_service.get_upcoming_birthdays_for_user(mock_user, mock_db)

        assert len(result) == 1
        assert result == mock_contacts

    # Test get contact by first name
    def test_get_contact_by_first_name(self):
        mock_user = User(id=1, username="neo", email="neo@example.com")
        mock_contact = Contact(
            id=1, first_name="John", last_name="Doe", email="john.doe@example.com", 
            phone="1234567890", birthday="2000-01-01", user_id=1, additional_info="Info"
        )
        
        mock_db = MagicMock()
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contact
        mock_db.execute.return_value = mock_result

        # Test get contact by first name
        result = contact_service.fetch_contact_by_first_name("John", mock_user, mock_db)

        assert result == mock_contact
        mock_db.execute.assert_called_once()

    # Test get contact by last name
    def test_get_contact_by_last_name(self):
        mock_user = User(id=1, username="neo", email="neo@example.com")
        mock_contact = Contact(
            id=1, first_name="John", last_name="Doe", email="john.doe@example.com", 
            phone="1234567890", birthday="2000-01-01", user_id=1, additional_info="Info"
        )
        
        mock_db = MagicMock()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contact
        mock_db.execute.return_value = mock_result

        # Test get contact by last name
        result = contact_service.fetch_contact_by_last_name("Doe", mock_user, mock_db)

        assert result == mock_contact
        mock_db.execute.assert_called_once()

    # Test get contact by email
    def test_get_contact_by_email(self):
        mock_user = User(id=1, username="neo", email="neo@example.com")
        mock_contact = Contact(
            id=1, first_name="John", last_name="Doe", email="john.doe@example.com", 
            phone="1234567890", birthday="2000-01-01", user_id=1, additional_info="Info"
        )
        
        mock_db = MagicMock()
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_contact
        mock_db.execute.return_value = mock_result

        # Test get contact by email
        result = contact_service.fetch_contact_by_email("john.doe@example.com", mock_user, mock_db)

        assert result == mock_contact
        mock_db.execute.assert_called_once()
