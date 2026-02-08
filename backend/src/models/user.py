from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class UserBase(SQLModel):
    username: str = Field(unique=True, nullable=False, min_length=3, max_length=30)
    email: str = Field(unique=True, nullable=False, max_length=255)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str = Field(nullable=False, min_length=8)  # Store hashed password
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to tasks - will be added after both models are defined
    # tasks: list["Task"] = Relationship(back_populates="user")

class UserRead(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

class UserCreate(UserBase):
    password: str

class UserUpdate(SQLModel):
    username: Optional[str] = Field(default=None, min_length=3, max_length=30)
    email: Optional[str] = None

class UserLogin(SQLModel):
    email: str
    password: str