---
description: "Comprehensive task list for clean Next.js frontend with App Router implementation"
---

# Tasks: Clean Next.js Frontend with App Router

**Input**: Design documents from `/specs/004-clean-frontend/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL - only included if explicitly requested in the feature specification.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Paths shown below are for the frontend structure

---

## Phase 1: Project Cleanup (Remove Legacy Code)

**Purpose**: Remove all Pages Router files, duplicate components, and legacy code to establish clean foundation

- [ ] T001 Delete Pages Router directory and all contents: `frontend/src/pages/`
- [ ] T002 Delete legacy React Router files: `frontend/src/App.jsx`, `frontend/src/main.jsx`
- [ ] T003 Delete legacy auth context: `frontend/src/context/AuthContext.jsx`
- [ ] T004 Delete legacy axios API client: `frontend/src/api/axios.js`
- [ ] T005 [P] Delete duplicate component files in root components folder that conflict with organized structure
- [ ] T006 [P] Delete unused page components: `frontend/src/pages/LandingPage.jsx`, `frontend/src/pages/LoginPage.jsx`, `frontend/src/pages/SignupPage.jsx`, `frontend/src/pages/DashboardPage.jsx`, `frontend/src/pages/TodoAddPage.jsx`, `frontend/src/pages/NotFoundPage.jsx`
- [ ] T007 [P] Delete duplicate auth form components: `frontend/src/components/auth/LoginForm.jsx`, `frontend/src/components/auth/SignupForm.jsx`
- [ ] T008 [P] Delete duplicate todo components: `frontend/src/components/todos/TodoForm.jsx`, `frontend/src/components/todos/TodoItem.jsx`, `frontend/src/components/TodoForm.jsx`, `frontend/src/components/TodoItem.jsx`, `frontend/src/components/TodoList.jsx`, `frontend/src/components/DashboardStats.jsx`
- [ ] T009 [P] Delete duplicate layout components: `frontend/src/components/layout/Header.jsx`, `frontend/src/components/layout/Footer.jsx`, `frontend/src/components/Header.jsx`, `frontend/src/components/Footer.jsx`, `frontend/src/components/HeroSection.jsx`
- [ ] T010 [P] Delete legacy protected route and error boundary: `frontend/src/components/ProtectedRoute.jsx`, `frontend/src/components/ErrorBoundary.jsx`
- [ ] T011 Remove react-router-dom and axios from package.json dependencies
- [ ] T012 Verify only one globals.css exists (consolidate `frontend/src/styles/globals.css` and `frontend/src/app/globals.css`)

**Checkpoint**: All legacy Pages Router code removed, only App Router structure remains

---

## Phase 2: Foundation (Core Infrastructure)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T013 [P] Install react-hook-form dependency: `npm install react-hook-form` in frontend directory
- [ ] T014 [P] Verify and update next.config.js with proper API proxy configuration for `/api` routes
- [ ] T015 [P] Verify tsconfig.json has path aliases configured: `@/*` pointing to `./src/*`
- [ ] T016 Create base UI components directory structure: `frontend/src/components/ui/`
- [ ] T017 [P] Create reusable Header component in `frontend/src/components/ui/header.tsx` with logout functionality
- [ ] T018 [P] Create reusable Container layout component in `frontend/src/components/layouts/container.tsx`
- [ ] T019 Create WithAuth HOC for protected routes in `frontend/src/components/hoc/with-auth.tsx`
- [ ] T020 Update auth provider in `frontend/src/app/providers/auth-provider.tsx` to consolidate all auth logic (login, signup, logout, token management)
- [ ] T021 Fix root layout in `frontend/src/app/layout.tsx` to remove duplicate Header components and properly wrap with AuthProvider
- [ ] T022 Update root layout metadata with proper title and description
- [ ] T023 [P] Consolidate global styles: merge `frontend/src/styles/globals.css` into `frontend/src/app/globals.css` and delete duplicate

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - User Authentication Flow (Priority: P1) 🎯 MVP

**Goal**: Enable users to register new accounts and sign in to existing ones with proper redirection to dashboard

**Independent Test**: Can be fully tested by registering a new user, logging in, and verifying redirection to dashboard. Delivers core access control functionality.

### Implementation for User Story 1

- [ ] T024 [P] [US1] Create login form component in `frontend/src/components/forms/login-form.tsx` using react-hook-form with email and password fields
- [ ] T025 [P] [US1] Create signup form component in `frontend/src/components/forms/signup-form.tsx` using react-hook-form with username, email, and password fields
- [ ] T026 [US1] Fix login page in `frontend/src/app/login/page.tsx` with proper syntax (fix missing quotes in className attributes) and integrate login-form component
- [ ] T027 [US1] Fix signup page in `frontend/src/app/signup/page.tsx` with proper syntax and integrate signup-form component
- [ ] T028 [US1] Implement login form submission handler that calls auth-client.ts login method and stores token in localStorage
- [ ] T029 [US1] Implement signup form submission handler that calls auth-client.ts register method and stores token in localStorage
- [ ] T030 [US1] Add redirect logic to login form: on success redirect to `/dashboard`
- [ ] T031 [US1] Add redirect logic to signup form: on success redirect to `/dashboard`
- [ ] T032 [US1] Add error handling to login form: display API errors (401, 422) in user-friendly format
- [ ] T033 [US1] Add error handling to signup form: display API errors (400, 422) in user-friendly format
- [ ] T034 [US1] Update landing page in `frontend/src/app/page.tsx` to redirect authenticated users to `/dashboard`
- [ ] T035 [US1] Add loading states to login and signup forms (disable submit button, show spinner)
- [ ] T036 [US1] Test authentication flow: signup → verify user saved in Neon DB → login → verify redirect to dashboard
- [ ] T037 [US1] Test token persistence: login → refresh page → verify still authenticated
- [ ] T038 [US1] Test logout functionality: click logout → verify token removed → verify redirect to login

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Task Creation (Priority: P1)

**Goal**: Allow authenticated users to create new tasks with all required fields that persist in the database

**Independent Test**: Can be fully tested by creating a task and verifying it appears in the task list. Delivers core task management functionality.

### Implementation for User Story 2

- [ ] T039 [US2] Create task form component in `frontend/src/components/forms/task-form.tsx` using react-hook-form
- [ ] T040 [US2] Add title field to task form (required, text input, max 200 chars)
- [ ] T041 [US2] Add description field to task form (optional, textarea, max 1000 chars)
- [ ] T042 [US2] Add due_date field to task form (optional, date input)
- [ ] T043 [US2] Add priority field to task form (required, select dropdown with High/Medium/Low, default Medium)
- [ ] T044 [US2] Add tags field to task form (optional, text input for comma-separated tags)
- [ ] T045 [US2] Add recursion_pattern field to task form (optional, text input)
- [ ] T046 [US2] Implement form validation: title required, description max length, valid date format
- [ ] T047 [US2] Implement form submission handler that calls task-client.ts createTask method
- [ ] T048 [US2] Add success feedback: show success message and clear form after task creation
- [ ] T049 [US2] Add error handling: display API errors (400, 401, 403, 422) in user-friendly format
- [ ] T050 [US2] Add loading state to task form (disable submit button, show spinner during submission)
- [ ] T051 [US2] Create or update task creation page in `frontend/src/app/tasks/new/page.tsx` with WithAuth wrapper
- [ ] T052 [US2] Integrate task form component into task creation page
- [ ] T053 [US2] Test task creation flow: fill form → submit → verify task saved in Neon DB via backend API
- [ ] T054 [US2] Test validation: submit empty form → verify error messages displayed
- [ ] T055 [US2] Test error handling: simulate API error → verify error message displayed

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Task Management Dashboard (Priority: P2)

**Goal**: Display user's tasks on a centralized dashboard with ability to manage them

**Independent Test**: Can be fully tested by viewing existing tasks, marking one complete, and deleting another. Delivers full task lifecycle management.

### Implementation for User Story 3

- [ ] T056 [P] [US3] Create task list component in `frontend/src/components/lists/task-list.tsx` to display array of tasks
- [ ] T057 [P] [US3] Create task item component within task-list.tsx to render individual task with title, description, due date, priority, tags
- [ ] T058 [US3] Add "Mark Complete" button to task item that calls task-client.ts toggleTaskCompletion method
- [ ] T059 [US3] Add "Delete" button to task item that calls task-client.ts deleteTask method
- [ ] T060 [US3] Add visual indication for completed tasks (strikethrough, different color)
- [ ] T061 [US3] Implement task list data fetching: call task-client.ts getUserTasks on component mount
- [ ] T062 [US3] Add loading state to task list (show spinner while fetching)
- [ ] T063 [US3] Add empty state to task list (show message when no tasks exist)
- [ ] T064 [US3] Add error handling to task list: display API errors (401, 403, 404) in user-friendly format
- [ ] T065 [US3] Update dashboard page in `frontend/src/app/dashboard/page.tsx` with WithAuth wrapper
- [ ] T066 [US3] Fix dashboard layout in `frontend/src/app/dashboard/layout.tsx` to remove duplicate headers
- [ ] T067 [US3] Integrate task list component into dashboard page
- [ ] T068 [US3] Add link to task creation page from dashboard
- [ ] T069 [US3] Implement automatic task list refresh after creating new task
- [ ] T070 [US3] Implement automatic task list refresh after marking task complete
- [ ] T071 [US3] Implement automatic task list refresh after deleting task
- [ ] T072 [US3] Test dashboard flow: login → view tasks → verify all user's tasks displayed
- [ ] T073 [US3] Test mark complete: click button → verify task status updates in UI and DB
- [ ] T074 [US3] Test delete: click button → verify task removed from UI and DB
- [ ] T075 [US3] Test unauthorized access: logout → try to access /dashboard → verify redirect to login

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Error Handling & Edge Cases

**Purpose**: Robust error handling across all user stories

- [ ] T076 [P] Add global error handler for 401 Unauthorized: redirect to login and clear token
- [ ] T077 [P] Add global error handler for 403 Forbidden: show "Access Denied" message
- [ ] T078 [P] Add global error handler for 404 Not Found: show "Resource not found" message
- [ ] T079 [P] Add global error handler for 422 Validation Error: display field-specific errors
- [ ] T080 [P] Add global error handler for 500 Server Error: show "Something went wrong" message
- [ ] T081 Add network error handling: detect offline state and show appropriate message
- [ ] T082 Ensure all error messages render as strings (no object rendering like [object Object])
- [ ] T083 Add token expiration handling: check expiry time and auto-logout when expired
- [ ] T084 Test error scenarios: invalid credentials, expired token, network failure, server error

---

## Phase 7: UI/UX Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T085 [P] Update global styles in `frontend/src/app/globals.css` for consistent spacing and colors
- [ ] T086 [P] Ensure responsive design: test on mobile, tablet, desktop viewports
- [ ] T087 [P] Add proper focus states to all interactive elements (buttons, inputs)
- [ ] T088 [P] Add proper hover states to all buttons and links
- [ ] T089 Add loading indicators for all async operations (consistent spinner component)
- [ ] T090 Ensure all forms have proper labels and accessibility attributes
- [ ] T091 Add proper page titles for all routes (login, signup, dashboard, tasks)
- [ ] T092 Code cleanup: remove console.logs, commented code, unused imports
- [ ] T093 Code cleanup: ensure consistent code formatting across all files
- [ ] T094 Verify no unused files remain in src/ directory
- [ ] T095 Final integration testing: complete full user journey from signup to task management
- [ ] T096 Performance check: verify fast initial load and responsive interactions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Cleanup (Phase 1)**: No dependencies - can start immediately
- **Foundation (Phase 2)**: Depends on Cleanup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundation phase completion
  - User Story 1 (P1): Can start after Foundation - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundation - No dependencies on other stories
  - User Story 3 (P2): Can start after Foundation - Depends on US1 (auth) and US2 (task data)
- **Error Handling (Phase 6)**: Can start after any user story is implemented
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundation (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundation (Phase 2) - Requires authentication from US1 to test properly
- **User Story 3 (P2)**: Can start after Foundation (Phase 2) - Requires US1 (authentication) and US2 (task data) to be functional

### Within Each User Story

- Form components before page components
- API integration before UI updates
- Core functionality before error handling
- Error handling before loading states
- Story complete before moving to next priority

### Parallel Opportunities

- All Cleanup tasks (T001-T012) can run in parallel
- Foundation tasks marked [P] (T013-T015, T017-T018, T023) can run in parallel
- US1 form components (T024-T025) can be created in parallel
- US1 error handling (T032-T033) can be added in parallel
- US3 components (T056-T057) can be created in parallel
- Error handlers (T076-T080) can be implemented in parallel
- Polish tasks (T085-T088) can be done in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Cleanup
2. Complete Phase 2: Foundation (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Authentication)
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Cleanup + Foundation → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add Error Handling → Test edge cases
6. Add Polish → Final testing
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Cleanup + Foundation together
2. Once Foundation is done:
   - Developer A: User Story 1 (Authentication)
   - Developer B: User Story 2 (Task Creation) - can work on forms/components
   - Developer C: User Story 3 (Dashboard) - can work on components
3. Stories integrate and test independently

---

## Validation Checklist

Before considering implementation complete, verify:

### User Story 1 - Authentication
- [ ] Can register new user with username, email, password
- [ ] New user is saved in Neon PostgreSQL database
- [ ] Can login with registered credentials
- [ ] Login redirects to /dashboard
- [ ] Signup redirects to /dashboard
- [ ] Token is stored securely in localStorage
- [ ] Token persists across page reloads
- [ ] Invalid credentials show error message
- [ ] Logout clears token and redirects to login

### User Story 2 - Task Creation
- [ ] Can access task creation form when authenticated
- [ ] Form has all required fields (title, description, due_date, priority, tags, recursion_pattern)
- [ ] Form validation works (title required, max lengths)
- [ ] Can submit form with valid data
- [ ] Task is saved in Neon PostgreSQL database via backend API
- [ ] Success message displayed after creation
- [ ] Form clears after successful submission
- [ ] API errors displayed in user-friendly format

### User Story 3 - Task Management
- [ ] Dashboard displays all user's tasks
- [ ] Can mark task as complete
- [ ] Task completion status updates in database
- [ ] Can delete task
- [ ] Task is removed from database
- [ ] Task list refreshes after operations
- [ ] Empty state shown when no tasks exist
- [ ] Loading state shown while fetching tasks

### General Requirements
- [ ] No Pages Router files remain (src/pages/ deleted)
- [ ] No duplicate components remain
- [ ] Only App Router structure exists (src/app/)
- [ ] All routes use proper Next.js App Router conventions
- [ ] Protected routes redirect to login when not authenticated
- [ ] All API calls go through existing backend
- [ ] No local or dummy data used
- [ ] Error messages render as strings (no [object Object])
- [ ] All forms have loading states
- [ ] Code is clean (no console.logs, commented code)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- All file paths are relative to repository root