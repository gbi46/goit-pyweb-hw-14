from datetime import datetime
from src.database.models import Contact, User
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
from sqlalchemy.orm import Session
from typing import List

def create_new_contact(body, user: User, db: Session) -> Contact:
    """Service function to create a new contact"""
    return create_contact(body=body, user=user, db=db)

def fetch_contact(contact_id: int, user: User, db: Session) -> Contact:
    """Service function to get a contact by ID"""
    return get_contact(contact_id=contact_id, user=user, db=db)

def fetch_contact_by_first_name(contact_first_name: str, user: User, db: Session) -> Contact:
    """Service function to get a contact by first name"""
    return get_contact_by_first_name(contact_first_name=contact_first_name, user=user, db=db)

def fetch_contact_by_last_name(contact_last_name: str, user: User, db: Session) -> Contact:
    """Service function to get a contact by last name"""
    return get_contact_by_last_name(contact_last_name=contact_last_name, user=user, db=db)

def fetch_contact_by_email(contact_email: str, user: User, db: Session) -> Contact:
    """Service function to get a contact by email"""
    return get_contact_by_email(contact_email=contact_email, user=user, db=db)

def list_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """Service function to get a list of contacts"""
    return get_contacts(skip=skip, limit=limit, user=user, db=db)

def delete_contact(contact_id: int, user: User, db: Session) -> Contact:
    """Service function to delete a contact"""
    return remove_contact(contact_id=contact_id, user=user, db=db)

def modify_contact(contact_id: int, body, user: User, db: Session) -> Contact:
    """Service function to update an existing contact"""
    return update_contact(contact_id=contact_id, body=body, user=user, db=db)

def get_upcoming_birthdays_for_user(user: User, db: Session) -> List[Contact]:
    """Service function to get upcoming birthdays"""
    return get_upcoming_birthdays(user=user, db=db)
