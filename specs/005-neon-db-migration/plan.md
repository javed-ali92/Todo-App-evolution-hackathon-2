# Implementation Plan: Neon Serverless PostgreSQL Database Migration

**Branch**: `005-neon-db-migration` | **Date**: 2026-02-08 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-neon-db-migration/spec.md`

## Summary

Migrate the Todo App backend from potential local database usage to exclusive Neon Serverless PostgreSQL persistence. The backend infrastructure is already configured for Neon, but has a SQLite fallback that must be removed. This plan ensures all user and task data is persisted exclusively in Neon PostgreSQL, with no local database usage.

**Primary Requirement**: Enforce Neon PostgreSQL as the single source of truth for all data persistence operations.

**Technical Approach**: Audit existing database configuration, remove SQLite fallback, validate Neon connection on startup, ensure schema creation in Neon, and verify end-to-end data persistence through comprehensive testing.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: FastAPI 0.104+, SQLModel 0.0.14+, SQLAlchemy 2.0+, psycopg2-binary 2.9+ (PostgreSQL adapter)
**Storage**: Neon Serverless PostgreSQL (already configured in .env)
**Testing**: pytest, httpx (for API testing)
**Target Platform**: Linux/Windows server (development and production)
**Project Type**: Web application (FastAPI backend + Next.js frontend)
**Performance Goals**: Database connection within 5 seconds, query response under 200ms for typical operations
**Constraints**: Must maintain 100% data persistence to Neon, zero local database writes, backward compatible with existing API contracts
**Scale/Scope**: Multi-user application, estimated 100-1000 users, 10,000+ tasks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Spec-Driven Development Compliance
- [x] All development follows strict workflow: Write Spec → Generate Plan → Break into Tasks → Implement
- [x] No direct implementation without approved specs, plans, and tasks

### Architecture Compliance
- [x] Maintains monorepo structure: frontend/ (Next.js), backend/ (FastAPI), specs/, docker-compose.yml
- [x] Clear separation between frontend and backend components

### Technology Stack Compliance
- [x] Frontend uses Next.js 16+ (App Router), TypeScript, Better Auth (no changes required for this feature)
- [x] Backend uses Python FastAPI, SQLModel ORM
- [x] Database uses Neon Serverless PostgreSQL
- [x] Authentication uses Better Auth with JWT (no changes required for this feature)

### Security Compliance
- [x] All API routes require JWT token authentication (existing implementation preserved)
- [x] Backend verifies JWT token and extracts user ID (existing implementation preserved)
- [x] Backend compares token_user_id == url_user_id to prevent unauthorized access (existing implementation preserved)
- [x] Users can only access their own tasks (existing implementation preserved)

### API Contract Compliance
- [x] All API routes follow the specified contract (no changes to API endpoints):
  - GET /api/{user_id}/tasks
  - POST /api/{user_id}/tasks
  - GET /api/{user_id}/tasks/{id}
  - PUT /api/{user_id}/tasks/{id}
  - DELETE /api/{user_id}/tasks/{id}
  - PATCH /api/{user_id}/tasks/{id}/complete

**Constitution Check Result**: ✅ PASS - This feature maintains all constitutional requirements. No API changes, no security model changes, no architecture changes. Only database persistence layer is being hardened to enforce Neon-only usage.

## Project Structure

### Documentation (this feature)

```text
specs/005-neon-db-migration/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (to be created)
├── data-model.md        # Phase 1 output (to be created)
├── quickstart.md        # Phase 1 output (to be created)
├── contracts/           # Phase 1 output (to be created)
│   └── database-schema.sql
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   ├── database.py          # [MODIFY] Remove SQLite fallback, add validation
│   │   ├── dependencies.py      # [AUDIT] Verify session management
│   │   └── validation.py        # [CREATE] Add Neon connection validation
│   ├── models/
│   │   ├── user.py              # [AUDIT] Verify schema matches Neon requirements
│   │   ├── task.py              # [AUDIT] Verify schema matches Neon requirements
│   │   └── session.py           # [AUDIT] Verify session table schema
│   ├── api/
│   │   ├── auth.py              # [AUDIT] Verify data persistence flow
│   │   └── tasks.py             # [AUDIT] Verify data persistence flow
│   ├── services/
│   │   ├── auth_service.py      # [AUDIT] Verify database operations
│   │   └── task_service.py      # [AUDIT] Verify database operations
│   └── main.py                  # [MODIFY] Add startup validation
├── tests/
│   ├── test_neon_connection.py  # [CREATE] Neon connection tests
│   ├── test_data_persistence.py # [CREATE] End-to-end persistence tests
│   └── test_auth.py             # [AUDIT] Existing auth tests
├── .env                         # [AUDIT] Verify DATABASE_URL configuration
└── requirements.txt             # [AUDIT] Verify PostgreSQL dependencies

