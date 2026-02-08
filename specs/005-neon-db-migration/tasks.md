# Tasks: Neon Serverless PostgreSQL Database Migration

**Input**: Design documents from `/specs/005-neon-db-migration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Tests are included as validation tasks to verify data persistence (per spec requirements)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `backend/tests/`, `frontend/src/`
- This feature only modifies backend (no frontend changes)

---

## Phase 1: Setup (Audit & Documentation)

**Purpose**: Audit current state and prepare for migration

- [ ] T001 Audit current database configuration in backend/src/database/database.py
- [ ] T002 [P] Audit session dependency usage in backend/src/database/dependencies.py
- [ ] T003 [P] Audit User model schema in backend/src/models/user.py
- [ ] T004 [P] Audit Task model schema in backend/src/models/task.py
- [ ] T005 [P] Audit Session model schema in backend/src/models/session.py
- [ ] T006 Search for local database files (*.db, *.sqlite) in backend directory
- [ ] T007 Verify DATABASE_URL is loaded from .env in backend/src/database/database.py
- [ ] T008 Document current engine configuration and connection pooling settings

**Checkpoint**: Audit complete - understand current state before making changes

---

## Phase 2: Foundational (Database Connection Infrastructure)

**Purpose**: Core database connection setup that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T009 Verify psycopg2-binary is in backend/requirements.txt (PostgreSQL adapter)
- [ ] T010 Verify python-dotenv is in backend/requirements.txt (environment variable loading)
- [ ] T011 Verify SQLModel and SQLAlchemy versions are compatible with PostgreSQL in backend/requirements.txt
- [ ] T012 Create database validation module in backend/src/database/validation.py
- [ ] T013 Implement connection test function in backend/src/database/validation.py
- [ ] T014 Implement schema validation function in backend/src/database/validation.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Database Connection Establishment (Priority: P1) 🎯 MVP

**Goal**: Ensure application connects exclusively to Neon PostgreSQL with no SQLite fallback

**Independent Test**: Start application and verify connection string points to Neon PostgreSQL, not local database. Verify no .db files are created.

### Implementation for User Story 1

- [ ] T015 [US1] Remove SQLite fallback from DATABASE_URL in backend/src/database/database.py line 12
- [ ] T016 [US1] Add DATABASE_URL validation on import in backend/src/database/database.py
- [ ] T017 [US1] Raise clear error if DATABASE_URL is missing in backend/src/database/database.py
- [ ] T018 [US1] Raise clear error if DATABASE_URL is invalid format in backend/src/database/database.py
- [ ] T019 [US1] Add startup validation call in backend/src/main.py on_startup event
- [ ] T020 [US1] Call connection test function on startup in backend/src/main.py
- [ ] T021 [US1] Log database connection details (sanitized) on startup in backend/src/main.py
- [ ] T022 [US1] Add error handling for connection failures in backend/src/main.py

### Validation for User Story 1

- [ ] T023 [US1] Create connection validation test in backend/tests/test_neon_connection.py
- [ ] T024 [P] [US1] Test DATABASE_URL is read correctly in backend/tests/test_neon_connection.py
- [ ] T025 [P] [US1] Test connection to Neon succeeds in backend/tests/test_neon_connection.py
- [ ] T026 [P] [US1] Test missing DATABASE_URL raises error in backend/tests/test_neon_connection.py
- [ ] T027 [P] [US1] Test invalid DATABASE_URL raises error in backend/tests/test_neon_connection.py
- [ ] T028 [US1] Verify no local .db files exist after startup in backend/tests/test_neon_connection.py
- [ ] T029 [US1] Verify SQLite is not imported in database module in backend/tests/test_neon_connection.py

**Checkpoint**: At this point, application connects exclusively to Neon PostgreSQL with proper validation

---

## Phase 4: User Story 2 - User Data Persistence (Priority: P1)

**Goal**: Ensure user registration and login data persists to Neon PostgreSQL

**Independent Test**: Create user account, restart application, verify user can still log in with same credentials

### Implementation for User Story 2

- [ ] T030 [US2] Verify User model has correct constraints in backend/src/models/user.py
- [ ] T031 [US2] Verify password hashing works with PostgreSQL in backend/src/services/auth_service.py
- [ ] T032 [US2] Verify user registration saves to Neon in backend/src/api/auth.py register endpoint
- [ ] T033 [US2] Verify user login reads from Neon in backend/src/api/auth.py login endpoint
- [ ] T034 [US2] Verify duplicate email check queries Neon in backend/src/api/auth.py register endpoint
- [ ] T035 [US2] Verify duplicate username check queries Neon in backend/src/api/auth.py register endpoint

### Validation for User Story 2

- [ ] T036 [US2] Create user persistence test file in backend/tests/test_data_persistence.py
- [ ] T037 [P] [US2] Test user registration persists to Neon in backend/tests/test_data_persistence.py
- [ ] T038 [P] [US2] Test user login reads from Neon in backend/tests/test_data_persistence.py
- [ ] T039 [P] [US2] Test user data survives application restart in backend/tests/test_data_persistence.py
- [ ] T040 [P] [US2] Test duplicate email rejection from Neon in backend/tests/test_data_persistence.py
- [ ] T041 [P] [US2] Test duplicate username rejection from Neon in backend/tests/test_data_persistence.py
- [ ] T042 [US2] Query Neon directly to verify user record exists in backend/tests/test_data_persistence.py

**Checkpoint**: At this point, user authentication data persists reliably to Neon PostgreSQL

---

## Phase 5: User Story 3 - Task Data Persistence (Priority: P1)

**Goal**: Ensure task CRUD operations persist to Neon PostgreSQL

**Independent Test**: Create task, log out, log back in, verify task still exists with correct data

### Implementation for User Story 3

- [ ] T043 [US3] Verify Task model has correct constraints in backend/src/models/task.py
- [ ] T044 [US3] Verify task creation saves to Neon in backend/src/api/tasks.py create_new_task endpoint
- [ ] T045 [US3] Verify task retrieval reads from Neon in backend/src/api/tasks.py read_tasks endpoint
- [ ] T046 [US3] Verify task update persists to Neon in backend/src/api/tasks.py update_existing_task endpoint
- [ ] T047 [US3] Verify task deletion removes from Neon in backend/src/api/tasks.py delete_existing_task endpoint
- [ ] T048 [US3] Verify task completion toggle persists to Neon in backend/src/api/tasks.py toggle_task_complete endpoint
- [ ] T049 [US3] Verify foreign key relationship to users in backend/src/models/task.py

### Validation for User Story 3

- [ ] T050 [P] [US3] Test task creation persists to Neon in backend/tests/test_data_persistence.py
- [ ] T051 [P] [US3] Test task retrieval reads from Neon in backend/tests/test_data_persistence.py
- [ ] T052 [P] [US3] Test task update persists to Neon in backend/tests/test_data_persistence.py
- [ ] T053 [P] [US3] Test task deletion removes from Neon in backend/tests/test_data_persistence.py
- [ ] T054 [P] [US3] Test task completion toggle persists to Neon in backend/tests/test_data_persistence.py
- [ ] T055 [P] [US3] Test task data survives application restart in backend/tests/test_data_persistence.py
- [ ] T056 [US3] Query Neon directly to verify task record exists in backend/tests/test_data_persistence.py
- [ ] T057 [US3] Test task foreign key constraint is enforced in backend/tests/test_data_persistence.py

**Checkpoint**: At this point, all task operations persist reliably to Neon PostgreSQL

---

## Phase 6: User Story 4 - Data Isolation and Security (Priority: P2)

**Goal**: Verify data isolation is enforced (users can only access their own data)

**Independent Test**: Create two users, have each create tasks, verify User A cannot access User B's tasks

### Implementation for User Story 4

- [ ] T058 [US4] Verify user_id filtering in task queries in backend/src/services/task_service.py
- [ ] T059 [US4] Verify token_user_id validation in task endpoints in backend/src/api/tasks.py
- [ ] T060 [US4] Verify unauthorized access is blocked in backend/src/api/tasks.py
- [ ] T061 [US4] Verify session validation requires re-authentication in backend/src/auth/jwt_handler.py

### Validation for User Story 4

- [ ] T062 [P] [US4] Test user can only see their own tasks in backend/tests/test_task_isolation.py
- [ ] T063 [P] [US4] Test user cannot access another user's tasks in backend/tests/test_task_isolation.py
- [ ] T064 [P] [US4] Test unauthorized API access is denied in backend/tests/test_task_isolation.py
- [ ] T065 [P] [US4] Test expired session requires re-authentication in backend/tests/test_task_isolation.py
- [ ] T066 [US4] Test task queries filter by user_id in Neon in backend/tests/test_task_isolation.py

**Checkpoint**: At this point, data isolation is verified and enforced

---

## Phase 7: User Story 5 - Database Schema Integrity (Priority: P2)

**Goal**: Verify database schema has proper constraints and relationships

**Independent Test**: Attempt to create invalid records (duplicate emails, tasks without user_id) and verify database rejects them

### Implementation for User Story 5

- [ ] T067 [US5] Verify users table schema in Neon matches spec in backend/src/database/validation.py
- [ ] T068 [US5] Verify tasks table schema in Neon matches spec in backend/src/database/validation.py
- [ ] T069 [US5] Verify session table schema in Neon matches spec in backend/src/database/validation.py
- [ ] T070 [US5] Verify unique constraints on username and email in backend/src/database/validation.py
- [ ] T071 [US5] Verify foreign key constraints exist in backend/src/database/validation.py
- [ ] T072 [US5] Verify priority enum type exists in Neon in backend/src/database/validation.py
- [ ] T073 [US5] Add schema validation to startup sequence in backend/src/main.py

### Validation for User Story 5

- [ ] T074 [P] [US5] Test unique constraint on email is enforced in backend/tests/test_schema_integrity.py
- [ ] T075 [P] [US5] Test unique constraint on username is enforced in backend/tests/test_schema_integrity.py
- [ ] T076 [P] [US5] Test foreign key constraint on task.user_id is enforced in backend/tests/test_schema_integrity.py
- [ ] T077 [P] [US5] Test priority enum values are enforced in backend/tests/test_schema_integrity.py
- [ ] T078 [P] [US5] Test NOT NULL constraints are enforced in backend/tests/test_schema_integrity.py
- [ ] T079 [US5] Query information_schema to verify all tables exist in backend/tests/test_schema_integrity.py
- [ ] T080 [US5] Query information_schema to verify all constraints exist in backend/tests/test_schema_integrity.py

**Checkpoint**: At this point, schema integrity is verified and enforced

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Cleanup, documentation, and final validation

- [ ] T081 [P] Delete any local database files (*.db, *.sqlite) from backend directory
- [ ] T082 [P] Update backend README with Neon configuration instructions
- [ ] T083 [P] Add troubleshooting section to documentation
- [ ] T084 Run all tests to verify 100% pass rate with pytest backend/tests/ -v
- [ ] T085 Verify quickstart.md validation steps all pass
- [ ] T086 [P] Add logging for database operations in backend/src/database/database.py
- [ ] T087 [P] Add performance monitoring for query times in backend/src/database/database.py
- [ ] T088 Verify no SQLite imports remain in codebase with grep -r "sqlite" backend/src/
- [ ] T089 Verify DATABASE_URL is used consistently with grep -r "DATABASE_URL" backend/src/
- [ ] T090 Create deployment checklist based on quickstart.md

**Checkpoint**: Migration complete and production-ready

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User Story 1 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 2 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 3 (P1): Can start after Foundational - No dependencies on other stories
  - User Story 4 (P2): Can start after Foundational - Should verify after US2 and US3 are complete
  - User Story 5 (P2): Can start after Foundational - Independent validation
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation for all data persistence - MUST complete first
- **User Story 2 (P1)**: Depends on US1 (connection must work) - Can run in parallel with US3
- **User Story 3 (P1)**: Depends on US1 (connection must work) - Can run in parallel with US2
- **User Story 4 (P2)**: Depends on US2 and US3 (needs data to verify isolation)
- **User Story 5 (P2)**: Depends on US1 (connection must work) - Can run in parallel with US2/US3

### Within Each User Story

- Implementation tasks before validation tasks
- Validation tasks marked [P] can run in parallel
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T002-T005 can run in parallel (different files)
- **Phase 2 (Foundational)**: T009-T011 can run in parallel (different files)
- **User Story 1**: T024-T027 validation tests can run in parallel
- **User Story 2**: T037-T041 validation tests can run in parallel
- **User Story 3**: T050-T055 validation tests can run in parallel
- **User Story 4**: T062-T065 validation tests can run in parallel
- **User Story 5**: T074-T078 validation tests can run in parallel
- **Phase 8 (Polish)**: T081-T083, T086-T087 can run in parallel

**After Foundational Phase**: User Stories 2, 3, and 5 can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all validation tests for User Story 1 together:
Task: "Test DATABASE_URL is read correctly in backend/tests/test_neon_connection.py"
Task: "Test connection to Neon succeeds in backend/tests/test_neon_connection.py"
Task: "Test missing DATABASE_URL raises error in backend/tests/test_neon_connection.py"
Task: "Test invalid DATABASE_URL raises error in backend/tests/test_neon_connection.py"
```

