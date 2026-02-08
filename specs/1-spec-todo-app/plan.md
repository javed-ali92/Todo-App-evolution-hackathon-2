# Implementation Plan: Todo Full-Stack Web Application

**Branch**: `1-spec-todo-app` | **Date**: 2026-01-30 | **Spec**: @specs/overview.md
**Input**: Feature specification from `/specs/1-spec-todo-app/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Implementation of a full-stack todo web application following the spec-driven development workflow. The application will feature user authentication, secure per-user task management, and a responsive web interface. The system implements all basic todo features (CRUD operations) with proper authentication and authorization using Better Auth and JWT tokens.

## Technical Context

**Language/Version**: Python 3.11 (Backend), TypeScript 5.x (Frontend)
**Primary Dependencies**: FastAPI, Next.js 16+, Better Auth, SQLModel, PostgreSQL
**Storage**: Neon Serverless PostgreSQL with SQLModel ORM
**Testing**: pytest (Backend), Jest/React Testing Library (Frontend)
**Target Platform**: Web application supporting modern browsers on desktop and mobile
**Project Type**: Full-stack web application with clear frontend/backend separation
**Performance Goals**: Sub-1 second response times for 95% of requests, support for 1000 concurrent users
**Constraints**: All API endpoints must follow the fixed contract with JWT authentication, users can only access their own data
**Scale/Scope**: Multi-user system with individual task ownership and data isolation

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-Driven Development Compliance
- [x] All development follows strict workflow: Write Spec → Generate Plan → Break into Tasks → Implement
- [x] No direct implementation without approved specs, plans, and tasks

### Architecture Compliance
- [x] Maintains monorepo structure: frontend/ (Next.js), backend/ (FastAPI), specs/, docker-compose.yml
- [x] Clear separation between frontend and backend components

### Technology Stack Compliance
- [x] Frontend uses Next.js 16+ (App Router), TypeScript, Better Auth
- [x] Backend uses Python FastAPI, SQLModel ORM
- [x] Database uses Neon Serverless PostgreSQL
- [x] Authentication uses Better Auth with JWT

### Security Compliance
- [x] All API routes require JWT token authentication
- [x] Backend verifies JWT token and extracts user ID
- [x] Backend compares token_user_id == url_user_id to prevent unauthorized access
- [x] Users can only access their own tasks

### API Contract Compliance
- [x] All API routes follow the specified contract:
  - GET /api/{user_id}/tasks
  - POST /api/{user_id}/tasks
  - GET /api/{user_id}/tasks/{id}
  - PUT /api/{user_id}/tasks/{id}
  - DELETE /api/{user_id}/tasks/{id}
  - PATCH /api/{user_id}/tasks/{id}/complete

## Project Structure

### Documentation (this feature)
```text
specs/1-spec-todo-app/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)
```text
hackathon-todo/
├── .specify/
├── specs/
├── frontend/            # Next.js application
│   ├── src/
│   │   ├── app/         # App Router pages
│   │   ├── components/  # Reusable UI components
│   │   ├── lib/         # Utilities and API clients
│   │   └── styles/      # Global styles
│   ├── public/          # Static assets
│   ├── package.json
│   └── next.config.js
├── backend/             # FastAPI application
│   ├── src/
│   │   ├── main.py      # Application entry point
│   │   ├── models/      # SQLModel definitions
│   │   ├── api/         # API route handlers
│   │   ├── auth/        # Authentication middleware
│   │   └── database/    # Database connection and setup
│   ├── requirements.txt
│   └── alembic/
├── docker-compose.yml   # Container orchestration
├── .env.example         # Environment variable template
└── README.md            # Project documentation
```

**Structure Decision**: Selected the web application structure with clear frontend/backend separation to maintain the monorepo architecture while ensuring technology stack compliance.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [None identified] | [All constitutional requirements met] | [N/A] |

## Phase 0: Research & Analysis

