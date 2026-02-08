---
id: 001
title: Clean Frontend Planning Phase
stage: plan
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: 004-clean-frontend
branch: 004-clean-frontend
user: user
command: /sp.plan
labels: ["planning", "frontend", "nextjs", "app-router", "refactoring"]
links:
  spec: ../specs/004-clean-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-clean-frontend/research.md
  - specs/004-clean-frontend/data-model.md
  - specs/004-clean-frontend/contracts/auth-api.md
  - specs/004-clean-frontend/contracts/task-api.md
  - specs/004-clean-frontend/quickstart.md
  - specs/004-clean-frontend/plan.md
  - specs/004-clean-frontend/tasks.md
tests:
  - None (testing not specified in requirements)
---

## Prompt

You are acting as a Senior Next.js Frontend Engineer.

Objective:
Create a detailed, step-by-step plan to refactor and fix the frontend of a Todo application built with Next.js.

Background:
- Backend authentication is working.
- Frontend is broken and confusing.
- There is a mix of `pages/` and `app/` folders.
- Login, signup, and task creation flows are unstable.
- Task data and user data must persist via backend APIs connected to Neon PostgreSQL.
- Frontend must be clean, minimal, and production-ready.

Planning Requirements:

1. Analysis Phase
   - Inspect current frontend folder structure
   - Identify incorrect usage of `pages/` vs `app/`
   - Identify unused, duplicate, or unnecessary files
   - Identify broken routes and API calls

2. Cleanup Strategy
   - Decide which folders/files must be deleted
   - Decide which parts can be reused
   - Ensure only **Next.js App Router** remains

3. Architecture Plan
   - Define final folder structure using `app/`
   - Define routing strategy (login, signup, dashboard, tasks)
   - Define component separation (forms, layouts, UI components)

4. Authentication Flow Plan
   - Login → dashboard redirect
   - Signup → dashboard redirect
   - Token handling strategy
   - Protected routes approach

5. Task Feature Plan
   - Task creation form fields: title, description, due_date, priority, tags, recursion_pattern
   - API integration plan
   - Success & error handling plan

6. State & Data Handling
   - Form state management approach
   - API service abstraction
   - No local or dummy data usage

7. Validation & Testing Plan
   - Verify login works
   - Verify signup works
   - Verify task creation saves to Neon DB
   - Verify dashboard loads correctly after login

Rules:
- Do NOT write code yet
- Do NOT change backend
- Do NOT add unnecessary libraries
- Keep the plan sequential and easy to follow

## Response snapshot

Successfully completed comprehensive planning phase for clean Next.js frontend refactoring:

**Phase 0: Research & Technology Decisions**
- Created research.md documenting all technology choices
- Decided on Next.js App Router exclusively (removing Pages Router)
- Selected React Hook Form for form state management
- Kept existing fetch-based API clients (auth-client.ts, task-client.ts)
- Continued using Tailwind CSS for styling
- Implemented HOC pattern for protected routes

**Phase 1: Design & Contracts**
- Created data-model.md defining all frontend entities:
  - User, UserSession, Task, TaskCreate, TaskUpdate
  - LoginCredentials, RegistrationData, LoginResponse
- Generated API contracts documentation:
  - auth-api.md: Registration, Login, Get Current User, Logout
  - task-api.md: CRUD operations for tasks (GET, POST, PUT, DELETE, PATCH)
- Created quickstart.md with setup instructions and validation checklist

**Key Architectural Decisions:**
1. Remove all Pages Router files (src/pages/*, src/App.jsx, src/context/AuthContext.jsx)
2. Consolidate to single auth provider in src/app/providers/auth-provider.tsx
3. Organize components by feature: forms/, lists/, layouts/, hoc/, ui/
4. Use TypeScript interfaces from lib/api/ for type safety
5. Implement protected routes with WithAuth HOC wrapper

**Project Structure Defined:**
```
frontend/src/
├── app/              # Next.js App Router only
├── components/       # Organized by feature type
├── lib/api/          # API clients
└── styles/           # Global styles
```

**Constitution Check:** All compliance requirements passed ✅

## Outcome

- ✅ Impact: Comprehensive planning artifacts created for clean frontend refactoring. All technical decisions documented and justified. Clear path forward for implementation.
- 🧪 Tests: No tests created (not specified in requirements). Testing strategy to be added in future iteration.
- 📁 Files: Created 7 planning documents (research.md, data-model.md, 2 API contracts, quickstart.md, plan.md, tasks.md)
- 🔁 Next prompts: Ready to proceed with implementation following tasks.md. Start with Phase 1: Cleanup (remove Pages Router files).
- 🧠 Reflection: Planning phase successfully identified all structural issues in current frontend. Clear separation between what to delete (Pages Router) and what to keep (App Router, API clients). All unknowns resolved through research phase.

## Evaluation notes (flywheel)

- Failure modes observed: None. Planning completed successfully with all required artifacts.
- Graders run and results (PASS/FAIL): Constitution Check: PASS (all compliance requirements met)
- Prompt variant (if applicable): Standard /sp.plan workflow
- Next experiment (smallest change to try): Begin implementation with Phase 1 cleanup tasks, starting with deletion of Pages Router files to immediately simplify codebase structure.