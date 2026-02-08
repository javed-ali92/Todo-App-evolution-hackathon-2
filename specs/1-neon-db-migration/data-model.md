# Data Model: Todo Application with Neon PostgreSQL

## Entity: User
**Description**: Represents an authenticated user of the todo application

**Fields**:
- id (Integer, Primary Key, Auto-increment): Unique identifier for the user
- username (String, Unique, Required): User's chosen username
- email (String, Unique, Required): User's email address for authentication
- password (String, Required, Encrypted): Hashed password for authentication
- created_at (DateTime, Required): Timestamp of user creation
- updated_at (DateTime, Required): Timestamp of last update

**Relationships**:
- One-to-Many: User has many Tasks (via owner_id foreign key)
- One-to-Many: User has many Sessions (via user_id foreign key)

**Validation Rules**:
- Email must be valid email format
- Username must be unique and 3-30 characters
- Password must be at least 8 characters with complexity requirements
- Created/updated timestamps automatically managed

## Entity: Task
**Description**: Represents a todo item owned by a specific user

**Fields**:
- id (Integer, Primary Key, Auto-increment): Unique identifier for the task
- user_id (Integer, Foreign Key to User.id, Required): Owner of the task
- title (String, Required): Task title/description
- description (String, Optional): Extended task description
- due_date (DateTime, Optional): Deadline for task completion
- priority (Enum: 'High'|'Medium'|'Low', Required): Task priority level
- tags (JSON Array, Optional): Array of tags associated with the task
- recursion_pattern (String, Optional): Recurrence pattern if task repeats
- completed (Boolean, Required, Default: false): Completion status
- created_at (DateTime, Required): Timestamp of task creation
- updated_at (DateTime, Required): Timestamp of last update

**Relationships**:
- Many-to-One: Task belongs to User (via user_id foreign key)

**Validation Rules**:
- Title must be 1-200 characters
- User_id must reference existing user
- Priority must be one of allowed values
- Due date must be in future if provided
- Tags array must contain valid string values

## Entity: Session
**Description**: Represents an active user session with authentication token

**Fields**:
- id (Integer, Primary Key, Auto-increment): Unique identifier for the session
- user_id (Integer, Foreign Key to User.id, Required): User associated with session
- token (String, Required, Unique): Authentication token value
- expires_at (DateTime, Required): Expiration timestamp for the token
- created_at (DateTime, Required): Timestamp of session creation
- last_used_at (DateTime, Required): Timestamp of last activity

**Relationships**:
- Many-to-One: Session belongs to User (via user_id foreign key)

**Validation Rules**:
- Token must be unique across all sessions
- User_id must reference existing user
- Expires_at must be in future
- Last_used_at automatically updated on access

## Database Schema Relationships

### User ↔ Task Relationship
```
User.id (1) ←→ (Many) Task.user_id
```
- One user can own many tasks
- Tasks are deleted when user is deleted (CASCADE)
- Foreign key constraint ensures referential integrity

### User ↔ Session Relationship
```
User.id (1) ←→ (Many) Session.user_id
```
- One user can have multiple active sessions
- Sessions are deleted when user is deleted (CASCADE)
- Foreign key constraint ensures referential integrity

## State Transitions

### Task State Transitions
- `pending` → `completed`: When user marks task as complete
- `completed` → `pending`: When user unmarks task as complete
- `created` → `deleted`: When user deletes task (soft delete via flag)

### Session State Transitions
- `active` → `expired`: When token reaches expiration time
- `active` → `revoked`: When user logs out or admin revokes access
- `expired` → `refreshed`: When token is renewed (if refresh allowed)

## Indexes for Performance
- User: email (unique), username (unique)
- Task: user_id (foreign key), completed (query optimization)
- Session: token (unique), expires_at (cleanup optimization)

## Constraints
- Referential integrity enforced for all foreign keys
- Unique constraints on email, username, and session token
- Check constraints for enum values and data validity
- Cascade delete for dependent records