# Quickstart Guide: Todo Application with Neon PostgreSQL

## Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.9+
- Neon Serverless PostgreSQL account
- Git

## Setup Instructions

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd hackathon-todo
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt
```

Create `.env` file with:
```env
DATABASE_URL=your_neon_postgresql_connection_string
BETTER_AUTH_SECRET=your-super-secret-jwt-key-here-make-it-long-and-random-change-in-production
API_HOST=0.0.0.0
API_PORT=8000
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

Create `.env.local` file with:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
```

### 4. Start Services

#### Option A: Manual Start
Backend:
```bash
cd backend
python -m uvicorn src.main:app --reload
```

Frontend:
```bash
cd frontend
npm run dev
```

#### Option B: Docker Compose
```bash
docker-compose up --build
```

### 5. Access Application
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Backend Docs: http://localhost:8000/docs

## Configuration Notes
- Ensure Neon PostgreSQL connection string includes SSL parameters
- Update API_BASE_URL in frontend if backend runs on different port
- The application will automatically create database tables on startup
- JWT tokens expire after 24 hours by default

## Development Commands
- Backend tests: `cd backend && python -m pytest`
- Frontend linting: `cd frontend && npm run lint`
- Frontend build: `cd frontend && npm run build`

## Troubleshooting
- If database tables aren't created, ensure the application has started successfully
- For authentication issues, verify that BETTER_AUTH_SECRET matches between frontend and backend
- For API connection issues, confirm NEXT_PUBLIC_API_BASE_URL matches backend URL