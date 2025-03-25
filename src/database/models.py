from sqlalchemy import Boolean, Column, Date, func, Integer, String
from sqlalchemy.orm import declarative_base as declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    email = Column(String(50), nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(50), nullable=False)
    birthday = Column(Date(), nullable=False)
    additional_info = Column(String(50), nullable=True)
    user_id = Column(
        'user_id',
        ForeignKey('users.id', ondelete='CASCADE'),
        default=None
    )
    user = relationship('User', backref="contacts")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(250), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=True)
    reset_token = Column(String(255), nullable=True)
    reset_token_expired = Column(DateTime(50), nullable=True)
    password = Column(String(255), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, nullable=False, default=False)
