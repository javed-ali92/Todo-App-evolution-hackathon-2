# Task Breakdown: NeonDB Authentication & Task Persistence

**Branch**: `002-neondb-persistence` | **Date**: 2026-02-03 | **Spec**: [link]

## Overview

This task breakdown implements Neon Serverless PostgreSQL persistence for authentication and task data in the Todo application. The system will store all user registration/login data and task CRUD operations in NeonDB with frontend forms aligned to the database schema, enforcing user data isolation and secure authentication with JWT tokens.

---

## Phase 1: Repository Setup

- [ ] T001 [P1] [US1] Create backend/src/models directory structure backend
- [ ] T002 [P1] [US1] Create frontend/src/lib/api directory structure frontend
- [ ] T003 [P1] [US1] Create backend/src/database directory structure backend
- [ ] T004 [P1] [US1] Create backend/src/api directory structure backend
- [ ] T005 [P1] [US1] Create backend/src/services directory structure backend
- [ ] T006 [P1] [US1] Create backend/src/auth directory structure backend
- [ ] T007 [P1] [US1] Create backend/src/utils directory structure backend
- [ ] T008 [P1] [US1] Create backend/src/middleware directory structure backend

---

## Phase 2: Environment Configuration

- [ ] T009 [P1] [US1] Create backend/.env file with NeonDB connection string backend
- [ ] T010 [P1] [US1] Create frontend/.env.local file with API endpoint configuration frontend
- [ ] T011 [P1] [US1] Configure DATABASE_URL with NeonDB SSL connection in backend/.env backend
- [ ] T012 [P1] [US1] Configure JWT SECRET_KEY in backend/.env backend
- [ ] T013 [P1] [US1] Configure NEXT_PUBLIC_API_BASE_URL in frontend/.env.local frontend
- [ ] T014 [P1] [US1] Add environment validation to backend startup backend
- [ ] T015 [P1] [US1] Add environment validation to frontend initialization frontend

---

## Phase 3: Database & Neon Migration

- [ ] T016 [P1] [US1] Create backend/src/database/__init__.py with SQLModel imports backend
- [ ] T017 [P1] [US1] Create backend/src/database/database.py with NeonDB connection logic backend
- [ ] T018 [P1] [US1] Create backend/src/database/dependencies.py with database session dependency backend
- [ ] T019 [P1] [US1] Implement SSL configuration for NeonDB connection backend
- [ ] T020 [P1] [US1] Create database connection pool configuration for Neon Serverless backend
- [ ] T021 [P1] [US1] Implement connection health check function backend
- [ ] T022 [P1] [US1] Create database initialization script backend

---

## Phase 4: Schema Verification

- [ ] T023 [P1] [US1] Create backend/src/models/user.py with User SQLModel definition backend
- [ ] T024 [P1] [US1] Create backend/src/models/task.py with Task SQLModel definition backend
- [ ] T025 [P1] [US1] Create backend/src/models/session.py with Session SQLModel definition backend
- [ ] T026 [P1] [US1] Implement User model with email uniqueness constraint backend
- [ ] T027 [P1] [US1] Implement Task model with user_id foreign key relationship backend
- [ ] T028 [P1] [US1] Implement Session model with token uniqueness constraint backend
- [ ] T029 [P1] [US1] Add validation rules to User model backend
- [ ] T030 [P1] [US1] Add validation rules to Task model backend
- [ ] T031 [P1] [US1] Add validation rules to Session model backend

---

## Phase 5: Backend Foundation

- [ ] T032 [P1] [US1] Create backend/src/auth/jwt_handler.py with JWT token functions backend
- [ ] T033 [P1] [US1] Implement create_access_token function with user_id payload backend
- [ ] T034 [P1] [US1] Implement verify_token function to extract user_id from token backend
- [ ] T035 [P1] [US1] Create backend/src/auth/__init__.py with authentication exports backend
- [ ] T036 [P1] [US1] Create backend/src/utils/logging.py with application logging setup backend
- [ ] T037 [P1] [US1] Create backend/src/utils/__init__.py with utility exports backend
- [ ] T038 [P1] [US1] Set up application logger with proper formatting backend

