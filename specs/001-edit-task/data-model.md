# Data Model: Edit Task

**Feature**: Edit Task
**Branch**: 001-edit-task
**Date**: 2026-02-09

## Overview

The Edit Task feature does not introduce any new data entities. It operates on the existing Task entity with modifications to existing fields. This document describes the Task entity structure and the state changes that occur during edit operations.

---

## Existing Entities

### Task

**Description**: Represents a todo item owned by a user. All fields except `id`, `owner_id`, `created_at`, and `updated_at` are editable.

**Storage**: PostgreSQL table `task` in Neon database

**Fields**:

| Field | Type | Constraints | Editable | Description |
|-------|------|-------------|----------|-------------|
| id | integer | PRIMARY KEY, AUTO INCREMENT | No | Unique task identifier |
| title | string | NOT NULL, max 200 chars | Yes | Task title/summary |
| description | string | NULLABLE, max 1000 chars | Yes | Detailed task description |
| due_date | string (ISO date) | NULLABLE | Yes | Task deadline |
| priority | enum | NOT NULL, values: High/Medium/Low | Yes | Task priority level |
| tags | string | NULLABLE | Yes | Comma-separated tags |
| recursion_pattern | string | NULLABLE, max 100 chars | Yes | Recurrence pattern (daily, weekly, monthly) |
| completed | boolean | NOT NULL, default false | Yes | Task completion status |
| owner_id | integer | FOREIGN KEY (user.id), NOT NULL | No | User who owns this task |
| created_at | timestamp | NOT NULL, default NOW() | No | Task creation timestamp |
| updated_at | timestamp | NOT NULL, default NOW() | Auto | Last modification timestamp |

**Relationships**:
- `owner_id` → `user.id` (Many-to-One): Each task belongs to exactly one user

**Indexes**:
- Primary key on `id`
- Foreign key index on `owner_id`
- Recommended: Index on `owner_id, completed` for efficient task list queries

---

## State Transitions

### Edit Operation Flow

```
[Task Exists]
    ↓
[User Clicks Edit]
    ↓
[Fetch Current State] ← GET /api/{user_id}/tasks/{id}
    ↓
[Display in Form] (Pre-populated fields)
    ↓
[User Modifies Fields]
    ↓
[Submit Changes] → PUT /api/{user_id}/tasks/{id}
    ↓
[Validate Ownership] (token_user_id == owner_id)
    ↓
[Update Database] (updated_at = NOW())
    ↓
[Return Updated Task]
```

### Field Modification Rules

**Editable Fields** (can be changed by user):
- `title` - Required, must not be empty
- `description` - Optional, can be set to null
- `due_date` - Optional, must be valid ISO date if provided
- `priority` - Required, must be High/Medium/Low
- `tags` - Optional, comma-separated string
- `recursion_pattern` - Optional, freeform text
- `completed` - Boolean toggle (also editable via PATCH endpoint)

**Read-Only Fields** (cannot be changed):
- `id` - Immutable identifier
- `owner_id` - Cannot transfer task ownership
- `created_at` - Historical timestamp

**Auto-Updated Fields**:
- `updated_at` - Automatically set to current timestamp on any update

---

## Validation Rules

### Frontend Validation (react-hook-form)

```typescript
{
  title: {
    required: "Title is required",
    maxLength: { value: 200, message: "Title must be 200 characters or less" }
  },
  description: {
    maxLength: { value: 1000, message: "Description must be 1000 characters or less" }
  },
  due_date: {
    pattern: { value: /^\d{4}-\d{2}-\d{2}$/, message: "Invalid date format" }
  },
  priority: {
    required: "Priority is required",
    enum: ["High", "Medium", "Low"]
  },
  recursion_pattern: {
    maxLength: { value: 100, message: "Pattern must be 100 characters or less" }
  }
}
```

### Backend Validation (SQLModel)

```python
class TaskUpdate(SQLModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    due_date: Optional[str] = Field(default=None)
    priority: Optional[PriorityEnum] = Field(default=None)
    tags: Optional[str] = Field(default=None)
    recursion_pattern: Optional[str] = Field(default=None, max_length=100)
    completed: Optional[bool] = Field(default=None)
```

**Authorization Validation**:
```python
# Backend verifies ownership before allowing update
token_user_id = get_user_id_from_jwt(token)
task = get_task_by_id(task_id)

if task.owner_id != token_user_id:
    raise HTTPException(status_code=403, detail="Not authorized")
```

---

## Data Flow Diagrams

### Read Flow (GET)

