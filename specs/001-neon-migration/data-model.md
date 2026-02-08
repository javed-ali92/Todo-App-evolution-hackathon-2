# Data Model for Neon PostgreSQL Migration

## Overview
This document defines the database schema and entity relationships for the Todo application using SQLModel with Neon PostgreSQL.

## Entity Definitions

### User Entity
- **Name**: User
- **Purpose**: Represents a registered user in the system
- **Fields**:
  - `id`: Primary key, auto-incrementing integer
  - `username`: String (max 255), unique, indexed, required
  - `email`: String (max 255), unique, indexed, required, email format validation
  - `password`: String (max 255), hashed password, required
  - `created_at`: DateTime, default to current timestamp, required
  - `updated_at`: DateTime, default to current timestamp, updated on modification, required

- **Relationships**:
  - One-to-many with Task (user has many tasks)
  - One-to-many with Session (user has many sessions)

- **Validation Rules**:
  - Username: 3-50 characters, alphanumeric + underscore
  - Email: Valid email format
  - Password: Minimum 8 characters (stored as bcrypt hash)

### Task Entity
- **Name**: Task
- **Purpose**: Represents a user's task/todo item
- **Fields**:
  - `id`: Primary key, auto-incrementing integer
  - `user_id`: Integer, foreign key to User.id, indexed, required
  - `title`: String (max 255), required
  - `description`: String (optional, nullable)
  - `due_date`: DateTime (optional, nullable)
  - `priority`: Enum (High, Medium, Low), default to Medium
  - `tags`: Array of strings (optional, stored as PostgreSQL array)
  - `recursion_pattern`: String (max 100, optional, nullable)
  - `completed`: Boolean, default to false
  - `created_at`: DateTime, default to current timestamp, required
  - `updated_at`: DateTime, default to current timestamp, updated on modification, required

- **Relationships**:
  - Many-to-one with User (task belongs to one user)
  - User can have many tasks

- **Validation Rules**:
  - Title: 1-255 characters, required
  - Priority: Must be one of High, Medium, Low
  - Due date: If provided, must be future date
  - Tags: Array of strings, max 50 tags, each max 50 characters
  - Recursion pattern: If provided, follows standard recurrence format

### Session Entity
- **Name**: Session
- **Purpose**: Tracks user authentication sessions and JWT tokens
- **Fields**:
  - `id`: Primary key, auto-incrementing integer
  - `user_id`: Integer, foreign key to User.id, indexed, required
  - `token_jti`: String (max 255), unique, indexed, required (JWT ID)
  - `token_hash`: String (max 255), SHA256 hash of token, required
  - `ip_address`: String (max 45, optional, nullable, IPv4/v6 format)
  - `user_agent`: Text (optional, nullable)
  - `created_at`: DateTime, default to current timestamp, required
  - `expires_at`: DateTime, required (token expiration)
  - `revoked`: Boolean, default to false
  - `revoked_at`: DateTime (optional, nullable, when session revoked)

- **Relationships**:
  - Many-to-one with User (session belongs to one user)
  - User can have many sessions

- **Validation Rules**:
  - Token JTI: Must be unique across all sessions
  - Expires_at: Must be in the future
  - Revoked_at: Only set when revoked is true

## Database Schema SQL

```sql
-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for users
CREATE UNIQUE INDEX idx_users_username ON users(username);
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    due_date TIMESTAMP,
    priority VARCHAR(20) DEFAULT 'Medium',
    tags TEXT[],
    recursion_pattern VARCHAR(100),
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for tasks
CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_completed ON tasks(completed);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);
CREATE INDEX idx_tasks_priority ON tasks(priority);

-- Sessions table
CREATE TABLE sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_jti VARCHAR(255) UNIQUE NOT NULL,
    token_hash VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP,
    CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Indexes for sessions
CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE UNIQUE INDEX idx_sessions_token_jti ON sessions(token_jti);
CREATE INDEX idx_sessions_expires_at ON sessions(expires_at);
CREATE INDEX idx_sessions_revoked ON sessions(revoked);
```

## State Transitions

### Task State Transitions
- **Completed Status**:
  - `false` (active) → `true` (completed) via toggle completion endpoint
  - `true` (completed) → `false` (active) via toggle completion endpoint

### Session State Transitions
- **Revocation Status**:
  - `false` (active) → `true` (revoked) via logout endpoint
  - Once revoked, session cannot be reactivated

## Constraints and Relationships

### Foreign Key Constraints
- `tasks.user_id` → `users.id` (ON DELETE CASCADE)
- `sessions.user_id` → `users.id` (ON DELETE CASCADE)

### Unique Constraints
- `users.username` (unique)
- `users.email` (unique)
- `sessions.token_jti` (unique)

### Indexes for Performance
- User lookup: username and email indexes
- Task filtering: user_id, completed, due_date, priority indexes
- Session lookup: user_id, token_jti, expires_at, revoked indexes

## Data Integrity Rules

### Referential Integrity
- Tasks are automatically deleted when user is deleted (CASCADE)
- Sessions are automatically deleted when user is deleted (CASCADE)

### Business Logic Constraints
- Users can only access their own tasks
- Sessions cannot be used once revoked
- Tokens expire after configured duration
- Passwords must be properly hashed before storage

## API Data Validation

### Input Validation
- All string fields have maximum length limits
- Date fields must be in valid ISO format
- Boolean fields accept true/false values
- Array fields validate element count and size

### Response Validation
- Sensitive fields (password, token) are never returned in responses
- Timestamps are returned in ISO format
- All responses include proper type validation