---

## Phase 6: Authentication Persistence

- [ ] T039 [P1] [US1] Create backend/src/services/auth_service.py with authentication functions backend
- [ ] T040 [P1] [US1] Implement get_password_hash function using bcrypt backend
- [ ] T041 [P1] [US1] Implement verify_password function using bcrypt backend
- [ ] T042 [P1] [US1] Implement authenticate_user function to verify credentials against NeonDB backend
- [ ] T043 [P1] [US1] Implement create_user function to save user to NeonDB backend
- [ ] T044 [P1] [US1] Implement get_user_by_email function to check for existing users backend
- [ ] T045 [P1] [US1] Add password validation to auth service backend
- [ ] T046 [P1] [US1] Add email format validation to auth service backend
- [ ] T047 [P1] [US1] Implement duplicate email detection in auth service backend
- [ ] T048 [P1] [US1] Create backend/src/api/auth.py with authentication API routes backend
- [ ] T049 [P1] [US1] Implement POST /api/auth/register endpoint backend
- [ ] T050 [P1] [US1] Implement POST /api/auth/login endpoint backend
- [ ] T051 [P1] [US1] Implement GET /api/auth/me endpoint backend
- [ ] T052 [P1] [US1] Implement POST /api/auth/logout endpoint backend
- [ ] T053 [P1] [US1] Add request validation to auth endpoints backend
- [ ] T054 [P1] [US1] Add response validation to auth endpoints backend
- [ ] T055 [P1] [US1] Add error handling to auth endpoints backend
- [ ] T056 [P1] [US1] Create backend/src/api/__init__.py with API router exports backend

---

## Phase 7: Task Persistence

- [ ] T057 [P1] [US2] Create backend/src/services/task_service.py with task management functions backend
- [ ] T058 [P1] [US2] Implement create_task function to save task to NeonDB backend
- [ ] T059 [P1] [US2] Implement get_tasks_for_user function to retrieve user's tasks from NeonDB backend
- [ ] T060 [P1] [US2] Implement get_task_by_id function to retrieve specific task from NeonDB backend
- [ ] T061 [P1] [US2] Implement update_task function to modify task in NeonDB backend
- [ ] T062 [P1] [US2] Implement delete_task function to remove task from NeonDB backend
- [ ] T063 [P1] [US2] Implement toggle_task_completion function to update completion status in NeonDB backend
- [ ] T064 [P1] [US2] Add user_id validation to task service functions backend
- [ ] T065 [P1] [US2] Add task validation to task service functions backend
- [ ] T066 [P1] [US2] Create backend/src/api/tasks.py with task management API routes backend
- [ ] T067 [P1] [US2] Implement GET /api/{user_id}/tasks endpoint backend
- [ ] T068 [P1] [US2] Implement POST /api/{user_id}/tasks endpoint backend
- [ ] T069 [P1] [US2] Implement GET /api/{user_id}/tasks/{id} endpoint backend
- [ ] T070 [P1] [US2] Implement PUT /api/{user_id}/tasks/{id} endpoint backend
- [ ] T071 [P1] [US2] Implement DELETE /api/{user_id}/tasks/{id} endpoint backend
- [ ] T072 [P1] [US2] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint backend
- [ ] T073 [P1] [US2] Add user_id verification to task endpoints backend
- [ ] T074 [P1] [US2] Add token validation to task endpoints backend
- [ ] T075 [P1] [US2] Add request validation to task endpoints backend
- [ ] T076 [P1] [US2] Add response validation to task endpoints backend
- [ ] T077 [P1] [US2] Add error handling to task endpoints backend
- [ ] T078 [P1] [US2] Add user data isolation verification to task endpoints backend

---

## Phase 8: Frontend Form Alignment