frontend/
└── [NO CHANGES REQUIRED]        # Frontend already configured correctly
```

## Phase 0: Research & Analysis

### Research Tasks

#### R1: Current Database Configuration Audit
**Objective**: Identify all database connection points and potential local database usage

**Investigation Areas**:
1. Analyze `backend/src/database/database.py`:
   - Document current engine creation logic
   - Identify SQLite fallback mechanism (line 12: `"sqlite:///./todo_app.db"`)
   - Review connection pooling configuration
   - Verify SSL parameter handling for Neon

2. Search for local database files:
   - Check for `*.db` files in backend directory
   - Check for `*.sqlite` files
   - Verify no hardcoded database paths exist

3. Analyze session management:
   - Review `get_session()` dependency in all API routes
   - Verify all routes use the same engine instance
   - Check for any direct database connections bypassing the engine

**Expected Findings**:
- SQLite fallback exists as safety mechanism
- All routes use centralized session dependency
- No direct database connections found
- Neon configuration is already present but not enforced

**Decision to Make**: Strategy for removing SQLite fallback while maintaining development safety

---

#### R2: Neon PostgreSQL Connection Best Practices
**Objective**: Research optimal configuration for Neon Serverless PostgreSQL with SQLModel

**Investigation Areas**:
1. Neon-specific connection parameters:
   - SSL mode requirements (already using `sslmode=require`)
   - Channel binding requirements (already using `channel_binding=require`)
   - Connection pooling recommendations for serverless
   - Timeout and retry strategies

2. SQLModel/SQLAlchemy with PostgreSQL:
   - Verify psycopg2-binary vs psycopg2 (binary recommended for ease)
   - Connection pool sizing for serverless (current: pool_size=5, max_overflow=10)
   - Pool pre-ping necessity (already enabled: `pool_pre_ping=True`)
   - Connection recycling (already set: `pool_recycle=300`)

3. Error handling patterns:
   - Connection failure detection
   - Graceful degradation strategies (or fail-fast approach)
   - Startup validation patterns

**Expected Findings**:
- Current configuration is already optimal for Neon
- psycopg2-binary is the correct choice
- Pool settings are appropriate for serverless
- Need to add startup validation to fail fast on misconfiguration

**Decision to Make**: Fail-fast vs graceful degradation on database connection failure

---

#### R3: Schema Migration and Validation Patterns
**Objective**: Research best practices for ensuring schema exists in Neon on startup

**Investigation Areas**:
1. SQLModel table creation:
   - Current approach: `SQLModel.metadata.create_all(engine)` in startup event
   - Idempotency of create_all (safe to run multiple times)
   - Verification that tables were created successfully

2. Schema validation approaches:
   - Query information_schema to verify tables exist
   - Verify constraints (foreign keys, unique constraints)
   - Validate enum types are created correctly

3. Migration strategies:
   - Alembic integration (out of scope per spec)
   - Manual schema verification scripts
   - Startup health checks

**Expected Findings**:
- `create_all()` is idempotent and safe
- Need to add post-creation validation
- Should verify foreign key constraints are enforced

**Decision to Make**: Level of schema validation required on startup

---

#### R4: Data Persistence Testing Strategies
**Objective**: Design comprehensive tests to verify data persists to Neon

**Investigation Areas**:
1. Test database setup:
   - Use same Neon instance or separate test database
   - Test data cleanup strategies
   - Isolation between test runs

2. End-to-end persistence tests:
   - User registration → verify in Neon
   - User login → verify read from Neon
   - Task CRUD → verify all operations persist
   - Application restart → verify data survives

3. Negative tests:
   - Verify no local .db files are created
   - Verify SQLite is not imported or used
   - Verify connection failures are detected

**Expected Findings**:
- Need separate test database or careful cleanup
- Should test application restart scenario
- Need file system monitoring to detect local database creation

**Decision to Make**: Test database strategy (shared Neon instance with cleanup vs separate test instance)

---

### Research Consolidation

**Output**: `research.md` document containing:
- Current state analysis with code references
- Neon configuration recommendations
- Schema validation approach
- Testing strategy
- Risk assessment and mitigation plans

## Phase 1: Design & Contracts

### Data Model

**Output**: `data-model.md`

#### Entity: User
**Purpose**: Represents a registered user account with authentication credentials

**Attributes**:
- `id` (integer, primary key, auto-increment): Unique identifier
- `username` (string, unique, 3-30 chars): User's display name
- `email` (string, unique, max 255 chars): User's email for login
- `hashed_password` (string, min 8 chars): Bcrypt-hashed password
- `created_at` (timestamp): Account creation time
- `updated_at` (timestamp): Last modification time

**Constraints**:
- UNIQUE constraint on username
- UNIQUE constraint on email
- NOT NULL on username, email, hashed_password

**Relationships**:
- One-to-many with Task (one user has many tasks)

**Validation Rules**:
- Username: 3-30 characters, alphanumeric
- Email: Valid email format
- Password: Minimum 8 characters (enforced at application layer)

**State Transitions**: None (users are created and remain active)

---

#### Entity: Task
**Purpose**: Represents a todo item belonging to a specific user

**Attributes**:
- `id` (integer, primary key, auto-increment): Unique identifier
- `user_id` (integer, foreign key → user.id, NOT NULL): Owner of the task
- `title` (string, 1-200 chars, NOT NULL): Task title
- `description` (string, optional): Detailed task description
- `due_date` (string, optional): Due date in ISO format
- `priority` (enum: High/Medium/Low, default Medium): Task priority
- `tags` (string, optional): Comma-separated tags
- `recursion_pattern` (string, optional, max 100 chars): Recurrence rule
- `completed` (boolean, default false): Completion status
- `created_at` (timestamp): Task creation time
- `updated_at` (timestamp): Last modification time

**Constraints**:
- FOREIGN KEY user_id REFERENCES user(id) ON DELETE CASCADE
- NOT NULL on user_id, title, completed
- CHECK constraint on priority enum values

**Relationships**:
- Many-to-one with User (many tasks belong to one user)

**Validation Rules**:
- Title: 1-200 characters, required
- Priority: Must be one of High, Medium, Low
- Tags: Stored as comma-separated string (JSON array in future)

**State Transitions**:
- Created → Incomplete (completed=false)
- Incomplete ↔ Complete (toggle via PATCH endpoint)
- Any state → Deleted (via DELETE endpoint)

---

#### Entity: Session (existing, no changes)
**Purpose**: Tracks active JWT sessions for logout functionality

**Attributes**:
- `id` (integer, primary key): Unique identifier
- `user_id` (integer, foreign key → user.id): Session owner
- `token_jti` (string, unique): JWT ID for token identification
- `token` (string): Hashed token value
- `expires_at` (timestamp): Token expiration time
- `revoked` (boolean, default false): Revocation status
- `created_at` (timestamp): Session creation time

**Note**: This entity already exists and requires no changes for Neon migration.

---

### API Contracts

**Output**: `contracts/database-schema.sql`

```sql
-- Neon PostgreSQL Database Schema
-- Generated for: 005-neon-db-migration
-- Date: 2026-02-08

