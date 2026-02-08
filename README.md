# Todo Full-Stack Web Application

A modern, multi-user todo application with persistent storage using Neon Serverless PostgreSQL.

## Features

- User authentication and authorization
- Task management (Create, Read, Update, Delete, Toggle Completion)
- Per-user data isolation
- Responsive web interface
- JWT-based authentication

## Tech Stack

- **Frontend**: Next.js 16+ (App Router), TypeScript, Better Auth
- **Backend**: Python FastAPI, SQLModel ORM
- **Database**: Neon Serverless PostgreSQL
- **Authentication**: Better Auth (Frontend), JWT verification (Backend)

## API Contract

The application implements the following fixed API endpoints:

- GET /api/{user_id}/tasks
- POST /api/{user_id}/tasks
- GET /api/{user_id}/tasks/{id}
- PUT /api/{user_id}/tasks/{id}
- DELETE /api/{user_id}/tasks/{id}
- PATCH /api/{user_id}/tasks/{id}/complete

All routes require JWT token authentication and enforce user data isolation.

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- Docker and Docker Compose
- Neon PostgreSQL account

### Installation

1. Clone the repository
2. Install backend dependencies: Requirement already satisfied: fastapi==0.115.0 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from -r requirements.txt (line 1)) (0.115.0)
Requirement already satisfied: uvicorn==0.32.0 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from uvicorn[standard]==0.32.0->-r requirements.txt (line 2)) (0.32.0)
Requirement already satisfied: sqlmodel==0.0.22 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from -r requirements.txt (line 3)) (0.0.22)
Requirement already satisfied: alembic==1.13.3 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from -r requirements.txt (line 4)) (1.13.3)
Requirement already satisfied: pydantic==2.9.2 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from -r requirements.txt (line 5)) (2.9.2)
Requirement already satisfied: python-jose==3.3.0 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from python-jose[cryptography]==3.3.0->-r requirements.txt (line 6)) (3.3.0)
Requirement already satisfied: passlib==1.7.4 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from passlib[bcrypt]==1.7.4->-r requirements.txt (line 7)) (1.7.4)
Requirement already satisfied: python-multipart==0.0.12 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from -r requirements.txt (line 8)) (0.0.12)
Requirement already satisfied: python-dotenv==1.0.1 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from -r requirements.txt (line 9)) (1.0.1)
Requirement already satisfied: starlette<0.39.0,>=0.37.2 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from fastapi==0.115.0->-r requirements.txt (line 1)) (0.38.6)
Requirement already satisfied: typing-extensions>=4.8.0 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from fastapi==0.115.0->-r requirements.txt (line 1)) (4.15.0)
Requirement already satisfied: click>=7.0 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from uvicorn==0.32.0->uvicorn[standard]==0.32.0->-r requirements.txt (line 2)) (8.3.1)
Requirement already satisfied: h11>=0.8 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from uvicorn==0.32.0->uvicorn[standard]==0.32.0->-r requirements.txt (line 2)) (0.16.0)
Requirement already satisfied: SQLAlchemy<2.1.0,>=2.0.14 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from sqlmodel==0.0.22->-r requirements.txt (line 3)) (2.0.35)
Requirement already satisfied: Mako in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from alembic==1.13.3->-r requirements.txt (line 4)) (1.3.10)
Requirement already satisfied: annotated-types>=0.6.0 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from pydantic==2.9.2->-r requirements.txt (line 5)) (0.7.0)
Requirement already satisfied: pydantic-core==2.23.4 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from pydantic==2.9.2->-r requirements.txt (line 5)) (2.23.4)
Requirement already satisfied: ecdsa!=0.15 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from python-jose==3.3.0->python-jose[cryptography]==3.3.0->-r requirements.txt (line 6)) (0.19.1)
Requirement already satisfied: rsa in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from python-jose==3.3.0->python-jose[cryptography]==3.3.0->-r requirements.txt (line 6)) (4.9.1)
Requirement already satisfied: pyasn1 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from python-jose==3.3.0->python-jose[cryptography]==3.3.0->-r requirements.txt (line 6)) (0.6.1)
Requirement already satisfied: bcrypt>=3.1.0 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from passlib[bcrypt]==1.7.4->-r requirements.txt (line 7)) (4.0.1)
Requirement already satisfied: cryptography>=3.4.0 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from python-jose[cryptography]==3.3.0->-r requirements.txt (line 6)) (46.0.3)
Requirement already satisfied: colorama>=0.4 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from uvicorn[standard]==0.32.0->-r requirements.txt (line 2)) (0.4.6)
Requirement already satisfied: httptools>=0.5.0 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from uvicorn[standard]==0.32.0->-r requirements.txt (line 2)) (0.7.1)
Requirement already satisfied: pyyaml>=5.1 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from uvicorn[standard]==0.32.0->-r requirements.txt (line 2)) (6.0.3)
Requirement already satisfied: watchfiles>=0.13 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from uvicorn[standard]==0.32.0->-r requirements.txt (line 2)) (1.1.1)
Requirement already satisfied: websockets>=10.4 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from uvicorn[standard]==0.32.0->-r requirements.txt (line 2)) (16.0)
Requirement already satisfied: cffi>=2.0.0 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from cryptography>=3.4.0->python-jose[cryptography]==3.3.0->-r requirements.txt (line 6)) (2.0.0)
Requirement already satisfied: six>=1.9.0 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from ecdsa!=0.15->python-jose==3.3.0->python-jose[cryptography]==3.3.0->-r requirements.txt (line 6)) (1.17.0)
Requirement already satisfied: anyio<5,>=3.4.0 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from starlette<0.39.0,>=0.37.2->fastapi==0.115.0->-r requirements.txt (line 1)) (3.7.1)
Requirement already satisfied: MarkupSafe>=0.9.2 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from Mako->alembic==1.13.3->-r requirements.txt (line 4)) (3.0.3)
Requirement already satisfied: idna>=2.8 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from anyio<5,>=3.4.0->starlette<0.39.0,>=0.37.2->fastapi==0.115.0->-r requirements.txt (line 1)) (3.11)
Requirement already satisfied: sniffio>=1.1 in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from anyio<5,>=3.4.0->starlette<0.39.0,>=0.37.2->fastapi==0.115.0->-r requirements.txt (line 1)) (1.3.1)
Requirement already satisfied: pycparser in c:\users\hp\appdata\local\programs\python\python313\lib\site-packages (from cffi>=2.0.0->cryptography>=3.4.0->python-jose[cryptography]==3.3.0->-r requirements.txt (line 6)) (2.23)
3. Install frontend dependencies: 
up to date, audited 27 packages in 4s

