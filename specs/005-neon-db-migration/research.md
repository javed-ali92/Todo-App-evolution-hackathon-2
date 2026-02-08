# Research: Neon Serverless PostgreSQL Database Migration

**Feature**: 005-neon-db-migration
**Date**: 2026-02-08
**Status**: Complete

## Executive Summary

This research document consolidates findings from auditing the current database configuration and researching best practices for Neon Serverless PostgreSQL integration. The backend is already configured for Neon but has a SQLite fallback that must be removed to ensure exclusive Neon usage.

**Key Finding**: The infrastructure is 95% ready for Neon-only operation. Only the SQLite fallback removal and startup validation are required.

---

## R1: Current Database Configuration Audit

### Current State Analysis

**File**: `backend/src/database/database.py`

**Current Engine Creation Logic** (lines 12-34):
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")  # ⚠️ SQLite fallback exists
```

**Findings**:
1. ✅ Neon connection string is properly configured in `.env`
2. ⚠️ SQLite fallback exists as default value (line 12)
3. ✅ SSL parameters are automatically added for Neon connections (lines 15-21)
4. ✅ Connection pooling is configured appropriately:
   - `pool_size=5`: Reasonable for serverless
   - `max_overflow=10`: Allows burst capacity
   - `pool_pre_ping=True`: Validates connections before use
   - `pool_recycle=300`: Recycles connections every 5 minutes
5. ✅ Connection timeout is set to 10 seconds (line 33)

**Session Management Analysis**:
- All API routes use `get_session()` dependency
- Single engine instance shared across all routes
- No direct database connections found
- Session lifecycle properly managed with context manager

**Local Database Files**:
- Checked for `*.db` and `*.sqlite` files
- Found: `todo_app.db` (likely from previous local testing)
- Action Required: Delete local database files after migration

**Code References**:
- Engine creation: `backend/src/database/database.py:24-35`
- Session dependency: `backend/src/database/dependencies.py:6-14`
- API route usage: `backend/src/api/auth.py:12-14`, `backend/src/api/tasks.py:16-18`

### Decision: Remove SQLite Fallback

**Strategy**: Fail-fast approach
- Remove default SQLite fallback
- Raise clear error if DATABASE_URL is missing
- Validate DATABASE_URL format on startup
- Log connection details (without credentials) for debugging

**Rationale**:
- Fail-fast prevents silent data loss to local database
- Clear error messages aid troubleshooting
- Production systems should never fall back to SQLite
- Development environments must have DATABASE_URL configured

---

## R2: Neon PostgreSQL Connection Best Practices

### Neon-Specific Configuration

**SSL Requirements**:
- ✅ Current: `sslmode=require` (automatically added)
- ✅ Current: `channel_binding=require` (in .env connection string)
- Recommendation: Keep current SSL configuration

**Connection Pooling for Serverless**:
- ✅ Current pool_size=5 is optimal for Neon
- ✅ Current max_overflow=10 provides adequate burst capacity
- ✅ pool_pre_ping=True prevents stale connection errors
- ✅ pool_recycle=300 (5 minutes) aligns with Neon's connection lifecycle
- Recommendation: No changes needed

**Timeout Strategy**:
- ✅ Current connect_timeout=10 seconds is appropriate
- Recommendation: Add query timeout for long-running queries (future enhancement)

### SQLModel/SQLAlchemy with PostgreSQL

**PostgreSQL Adapter**:
- Decision: Use `psycopg2-binary` (not `psycopg2`)
- Rationale: Binary version includes compiled C libraries, easier installation
- Current Status: Needs verification in requirements.txt

**Connection Pool Behavior**:
- QueuePool is appropriate for web applications
- Pre-ping ensures connections are valid before use
- Connection recycling prevents stale connections

### Error Handling Strategy

**Decision**: Fail-fast on connection failure
- Application should not start if database is unreachable
- Clear error messages for common issues:
  - Missing DATABASE_URL
  - Invalid connection string format
  - Network connectivity issues
  - SSL certificate problems
  - Authentication failures

**Rationale**:
- Prevents silent failures
- Forces proper configuration
- Easier debugging in production
- Aligns with 12-factor app principles

---

## R3: Schema Migration and Validation Patterns

### SQLModel Table Creation

**Current Approach**: `SQLModel.metadata.create_all(engine)` in startup event

**Analysis**:
- ✅ Idempotent: Safe to run multiple times
- ✅ Creates tables if they don't exist
- ✅ Does not modify existing tables
- ⚠️ No validation that tables were created successfully
- ⚠️ No verification of constraints

**Recommendation**: Add post-creation validation

### Schema Validation Approach

**Decision**: Implement startup validation checks

**Validation Steps**:
1. Verify connection to Neon
2. Run `create_all()` to ensure tables exist
3. Query `information_schema.tables` to verify tables were created
4. Verify foreign key constraints exist
5. Verify unique constraints exist
6. Log validation results

**Implementation Strategy**:
```python
def validate_schema(engine):
    """Validate that all required tables and constraints exist"""
    with Session(engine) as session:
        # Check tables exist
        result = session.exec(text("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('user', 'task', 'session')
        """))
        tables = [row[0] for row in result]

        if len(tables) != 3:
            raise RuntimeError(f"Missing tables. Found: {tables}")

        # Check foreign keys exist
        result = session.exec(text("""
            SELECT constraint_name FROM information_schema.table_constraints
            WHERE constraint_type = 'FOREIGN KEY'
            AND table_name IN ('task', 'session')
        """))
        fks = [row[0] for row in result]

        if len(fks) < 2:
            raise RuntimeError(f"Missing foreign keys. Found: {fks}")
```

**Level of Validation**: Medium
- Verify tables exist
- Verify foreign keys exist
- Skip column-level validation (trust SQLModel)
- Skip index validation (nice-to-have, not critical)

---

## R4: Data Persistence Testing Strategies

### Test Database Strategy

**Decision**: Use same Neon instance with test data cleanup

**Rationale**:
- Separate test database adds complexity
- Neon free tier may limit number of databases
- Cleanup strategy is straightforward
- Mirrors production environment more closely

**Cleanup Strategy**:
```python
@pytest.fixture(autouse=True)
def cleanup_test_data():
    """Clean up test data after each test"""
    yield
    # Delete test users (cascade will delete tasks and sessions)
    with Session(engine) as session:
        test_users = session.exec(
            select(User).where(User.email.like('%@test.example.com'))
        ).all()
        for user in test_users:
            session.delete(user)
        session.commit()
```

### End-to-End Persistence Tests

**Test Scenarios**:

1. **User Registration Persistence**:
   - Create user via API
   - Query Neon directly to verify user exists
   - Verify password is hashed
   - Verify timestamps are set

2. **User Login Persistence**:
   - Register user
   - Login with credentials
   - Verify JWT token is issued
   - Verify session is created in Neon

3. **Task CRUD Persistence**:
   - Create task via API
   - Query Neon to verify task exists
   - Update task via API
   - Verify update persisted to Neon
   - Delete task via API
   - Verify task removed from Neon

4. **Application Restart Simulation**:
   - Create user and tasks
   - Simulate restart (close all connections)
   - Reconnect and verify data still exists
   - Verify user can login
   - Verify tasks are retrieved

### Negative Tests

**Test Scenarios**:

1. **No Local Database Files**:
   ```python
   def test_no_local_database_files():
       """Verify no .db or .sqlite files are created"""
       db_files = list(Path('backend').rglob('*.db'))
       sqlite_files = list(Path('backend').rglob('*.sqlite'))
       assert len(db_files) == 0, f"Found local database files: {db_files}"
       assert len(sqlite_files) == 0, f"Found SQLite files: {sqlite_files}"
   ```

2. **SQLite Not Imported**:
   ```python
   def test_sqlite_not_used():
       """Verify SQLite is not imported in database module"""
       with open('backend/src/database/database.py') as f:
           content = f.read()
       assert 'sqlite' not in content.lower(), "SQLite reference found in database.py"
   ```

3. **Connection Failure Detection**:
   ```python
   def test_invalid_database_url_fails():
       """Verify application fails with invalid DATABASE_URL"""
       os.environ['DATABASE_URL'] = 'invalid://connection'
       with pytest.raises(Exception):
           from src.database.database import engine
   ```

---

## Risk Assessment and Mitigation

### High Priority Risks

**R1: DATABASE_URL Not Loaded**
- **Mitigation**: Add explicit validation, fail if missing
- **Detection**: Startup validation, log connection string (sanitized)
- **Status**: Addressed in implementation plan

**R2: Connection Pool Exhaustion**
- **Mitigation**: Current pool settings are appropriate
- **Detection**: Monitor connection usage, add logging
- **Status**: Low risk with current configuration

**R3: Schema Creation Failure**
- **Mitigation**: Add post-creation validation
- **Detection**: Startup validation checks
- **Status**: Addressed in implementation plan

### Medium Priority Risks

**R4: SSL Certificate Issues**
- **Mitigation**: Document SSL requirements, ensure sslmode=require
- **Detection**: SSL errors in logs
- **Status**: Already configured correctly

**R5: Data Type Mismatches**
- **Mitigation**: Verify schema with validation tests
- **Detection**: Type conversion errors
- **Status**: Low risk, SQLModel handles type mapping

---

## Technology Decisions

### PostgreSQL Adapter
**Decision**: psycopg2-binary
**Alternatives Considered**: psycopg2, asyncpg
**Rationale**: Binary version is easier to install, synchronous API matches current code

### Connection Pooling
**Decision**: Keep current QueuePool configuration
**Alternatives Considered**: NullPool (no pooling), StaticPool
**Rationale**: QueuePool is standard for web applications, current settings are optimal

### Validation Strategy
**Decision**: Fail-fast with startup validation
**Alternatives Considered**: Graceful degradation, lazy validation
**Rationale**: Fail-fast prevents silent failures, easier debugging

### Testing Strategy
**Decision**: Same Neon instance with cleanup
**Alternatives Considered**: Separate test database, in-memory SQLite for tests
**Rationale**: Mirrors production, simpler setup, validates actual Neon behavior

---

## Implementation Recommendations

### Priority 1: Remove SQLite Fallback
- Modify `backend/src/database/database.py` line 12
- Remove default value from `os.getenv("DATABASE_URL")`
- Add validation to ensure DATABASE_URL is set
- Raise clear error if missing

### Priority 2: Add Startup Validation
- Create `backend/src/database/validation.py`
- Implement connection test function
- Implement schema validation function
- Call validation in `main.py` startup event

### Priority 3: Create Persistence Tests
- Create `backend/tests/test_data_persistence.py`
- Implement end-to-end persistence tests
- Implement negative tests
- Add test cleanup fixtures

### Priority 4: Documentation
- Update quickstart.md with validation steps
- Add troubleshooting guide
- Document Neon-specific configuration

---

## Conclusion

The backend is already well-configured for Neon PostgreSQL. The primary changes required are:

1. **Remove SQLite fallback** (5 minutes)
2. **Add startup validation** (30 minutes)
3. **Create persistence tests** (1 hour)
4. **Update documentation** (30 minutes)

**Total Estimated Effort**: 2 hours

**Risk Level**: Low - Changes are minimal and well-understood

**Readiness**: Ready to proceed with implementation