- [ ] T079 [P1] [US1] Create frontend/src/app/signup/page.tsx with signup form component frontend
- [ ] T080 [P1] [US1] Create frontend/src/app/login/page.tsx with login form component frontend
- [ ] T081 [P1] [US1] Create frontend/src/components/task-form.tsx with task creation form frontend
- [ ] T082 [P1] [US1] Create frontend/src/components/task-list.tsx with task display component frontend
- [ ] T083 [P1] [US1] Implement email validation matching database requirements in signup form frontend
- [ ] T084 [P1] [US1] Implement password validation matching database requirements in signup form frontend
- [ ] T085 [P1] [US1] Implement email validation matching database requirements in login form frontend
- [ ] T086 [P1] [US1] Implement password validation matching database requirements in login form frontend
- [ ] T087 [P1] [US2] Implement title validation matching database requirements in task form frontend
- [ ] T088 [P1] [US2] Implement description validation matching database requirements in task form frontend
- [ ] T089 [P1] [US1] Add form validation error handling to signup form frontend
- [ ] T090 [P1] [US1] Add form validation error handling to login form frontend
- [ ] T091 [P1] [US2] Add form validation error handling to task form frontend
- [ ] T092 [P1] [US1] Add loading states to signup form frontend
- [ ] T093 [P1] [US1] Add loading states to login form frontend
- [ ] T094 [P1] [US2] Add loading states to task form frontend
- [ ] T095 [P1] [US2] Add loading states to task list component frontend

---

## Phase 9: Frontend Features

- [ ] T096 [P1] [US1] Create frontend/src/lib/api/auth-client.ts with authentication API client frontend
- [ ] T097 [P1] [US1] Implement registerUser function in auth client frontend
- [ ] T098 [P1] [US1] Implement loginUser function in auth client frontend
- [ ] T099 [P1] [US1] Implement getUserInfo function in auth client frontend
- [ ] T100 [P1] [US1] Implement logoutUser function in auth client frontend
- [ ] T101 [P1] [US2] Create frontend/src/lib/api/task-client.ts with task management API client frontend
- [ ] T102 [P1] [US2] Implement getTasksForUser function in task client frontend
- [ ] T103 [P1] [US2] Implement createTask function in task client frontend
- [ ] T104 [P1] [US2] Implement getTaskById function in task client frontend
- [ ] T105 [P1] [US2] Implement updateTask function in task client frontend
- [ ] T106 [P1] [US2] Implement deleteTask function in task client frontend
- [ ] T107 [P1] [US2] Implement toggleTaskCompletion function in task client frontend
- [ ] T108 [P1] [US1] Add JWT token storage to auth client frontend
- [ ] T109 [P1] [US1] Add JWT token retrieval to auth client frontend
- [ ] T110 [P1] [US1] Add JWT token removal to auth client frontend
- [ ] T111 [P1] [US1] Add JWT token validation to auth client frontend
- [ ] T112 [P1] [US2] Add user_id validation to task client frontend
- [ ] T113 [P1] [US2] Add authorization headers to task client frontend
- [ ] T114 [P1] [US1] Connect signup form to auth client API frontend
- [ ] T115 [P1] [US1] Connect login form to auth client API frontend
- [ ] T116 [P1] [US2] Connect task form to task client API frontend
- [ ] T117 [P1] [US2] Connect task list to task client API frontend

---

## Phase 10: Security Hardening

- [ ] T118 [P1] [US1] Create backend/src/middleware/auth_middleware.py with JWT validation middleware backend
- [ ] T119 [P1] [US1] Implement token extraction from Authorization header middleware backend
- [ ] T120 [P1] [US1] Implement token validation in auth middleware backend
- [ ] T121 [P1] [US1] Implement user_id extraction from token in auth middleware backend
- [ ] T122 [P1] [US1] Add token expiration validation to auth middleware backend
- [ ] T123 [P1] [US1] Apply auth middleware to protected endpoints backend
- [ ] T124 [P1] [US1] Add user_id verification in middleware against URL parameter backend
- [ ] T125 [P1] [US1] Implement secure password hashing with bcrypt backend
- [ ] T126 [P1] [US1] Add password strength validation to auth service backend
- [ ] T127 [P1] [US1] Add rate limiting to auth endpoints backend
- [ ] T128 [P1] [US2] Add rate limiting to task endpoints backend
- [ ] T129 [P1] [US1] Add input sanitization to all API endpoints backend
- [ ] T130 [P1] [US2] Add input sanitization to all task endpoints backend

