from sqlmodel import SQLModel, Field, Column
from sqlalchemy import String
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum
from pydantic import field_serializer, model_validator

class PriorityEnum(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    due_date: Optional[str] = Field(default=None, sa_column=Column(String))  # Explicitly use String type
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)
    tags: Optional[str] = Field(default=None)  # Store as JSON string for simplicity
    recursion_pattern: Optional[str] = Field(default=None, max_length=100)
    completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", nullable=False)  # Foreign key to users table
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to User - removed to prevent circular dependency issues
    # user: "User" = Relationship(back_populates="tasks")

class TaskRead(SQLModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    due_date: Optional[str] = None
    priority: PriorityEnum
    tags: Optional[str] = None
    recursion_pattern: Optional[str] = None
    completed: bool
    created_at: datetime
    updated_at: datetime

    @model_validator(mode='before')
    @classmethod
    def convert_datetime_fields(cls, data):
        """Convert datetime due_date to string before validation"""
        # Handle both dict and object inputs
        if isinstance(data, dict):
            if 'due_date' in data and isinstance(data['due_date'], datetime):
                data['due_date'] = data['due_date'].isoformat()
        else:
            # Handle SQLModel/ORM objects
            if hasattr(data, '__dict__'):
                data_dict = data.__dict__.copy()
                if 'due_date' in data_dict and isinstance(data_dict['due_date'], datetime):
                    data_dict['due_date'] = data_dict['due_date'].isoformat()
                return data_dict
        return data

class TaskCreate(TaskBase):
    pass

class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    due_date: Optional[str] = Field(default=None)  # Changed to string to match frontend
    priority: Optional[PriorityEnum] = Field(default=None)
    tags: Optional[str] = Field(default=None)  # Changed to string to match frontend
    recursion_pattern: Optional[str] = Field(default=None, max_length=100)
    completed: Optional[bool] = Field(default=None)

class TaskToggleComplete(SQLModel):
    completed: bool