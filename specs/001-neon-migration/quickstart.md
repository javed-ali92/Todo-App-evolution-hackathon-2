# Quickstart Guide for Neon PostgreSQL Migration

## Overview
This guide provides the essential steps to set up and run the Todo application with Neon PostgreSQL backend.

## Prerequisites
- Python 3.9 or higher
- Pip package manager
- Git
- Neon PostgreSQL account with connection string
- Virtual environment tool (recommended)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hackathon-todo
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create `.env` file based on `.env.example`:
```bash
cp .env.example .env
```

Edit `.env` with your Neon PostgreSQL connection details:
```env
# Database Configuration
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require&channel_binding=require

# JWT Configuration
SECRET_KEY=your-generated-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Configuration
ENVIRONMENT=development
DEBUG=True
```

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 5. Initialize Database
The application will automatically create tables on startup. Ensure your Neon PostgreSQL database exists and the connection string is correct.

## Running the Application

### Development Mode
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Documentation
Once the application is running, access the interactive API documentation at:
- http://localhost:8000/docs

## Key Endpoints

### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - Authenticate user
- `POST /auth/logout` - End user session
- `GET /auth/me` - Get current user info

### Tasks
- `POST /tasks` - Create new task
- `GET /tasks` - Get user's tasks with optional filters
- `GET /tasks/{id}` - Get specific task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task
- `PATCH /tasks/{id}/toggle` - Toggle task completion

## Environment Configuration

### Required Variables
- `DATABASE_URL`: Neon PostgreSQL connection string with SSL
- `SECRET_KEY`: JWT signing key (32+ characters recommended)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token validity period

### Optional Variables
- `ENVIRONMENT`: Set to "production" for production mode
- `DEBUG`: Enable/disable debug mode

## Database Migration
The application uses SQLModel's automatic schema creation. On first run, it will create all required tables:
- `users` - User accounts
- `tasks` - Todo items
- `sessions` - Active user sessions

## Security Notes
- Never commit `.env` file to version control
- Use strong SECRET_KEY values
- Ensure SSL is enabled for database connections
- Passwords are automatically hashed with bcrypt
- JWT tokens are validated on every request

## Troubleshooting

### Common Issues
1. **Database Connection Failed**: Verify `DATABASE_URL` is correct and Neon database is accessible
2. **JWT Authentication Errors**: Ensure `SECRET_KEY` is properly set
3. **SSL Connection Issues**: Confirm SSL mode is set to "require" in connection string

### Testing Database Connection
```bash
python -c "from database.connection import test_connection; test_connection()"
```

## Next Steps
1. Test authentication flow with signup/login
2. Create sample tasks to verify functionality
3. Test user isolation to ensure data privacy
4. Review API documentation for detailed endpoint information