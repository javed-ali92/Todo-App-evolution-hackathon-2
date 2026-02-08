# Quickstart Guide: NeonDB Authentication & Task Persistence

## Overview
This guide provides quick setup instructions for the NeonDB authentication and task persistence implementation. The system integrates Neon Serverless PostgreSQL with the Todo application for secure user authentication and persistent task management.

## Prerequisites
- Python 3.9+ installed
- Node.js 18+ installed
- Neon Serverless PostgreSQL account with connection string
- Git for version control

## Environment Setup

### Backend Environment
Create a `.env` file in the backend directory with the following variables:

```bash
# Database Configuration
DATABASE_URL="postgresql://username:password@ep-xxxxxx.ap-southeast-1.aws.neon.tech/dbname?sslmode=require"

# JWT Configuration
SECRET_KEY="your-super-secret-jwt-key-here-make-it-long-and-random"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
ENVIRONMENT="development"
DEBUG="True"
```

### Frontend Environment
Create a `.env.local` file in the frontend directory with the following variables:

```bash
# Frontend Environment Variables
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
```

## Database Setup

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Initialize Database Tables
```bash
# This will create the required tables in NeonDB
python -c "from database.connection import create_db_and_tables; create_db_and_tables()"
```

## Backend Implementation

### 1. User Model (src/models/user.py)
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class UserBase(SQLModel):
    email: str = Field(unique=True, nullable=False, max_length=255)

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password_hash: str = Field(nullable=False, min_length=8)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Task Model (src/models/task.py)
```python
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from .user import User

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    completed: bool = Field(default=False)

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3. Authentication Service (src/services/auth_service.py)
```python
from sqlmodel import Session, select
from passlib.context import CryptContext
from ..models.user import User
from datetime import datetime, timedelta
from jose import jwt
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user or not verify_password(password, user.password_hash):
        return None

    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

## Frontend Implementation

### 1. Signup Form Validation
Ensure the signup form includes:
- Email field (validates email format)
- Password field (minimum 8 characters)
- Proper error handling for validation failures

### 2. Login Form Validation
Ensure the login form includes:
- Email field (matches database format)
- Password field (matches encrypted password validation)
- Proper error handling for authentication failures

### 3. Task Form Validation
Ensure the task form includes:
- Title field (required, max 255 characters)
- Description field (optional)
- Completion status (boolean)
- Proper validation matching database constraints

## API Integration

### Authentication Routes
- POST `/api/auth/register` - User registration with data persistence to NeonDB
- POST `/api/auth/login` - User authentication against NeonDB data
- GET `/api/auth/me` - Get authenticated user information

### Task Routes
- GET `/api/{user_id}/tasks` - Retrieve user's tasks from NeonDB
- POST `/api/{user_id}/tasks` - Create new task in NeonDB
- GET `/api/{user_id}/tasks/{id}` - Retrieve specific task from NeonDB
- PUT `/api/{user_id}/tasks/{id}` - Update task in NeonDB
- DELETE `/api/{user_id}/tasks/{id}` - Delete task from NeonDB
- PATCH `/api/{user_id}/tasks/{id}/complete` - Toggle task completion in NeonDB

## Security Implementation

### JWT Token Validation
- Backend verifies JWT tokens from frontend
- Extracts user ID from token payload
- Compares token_user_id with url_user_id to prevent unauthorized access
- Users can only access their own data

### Password Security
- Passwords are hashed using bcrypt before storage
- Never store plaintext passwords in NeonDB
- Use industry-standard encryption practices

## Testing

### Backend Tests
```bash
# Run backend tests to verify database persistence
python -m pytest tests/test_auth.py
python -m pytest tests/test_tasks.py
```

### Manual Verification
1. Register a new user and verify data appears in NeonDB users table
2. Login with credentials and verify authentication works
3. Create tasks and verify they appear in NeonDB tasks table
4. Verify user data isolation (users can only access their own tasks)