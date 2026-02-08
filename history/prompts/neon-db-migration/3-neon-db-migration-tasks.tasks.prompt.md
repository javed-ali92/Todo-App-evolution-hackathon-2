---
id: 3
title: neon-db-migration-tasks
stage: tasks
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: neon-db-migration
branch: 005-neon-db-migration
user: user
command: /sp.tasks
labels: ["database", "migration", "neon", "postgresql", "tasks", "implementation"]
links:
  spec: specs/005-neon-db-migration/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/005-neon-db-migration/tasks.md
tests:
 - backend/tests/test_neon_connection.py (to be created)
 - backend/tests/test_data_persistence.py (to be created)
 - backend/tests/test_task_isolation.py (to be created)
 - backend/tests/test_schema_integrity.py (to be created)
---

## Prompt

====================================
TASK GROUP 1 — DATABASE AUDIT
====================================

Task 1.1:
- Locate database engine creation file
- Identify current database URL usage
- Detect any SQLite / local DB references

Task 1.2:
- Locate session dependency
- Confirm how `Session` is injected into routes
- Identify duplicate or unused engines

====================================
TASK GROUP 2 — ENV & CONFIG FIX
====================================

Task 2.1:
- Verify `.env` loading mechanism
- Confirm DATABASE_URL is read from environment
- Remove any fallback to local DB

Task 2.2:
- Sanitize config
- Ensure only ONE database URL exists
- Ensure Neon URL is not overwritten

====================================
TASK GROUP 3 — NEON ENGINE SETUP
====================================

Task 3.1:
- Replace local engine with Neon PostgreSQL engine
- Use SQLModel `create_engine`
- Apply Neon-compatible connection args

Task 3.2:
- Refactor session dependency
- Ensure all routes use the Neon engine
- Validate session lifecycle

====================================
TASK GROUP 4 — SCHEMA INITIALIZATION
====================================

Task 4.1:
- Define / verify User model
- Enforce unique username & email
- Ensure password hashing compatibility

Task 4.2:
- Define / verify Task model
- Add foreign key to users
- Add ENUM for priority
- Add array field for tags

Task 4.3:
- Initialize database tables in Neon
- Run `SQLModel.metadata.create_all(engine)`
- Confirm schema creation

====================================
TASK GROUP 5 — AUTH DATA FLOW
====================================

Task 5.1:
- Fix signup route
- Save new users to Neon DB
- Validate insert success

Task 5.2:
- Fix login route
- Fetch user from Neon DB
- Validate credentials and JWT

====================================
TASK GROUP 6 — TASK DATA FLOW
====================================

Task 6.1:
- Fix task creation endpoint
- Bind task to authenticated user
- Persist task in Neon DB

Task 6.2:
- Fix task retrieval endpoint
- Fetch tasks from Neon DB
- Enforce user-based filtering

## Response snapshot

Generated comprehensive task breakdown with 90 tasks organized by 5 user stories from the specification, following strict checklist format with Task IDs, parallel markers, story labels, and file paths.

**Task Organization:**

Reorganized user's suggested task groups into user story-based phases:
- Phase 1: Setup (8 tasks) - Audit current state
- Phase 2: Foundational (6 tasks) - Database infrastructure
- Phase 3: User Story 1 - Database Connection (15 tasks, P1)
- Phase 4: User Story 2 - User Data Persistence (13 tasks, P1)
- Phase 5: User Story 3 - Task Data Persistence (15 tasks, P1)
- Phase 6: User Story 4 - Data Isolation (9 tasks, P2)
- Phase 7: User Story 5 - Schema Integrity (14 tasks, P2)
- Phase 8: Polish (10 tasks)

**Key Decisions:**

1. **User Story Organization**: Mapped user's task groups to spec user stories:
   - Task Group 1 (Audit) → Phase 1 (Setup)
   - Task Group 2 (Config Fix) → User Story 1 (Connection)
   - Task Group 3 (Engine Setup) → User Story 1 (Connection)
   - Task Group 4 (Schema Init) → User Story 5 (Schema Integrity)
   - Task Group 5 (Auth Flow) → User Story 2 (User Persistence)
   - Task Group 6 (Task Flow) → User Story 3 (Task Persistence)

2. **Validation Tasks Included**: Added validation tasks for each user story to verify data persists to Neon (per spec success criteria requiring verification)

3. **Strict Format Compliance**: All 90 tasks follow required format:
   - Checkbox: `- [ ]`
   - Task ID: T001-T090 (sequential)
   - [P] marker: 42 tasks marked as parallelizable
   - [Story] label: US1-US5 for user story tasks
   - File paths: Exact paths for all tasks

4. **Dependency Management**:
   - User Story 1 (Connection) MUST complete first
   - User Stories 2, 3, 5 can proceed in parallel after US1
   - User Story 4 (Isolation) should complete after US2 and US3

**Parallel Opportunities**: 42 tasks marked [P] can run in parallel, enabling efficient team execution

**MVP Scope**: Phase 1 + Phase 2 + Phase 3 (User Story 1 only) = 29 tasks for minimal viable migration

## Outcome

- ✅ Impact: Complete task breakdown enabling independent implementation and testing of each user story
- 🧪 Tests: 34 validation tasks across 4 test files to verify data persistence to Neon
- 📁 Files: Created tasks.md (90 tasks, ~500 lines)
- 🔁 Next prompts: `/sp.implement` to execute tasks in priority order
- 🧠 Reflection: Task organization by user story enables incremental delivery - each story can be completed, tested, and deployed independently. User Story 1 (Connection) is the critical foundation that must complete before other stories can proceed.

## Evaluation notes (flywheel)

- Failure modes observed: None - task generation completed successfully
- Graders run and results (PASS/FAIL): Format validation - ALL PASS (90/90 tasks follow checklist format)
- Prompt variant (if applicable): User provided task group suggestions which were reorganized by user story priority
- Next experiment (smallest change to try): Execute User Story 1 tasks (T015-T029) to establish Neon connection, then validate before proceeding to other stories
