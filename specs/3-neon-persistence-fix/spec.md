# Specification: Fix Task Creation Form, Enforce Dashboard Redirect After Login, and Ensure User & Task Persistence in Neon PostgreSQL

## Overview
Address critical issues in the authentication and task management flow where users successfully login but aren't redirected to dashboard, and tasks are not properly persisted to Neon PostgreSQL database. This specification outlines requirements to fix the complete data persistence flow from frontend to Neon database.

## Context
- Authentication is partially working (can login)
- Users login successfully but are not redirected to dashboard
- Task creation lacks proper form structure and doesn't persist to Neon database
- User and task data is not persisting in Neon PostgreSQL
- Local database usage must be eliminated
- Complete end-to-end flow from signup/login to dashboard and task creation must work

## Scope
### In Scope
- User signup data persistence in Neon PostgreSQL
- User login authentication against Neon database
- Automatic redirect to dashboard after successful login
- Proper task creation form with all required fields
- Task data persistence in Neon PostgreSQL with user associations
- Complete data flow from frontend form to Neon database
- Proper user isolation (users only see their own tasks)

### Out of Scope
- Changing backend database technology
- Modifying existing UI design aesthetics (only functionality fixes)
- Adding new features beyond the core persistence issues
- Performance optimization beyond fixing the persistence flow

## Key Entities
- **User**: Authentication identity with username, email, hashed password
- **Task**: User-associated items with title, description, due_date, priority, tags, recursion_pattern
- **Neon PostgreSQL**: Cloud database requiring proper connection configuration
- **Authentication Session**: JWT-based user session management

## User Scenarios & Testing
### Scenario 1: User Registration Flow
1. User visits signup page and fills form with username, email, password
2. Data is sent to backend and saved in Neon PostgreSQL users table
3. User is authenticated and redirected to dashboard
4. Backend properly validates and hashes password before storage

### Scenario 2: User Login Flow
1. User enters email and password on login page
2. Credentials are verified against Neon PostgreSQL database
3. On success, JWT token is generated and user session established
4. User is automatically redirected to dashboard (not kept on login page)

### Scenario 3: Task Creation Flow
1. Authenticated user accesses dashboard
2. User fills task form with all required fields (title, description, due_date, etc.)
3. Form sends structured JSON to backend task endpoint
4. Task is saved to Neon PostgreSQL with proper user association
5. Task appears in user's dashboard after creation

### Scenario 4: Data Persistence Verification
1. User creates account and logs in
2. User creates multiple tasks over time
3. After browser restart or page refresh, all data persists
4. Only user's own tasks are accessible to that user

## Functional Requirements
### FR1: User Signup Persistence
- **REQ**: When a user submits signup form, all data must be stored in Neon PostgreSQL users table
- **ACCEPTANCE**:
  - User records created with username, email, properly hashed password
  - Email uniqueness constraint enforced at database level
  - Username uniqueness constraint enforced at database level
  - User creation timestamp recorded

### FR2: Login Authentication Against Neon DB
- **REQ**: Login credentials must be validated against user records in Neon PostgreSQL
- **ACCEPTANCE**:
  - Email/password combinations checked against Neon database
  - Password verification works with hashed passwords
  - Invalid credentials return appropriate error message
  - Valid credentials establish JWT session

### FR3: Post-Login Dashboard Redirect
- **REQ**: After successful login, user must be automatically redirected to dashboard
- **ACCEPTANCE**:
  - Successful login triggers immediate redirect to /dashboard
  - User doesn't remain on login page after authentication
  - JWT token is properly stored for subsequent API calls
  - Dashboard loads user-specific content

### FR4: Structured Task Creation Form
- **REQ**: Dashboard must contain comprehensive task form supporting all required fields
- **ACCEPTANCE**:
  - Form collects title (required), description (optional), due_date (optional)
  - Form supports priority selection (High | Medium | Low)
  - Form handles tags as list of strings
  - Form includes recursion_pattern field (optional)
  - Form validates required fields before submission

### FR5: Task Persistence in Neon DB
- **REQ**: Created tasks must be stored in Neon PostgreSQL tasks table with user association
- **ACCEPTANCE**:
  - Task records include proper foreign key linking to user_id
  - All task fields (title, description, due_date, priority, tags, recursion_pattern) saved
  - Completed status tracked (default: false)
  - Creation/update timestamps recorded

### FR6: User-Task Association
- **REQ**: Tasks must be properly linked to authenticated user via foreign key relationship
- **ACCEPTANCE**:
  - Task.user_id field properly set to authenticated user's ID
  - No orphaned task records without valid user association
  - Foreign key constraints enforced at database level
  - User isolation maintained in all queries

### FR7: Backend API Data Flow
- **REQ**: Task form data must flow properly from frontend to Neon database through backend
- **ACCEPTANCE**:
  - Frontend sends JSON matching backend schema exactly
  - Backend properly receives and validates task data
  - SQLModel handles database operations correctly
  - Backend returns saved task record with all properties

### FR8: Frontend Data Synchronization
- **REQ**: After successful task creation, UI must update with server response
- **ACCEPTANCE**:
  - UI updates immediately after successful API response
  - Newly created task appears in task list
  - Loading states properly displayed during API operations
  - Error states handled gracefully

## Non-Functional Requirements
### NFR1: Database Connection
- Must use Neon PostgreSQL serverless via DATABASE_URL environment variable
- Connection pooling must be configured for optimal performance
- All database operations must handle connection timeouts gracefully

### NFR2: Security
- Passwords must be securely hashed using bcrypt or similar
- JWT tokens must be properly validated and secured
- All API endpoints must require authentication where appropriate
- No plain text passwords stored in database

### NFR3: Performance
- Login operations should complete within 2 seconds
- Task creation should complete within 1 second
- Dashboard should load within 3 seconds with all tasks
- Database queries should be optimized for user-specific access patterns

## Success Criteria
- **Quantitative**: 100% of successful logins result in dashboard redirect
- **Performance**: Task creation completes within 1 second with data persisted
- **Reliability**: All user data persists between browser sessions
- **Security**: Passwords are properly hashed, no plain text storage
- **User Experience**: Seamless flow from login to dashboard to task creation
- **Isolation**: Users only see their own tasks, no cross-user access
- **Completeness**: All task form fields properly supported end-to-end

## Constraints
- Must use existing tech stack (React, FastAPI, SQLModel, Neon PostgreSQL)
- Cannot introduce additional databases or storage systems
- Must not hardcode credentials or secrets
- Must use environment variables for configuration
- All data operations must go through Neon PostgreSQL (no local caching as source of truth)

## Dependencies
- Neon PostgreSQL database availability
- Correct DATABASE_URL configuration in environment
- Proper JWT secret configuration
- Working SQLModel/Pydantic integration

## Assumptions
- Neon PostgreSQL is properly configured and accessible
- Backend authentication endpoints are available
- Frontend can make cross-origin requests to backend
- User accounts can be created and authenticated properly
- Network connectivity exists between frontend and backend