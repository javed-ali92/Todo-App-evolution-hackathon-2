---
id: 002
title: Frontend Tasks Generation
stage: tasks
date: 2026-02-07
surface: agent
model: claude-sonnet-4-5
feature: 004-clean-frontend
branch: 004-clean-frontend
user: user
command: /sp.tasks
labels: ["tasks", "frontend", "nextjs", "app-router", "implementation"]
links:
  spec: ../specs/004-clean-frontend/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/004-clean-frontend/tasks.md
tests:
  - None (testing not specified in requirements)
---

## Prompt

You are acting as a Senior Next.js Frontend Engineer.

Objective:
Break down the approved frontend refactor plan into clear, executable tasks for a clean Next.js App Router frontend.

Context:
- Backend is already working.
- Authentication APIs are functional.
- Neon PostgreSQL is used via backend APIs.
- Frontend must use **Next.js App Router only**.
- No `pages/` directory allowed.
- No dummy or local data.

Task Breakdown Requirements:

1. Project Cleanup Tasks
   - Remove `pages/` directory completely
   - Remove duplicate `app/` folders (ensure only one exists at `src/app`)
   - Remove unused components, hooks, services, and configs
   - Verify `next.config.js` and `tsconfig/jsconfig` alignment

2. Folder Structure Setup
   - Create clean `src/app` structure
   - Create shared layout and providers
   - Create reusable UI components folder

3. Routing Tasks
   - Implement App Router routing
   - Ensure login → dashboard redirect
   - Ensure signup → dashboard redirect
   - Protect dashboard and task routes

4. Authentication Tasks
   - Connect login form to backend API
   - Connect signup form to backend API
   - Handle token storage securely
   - Implement auth context/provider
   - Handle unauthorized access properly

5. Task Feature Tasks
   - Build task creation form with all required fields
   - Connect form submission to backend API
   - Handle validation errors
   - Display success and failure states

6. API Integration Tasks
   - Create centralized API service layer
   - Standardize error handling
   - Handle all HTTP error responses
   - Ensure Neon DB persistence via backend

7. UI & UX Tasks
   - Clean minimal layout
   - Proper loading states
   - Error messages rendered safely
   - Empty states for task list

8. Testing & Verification Tasks
   - Verify signup saves user in Neon DB
   - Verify task creation persists data

## Response snapshot

Successfully generated comprehensive task breakdown with 96 executable tasks organized by user story:

**Phase 1: Project Cleanup (12 tasks)**
- T001-T012: Remove all Pages Router files, duplicate components, legacy code
- Includes deletion of src/pages/, App.jsx, AuthContext.jsx, axios.js
- Removes duplicate auth forms, todo components, layout components
- Consolidates global styles

**Phase 2: Foundation (11 tasks)**
- T013-T023: Core infrastructure required before user story implementation
- Install react-hook-form, configure Next.js settings
- Create base UI components (Header, Container, WithAuth HOC)
- Update auth provider to consolidate all auth logic
- Fix root layout to remove duplicate headers

**Phase 3: User Story 1 - Authentication (15 tasks)**
- T024-T038: Complete authentication flow implementation
- Create login and signup forms with react-hook-form
- Fix syntax errors in existing pages
- Implement form submission handlers with API integration
- Add redirect logic, error handling, loading states
- Test authentication flow end-to-end

**Phase 4: User Story 2 - Task Creation (17 tasks)**
- T039-T055: Task creation form with all required fields
- Create task form component with 6 fields (title, description, due_date, priority, tags, recursion_pattern)
- Implement validation and error handling
- Connect to backend API for persistence
- Test task creation flow

**Phase 5: User Story 3 - Task Management Dashboard (20 tasks)**
- T056-T075: Complete task management functionality
- Create task list and task item components
- Implement mark complete and delete operations
- Add loading, empty, and error states
- Fix dashboard layout issues
- Test full CRUD operations

**Phase 6: Error Handling (9 tasks)**
- T076-T084: Robust error handling for all scenarios
- Global handlers for 401, 403, 404, 422, 500 errors
- Network error handling
- Token expiration handling

**Phase 7: UI/UX Polish (12 tasks)**
- T085-T096: Final polish and cross-cutting concerns
- Responsive design, accessibility
- Loading indicators, proper styling
- Code cleanup and final testing

**Key Features:**
- All tasks follow strict checklist format: `- [ ] T### [P?] [Story?] Description with file path`
- Tasks organized by user story for independent implementation
- Clear parallel opportunities identified (marked with [P])
- Comprehensive validation checklist for each user story
- Implementation strategies: MVP first, incremental delivery, parallel team
- Total: 96 tasks across 7 phases

## Outcome

- ✅ Impact: Comprehensive, executable task breakdown ready for immediate implementation. Each task is specific with exact file paths and clear acceptance criteria.
- 🧪 Tests: No automated tests generated (not requested in spec). Manual testing tasks included for each user story.
- 📁 Files: Updated tasks.md with complete task breakdown (96 tasks)
- 🔁 Next prompts: Ready to begin implementation. Start with Phase 1 (Cleanup) tasks T001-T012.
- 🧠 Reflection: Task breakdown successfully maps all user stories to concrete implementation steps. Each user story can be implemented and tested independently. Clear checkpoints after each phase enable incremental validation.

## Evaluation notes (flywheel)

- Failure modes observed: None. Task generation completed successfully with proper organization.
- Graders run and results (PASS/FAIL): Format validation: PASS (all tasks follow checklist format with IDs, labels, file paths)
- Prompt variant (if applicable): Standard /sp.tasks workflow with user story organization
- Next experiment (smallest change to try): Begin Phase 1 cleanup by executing T001 (delete Pages Router directory) to immediately simplify codebase structure and validate task execution workflow.