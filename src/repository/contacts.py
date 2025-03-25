from datetime import datetime, timedelta
from sqlalchemy import and_, func, or_
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from sqlalchemy.types import String
from src.schemas import ContactModel
from src.database.models import Contact, User
from typing import List

def create_contact(body: ContactModel, user: User, db: Session) -> Contact:
    """
    Creates a new contact for a specific user.

    :param body: The data for the contact to create.
    :type body: ContactModel
    :param user: The user to create the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The newly created contact.
    :rtype: Contact
    """
    contact = Contact(
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone=body.phone,
        birthday=body.birthday,
        additional_info=body.additional_info,
        user_id=user.id,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

def get_contact(contact_id: int, user: User, db: Session) -> Contact:
    """
    Retrieves a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to retrieve.
    :type contact_id: int
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified ID, or None if it does not exist.
    :rtype: Contact | None
    """
    stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == user.id)
    result = db.execute(stmt)
    return result.scalar_one_or_none()

def get_contact_by_first_name(contact_first_name: str, user: User, db: Session) -> Contact:
    """
    Retrieves a single contact with the specified first name for a specific user.

    :param contact_first_name: The first name of the contact to retrieve.
    :type contact_first_name: str
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified first name, or None if it does not exist.
    :rtype: Contact | None
    """
    contact_first_name = contact_first_name
    stmt = select(Contact).where(Contact.first_name == contact_first_name, Contact.user_id == user.id)
    result = db.execute(stmt)

    return result.scalar_one_or_none()

def get_contact_by_last_name(contact_last_name: str, user: User, db: Session) -> Contact:
    """
    Retrieves a single contact with the specified last name for a specific user.

    :param contact_last_name: The last name of the contact to retrieve.
    :type contact_last_name: str
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified last name, or None if it does not exist.
    :rtype: Contact | None
    """
    contact_last_name = contact_last_name.strip()
    stmt = select(Contact).where(
        Contact.last_name == contact_last_name, 
        Contact.user_id == user.id
    )
    result = db.execute(stmt)

    return result.scalar_one_or_none()

def get_contact_by_email(contact_email: str, user: User, db: Session) -> Contact:
    """
    Retrieves a single contact with the specified email for a specific user.

    :param contact_email: The email of the contact to retrieve.
    :type contact_email: str
    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The contact with the specified email, or None if it does not exist.
    :rtype: Contact | None
    """
    contact_email = contact_email.strip()
    stmt = select(Contact).where(
        Contact.email == contact_email, 
        Contact.user_id == user.id
    )
    result = db.execute(stmt)

    return result.scalar_one_or_none()

def get_contacts(skip: int, limit: int, user: User, db: Session) -> List[Contact]:
    """
    Retrieves a list of contacts for a specific user with specified pagination parameters.

    :param skip: The number of contacts to skip.
    :type skip: int
    :param limit: The maximum number of contacts to return.
    :type limit: int
    :param user: The user to retrieve contacts for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: A list of contacts.
    :rtype: List[Contact]
    """
    stmt = select(Contact).where(Contact.user_id == user.id).offset(skip).limit(limit)
    result = db.execute(stmt)
    
    return result.scalars().all()

def remove_contact(contact_id: int, user: User, db: Session) -> Contact | None:
    """
    Removes a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to remove.
    :type contact_id: int
    :param user: The user to remove the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The removed contact, or None if it does not exist.
    :rtype: Contact | None
    """
    stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == user.id)
    result = db.execute(stmt)
    contact = result.scalar_one_or_none()
    
    if contact:
        db.delete(contact)
        db.commit()
    return contact

def update_contact(contact_id: int, body: ContactModel, user: User, db: Session) -> Contact:
    """
    Updates a single contact with the specified ID for a specific user.

    :param contact_id: The ID of the contact to update.
    :type contact_id: int
    :param body: The updated data for the contact.
    :type body: ContactModel
    :param user: The user to update the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: The updated contact, or None if it does not exist.
    :rtype: Contact | None
    """
    
    # Select the contact for the specific user and contact_id
    stmt = select(Contact).where(Contact.id == contact_id, Contact.user_id == user.id)
    result = db.execute(stmt)
    print(result)
    contact = result.scalar_one_or_none()

    if contact:
        # Update the contact fields
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.phone = body.phone
        contact.birthday = body.birthday
        contact.additional_info = body.additional_info
        
        # Commit the changes to the database
        db.commit()

    return contact

def get_upcoming_birthdays(user: User, db: Session) -> List[Contact]:
    """
    Retrieves contacts for a specific user with upcoming birthdays.

    :param user: The user to retrieve the contact for.
    :type user: User
    :param db: The database session.
    :type db: Session
    :return: contacts for a specific user with upcoming birthdays or empty List if it does not exist.
    :rtype: List[Contact]
    """
    today_date = datetime.now()
    dates_to_check = [(today_date + timedelta(days=i)).strftime("%m-%d") for i in range(8)]
    
    stmt = (
    select(Contact)
        .where(
            Contact.user_id == user.id,
            or_(*[func.cast(Contact.birthday, String).like(f"%{d}%") for d in dates_to_check])
        )
    )
    result = db.execute(stmt)
    contacts = result.scalars().all()

    return contacts