3 packages are looking for funding
  run `npm fund` for details

1 high severity vulnerability

To address all issues (including breaking changes), run:
  npm audit fix --force

Run `npm audit` for details.
4. Set up environment variables (see .env.example)
5. Start the application: 

### Environment Variables

Copy .env.example to .env and configure the following variables:

- DATABASE_URL: Neon PostgreSQL connection string
- JWT_SECRET_KEY: Secret key for JWT token signing
- FRONTEND_URL: Frontend application URL
- BACKEND_URL: Backend application URL

## Development

The project follows a spec-driven development workflow:

1. Write specifications (@specs/)
2. Generate implementation plan (@specs/*/plan.md)
3. Break into tasks (@specs/*/tasks.md)
4. Implement following the tasks

## Security

- JWT-based authentication with token verification
- Per-user data isolation enforced at API and database levels
- Passwords are securely hashed using bcrypt
- All API requests require authentication

## Architecture

The application follows a monorepo structure:



## Testing

Run backend tests: ============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-7.4.3, pluggy-1.6.0
rootdir: E:\javed\hacathon_2\Evalution_Todo_App_1\backend
plugins: anyio-3.7.1
collected 0 items

============================ no tests ran in 0.04s ============================
Run frontend tests: 

## Deployment

The application is designed to be deployed with Docker containers. Update the environment variables for your deployment environment and run:



## Contributing

This project follows a spec-driven development approach. All contributions should follow the established workflow:

1. Create a feature specification
2. Generate a plan
3. Break into tasks
4. Implement following the tasks

## License

MIT
"# Todo-App-evolution-hackathon-2" 
