---
id: 1
title: Update Constitution
stage: constitution
date: 2026-01-30
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: Claude
command: /sp.constitution
labels: [constitution,update,spec-driven-development]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
tests:
---

## Prompt

```text
You are Claude Code operating under Spec-Kit Plus in Agentic Dev Stack mode.

This constitution defines permanent rules, standards, architecture, and constraints for the Todo Full-Stack Web Application project. You must follow ALL rules below for every future step.

==============================
PROJECT PURPOSE
==============================
Transform an existing console-based Todo application into a modern, multi-user, full-stack web application with persistent storage.

No manual coding by the human.
All code must be generated, edited, and refactored by Claude Code.

Workflow is strictly:
1. Write Spec
2. Generate Plan
3. Break into Tasks
4. Implement

Never jump directly to implementation without approved specs, plans, and tasks.

==============================
CORE FUNCTIONAL REQUIREMENTS
==============================
The system MUST implement all Basic Level Todo features:

1. Create Task
2. Read/List Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete / Toggle Completion

Each feature must work per-user.

==============================
ARCHITECTURE
==============================
Monorepo project with frontend and backend:

hackathon-todo/
├── .spec-kit/
├── specs/
├── frontend/   (Next.js)
├── backend/    (FastAPI)
├── docker-compose.yml
└── README.md

Both frontend and backend are edited inside the same repository.

==============================
TECHNOLOGY STACK
==============================
Frontend:
- Next.js 16+ (App Router)
- TypeScript
- Better Auth

Backend:
- Python FastAPI
- SQLModel ORM

Database:
- Neon Serverless PostgreSQL

Authentication:
- Better Auth (Frontend)
- JWT verification in FastAPI backend

==============================
AUTHENTICATION MODEL
==============================
Better Auth runs ONLY on frontend.

Better Auth MUST:
- Use JWT plugin
- Issue JWT access tokens on login

Frontend MUST:
- Attach JWT token to every API request:
  Authorization: Bearer <token>

Backend MUST:
- Verify JWT token using shared secret
- Extract user id from token
- Reject missing or invalid tokens with 401

Shared secret is stored in env:
BETTER_AUTH_SECRET

==============================
SECURITY RULES
==============================
- Every endpoint requires authentication
- User can ONLY access their own tasks
- Backend must never trust user_id from request alone
- Backend must always compare:
  token_user_id == url_user_id

==============================
API CONTRACT (MUST NOT CHANGE)
==============================
GET     /api/{user_id}/tasks
POST    /api/{user_id}/tasks
GET     /api/{user_id}/tasks/{id}
PUT     /api/{user_id}/tasks/{id}
DELETE  /api/{user_id}/tasks/{id}
PATCH   /api/{user_id}/tasks/{id}/complete

All routes require JWT token.

==============================
DATABASE RULES
==============================
- Use PostgreSQL via Neon
- Use SQLModel
- Tables must include:
  - users
  - tasks
- tasks must include:
  id
  title
  description
  completed
  owner_id (FK to user)

==============================
FRONTEND REQUIREMENTS
==============================
- Responsive UI
- Mobile and desktop friendly
- Auth pages (signup, login)
- Task dashboard
- Create, edit, delete, complete tasks
- Show only logged-in user's tasks

==============================
SPEC-KIT ORGANIZATION
==============================
Specs must be placed inside:

/specs/overview.md
/specs/architecture.md
/specs/features/
/specs/api/
/specs/database/
/specs/ui/

Claude Code must reference specs using:

@specs/file.md
@specs/features/file.md

==============================
IMPLEMENTATION RULES
==============================
- Never invent new stack
- Never mix backend into frontend
- Never store secrets in code
- Always use environment variables
- Write production-quality code
- Add error handling
- Add logging where useful

==============================
TESTING REQUIREMENTS
==============================
- Backend endpoint tests
- Auth verification tests
- Basic frontend interaction tests

==============================
EVALUATION CRITERIA AWARENESS
===========================
```

## Response snapshot

Updated the project constitution file (.specify/memory/constitution.md) to version 1.2.0, incorporating all the specified requirements for the Todo Full-Stack Web Application project. The constitution now includes:
- Spec-Driven Development workflow requirements
- Full-Stack Feature Completeness requirements
- Architecture and Technology Stack specifications
- Authentication Model with security rules
- Fixed API Contract requirements
- Database Rules and Frontend Requirements
- Spec-Kit Organization guidelines
- Implementation and Testing Requirements

The version was incremented from 1.1.0 to 1.2.0 to reflect the governance update, and the Sync Impact Report was updated accordingly.

## Outcome

- ✅ Impact: Updated project constitution to version 1.2.0 with comprehensive requirements
- 🧪 Tests: No tests required for constitution update
- 📁 Files: Modified .specify/memory/constitution.md
- 🔁 Next prompts: Generate spec for the todo application features
- 🧠 Reflection: Constitution now properly defines all project constraints and requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
- Prompt variant (if applicable): Standard constitution update
- Next experiment (smallest change to try): Begin writing feature specifications