-- Enable UUID extension (if needed for future enhancements)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(30) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on email for faster login queries
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);

-- Priority Enum Type
CREATE TYPE priority_enum AS ENUM ('High', 'Medium', 'Low');

-- Tasks Table
CREATE TABLE IF NOT EXISTS task (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date VARCHAR(50),  -- Stored as string for flexibility
    priority priority_enum NOT NULL DEFAULT 'Medium',
    tags TEXT,  -- Comma-separated tags
    recursion_pattern VARCHAR(100),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on user_id for faster task queries
CREATE INDEX IF NOT EXISTS idx_task_user_id ON task(user_id);

-- Create index on completed status for filtering
CREATE INDEX IF NOT EXISTS idx_task_completed ON task(completed);

-- Sessions Table (for JWT session management)
CREATE TABLE IF NOT EXISTS session (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    token_jti VARCHAR(255) NOT NULL UNIQUE,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on token_jti for faster session lookups
CREATE INDEX IF NOT EXISTS idx_session_token_jti ON session(token_jti);

-- Create index on user_id for faster session queries
CREATE INDEX IF NOT EXISTS idx_session_user_id ON session(user_id);

-- Trigger to update updated_at timestamp on user updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_updated_at BEFORE UPDATE ON "user"
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_task_updated_at BEFORE UPDATE ON task
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

---

### Quickstart Guide

**Output**: `quickstart.md`

```markdown
# Quickstart: Neon Database Migration

## Prerequisites

1. Neon PostgreSQL database provisioned
2. DATABASE_URL configured in `.env` file
3. Python 3.11+ installed
4. Backend dependencies installed (`pip install -r requirements.txt`)

## Verification Steps

### Step 1: Verify Environment Configuration

```bash
# Check that DATABASE_URL is set
cd backend
cat ../.env | grep DATABASE_URL

# Expected output:
# DATABASE_URL='postgresql://neondb_owner:...@ep-....neon.tech/neondb?sslmode=require'
```

### Step 2: Test Database Connection

```bash
# Run connection validation script
python -c "from src.database.database import engine; print('Connection successful!' if engine else 'Connection failed')"
```

### Step 3: Verify Schema Creation

```bash
# Start the backend server (creates tables on startup)
cd backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001

# Check logs for "Database tables created successfully!"
```

### Step 4: Test Data Persistence

```bash
# Run end-to-end persistence tests
pytest tests/test_data_persistence.py -v

# Expected: All tests pass, confirming data persists to Neon
```

### Step 5: Verify No Local Database Files

```bash
# Check for local database files (should return nothing)
find backend -name "*.db" -o -name "*.sqlite"

# Expected: No output (no local database files)
```

## Troubleshooting

### Connection Timeout
- **Symptom**: "Connection timeout" error on startup
- **Solution**: Check network connectivity to Neon, verify DATABASE_URL is correct

### SSL Certificate Error
- **Symptom**: "SSL certificate verify failed"
- **Solution**: Ensure `sslmode=require` is in DATABASE_URL

### Table Creation Failed
- **Symptom**: "Table does not exist" errors
- **Solution**: Check Neon database permissions, verify user has CREATE TABLE privilege

### Data Not Persisting
- **Symptom**: Data disappears after restart
- **Solution**: Verify DATABASE_URL is being read (not using SQLite fallback)

## Success Criteria

✅ Backend starts without errors
✅ Log shows "Database tables created successfully!"
✅ No local .db files exist
✅ User registration creates record in Neon
✅ Task creation persists to Neon
✅ Data survives application restart
```

---

### Agent Context Update

**Action**: Run `.specify/scripts/powershell/update-agent-context.ps1 -AgentType claude`

**Technologies to Add**:
- Neon Serverless PostgreSQL
- psycopg2-binary (PostgreSQL adapter)
- SQLAlchemy connection pooling
- Database validation patterns

**Note**: This will update the Claude-specific context file with Neon-related information for future reference.

---

## Phase 2: Implementation Phases (Overview Only)

**Note**: Detailed task breakdown will be created by `/sp.tasks` command. This section provides high-level implementation phases for planning purposes.

### Phase 2.1: Database Configuration Hardening
- Remove SQLite fallback from database.py
- Add DATABASE_URL validation on import
- Implement fail-fast behavior if DATABASE_URL is missing or invalid
- Add connection validation function

### Phase 2.2: Startup Validation
- Add Neon connection test on application startup
- Verify tables exist after creation
- Validate foreign key constraints are enforced
- Log database connection details (without exposing credentials)

### Phase 2.3: Schema Verification
- Create schema validation utility
- Verify all required tables exist
- Verify all required columns exist with correct types
- Verify indexes are created

### Phase 2.4: Data Persistence Testing
- Create end-to-end persistence tests
- Test user registration → Neon persistence
- Test user login → Neon read
- Test task CRUD → Neon persistence
- Test application restart → data survives

### Phase 2.5: Cleanup and Documentation
- Remove any local database files
- Update documentation with Neon-specific notes
- Add troubleshooting guide
- Create deployment checklist

---

## Risk Assessment

### High Priority Risks

**R1: DATABASE_URL Not Loaded**
- **Risk**: Environment variable not read correctly, falls back to SQLite
- **Impact**: Data saved locally instead of Neon
- **Mitigation**: Add explicit validation on startup, fail if DATABASE_URL is missing
- **Detection**: Check for .db files, verify connection string in logs

**R2: Connection Pool Exhaustion**
- **Risk**: Too many concurrent connections to Neon
- **Impact**: Connection timeouts, failed requests
- **Mitigation**: Current pool settings (size=5, max_overflow=10) are appropriate; monitor connection usage
- **Detection**: Connection timeout errors in logs

**R3: Schema Creation Failure**
- **Risk**: Tables not created in Neon due to permissions or network issues
- **Impact**: Application fails on first data operation
- **Mitigation**: Add post-creation validation, fail fast on startup if tables don't exist
- **Detection**: "Table does not exist" errors

### Medium Priority Risks

**R4: SSL Certificate Issues**
- **Risk**: SSL verification fails in certain environments
- **Impact**: Cannot connect to Neon
- **Mitigation**: Ensure sslmode=require is in connection string, document SSL requirements
- **Detection**: SSL certificate errors in logs

**R5: Data Type Mismatches**
- **Risk**: SQLModel types don't map correctly to PostgreSQL
- **Impact**: Data corruption or insertion failures
- **Mitigation**: Verify schema matches expected PostgreSQL types, add validation tests
- **Detection**: Type conversion errors, constraint violations

### Low Priority Risks

**R6: Connection Latency**
- **Risk**: Network latency to Neon affects performance
- **Impact**: Slower response times
- **Mitigation**: Use connection pooling (already configured), consider caching for read-heavy operations (future enhancement)
- **Detection**: Slow query logs, performance monitoring

---

## Dependencies

### External Dependencies
- **Neon PostgreSQL Service**: Database must be provisioned and accessible
- **Network Connectivity**: Application server must reach Neon endpoints
- **DATABASE_URL Configuration**: Must be set in .env file

### Internal Dependencies
- **Existing Models**: User, Task, Session models already defined correctly
- **Existing API Routes**: No changes required to API endpoints
- **Existing Authentication**: JWT verification continues to work unchanged

### Python Package Dependencies
- `fastapi>=0.104.0`: Web framework
- `sqlmodel>=0.0.14`: ORM layer
- `sqlalchemy>=2.0.0`: Database toolkit
- `psycopg2-binary>=2.9.0`: PostgreSQL adapter
- `python-dotenv>=1.0.0`: Environment variable loading
- `bcrypt>=4.0.0`: Password hashing

---

## Success Metrics

### Functional Metrics
- ✅ 100% of user registrations persist to Neon (verified by direct database query)
- ✅ 100% of task operations persist to Neon (verified by direct database query)
- ✅ Zero local database files created (verified by file system check)
- ✅ Application starts successfully with Neon connection (verified by startup logs)
- ✅ Data survives application restart (verified by end-to-end test)

### Performance Metrics
- ✅ Database connection established within 5 seconds of startup
- ✅ User registration completes within 1 second
- ✅ Task creation completes within 500ms
- ✅ Task list retrieval completes within 200ms for typical user (< 100 tasks)

### Quality Metrics
- ✅ All existing tests continue to pass
- ✅ New persistence tests achieve 100% pass rate
- ✅ No SQLite imports remain in codebase
- ✅ Schema validation passes on startup
- ✅ Foreign key constraints are enforced

---

## Next Steps

1. **Complete Phase 0 Research**: Execute research tasks R1-R4, consolidate findings in `research.md`
2. **Review Research Findings**: Validate assumptions and decisions with stakeholders
3. **Finalize Data Model**: Review `data-model.md` for accuracy
4. **Generate Tasks**: Run `/sp.tasks` to create detailed implementation task breakdown
5. **Begin Implementation**: Execute tasks in priority order (P1 first)

---

## Notes

- **No API Changes**: This migration is transparent to the frontend; no API contract changes required
- **No Authentication Changes**: JWT verification and session management remain unchanged
- **Backward Compatibility**: Existing data operations continue to work identically
- **Infrastructure Only**: This is purely an infrastructure change to enforce Neon usage
- **Testing Critical**: Comprehensive testing is essential to verify data persistence

---

**Plan Status**: ✅ Complete - Ready for Phase 0 Research

**Constitution Re-Check**: ✅ PASS - All constitutional requirements maintained