---

## Phase 11: Testing

- [ ] T131 [P1] [US1] Create backend/tests/test_auth.py with authentication tests backend
- [ ] T132 [P1] [US1] Create backend/tests/test_tasks.py with task management tests backend
- [ ] T133 [P1] [US1] Implement user registration test with NeonDB verification backend
- [ ] T134 [P1] [US1] Implement user login test with NeonDB verification backend
- [ ] T135 [P1] [US1] Implement duplicate email registration test backend
- [ ] T136 [P1] [US1] Implement invalid credentials test backend
- [ ] T137 [P1] [US2] Implement task creation test with NeonDB verification backend
- [ ] T138 [P1] [US2] Implement task retrieval test with NeonDB verification backend
- [ ] T139 [P1] [US2] Implement task update test with NeonDB verification backend
- [ ] T140 [P1] [US2] Implement task deletion test with NeonDB verification backend
- [ ] T141 [P1] [US2] Implement task completion toggle test with NeonDB verification backend
- [ ] T142 [P1] [US1] Implement user data isolation test backend
- [ ] T143 [P1] [US2] Implement unauthorized access test for tasks backend
- [ ] T144 [P1] [US1] Implement JWT token validation test backend
- [ ] T145 [P1] [US1] Implement expired token test backend
- [ ] T146 [P1] [US1] Create test database connection configuration backend
- [ ] T147 [P1] [US1] Implement test cleanup for database records backend
- [ ] T148 [P1] [US1] Add database transaction rollback to auth tests backend
- [ ] T149 [P1] [US2] Add database transaction rollback to task tests backend

---

## Phase 12: Validation & Acceptance

- [ ] T150 [P1] [US1] Test user registration and verify data appears in NeonDB database
- [ ] T151 [P1] [US1] Test user login using credentials stored in NeonDB
- [ ] T152 [P1] [US2] Test task creation and verify data appears in NeonDB database
- [ ] T153 [P1] [US2] Test task retrieval from NeonDB database
- [ ] T154 [P1] [US2] Test task updates and verify changes persist in NeonDB
- [ ] T155 [P1] [US2] Test task deletion and verify removal from NeonDB
- [ ] T156 [P1] [US1] Test user data isolation - users only see their own tasks
- [ ] T157 [P1] [US1] Test password hashing and verification process
- [ ] T158 [P1] [US1] Test JWT token generation and validation
- [ ] T159 [P1] [US1] Test database connection reliability and SSL configuration
- [ ] T160 [P1] [US1] Test frontend form validation alignment with database schema
- [ ] T161 [P1] [US1] Test error handling for database connection failures
- [ ] T162 [P1] [US1] Test duplicate email registration prevention
- [ ] T163 [P1] [US1] Test invalid input validation across all endpoints
- [ ] T164 [P1] [US3] Test cross-device data synchronization
- [ ] T165 [P1] [US1] Final system validation and acceptance testing

---

## Final System Validation & Acceptance Testing

- [ ] T165 [P1] [US1] Complete end-to-end user registration and login flow validation
- [ ] T166 [P1] [US2] Complete end-to-end task management flow validation
- [ ] T167 [P1] [US3] Complete cross-device data synchronization validation
- [ ] T168 [P1] [US1] Verify all functional requirements are met (FR-001 through FR-010)
- [ ] T169 [P1] [US1] Verify all success criteria are achieved (SC-001 through SC-007)
- [ ] T170 [P1] [US1] Complete final acceptance testing with all user stories validated