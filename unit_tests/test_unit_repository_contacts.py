from unittest import TestCase
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.schemas import ContactModel
from src.database.models import Base, Contact, User
from src.repository.contacts import (
    create_contact,
    get_contact,
    get_contact_by_first_name,
    get_contact_by_last_name,
    get_contact_by_email,
    get_contacts,
    remove_contact,
    update_contact,
    get_upcoming_birthdays,
)
import pytest

class TestContacts(TestCase):
    @pytest.fixture(scope="module")
    def session():
        SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

        engine = create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        # Create the database

        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    @patch('src.repository.contacts')
    def test_create_contact(self, session):
        # Mocking the DB session
        session.add = MagicMock()
        session.commit = MagicMock()
        session.refresh = MagicMock()

        # Mock user and contact data
        user = User(id=1, username="john_doe")
        body = ContactModel(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="123-456-7890",
            birthday="1990-01-01",
            additional_info="Some info"
        )

        # Mock the Contact object to be created
        mock_contact = Contact(
            id=1, 
            first_name=body.first_name, 
            last_name=body.last_name, 
            email=body.email, 
            phone=body.phone,
            birthday=body.birthday,
            additional_info=body.additional_info,
            user_id=user.id
        )

        # Mock the function call
        session.add.return_value = None  # Simulate adding to DB
        session.commit.return_value = None
        session.refresh.return_value = mock_contact  # Simulate the refresh call

        # Run the create_contact function
        result = create_contact(body, user, session)

        # Compare the result's attributes with mock_contact
        self.assertEqual(result.first_name, mock_contact.first_name)
        self.assertEqual(result.last_name, mock_contact.last_name)
        self.assertEqual(result.email, mock_contact.email)
        self.assertEqual(result.phone, mock_contact.phone)
        self.assertEqual(result.birthday, mock_contact.birthday)
        self.assertEqual(result.additional_info, mock_contact.additional_info)
        self.assertEqual(result.user_id, mock_contact.user_id)
    
    @patch('src.repository.contacts')
    def test_get_contact_found(self, session):
        user = User(id=1, username="john_doe")
        contact_id = 1

        # Mock the result of the query
        mock_contact = Contact(id=contact_id, first_name="John", last_name="Doe", email="john.doe@example.com")
        session.execute.return_value.scalar_one_or_none.return_value = mock_contact
        
        # Run the get_contact function
        result = get_contact(contact_id, user, session)

        # Check the result
        self.assertEqual(result, mock_contact)

    @patch('src.repository.contacts')
    def test_get_contact_not_found(self, session):
        user = User(id=1, username="john_doe")
        contact_id = 999

        # Mock the result of the query to return None (not found)
        session.execute.return_value.scalar_one_or_none.return_value = None

        # Run the get_contact function
        result = get_contact(contact_id, user, session)

        # Check the result
        self.assertIsNone(result)

    @patch('src.repository.contacts')
    def test_remove_contact_found(self, session):
        user = User(id=1, username="john_doe")
        contact_id = 1

        # Mock the contact to be removed
        mock_contact = Contact(id=contact_id, first_name="John", last_name="Doe", email="john.doe@example.com")
        session.execute.return_value.scalar_one_or_none.return_value = mock_contact

        # Run the remove_contact function
        result = remove_contact(contact_id, user, session)

        # Check the result
        self.assertEqual(result, mock_contact)

    @patch('src.repository.contacts')
    def test_remove_contact_not_found(self, session):
        user = User(id=1, username="john_doe")
        contact_id = 999

        # Mock the query to return None (not found)
        session.execute.return_value.scalar_one_or_none.return_value = None

        # Run the remove_contact function
        result = remove_contact(contact_id, user, session)

        # Check the result
        self.assertIsNone(result)

    @patch('src.repository.contacts')
    def test_update_contact_found(self, session):
        user = User(id=1, username="john_doe")
        contact_id = 1
        body = ContactModel(
            first_name="Updated Name",
            last_name="Updated Last",
            email="updated@example.com",
            phone="987-654-3210",
            birthday="1991-02-01",
            additional_info="Updated info"
        )

        # Mock the contact to be updated
        mock_contact = Contact(id=contact_id, first_name="John", last_name="Doe", email="john.doe@example.com")
        session.execute.return_value.scalar_one_or_none.return_value = mock_contact

        # Run the update_contact function
        result = update_contact(contact_id, body, user, session)

        # Check the result
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)

    @patch('src.repository.contacts')
    def test_update_contact_not_found(self, session):
        user = User(id=1, username="john_doe")
        contact_id = 999
        body = ContactModel(
            first_name="Nonexistent",
            last_name="Contact",
            email="nonexistent@example.com",
            phone="000-000-0000",
            birthday="2000-01-01",
            additional_info="No info"
        )

        # Mock the query to return None (contact not found)
        session.execute.return_value.scalar_one_or_none.return_value = None

        # Run the update_contact function
        result = update_contact(contact_id, body, user, session)

        # Check the result
        self.assertIsNone(result)
