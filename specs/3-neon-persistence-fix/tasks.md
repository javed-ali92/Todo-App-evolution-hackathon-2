# Tasks: Fix Task Creation Form, Enforce Dashboard Redirect After Login, and Ensure User & Task Persistence in Neon PostgreSQL

## Feature Overview
Implementation of task creation form, dashboard redirect after login, and Neon PostgreSQL persistence for all user and task data.

## Tech Stack
- Backend: FastAPI, SQLModel, Neon PostgreSQL, JWT authentication
- Frontend: React, Vite, React Router DOM, Axios
- Authentication: User registration/login with token-based sessions
- Environment: DATABASE_URL for Neon connection

## User Stories (from spec.md)
- US1: Users can sign up and their data persists in Neon DB
- US2: Users can login and are redirected to dashboard
- US3: Users can create tasks through a proper form with data persistence
- US4: Tasks are associated with authenticated user and properly isolated
- US5: All data persists between sessions

## Phase 1: Setup
- [ ] T001 Create tasks.md file with implementation plan breakdown
- [ ] T002 Verify backend server running on http://localhost:8000
- [ ] T003 Verify frontend server running on http://localhost:5173
- [ ] T004 Confirm DATABASE_URL configured in backend .env
- [ ] T005 Inspect current project structure and dependencies

## Phase 2: Database Connection & Models
- [ ] T006 [P] Inspect backend .env for DATABASE_URL configuration
- [ ] T007 [P] Remove any SQLite or local DB configurations
- [ ] T008 [P] Configure SQLModel engine with Neon DATABASE_URL
- [ ] T009 [P] Test database connection to Neon
- [ ] T010 [P] Enable table creation on startup
- [ ] T011 [P] Create User SQLModel with proper fields
- [ ] T012 [P] Create Task SQLModel with proper fields
- [ ] T013 [P] Add foreign key relationship between User and Task
- [ ] T014 [P] Add timestamps to both models (created_at, updated_at)

## Phase 3: [US1] Authentication Persistence
- [ ] T015 [US1] Update signup endpoint to save user in Neon DB
- [ ] T016 [US1] Implement proper password hashing in auth service
- [ ] T017 [US1] Verify user data persists after signup (username, email, hashed_password)
- [ ] T018 [US1] Test user creation and verify record appears in Neon DB
- [ ] T019 [US1] Update login endpoint to verify credentials against Neon DB

## Phase 4: [US2] Login Redirect & Session Management
- [ ] T020 [US2] Verify login endpoint returns proper JWT token
- [ ] T021 [US2] Update frontend to redirect to /dashboard after successful login
- [ ] T022 [US2] Implement proper token storage and validation
- [ ] T023 [US2] Ensure dashboard route is protected
- [ ] T024 [US2] Test login redirect functionality

## Phase 5: [US3] Task Management API
- [ ] T025 [US3] Implement create-task endpoint that saves to Neon DB
- [ ] T026 [US3] Implement fetch-tasks endpoint that filters by user
- [ ] T027 [US3] Implement update-task endpoint that modifies Neon records
- [ ] T028 [US3] Implement delete-task endpoint that removes from Neon DB
- [ ] T029 [US3] Enforce user_id filtering to ensure proper isolation

## Phase 6: [US3] Frontend Task Form Implementation
- [ ] T030 [US3] Build task form with title field
- [ ] T031 [US3] Build task form with description field
- [ ] T032 [US3] Build task form with due_date field
- [ ] T033 [US3] Build task form with priority dropdown (High/Medium/Low)
- [ ] T034 [US3] Build task form with tags field
- [ ] T035 [US3] Build task form with recursion_pattern field
- [ ] T036 [US3] Add form validation for required fields
- [ ] T037 [US3] Map form fields to API payload structure
- [ ] T038 [US3] Handle form submission success
- [ ] T039 [US3] Handle form submission errors

## Phase 7: [US4] User-Task Association & Isolation
- [ ] T040 [US4] Update task creation to include authenticated user_id
- [ ] T041 [US4] Update task retrieval to filter by authenticated user_id
- [ ] T042 [US4] Update task modification to verify user ownership
- [ ] T043 [US4] Update task deletion to verify user ownership
- [ ] T044 [US4] Test user isolation (users only see their own tasks)

## Phase 8: [US5] Frontend Data Synchronization
- [ ] T045 [US5] Fetch tasks on dashboard page load
- [ ] T046 [US5] Refresh task list after successful task creation
- [ ] T047 [US5] Render task list from API response
- [ ] T048 [US5] Test data persistence after page refresh
- [ ] T049 [US5] Ensure all data persists between sessions

## Phase 9: Validation & Testing
- [ ] T050 Verify signup creates user record in Neon DB
- [ ] T051 Verify login authenticates against Neon DB and redirects
- [ ] T052 Verify task creation saves to Neon DB with proper user association
- [ ] T053 Verify task retrieval filters properly by user
- [ ] T054 Verify page refresh maintains all data
- [ ] T055 Test complete flow: signup → login → dashboard → create task → persist

## Dependencies
- T006, T007, T008 → T009, T010 (Database setup needed before models)
- T011, T012 → T013, T014 (Base models needed before relationships)
- T013, T014 → T015, T019 (Models needed before endpoints)
- T015 → T021 (Signup before login redirect)
- T021 → T025, T030 (Login before task operations)
- T025, T026, T027, T028 → T030 (API endpoints before frontend)

## Parallel Execution Opportunities
- T006, T007, T008 can run in parallel (database setup tasks)
- T011, T012 can run in parallel (model creation)
- T013, T014 can run in parallel (model relationships)
- T025, T026, T027, T028 can run in parallel (API endpoints)
- T030, T031, T032, T033, T034, T035 can run in parallel (form fields)
- T036, T037, T038, T039 can run in parallel (form functionality)

## Implementation Strategy
**MVP Scope (US1-2 only)**: Tasks T001-T014, T015-T019, T020-T024 - Just signup/login with redirect
**Incremental Delivery**: Add task functionality in phases while maintaining working system
**Testing First**: Validate database connection before building features
**Independent Stories**: Each user story can be tested independently after foundational setup