---

## Parallel Example: User Story 2

```bash
# Launch all validation tests for User Story 2 together:
Task: "Test user registration persists to Neon in backend/tests/test_data_persistence.py"
Task: "Test user login reads from Neon in backend/tests/test_data_persistence.py"
Task: "Test user data survives application restart in backend/tests/test_data_persistence.py"
Task: "Test duplicate email rejection from Neon in backend/tests/test_data_persistence.py"
Task: "Test duplicate username rejection from Neon in backend/tests/test_data_persistence.py"
```

---

## Parallel Example: User Story 3

```bash
# Launch all validation tests for User Story 3 together:
Task: "Test task creation persists to Neon in backend/tests/test_data_persistence.py"
Task: "Test task retrieval reads from Neon in backend/tests/test_data_persistence.py"
Task: "Test task update persists to Neon in backend/tests/test_data_persistence.py"
Task: "Test task deletion removes from Neon in backend/tests/test_data_persistence.py"
Task: "Test task completion toggle persists to Neon in backend/tests/test_data_persistence.py"
Task: "Test task data survives application restart in backend/tests/test_data_persistence.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Audit)
2. Complete Phase 2: Foundational (Database infrastructure)
3. Complete Phase 3: User Story 1 (Database Connection)
4. **STOP and VALIDATE**: Test connection works, no SQLite fallback
5. Deploy/demo if ready

### Incremental Delivery (Recommended)

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Verify connection (MVP!)
3. Add User Story 2 → Test independently → Verify user persistence
4. Add User Story 3 → Test independently → Verify task persistence
5. Add User Story 4 → Test independently → Verify data isolation
6. Add User Story 5 → Test independently → Verify schema integrity
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Database Connection) - MUST complete first
3. After User Story 1 completes:
   - Developer A: User Story 2 (User Persistence)
   - Developer B: User Story 3 (Task Persistence)
   - Developer C: User Story 5 (Schema Integrity)
4. After US2 and US3 complete:
   - Any developer: User Story 4 (Data Isolation)
5. Stories complete and integrate independently

---

## Task Summary

**Total Tasks**: 90 tasks

**Tasks by Phase**:
- Phase 1 (Setup): 8 tasks
- Phase 2 (Foundational): 6 tasks
- Phase 3 (User Story 1): 15 tasks (8 implementation + 7 validation)
- Phase 4 (User Story 2): 13 tasks (6 implementation + 7 validation)
- Phase 5 (User Story 3): 15 tasks (7 implementation + 8 validation)
- Phase 6 (User Story 4): 9 tasks (4 implementation + 5 validation)
- Phase 7 (User Story 5): 14 tasks (7 implementation + 7 validation)
- Phase 8 (Polish): 10 tasks

**Parallel Opportunities**: 42 tasks marked [P] can run in parallel

**Independent Test Criteria**:
- US1: Start app, verify Neon connection, no .db files
- US2: Create user, restart app, login succeeds
- US3: Create task, restart app, task still exists
- US4: Two users cannot access each other's tasks
- US5: Invalid data is rejected by database constraints

**Suggested MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Validation tasks verify data persists to Neon (not local database)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- User Story 1 MUST complete before other stories (establishes connection)
- User Stories 2, 3, 5 can proceed in parallel after US1
- User Story 4 should complete after US2 and US3 (needs data to verify isolation)
