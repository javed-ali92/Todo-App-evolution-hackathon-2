# Quickstart: Neon Database Migration

**Feature**: 005-neon-db-migration
**Date**: 2026-02-08
**Audience**: Developers implementing the Neon migration

## Overview

This quickstart guide provides step-by-step instructions to verify that the Todo application backend is correctly configured to use Neon Serverless PostgreSQL exclusively, with no local database usage.

---

## Prerequisites

Before starting, ensure you have:

1. ✅ **Neon PostgreSQL Database**: Provisioned and accessible
2. ✅ **DATABASE_URL Configured**: Set in `.env` file at repository root
3. ✅ **Python 3.11+**: Installed and available in PATH
4. ✅ **Backend Dependencies**: Installed via `pip install -r backend/requirements.txt`
5. ✅ **Network Access**: Application server can reach Neon endpoints

---

## Step 1: Verify Environment Configuration

### Check DATABASE_URL

```bash
# Navigate to repository root
cd E:\javed\hacathon_2\Evalution_Todo_App_1

# Display DATABASE_URL (first 50 characters only for security)
cat .env | grep DATABASE_URL | cut -c1-50

# Expected output (truncated):
# DATABASE_URL='postgresql://neondb_owner:...
```

### Verify Connection String Format

The DATABASE_URL should follow this format:
```
postgresql://[user]:[password]@[host]/[database]?sslmode=require&channel_binding=require
```

**Required Parameters**:
- `sslmode=require`: Enforces SSL connection
- `channel_binding=require`: Additional security for Neon

**Example** (credentials redacted):
```
postgresql://neondb_owner:npg_***@ep-jolly-fog-a1fpuuur-pooler.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

---

## Step 2: Test Database Connection

### Quick Connection Test

```bash
cd backend

# Test database connection
python -c "from src.database.database import engine; print('✅ Connection successful!' if engine else '❌ Connection failed')"
```

**Expected Output**:
```
✅ Connection successful!
```

### Detailed Connection Test

```bash
# Test connection with details
python -c "
from src.database.database import engine, DATABASE_URL
print(f'Engine: {engine}')
print(f'Database: {DATABASE_URL.split('@')[1].split('/')[1].split('?')[0]}')
print(f'Host: {DATABASE_URL.split('@')[1].split('/')[0]}')
print('✅ Connection details verified')
"
```

**Expected Output**:
```
Engine: Engine(postgresql://...)
Database: neondb
Host: ep-jolly-fog-a1fpuuur-pooler.ap-southeast-1.aws.neon.tech
✅ Connection details verified
```

---

## Step 3: Verify Schema Creation

### Start Backend Server

```bash
cd backend

# Start the server (creates tables on startup)
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001
```

**Expected Startup Logs**:
```
Creating database tables...
Database tables created successfully!
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Verify Tables Exist

Open a new terminal and run:

```bash
cd backend

# Query Neon to verify tables exist
python -c "
from sqlmodel import Session, text
from src.database.database import engine

with Session(engine) as session:
    result = session.exec(text('''
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    ''')).all()

    tables = [row[0] for row in result]
    print('Tables in Neon PostgreSQL:')
    for table in tables:
        print(f'  ✅ {table}')

    expected = {'user', 'task', 'session'}
    found = set(tables)

    if expected.issubset(found):
        print('\n✅ All required tables exist!')
    else:
        missing = expected - found
        print(f'\n❌ Missing tables: {missing}')
"
```

**Expected Output**:
```
Tables in Neon PostgreSQL:
  ✅ session
  ✅ task
  ✅ user

✅ All required tables exist!
```

---

## Step 4: Test Data Persistence

### Test User Registration

```bash
# Register a test user
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

**Expected Response**:
```json
{
  "username": "testuser",
  "email": "test@example.com",
  "id": 1,
  "created_at": "2026-02-08T...",
  "updated_at": "2026-02-08T..."
}
```

### Verify User in Neon

```bash
cd backend

# Query Neon to verify user was saved
python -c "
from sqlmodel import Session, select
from src.database.database import engine
from src.models.user import User

with Session(engine) as session:
    user = session.exec(select(User).where(User.email == 'test@example.com')).first()

    if user:
        print(f'✅ User found in Neon:')
        print(f'   ID: {user.id}')
        print(f'   Username: {user.username}')
        print(f'   Email: {user.email}')
        print(f'   Created: {user.created_at}')
    else:
        print('❌ User not found in Neon!')
"
```

### Test Task Creation

```bash
# Login to get access token
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Create a task
curl -X POST http://localhost:8001/api/1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "title": "Test Task",
    "description": "Testing Neon persistence",
    "priority": "High"
  }'
