# Feature Specification: Clean Next.js Frontend with App Router

**Feature Branch**: `004-clean-frontend`
**Created**: 2026-02-07
**Status**: Draft
**Input**: You are acting as a Senior Frontend Architect specialized in Next.js.

Context:
The backend authentication is now working correctly.
However, the frontend has structural issues and is confusing.

Problems Identified:
1. Frontend structure is unclear (mix of `app` and `pages`)
2. Unnecessary / extra files exist
3. Task creation form is not working correctly
4. Login & signup UI exists but flow is inconsistent
5. Codebase is hard to understand and maintain

Goal:
Create a clean, minimal, and fully working Next.js frontend using best practices.

Requirements:

1. Framework
   - Use **Next.js (App Router ONLY)**
   - Do NOT use `pages` folder
   - Use `app` directory exclusively

2. Folder Structure (clean & minimal)
   - app/
     - layout.tsx
     - page.tsx (landing or login redirect)
     - login/
     - signup/
     - dashboard/
       - page.tsx
     - tasks/
       - new/
         - page.tsx
   - components/
   - lib/
   - services/
   - styles/ (if needed)

3. Authentication Flow
   - Login form → redirects to `/dashboard`
   - Signup form → redirects to `/dashboard`
   - Token handling handled cleanly
   - No local dummy data

4. Task Management
   - Proper task creation form with fields:
     - title
     - description
     - due_date
     - priority
     - tags
     - recursion_pattern
   - Submit form → call backend API
   - Data must persist in Neon PostgreSQL DB
   - Show success or error feedback

5. Frontend Quality Rules
   - No unused files
   - No duplicate components
   - No commented junk code
   - Simple, readable, maintainable code
   - Use reusable components where appropriate

6. Analysis First
   - First analyze existing frontend
   - Identify what should be deleted
   - Identify what should be kept
   - Then refactor step-by-step

Constraints:
- Do NOT change backend
- Do NOT add unnecessary libraries
- Keep UI simple (no heavy styling frameworks unless already used)

Output Expectations:
- Explain frontend issues clearly
- Show final folder structure
- Show key component files
- Co

## User Scenarios & Testing *(mandatory)*

<!--IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
you should still have a viable MVP (Minimum Viable Product) that delivers value.

Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
Think of each story as a standalone slice of functionality that can be:
- Developed independently
- Tested independently
- Deployed independently
- Demonstrated to users independently-->

### User Story 1 - User Authentication Flow (Priority: P1)

A user navigates to the application and can register a new account or sign in to an existing one. After successful authentication, the user is redirected to their dashboard. The authentication flow handles token storage and validation properly across page reloads.

**Why this priority**: Authentication is foundational - without it, users cannot access the core functionality of managing their tasks.

**Independent Test**: Can be fully tested by registering a new user, logging in, and verifying redirection to dashboard. Delivers core access control functionality.

**Acceptance Scenarios**:

1. **Given** a user visits the site without authentication, **When** they click signup and complete registration form, **Then** they are redirected to the dashboard with valid session
2. **Given** a user has an account, **When** they visit login page and submit valid credentials, **Then** they are redirected to dashboard with valid session
3. **Given** a user has invalid credentials, **When** they submit login form, **Then** they see error message and remain on login page

---

### User Story 2 - Task Creation (Priority: P1)

An authenticated user can create new tasks with all required fields (title, description, due date, priority, tags, recursion pattern). Submitted tasks are persisted in the database and reflected in the UI immediately.

**Why this priority**: This is the primary value-add functionality that users need from the application.

**Independent Test**: Can be fully tested by creating a task and verifying it appears in the task list. Delivers core task management functionality.

**Acceptance Scenarios**:

1. **Given** an authenticated user is on the dashboard, **When** they fill out the task creation form and submit, **Then** the new task appears in the task list and is stored in database
2. **Given** a user enters invalid task data, **When** they submit the form, **Then** they see appropriate error messages without submitting

---

### User Story 3 - Task Management Dashboard (Priority: P2)

An authenticated user can view, manage, and interact with their existing tasks on a centralized dashboard. The dashboard displays all tasks with key information and allows operations like completion toggling and deletion.

**Why this priority**: This completes the core CRUD functionality that makes the application useful for ongoing task management.

**Independent Test**: Can be fully tested by viewing existing tasks, marking one complete, and deleting another. Delivers full task lifecycle management.

**Acceptance Scenarios**:

1. **Given** a user has created tasks, **When** they visit the dashboard, **Then** all their tasks are displayed in the task list
2. **Given** a user views an existing task, **When** they click to mark it complete, **Then** the task status updates and saves to the database

---

### Edge Cases

- What happens when the user's authentication token expires during a session? (Should redirect to login)
- How does the system handle network failures when submitting forms? (Should show appropriate error messages)
- What happens when a user tries to access protected routes without authentication? (Should redirect to login)

## Requirements *(mandatory)*

<!--ACTION REQUIRED: The content in this section represents placeholders.
Fill them out with the right functional requirements.-->

### Functional Requirements

- **FR-001**: System MUST use Next.js App Router exclusively and eliminate all Pages Router files and dependencies
- **FR-002**: System MUST implement user authentication with signup, login, and token management using secure storage
- **FR-003**: System MUST redirect authenticated users from login/signup pages to dashboard upon successful authentication
- **FR-004**: System MUST provide a task creation form with fields: title, description, due_date, priority, tags, recursion_pattern
- **FR-005**: System MUST connect task form submissions to the backend API to persist data in Neon PostgreSQL DB
- **FR-006**: System MUST display proper success/error feedback for user actions
- **FR-007**: System MUST maintain clean folder structure following Next.js App Router conventions
- **FR-008**: System MUST eliminate duplicate auth providers and consolidate to single, consistent auth solution
- **FR-009**: System MUST ensure no unused or redundant files remain after cleanup

### Key Entities *(include if feature involves data)*

- **User Session**: Represents an authenticated user with associated token, user ID, and authentication status, used for access control and API authorization
- **Task**: Represents a user's task with properties (title, description, due_date, priority, tags, recursion_pattern) that are stored in the database and displayed in the UI

## Success Criteria *(mandatory)*

<!--ACTION REQUIRED: Define measurable success criteria.
These must be technology-agnostic and measurable.-->

### Measurable Outcomes

- **SC-001**: Users can complete account registration and login flow within 30 seconds without confusion
- **SC-002**: Users can successfully create new tasks that persist in the database and appear in the task list immediately
- **SC-003**: Application contains no duplicate authentication systems or conflicting frontend frameworks (100% App Router structure)
- **SC-004**: 95% of users successfully complete primary task creation workflow without encountering errors