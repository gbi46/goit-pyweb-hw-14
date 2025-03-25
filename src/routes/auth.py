from datetime import datetime, timedelta
from fastapi import (
    APIRouter, BackgroundTasks, Depends, Form, HTTPException,
    status, Request, Security
)
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.schemas import PasswordResetRequest, UserModel, UserResponse, RequestEmail, TokenModel
from src.repository import users as repository_users
from src.repository.utils import logger
from src.services.auth import auth_service
from src.services.email import send_email, send_password_reset_email
import bcrypt
import pytz
import uuid

router = APIRouter(prefix='/auth', tags=["auth"])
security = HTTPBearer()

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(
        background_tasks: BackgroundTasks,
        request: Request, 
        username: str = Form(...),
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    exist_user = await repository_users.get_user_by_email(email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    body = UserModel(email=email, password=password, username=username)
    body.password = auth_service.get_password_hash(password)
    new_user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, new_user.email, new_user.username, request.base_url)
    return {
        "user": new_user,
        "detail": "User successfully created. Check your email for confirmation"
    }

@router.post("/login", response_model=TokenModel)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

from fastapi import HTTPException

@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        email = await auth_service.decode_refresh_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user = await repository_users.get_user_by_email(email, db)

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.get('/confirmed_email/{token}')
async def confirmed_email(
    token: str,
    db: Session = Depends(get_db)
):
    email = await auth_service.get_email_from_token(token)
    logger.info(f"Received email: {email}")
    user = await repository_users.get_user_by_email(email, db)
    logger.info(f"User in routes/auth ln 91: {user}")
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    if user.confirmed:
        logger.info(f"Your email is already confirmed routes/auth ln 94, user: {user}")
        return {"message": "Your email is already confirmed"}
    await repository_users.confirmed_email(email, db)
    return {"message": "Email confirmed"}

@router.post("/password-reset-request")
async def password_reset_request(
        request_data: PasswordResetRequest,
        request: Request,
        background_tasks: BackgroundTasks, 
        current_user: User = Depends(auth_service.get_current_user),
        db: Session = Depends(get_db)
    ):
    email = request_data.email
    if not email:
        raise HTTPException(status_code=400, detail="Email is required")
    
    user = await repository_users.get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = str(uuid.uuid4())
    reset_token_expiry = datetime.utcnow().replace(tzinfo=pytz.UTC) + timedelta(hours=1)

    user.reset_token = reset_token
    user.reset_token_expired = reset_token_expiry
    db.commit()

    background_tasks.add_task(send_password_reset_email, user.email, user.username, user.reset_token, request.base_url)

    return {"message": "Password reset email sent"}

@router.get("/password-reset")
async def password_reset(
    token: str,
    db: Session = Depends(get_db)
):
    user = await repository_users.get_user_by_reset_token(token, db)
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    if await repository_users.is_reset_token_expired(user.reset_token_expired):
        raise HTTPException(status_code=400, detail="Reset token expired")
    return {"reset-token": token}

@router.post("/set-new-password")
async def set_new_password(
        token: str,
        new_password: str, 
        request: Request,
        background_tasks: BackgroundTasks,
        db: Session = Depends(get_db)
    ):
    user = await repository_users.get_user_by_reset_token(token, db)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    
    if await repository_users.is_reset_token_expired(user.reset_token_expired):
        raise HTTPException(status_code=400, detail="Reset token expired")

    hashed_password = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt())

    user.hashed_password = hashed_password
    user.password = auth_service.get_password_hash(new_password)
    user.reset_token = None
    user.reset_token_expired = None
    db.commit()

    return {"message": "Password updated successfully"}

@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}