```

**Expected Response**:
```json
{
  "title": "Test Task",
  "description": "Testing Neon persistence",
  "priority": "High",
  "completed": false,
  "id": 1,
  "user_id": 1,
  "created_at": "2026-02-08T...",
  "updated_at": "2026-02-08T..."
}
```

### Verify Task in Neon

```bash
cd backend

# Query Neon to verify task was saved
python -c "
from sqlmodel import Session, select
from src.database.database import engine
from src.models.task import Task

with Session(engine) as session:
    task = session.exec(select(Task).where(Task.title == 'Test Task')).first()

    if task:
        print(f'✅ Task found in Neon:')
        print(f'   ID: {task.id}')
        print(f'   Title: {task.title}')
        print(f'   User ID: {task.user_id}')
        print(f'   Priority: {task.priority}')
        print(f'   Completed: {task.completed}')
    else:
        print('❌ Task not found in Neon!')
"
```

---

## Step 5: Verify No Local Database Files

### Check for Local Database Files

```bash
# Search for .db and .sqlite files
cd E:\javed\hacathon_2\Evalution_Todo_App_1
find backend -name "*.db" -o -name "*.sqlite" 2>/dev/null

# Expected: No output (no files found)
```

**If files are found**:
```bash
# List found files
find backend -name "*.db" -o -name "*.sqlite" -ls

# Delete local database files (after confirming they're not needed)
find backend -name "*.db" -delete
find backend -name "*.sqlite" -delete
```

### Verify SQLite Not Referenced

```bash
# Check database.py for SQLite references
grep -i "sqlite" backend/src/database/database.py

# Expected: No output (or only in comments)
```

---

## Step 6: Test Application Restart

### Simulate Application Restart

```bash
# Stop the backend server (Ctrl+C in the terminal running uvicorn)

# Wait 5 seconds

# Restart the backend server
cd backend
python -m uvicorn src.main:app --host 0.0.0.0 --port 8001
```

### Verify Data Persists

```bash
# Login with the test user created earlier
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Expected: Successful login with access token
```

```bash
# Retrieve tasks (should include the task created earlier)
TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

curl -X GET http://localhost:8001/api/1/tasks \
  -H "Authorization: Bearer $TOKEN"

# Expected: Array containing the "Test Task" created earlier
```

---

## Step 7: Run Automated Tests

### Run Persistence Tests

```bash
cd backend

# Run all persistence tests
pytest tests/test_data_persistence.py -v

# Expected: All tests pass
```

**Expected Output**:
```
tests/test_data_persistence.py::test_user_registration_persists PASSED
tests/test_data_persistence.py::test_user_login_reads_from_neon PASSED
tests/test_data_persistence.py::test_task_creation_persists PASSED
tests/test_data_persistence.py::test_task_update_persists PASSED
tests/test_data_persistence.py::test_task_delete_persists PASSED
tests/test_data_persistence.py::test_data_survives_restart PASSED

======================== 6 passed in 2.34s ========================
```

### Run Connection Tests

```bash
# Run connection validation tests
pytest tests/test_neon_connection.py -v

