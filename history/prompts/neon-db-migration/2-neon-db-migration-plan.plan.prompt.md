---
id: 2
title: neon-db-migration-plan
stage: plan
date: 2026-02-08
surface: agent
model: claude-sonnet-4-5
feature: neon-db-migration
branch: 005-neon-db-migration
user: user
command: /sp.plan
labels: ["database", "migration", "neon", "postgresql", "planning", "architecture"]
links:
  spec: specs/005-neon-db-migration/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/005-neon-db-migration/plan.md
 - specs/005-neon-db-migration/research.md
 - specs/005-neon-db-migration/data-model.md
 - specs/005-neon-db-migration/quickstart.md
 - specs/005-neon-db-migration/contracts/database-schema.sql
tests:
 - none (planning phase)
---

## Prompt

OBJECTIVE:
Migrate the Todo App backend from a local database to Neon Serverless PostgreSQL
and enforce Neon as the single source of truth for all user and task data.

====================================
PHASE 1 — AUDIT & ANALYSIS
====================================
1. Locate current database configuration
   - Identify engine creation
   - Identify session dependencies
   - Identify any SQLite or local DB usage

2. Verify `.env` loading
   - Confirm DATABASE_URL is read correctly
   - Confirm no fallback to local DB exists

3. Inspect models
   - Users model
   - Tasks model
   - Relationships and constraints

====================================
PHASE 2 — NEON DATABASE INTEGRATION
====================================
4. Replace local engine with Neon PostgreSQL engine
   - Use DATABASE_URL from environment
   - Remove hardcoded DB paths
   - Ensure SQLModel compatibility

5. Configure session dependency
   - Single engine
   - Proper session lifecycle
   - Safe connection handling

====================================
PHASE 3 — SCHEMA INITIALIZATION
====================================
6. Create tables in Neon PostgreSQL
   - Users table
   - Tasks table
   - Enums (priority)
   - Indexes and foreign keys

7. Validate schema creation
   - Confirm tables exist in Neon
   - Confirm constraints applied

====================================
PHASE 4 — AUTHENTICATION DATA FLOW
====================================
8. Fix signup flow
   - Persist user in Neon DB
   - Hash password correctly

9. Fix login flow
   - Read user from Neon DB
   - Validate credentials
   - Return JWT

====================================
PHASE 5 — TASK DATA FLOW
====================================
10. Fix task creation
    - Ensure task is saved in Neon DB
    - Attach task to authenticated user

11. Fix task retrieval
    - Fetch tasks from Neon DB
    - Enforce user-based filtering

12. Fix task update & delete
    - Operate only on user-owned tasks

====================================
PHASE 6 — VALIDATION & HARDENING
====================================
13. End-to-end testing
    - Signup → Neon DB
    - Login → Neon DB
    - Create task → Neon DB
    - Refresh → data persists

14. Remove legacy code
    - Delete unused local DB code
    - Confirm no duplicate

## Response snapshot

Created comprehensive implementation plan for Neon Serverless PostgreSQL database migration with complete Phase 0 (Research) and Phase 1 (Design & Contracts) artifacts.

**Planning Artifacts Created:**

1. **plan.md** (668 lines):
   - Technical context and constitution check (all passed)
   - Project structure with file-level annotations
   - Phase 0: 4 research tasks (R1-R4) with investigation areas
   - Phase 1: Data model, API contracts, quickstart guide
   - Phase 2: Implementation phases overview (5 phases)
   - Risk assessment (6 risks identified and mitigated)
   - Success metrics (functional, performance, quality)

2. **research.md** (Complete Phase 0):
   - R1: Current database configuration audit
     - Found SQLite fallback on line 12 of database.py
     - Verified Neon configuration is 95% ready
     - Decision: Remove SQLite fallback, fail-fast approach
   - R2: Neon PostgreSQL connection best practices
     - Current pool settings are optimal (size=5, max_overflow=10)
     - Decision: Use psycopg2-binary, keep current configuration
   - R3: Schema migration and validation patterns
     - Decision: Add startup validation, verify tables and constraints
   - R4: Data persistence testing strategies
     - Decision: Use same Neon instance with test data cleanup
     - Designed end-to-end and negative test scenarios

3. **data-model.md** (Complete Phase 1):
   - Entity: User (6 attributes, relationships, constraints, validation rules)
   - Entity: Task (11 attributes, state transitions, indexes)
   - Entity: Session (7 attributes, existing, no changes)
   - Entity relationship diagram
   - Data integrity rules and migration considerations

4. **quickstart.md** (Complete Phase 1):
   - 7-step verification process
   - Prerequisites checklist
   - Connection testing procedures
   - Schema verification steps
   - Data persistence testing
   - Troubleshooting guide (6 common issues)
   - Success criteria checklist (12 items)

5. **contracts/database-schema.sql** (Complete Phase 1):
   - Complete PostgreSQL schema (200+ lines)
   - 3 tables: user, task, session
   - Priority enum type
   - 10 indexes (including composite and partial)
   - 2 triggers for auto-updating timestamps
   - 2 views for active/completed tasks
   - 1 function for user task statistics
   - Comprehensive comments and documentation

**Key Findings:**
- Backend is 95% ready for Neon-only operation
- Only SQLite fallback removal and startup validation required
- No schema changes needed (SQLModel definitions are compatible)
- Estimated implementation effort: 2 hours
- Risk level: Low

**Constitution Check:** ✅ PASS - All requirements maintained, no API changes, no security changes

## Outcome

- ✅ Impact: Complete implementation plan with research, data model, contracts, and quickstart guide ready for task generation
- 🧪 Tests: Test strategies defined in research.md; actual tests will be created during implementation
- 📁 Files: Created 5 planning artifacts (plan.md, research.md, data-model.md, quickstart.md, database-schema.sql)
- 🔁 Next prompts: `/sp.tasks` to generate detailed task breakdown, then `/sp.implement` to execute tasks
- 🧠 Reflection: Planning revealed that infrastructure is already well-configured for Neon. The migration is primarily about removing safety fallbacks and adding validation, not rebuilding the database layer. This significantly reduces risk and implementation time.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning completed successfully with all required artifacts
- Graders run and results (PASS/FAIL): Constitution check - ALL PASS (5/5 categories)
- Prompt variant (if applicable): Standard /sp.plan workflow with user-provided phase breakdown
- Next experiment (smallest change to try): Execute /sp.tasks to generate actionable task breakdown from this plan
