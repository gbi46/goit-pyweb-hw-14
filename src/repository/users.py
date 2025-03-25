from libgravatar import Gravatar
from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas import UserModel
from datetime import datetime, timezone
import pytz

async def get_user_by_email(email: str, db: Session) -> User:
    return db.query(User).filter(User.email == email).first()

async def get_user_by_reset_token(reset_token: str, db: Session) -> User:
    return db.query(User).filter(User.reset_token == reset_token).first()

async def create_user(body: UserModel, db: Session) -> User:
    avatar = None
    try:
        g = Gravatar(body.email)
        avatar = g.get_image()
    except Exception as e:
        return {f"error: {e}"}

    user_data = body.model_dump()
    new_user = User(**user_data, avatar=avatar)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

async def is_reset_token_expired(token_expired):
    if token_expired is None:
        return False
    
    if token_expired:
        user_token_expiry = token_expired.replace(tzinfo=pytz.UTC)
    else:
        user_token_expiry = None

    if user_token_expiry is not None:
        datetimenow = datetime.now(timezone.utc).replace(tzinfo=pytz.UTC)
        if user_token_expiry and user_token_expiry < datetimenow:
            return True
        else:
            return False
    else:
        return False

async def update_token(user: User, token: str | None, db: Session) -> None:
    user.refresh_token = token
    db.commit()

async def confirmed_email(email: str, db: Session) -> None:
    user = await get_user_by_email(email, db)
    print(f"User rep/users ln 50: {user}")
    if(user.confirmed):
        print("rep/users ln 52 user confirmed")
        return {"message": "Your email is already confirmed rep/users ln 53"}
    user.confirmed = True
    db.commit()
    return {"message": "Email confirmed"}

async def update_avatar(email, url: str, db: Session) -> User:
    user = await get_user_by_email(email, db)
    user.avatar = url
    db.commit()
    return user