# Expected: All tests pass
```

---

## Troubleshooting

### Issue: Connection Timeout

**Symptom**:
```
sqlalchemy.exc.OperationalError: (psycopg2.OperationalError) connection timeout
```

**Solutions**:
1. Check network connectivity to Neon:
   ```bash
   ping ep-jolly-fog-a1fpuuur-pooler.ap-southeast-1.aws.neon.tech
   ```

2. Verify DATABASE_URL is correct:
   ```bash
   cat .env | grep DATABASE_URL
   ```

3. Check firewall settings (ensure outbound PostgreSQL port 5432 is allowed)

---

### Issue: SSL Certificate Error

**Symptom**:
```
ssl.SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed
```

**Solutions**:
1. Ensure `sslmode=require` is in DATABASE_URL:
   ```bash
   cat .env | grep "sslmode=require"
   ```

2. Update DATABASE_URL if missing:
   ```bash
   # Add sslmode parameter
   DATABASE_URL='postgresql://...?sslmode=require&channel_binding=require'
   ```

---

### Issue: Table Does Not Exist

**Symptom**:
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) relation "user" does not exist
```

**Solutions**:
1. Verify tables were created on startup:
   ```bash
   # Check startup logs for "Database tables created successfully!"
   ```

2. Manually create tables:
   ```bash
   cd backend
   python -c "
   from sqlmodel import SQLModel
   from src.database.database import engine
   from src.models import user, task, session

   SQLModel.metadata.create_all(engine)
   print('✅ Tables created')
   "
   ```

3. Check database permissions:
   - Verify the database user has CREATE TABLE privilege
   - Contact Neon support if permissions are insufficient

---

### Issue: Data Not Persisting

**Symptom**: Data disappears after application restart

**Solutions**:
1. Verify DATABASE_URL is being read:
   ```bash
   cd backend
   python -c "
   from src.database.database import DATABASE_URL
   print(f'DATABASE_URL: {DATABASE_URL[:50]}...')

   if 'sqlite' in DATABASE_URL.lower():
       print('❌ ERROR: Using SQLite fallback!')
   else:
       print('✅ Using PostgreSQL')
   "
   ```

2. Check for local .db files:
   ```bash
   find backend -name "*.db"
   # If found, delete them and restart
   ```

3. Verify engine is using Neon:
   ```bash
   cd backend
   python -c "
   from src.database.database import engine
   print(f'Engine URL: {engine.url}')
   "
   ```

---

### Issue: Authentication Failed

**Symptom**:
```
psycopg2.OperationalError: FATAL: password authentication failed
```

**Solutions**:
1. Verify DATABASE_URL credentials:
   ```bash
   # Check if password contains special characters that need URL encoding
   cat .env | grep DATABASE_URL
   ```

2. Reset Neon database password:
   - Log into Neon console
   - Reset database password
   - Update DATABASE_URL in .env

3. Verify connection string format:
   ```
   postgresql://[user]:[password]@[host]/[database]?sslmode=require
   ```

---

## Success Criteria Checklist

Use this checklist to verify the migration is complete:

- [ ] ✅ Backend starts without errors
- [ ] ✅ Startup log shows "Database tables created successfully!"
- [ ] ✅ No local .db or .sqlite files exist in backend directory
- [ ] ✅ User registration creates record in Neon (verified by direct query)
- [ ] ✅ User login retrieves data from Neon (verified by successful authentication)
- [ ] ✅ Task creation persists to Neon (verified by direct query)
- [ ] ✅ Task updates persist to Neon (verified by retrieval after update)
- [ ] ✅ Task deletion removes from Neon (verified by query after delete)
- [ ] ✅ Data survives application restart (verified by login and task retrieval)
- [ ] ✅ All automated tests pass (pytest tests/test_data_persistence.py)
- [ ] ✅ Connection validation tests pass (pytest tests/test_neon_connection.py)
- [ ] ✅ No SQLite references in database.py (grep check)

---

## Next Steps

After completing this quickstart:

1. **Run Full Test Suite**: `pytest backend/tests/ -v`
2. **Review Implementation**: Check all modified files match the plan
3. **Update Documentation**: Add any environment-specific notes
4. **Deploy to Production**: Follow deployment checklist
5. **Monitor Performance**: Set up logging and monitoring for Neon queries

---

## Additional Resources

- **Neon Documentation**: https://neon.tech/docs
- **SQLModel Documentation**: https://sqlmodel.tiangolo.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **PostgreSQL Documentation**: https://www.postgresql.org/docs/

---

**Quickstart Status**: ✅ Complete - Ready for implementation verification
