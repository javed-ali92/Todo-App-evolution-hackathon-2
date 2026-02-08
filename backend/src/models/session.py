from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class SessionBase(SQLModel):
    user_id: int = Field(foreign_key="user.id", nullable=False)
    token: str = Field(unique=True, nullable=False, max_length=500)
    token_jti: str = Field(unique=True, nullable=False, max_length=255)  # JWT ID for the token
    expires_at: datetime = Field(nullable=False)

class Session(SessionBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_used_at: datetime = Field(default_factory=datetime.utcnow)
    revoked: bool = Field(default=False)
    revoked_at: Optional[datetime] = Field(default=None)

class SessionRead(SessionBase):
    id: int
    created_at: datetime
    last_used_at: datetime

class SessionCreate(SessionBase):
    pass

class SessionUpdate(SQLModel):
    last_used_at: Optional[datetime] = Field(default_factory=datetime.utcnow)