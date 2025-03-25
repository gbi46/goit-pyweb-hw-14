from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.repository import contacts as repository_contacts
from src.schemas import ContactModel, ContactResponse, ContactUpdate
from src.services.auth import Auth
from typing import List

auth_service = Auth()
router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get(
    "/",
    response_model=List[ContactResponse],
    description="No more than 10 requests pro minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def read_contacts(
        skip: int = 0,
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(skip, limit, current_user, db)
    return contacts

@router.get(
    "/{contact_id}", 
    response_model=ContactResponse,
    description="No more than 10 requests pro minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def read_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    contact = await repository_contacts.get_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.post(
    "/", 
    response_model=ContactResponse, 
    status_code=status.HTTP_201_CREATED,
    description="No more than 10 requests pro minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],
)
async def create_contact(
        body: ContactModel,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):

    return await repository_contacts.create_contact(body, current_user, db)

@router.delete(
    "/delete/{contact_id}", 
    response_model=ContactResponse,
    description="No more than 10 requests pro minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],    
)
async def remove_contact(
        contact_id: int,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):

    contact = await repository_contacts.remove_contact(contact_id, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.put(
    "/update/{contact_id}", 
    response_model=ContactResponse,
    description="No more than 10 requests pro minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],    
)
async def update_contact(
        contact_id: int,
        body: ContactUpdate,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    contact = await repository_contacts.update_contact(contact_id, body, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.get(
    "/contact_by_first_name/{contact_first_name}", 
    response_model=ContactResponse,
    description="No more than 10 requests pro minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],    
)
async def read_contact_by_first_name(
        contact_first_name: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    contact = await repository_contacts.get_contact_by_first_name(contact_first_name, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.get(
    "/contact_by_last_name/{contact_last_name}", 
    response_model=ContactResponse,
    description="No more than 10 requests pro minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],    
)
async def read_contact_by_last_name(
        contact_last_name: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    contact = await repository_contacts.get_contact_by_last_name(contact_last_name, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.get(
    "/contact_by_email/{contact_email}", 
    response_model=ContactResponse,
    description="No more than 10 requests pro minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))],    
)
async def read_contact_by_email(
        contact_email: str,
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    contact = await repository_contacts.get_contact_by_email(contact_email, current_user, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact

@router.get(
    "/upcoming_birthdays/",
    response_model=List[ContactResponse],
    description="No more than 10 requests pro minute",
    dependencies=[Depends(RateLimiter(times=10, seconds=60))]   
)
async def get_upcoming_birthdays(
        db: Session = Depends(get_db),
        current_user: User = Depends(auth_service.get_current_user)
):
    contacts = await repository_contacts.get_upcoming_birthdays(current_user, db)
    return contacts