```
Frontend                    Backend                     Database
   |                           |                            |
   |-- GET /api/25/tasks/5 -->|                            |
   |   (Authorization: Bearer) |                            |
   |                           |-- Verify JWT token ------->|
   |                           |<-- token_user_id = 25 -----|
   |                           |                            |
   |                           |-- SELECT * FROM task ----->|
   |                           |    WHERE id=5              |
   |                           |<-- task (owner_id=25) -----|
   |                           |                            |
   |                           |-- Check: 25 == 25 ✓        |
   |<-- 200 OK: task data -----|                            |
```

### Update Flow (PUT)

```
Frontend                    Backend                     Database
   |                           |                            |
   |-- PUT /api/25/tasks/5 -->|                            |
   |   (Authorization: Bearer) |                            |
   |   Body: {title: "New"}    |                            |
   |                           |-- Verify JWT token ------->|
   |                           |<-- token_user_id = 25 -----|
   |                           |                            |
   |                           |-- SELECT owner_id -------->|
   |                           |    FROM task WHERE id=5    |
   |                           |<-- owner_id = 25 ----------|
   |                           |                            |
   |                           |-- Check: 25 == 25 ✓        |
   |                           |                            |
   |                           |-- UPDATE task SET -------->|
   |                           |    title='New',            |
   |                           |    updated_at=NOW()        |
   |                           |    WHERE id=5              |
   |                           |<-- 1 row updated ----------|
   |                           |                            |
   |                           |-- SELECT * FROM task ----->|
   |                           |    WHERE id=5              |
   |                           |<-- updated task -----------|
   |<-- 200 OK: updated task --|                            |
```

---

## TypeScript Interfaces

### Frontend Types

```typescript
// Complete task object
interface Task {
  id: number;
  title: string;
  description?: string;
  due_date?: string;
  priority: 'High' | 'Medium' | 'Low';
  tags?: string;
  recursion_pattern?: string;
  completed: boolean;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

// Data for creating/updating tasks
interface TaskFormData {
  title: string;
  description?: string;
  due_date?: string;
  priority: 'High' | 'Medium' | 'Low';
  tags?: string;
  recursion_pattern?: string;
}

// Update request payload (all fields optional except what user changes)
interface TaskUpdate {
  title?: string;
  description?: string;
  due_date?: string;
  priority?: 'High' | 'Medium' | 'Low';
  tags?: string;
  recursion_pattern?: string;
  completed?: boolean;
}
```

---

## Database Schema

### Task Table (Existing)

```sql
CREATE TABLE task (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date VARCHAR(50),  -- Stored as ISO string
    priority VARCHAR(10) NOT NULL DEFAULT 'Medium',
    tags TEXT,
    recursion_pattern VARCHAR(100),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    owner_id INTEGER NOT NULL REFERENCES "user"(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_task_owner ON task(owner_id);
CREATE INDEX idx_task_owner_completed ON task(owner_id, completed);
```

**Note**: The `due_date` field is stored as VARCHAR to accommodate the datetime-to-string serialization fix implemented in the backend.

---

## Concurrency Considerations

### Last-Write-Wins Strategy

The current implementation uses a simple last-write-wins approach:
- No optimistic locking or version numbers
- Concurrent edits will result in the last submitted change being persisted
- Acceptable for MVP with single-user editing

### Future Enhancements (Out of Scope)

If concurrent editing becomes a concern:
1. Add `version` field to Task entity
2. Implement optimistic locking (check version on update)
3. Return 409 Conflict if version mismatch
4. Prompt user to refresh and retry

---

## Data Integrity

### Constraints Enforced

1. **Foreign Key Constraint**: `owner_id` must reference valid user
2. **NOT NULL Constraints**: `title`, `priority`, `owner_id`, `completed`
3. **Length Constraints**: `title` (200), `recursion_pattern` (100)
4. **Enum Constraint**: `priority` must be High/Medium/Low

### Cascade Behavior

- If user is deleted: `ON DELETE CASCADE` removes all their tasks
- If task is deleted: No cascade (task is leaf entity)

---

## Performance Considerations

### Query Optimization

**Fetch Single Task**:
```sql
SELECT * FROM task WHERE id = ? AND owner_id = ?;
```
- Uses primary key index (id)
- Additional owner_id check for security

**Update Single Task**:
```sql
UPDATE task
SET title = ?, description = ?, due_date = ?, priority = ?,
    tags = ?, recursion_pattern = ?, completed = ?, updated_at = NOW()
WHERE id = ? AND owner_id = ?;
```
- Uses primary key index
- Single query, no N+1 issues

### Expected Load

- Edit operations: Low frequency (< 10% of reads)
- Response time target: < 200ms for update
- No caching needed for edit operations (always fetch fresh data)

---

## Summary

The Edit Task feature operates entirely on the existing Task entity with no schema changes required. All editable fields are clearly defined, validation rules are consistent between frontend and backend, and authorization is enforced at the database query level. The data model is simple, well-understood, and sufficient for the feature requirements.