### 1) Repository & Monorepo Setup Plan
- Establish monorepo structure with frontend/ and backend/ directories
- Configure Spec-Kit Plus in the repository
- Set up environment variable strategy with proper secrets handling
- Create .env.example with required variables (BETTER_AUTH_SECRET, DATABASE_URL)

### 2) Backend Architecture Plan (FastAPI)
- Design FastAPI project structure with proper module organization
- Implement Neon PostgreSQL connection using SQLModel ORM
- Create User and Task models with proper relationships
- Set up Alembic for database migrations
- Implement JWT verification middleware for authentication
- Organize API routes according to the fixed contract
- Design comprehensive error handling strategy

### 3) Frontend Architecture Plan (Next.js)
- Structure Next.js application using App Router
- Integrate Better Auth for frontend authentication
- Implement session management with proper token handling
- Design API client to communicate with backend
- Create page routing for authentication and task management
- Plan state management approach for task data

### 4) Authentication Flow Plan
- Implement signup flow using Better Auth
- Design login flow with JWT token retrieval
- Plan secure token storage in browser
- Implement token attachment to API requests
- Design token verification in backend
- Plan logout flow with token invalidation

### 5) Task Management Plan
- Implement Create operation for tasks with validation
- Design Read operations to list and retrieve tasks
- Implement Update operation with proper validation
- Create Delete operation with authorization checks
- Design Toggle Completion operation
- Enforce ownership rules for all operations

### 6) Security Plan
- Implement secrets handling with environment variables
- Plan token expiry and refresh strategy
- Design comprehensive authorization checks
- Implement input validation on both frontend and backend
- Plan audit logging for security events

### 7) Testing Plan
- Design backend tests for API endpoints
- Plan authentication flow tests
- Create frontend component and integration tests
- Plan end-to-end user journey tests

### 8) Deployment & Local Dev Plan
- Create Docker configuration for both frontend and backend
- Plan local development startup sequence
- Design environment configuration for different stages
- Plan CI/CD pipeline for automated testing and deployment

## Phase 1: Design & Architecture

### Data Model Design
- **User Entity**: id, email, hashed_password, created_at, updated_at
- **Task Entity**: id, title, description, completed, owner_id (FK to User), created_at, updated_at
- **Relationships**: User (1) -> (Many) Task (owner_id foreign key)

### API Contract Design
- **POST /api/{user_id}/tasks**: Create new task for user (requires JWT)
- **GET /api/{user_id}/tasks**: Retrieve all tasks for user (requires JWT)
- **GET /api/{user_id}/tasks/{id}**: Retrieve specific task (requires JWT)
- **PUT /api/{user_id}/tasks/{id}**: Update task details (requires JWT)
- **DELETE /api/{user_id}/tasks/{id}**: Delete task (requires JWT)
- **PATCH /api/{user_id}/tasks/{id}/complete**: Toggle task completion (requires JWT)

### Authentication Flow Design
1. User registers/logs in via Better Auth on frontend
2. Better Auth issues JWT access token
3. Frontend stores token securely
4. Frontend attaches token to all API requests as "Authorization: Bearer <token>"
5. Backend verifies JWT using shared secret
6. Backend extracts user ID from token
7. Backend validates token_user_id == url_user_id for authorization
8. Backend rejects invalid/missing tokens with 401

### Security Design
- All endpoints require JWT authentication
- Authorization enforced by comparing token_user_id with url_user_id
- Input validation on all user-provided data
- SQL injection prevention via SQLModel ORM
- XSS protection through proper output encoding
- Secure token storage using httpOnly cookies where possible

## Phase 2: Implementation Planning

The detailed implementation tasks will be broken down in the tasks.md file, organizing work by user stories and dependencies. The implementation will follow the spec-driven workflow with proper testing and validation at each stage.

**Next Step**: Generate detailed task breakdown using `/sp.tasks` command