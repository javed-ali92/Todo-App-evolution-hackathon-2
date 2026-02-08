# Quickstart Guide: Todo Full-Stack Web Application

## Prerequisites
- Node.js 18+ (for frontend development)
- Python 3.11+ (for backend development)
- PostgreSQL (local installation or Neon Serverless account)
- Docker and Docker Compose (optional, for containerized setup)

## Environment Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd hackathon-todo
```

### 2. Install Dependencies
#### Backend
```bash
cd backend
pip install -r requirements.txt
```

#### Frontend
```bash
cd frontend
npm install
```

### 3. Environment Variables
Copy the example environment file and configure your settings:

```bash
# In the project root
cp .env.example .env
```

Configure the following variables in your `.env` file:
- `BETTER_AUTH_SECRET`: Secret key for JWT signing (use a strong random value)
- `DATABASE_URL`: PostgreSQL connection string for Neon or local database
- `NEXT_PUBLIC_BETTER_AUTH_URL`: URL for the frontend to connect to auth service

## Running the Application

### Option 1: Local Development
#### Terminal 1 - Start Backend:
```bash
cd backend
python src/main.py
```

#### Terminal 2 - Start Frontend:
```bash
cd frontend
npm run dev
```

### Option 2: Docker Compose
```bash
docker-compose up --build
```

## API Testing
Once running, the API endpoints will be available at:
- Base API: `http://localhost:8000/api/{user_id}/...`
- Frontend: `http://localhost:3000`

## Initial Setup
1. Register a new user account via the frontend signup page
2. Verify the account can log in successfully
3. Create a test task to verify the full CRUD flow works
4. Verify that authentication is required for all task operations

## Troubleshooting
- If authentication fails, verify that `BETTER_AUTH_SECRET` is identical in both frontend and backend environments
- If database connections fail, verify the `DATABASE_URL` is correctly configured
- If API calls return 401/403, verify JWT token is being properly attached to requests

## Next Steps
1. Run the full test suite: `npm test` (frontend) and `pytest` (backend)
2. Review the API contract in `/contracts/api-contract.md`
3. Begin implementing the user stories as outlined in the specifications