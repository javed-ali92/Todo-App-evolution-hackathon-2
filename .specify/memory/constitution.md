<!-- Sync Impact Report:
Version change: 1.1.0 → 1.2.0
Modified principles: Updated governance information and versioning
Added sections: None
Removed sections: None
Templates requiring updates: ✅ .specify/templates/plan-template.md, ✅ .specify/templates/spec-template.md, ✅ .specify/templates/tasks-template.md, ⚠ .specify/templates/commands/*.md
Follow-up TODOs: None
-->

# Todo Full-Stack Web Application Constitution

## Core Principles

### I. Spec-Driven Development (NON-NEGOTIABLE)
All development follows strict workflow: Write Spec → Generate Plan → Break into Tasks → Implement. No direct implementation without approved specs, plans, and tasks.
<!-- All development must follow the spec-driven workflow with proper documentation and planning before any code is written -->

### II. Monorepo Architecture
Maintain a single repository with separate frontend and backend: hackathon-todo/ ├── .spec-kit/ ├── specs/ ├── frontend/ (Next.js) ├── backend/ (FastAPI) ├── docker-compose.yml └── README.md
<!-- The project structure must maintain clear separation between frontend and backend while keeping them in the same repository -->

### III. Full-Stack Feature Completeness
System MUST implement all Basic Level Todo features: Create Task, Read/List Tasks, Update Task, Delete Task, Mark Task Complete/Toggle Completion. Each feature must work per-user.
<!-- Every core todo functionality must be implemented and accessible per user account -->

### IV. Technology Stack Adherence
Use prescribed technology stack: Frontend (Next.js 16+, TypeScript, Better Auth), Backend (Python FastAPI, SQLModel ORM), Database (Neon Serverless PostgreSQL), Authentication (Better Auth with JWT).
<!-- Never deviate from the specified technology stack; all components must use the designated technologies -->

### V. Authentication Security
Better Auth runs only on frontend with JWT plugin. Frontend attaches JWT token to every API request. Backend verifies JWT token, extracts user ID, and compares token_user_id == url_user_id to prevent unauthorized access.
<!-- Security model must be strictly followed to ensure users only access their own data -->

### VI. API Contract Compliance
All API routes must follow the specified contract: GET /api/{user_id}/tasks, POST /api/{user_id}/tasks, GET /api/{user_id}/tasks/{id}, PUT /api/{user_id}/tasks/{id}, DELETE /api/{user_id}/tasks/{id}, PATCH /api/{user_id}/tasks/{id}/complete. All routes require JWT token.
<!-- API endpoints must strictly adhere to the defined contract without deviation -->

## Project Purpose
Transform an existing console-based Todo application into a modern, multi-user, full-stack web application with persistent storage. No manual coding by the human. All code must be generated, edited, and refactored by Claude Code.

<!-- The transformation goal and development methodology for the project -->

## Core Functional Requirements
The system MUST implement all Basic Level Todo features: Create Task, Read/List Tasks, Update Task, Delete Task, Mark Task Complete / Toggle Completion. Each feature must work per-user.

<!-- Essential functionality that must be implemented -->

## Architecture
Monorepo project with frontend and backend: hackathon-todo/ ├── .spec-kit/ ├── specs/ ├── frontend/ (Next.js) ├── backend/ (FastAPI) ├── docker-compose.yml └── README.md. Both frontend and backend are edited inside the same repository.

<!-- Structural requirements for the project organization -->

## Technology Stack
Frontend: Next.js 16+ (App Router), TypeScript, Better Auth. Backend: Python FastAPI, SQLModel ORM. Database: Neon Serverless PostgreSQL. Authentication: Better Auth (Frontend), JWT verification in FastAPI backend.

<!-- Specific technologies that must be used for each component -->

## Authentication Model
Better Auth runs ONLY on frontend. Better Auth MUST use JWT plugin and issue JWT access tokens on login. Frontend MUST attach JWT token to every API request as Authorization: Bearer <token>. Backend MUST verify JWT token using shared secret, extract user id for own tasks, never trust user_id from request alone, and always compare token_user_id == url_user_id.

<!-- Security requirements for authentication and authorization -->

## API Contract (MUST NOT CHANGE)
GET /api/{user_id}/tasks, POST /api/{user_id}/tasks, GET /api/{user_id}/tasks/{id}, PUT /api/{user_id}/tasks/{id}, DELETE /api/{user_id}/tasks/{id}, PATCH /api/{user_id}/tasks/{id}/complete. All routes require JWT token.

<!-- Fixed API endpoints that cannot be modified -->

## Database Rules
Use PostgreSQL via Neon. Use SQLModel. Tables must include: users, tasks. Tasks must include: id, title, description, completed, owner_id (FK to user).

<!-- Database schema and technology requirements -->

## Frontend Requirements
Responsive UI, Mobile and desktop friendly, Auth pages (signup, login), Task dashboard, Create, edit, delete, complete tasks, Show only logged-in user's tasks.

<!-- User interface and experience requirements -->

## Spec-Kit Organization
Specs must be placed inside: /specs/overview.md, /specs/architecture.md, /specs/features/, /specs/api/, /specs/database/, /specs/ui/. Claude Code must reference specs using: @specs/file.md, @specs/features/file.md.

<!-- Organizational requirements for documentation and specifications -->

## Implementation Rules
Never invent new stack, Never mix backend into frontend, Never store secrets in code, Always use environment variables, Write production-quality code, Add error handling, Add logging where useful.

<!-- Coding standards and security requirements -->

## Testing Requirements
Backend endpoint tests, Auth verification tests, Basic frontend interaction tests.

<!-- Testing coverage requirements -->

## Evaluation Criteria Awareness
Project will be judged on: Following spec-driven workflow, Clear specs, Proper plans, Logical task breakdown, Correct implementation, Security correctness.

<!-- Quality metrics for the project -->

## Failure Conditions
Any deviation from the prescribed workflow, security vulnerabilities, failure to implement required functionality, or non-compliance with architectural constraints.

<!-- Conditions that would result in project failure -->

## Governance
This constitution supersedes all other practices. All development must comply with these rules. Amendments require proper documentation and approval following the established workflow. All implementations must verify compliance with these principles.

**Version**: 1.2.0 | **Ratified**: 2026-01-30 | **Last Amended**: 2026-01-30
