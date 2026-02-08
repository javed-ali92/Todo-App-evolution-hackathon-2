-- Neon PostgreSQL Database Schema
-- Feature: 005-neon-db-migration
-- Generated: 2026-02-08
-- Purpose: Complete database schema for Todo application on Neon Serverless PostgreSQL

-- =============================================================================
-- EXTENSIONS
-- =============================================================================

-- Enable UUID extension (for future enhancements)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- =============================================================================
-- ENUM TYPES
-- =============================================================================

-- Priority levels for tasks
CREATE TYPE priority_enum AS ENUM ('High', 'Medium', 'Low');

-- =============================================================================
-- TABLES
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Users Table
-- -----------------------------------------------------------------------------
-- Stores registered user accounts with authentication credentials
-- Note: Table name is "user" (quoted) to avoid PostgreSQL reserved word conflict

CREATE TABLE IF NOT EXISTS "user" (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- User credentials
    username VARCHAR(30) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT user_username_length CHECK (LENGTH(username) >= 3 AND LENGTH(username) <= 30),
    CONSTRAINT user_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Indexes for user table
CREATE INDEX IF NOT EXISTS idx_user_email ON "user"(email);
CREATE INDEX IF NOT EXISTS idx_user_username ON "user"(username);

-- Comments for documentation
COMMENT ON TABLE "user" IS 'Registered user accounts with authentication credentials';
COMMENT ON COLUMN "user".id IS 'Unique identifier for the user';
COMMENT ON COLUMN "user".username IS 'User display name (3-30 characters, unique)';
COMMENT ON COLUMN "user".email IS 'User email address for login (unique)';
COMMENT ON COLUMN "user".hashed_password IS 'Bcrypt-hashed password';
COMMENT ON COLUMN "user".created_at IS 'Account creation timestamp';
COMMENT ON COLUMN "user".updated_at IS 'Last modification timestamp';

-- -----------------------------------------------------------------------------
-- Tasks Table
-- -----------------------------------------------------------------------------
-- Stores todo items belonging to users

CREATE TABLE IF NOT EXISTS task (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Foreign key to user
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,

    -- Task details
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date VARCHAR(50),  -- Stored as ISO format string (YYYY-MM-DD)
    priority priority_enum NOT NULL DEFAULT 'Medium',
    tags TEXT,  -- Comma-separated tags (future: migrate to array)
    recursion_pattern VARCHAR(100),  -- Recurrence rule (e.g., "daily", "weekly")
    completed BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT task_title_length CHECK (LENGTH(title) >= 1 AND LENGTH(title) <= 200)
);

-- Indexes for task table
CREATE INDEX IF NOT EXISTS idx_task_user_id ON task(user_id);
CREATE INDEX IF NOT EXISTS idx_task_completed ON task(completed);
CREATE INDEX IF NOT EXISTS idx_task_user_completed ON task(user_id, completed);  -- Composite index for filtering
CREATE INDEX IF NOT EXISTS idx_task_due_date ON task(due_date) WHERE due_date IS NOT NULL;  -- Partial index

-- Comments for documentation
COMMENT ON TABLE task IS 'Todo items belonging to users';
COMMENT ON COLUMN task.id IS 'Unique identifier for the task';
COMMENT ON COLUMN task.user_id IS 'Owner of the task (foreign key to user.id)';
COMMENT ON COLUMN task.title IS 'Task title/summary (1-200 characters)';
COMMENT ON COLUMN task.description IS 'Detailed task description (optional)';
COMMENT ON COLUMN task.due_date IS 'Due date in ISO format YYYY-MM-DD (optional)';
COMMENT ON COLUMN task.priority IS 'Task priority: High, Medium, or Low';
COMMENT ON COLUMN task.tags IS 'Comma-separated tags for categorization (optional)';
COMMENT ON COLUMN task.recursion_pattern IS 'Recurrence rule for recurring tasks (optional)';
COMMENT ON COLUMN task.completed IS 'Completion status (true=complete, false=incomplete)';
COMMENT ON COLUMN task.created_at IS 'Task creation timestamp';
COMMENT ON COLUMN task.updated_at IS 'Last modification timestamp';

-- -----------------------------------------------------------------------------
-- Sessions Table
-- -----------------------------------------------------------------------------
-- Tracks active JWT sessions for logout functionality

CREATE TABLE IF NOT EXISTS session (
    -- Primary key
    id SERIAL PRIMARY KEY,

    -- Foreign key to user
    user_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,

    -- Session details
    token_jti VARCHAR(255) NOT NULL UNIQUE,  -- JWT ID (jti claim)
    token VARCHAR(255) NOT NULL,  -- Hashed token value
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN NOT NULL DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Constraints
    CONSTRAINT session_expires_future CHECK (expires_at > created_at)
);

-- Indexes for session table
CREATE INDEX IF NOT EXISTS idx_session_token_jti ON session(token_jti);
CREATE INDEX IF NOT EXISTS idx_session_user_id ON session(user_id);
CREATE INDEX IF NOT EXISTS idx_session_expires_at ON session(expires_at);
CREATE INDEX IF NOT EXISTS idx_session_revoked ON session(revoked) WHERE revoked = FALSE;  -- Partial index for active sessions

-- Comments for documentation
COMMENT ON TABLE session IS 'Active JWT sessions for authentication and logout';
COMMENT ON COLUMN session.id IS 'Unique identifier for the session';
COMMENT ON COLUMN session.user_id IS 'Session owner (foreign key to user.id)';
COMMENT ON COLUMN session.token_jti IS 'JWT ID (jti claim) for token identification';
COMMENT ON COLUMN session.token IS 'Hashed token value for validation';
COMMENT ON COLUMN session.expires_at IS 'Token expiration timestamp';
COMMENT ON COLUMN session.revoked IS 'Revocation status (true=logged out, false=active)';
COMMENT ON COLUMN session.created_at IS 'Session creation timestamp';

-- =============================================================================
-- TRIGGERS
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Auto-update updated_at timestamp
-- -----------------------------------------------------------------------------

-- Function to update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for user table
CREATE TRIGGER update_user_updated_at
    BEFORE UPDATE ON "user"
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for task table
CREATE TRIGGER update_task_updated_at
    BEFORE UPDATE ON task
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- VIEWS (Optional - for future enhancements)
-- =============================================================================

-- View for active tasks (not completed)
CREATE OR REPLACE VIEW active_tasks AS
SELECT
    t.id,
    t.user_id,
    t.title,
    t.description,
    t.due_date,
    t.priority,
    t.tags,
    t.recursion_pattern,
    t.created_at,
    t.updated_at,
    u.username,
    u.email
FROM task t
JOIN "user" u ON t.user_id = u.id
WHERE t.completed = FALSE;

COMMENT ON VIEW active_tasks IS 'All incomplete tasks with user information';

-- View for completed tasks
CREATE OR REPLACE VIEW completed_tasks AS
SELECT
    t.id,
    t.user_id,
    t.title,
    t.description,
    t.due_date,
    t.priority,
    t.tags,
    t.recursion_pattern,
    t.created_at,
    t.updated_at,
    u.username,
    u.email
FROM task t
JOIN "user" u ON t.user_id = u.id
WHERE t.completed = TRUE;

COMMENT ON VIEW completed_tasks IS 'All completed tasks with user information';

-- =============================================================================
-- FUNCTIONS (Optional - for future enhancements)
-- =============================================================================

-- Function to get user task statistics
CREATE OR REPLACE FUNCTION get_user_task_stats(p_user_id INTEGER)
RETURNS TABLE (
    total_tasks BIGINT,
    completed_tasks BIGINT,
    incomplete_tasks BIGINT,
    high_priority_tasks BIGINT,
    overdue_tasks BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) AS total_tasks,
        COUNT(*) FILTER (WHERE completed = TRUE) AS completed_tasks,
        COUNT(*) FILTER (WHERE completed = FALSE) AS incomplete_tasks,
        COUNT(*) FILTER (WHERE priority = 'High' AND completed = FALSE) AS high_priority_tasks,
        COUNT(*) FILTER (WHERE due_date IS NOT NULL AND due_date < CURRENT_DATE::TEXT AND completed = FALSE) AS overdue_tasks
    FROM task
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION get_user_task_stats IS 'Get task statistics for a specific user';

-- =============================================================================
-- SAMPLE QUERIES (for testing and validation)
-- =============================================================================

-- Verify all tables exist
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

-- Verify all foreign keys exist
-- SELECT constraint_name, table_name FROM information_schema.table_constraints WHERE constraint_type = 'FOREIGN KEY' AND table_schema = 'public';

-- Verify all indexes exist
-- SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname;

-- Count records in each table
-- SELECT 'user' AS table_name, COUNT(*) AS record_count FROM "user"
-- UNION ALL
-- SELECT 'task', COUNT(*) FROM task
-- UNION ALL
-- SELECT 'session', COUNT(*) FROM session;

-- =============================================================================
-- CLEANUP (for development/testing only)
-- =============================================================================

-- WARNING: These commands will delete all data!
-- Uncomment only for development/testing purposes

-- DROP VIEW IF EXISTS completed_tasks CASCADE;
-- DROP VIEW IF EXISTS active_tasks CASCADE;
-- DROP FUNCTION IF EXISTS get_user_task_stats(INTEGER) CASCADE;
-- DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
-- DROP TABLE IF EXISTS session CASCADE;
-- DROP TABLE IF EXISTS task CASCADE;
-- DROP TABLE IF EXISTS "user" CASCADE;
-- DROP TYPE IF EXISTS priority_enum CASCADE;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
