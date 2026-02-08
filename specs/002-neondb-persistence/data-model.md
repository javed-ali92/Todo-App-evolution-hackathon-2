# Data Model: NeonDB Authentication & Task Persistence

## Entity Definitions

### User Entity
Represents an authenticated user account with email (unique identifier), encrypted password, account creation timestamp, and associated tasks.

**Attributes:**
- id: Integer (Primary Key, Auto-increment)
- email: String (Unique, Not Null) - User's email address for login
- password_hash: String (Not Null) - BCrypt hashed password
- created_at: DateTime (Not Null) - Account creation timestamp
- updated_at: DateTime (Not Null) - Last update timestamp

**Relationships:**
- One-to-Many with Task (via user_id foreign key)
- One-to-Many with Session (via user_id foreign key)

**Validation Rules:**
- Email must be in valid email format
- Email must be unique across all users
- Password must be at least 8 characters when creating/updating
- All required fields must be present

### Task Entity
Represents a user's individual task with title, description, completion status, creation/update timestamps, and association to a specific user account.

**Attributes:**
- id: Integer (Primary Key, Auto-increment)
- user_id: Integer (Foreign Key, Not Null) - References user who owns the task
- title: String (Not Null) - Task title (max 255 characters)
- description: Text (Nullable) - Task description
- completed: Boolean (Not Null, Default: false) - Completion status
- created_at: DateTime (Not Null) - Task creation timestamp
- updated_at: DateTime (Not Null) - Last update timestamp

**Relationships:**
- Many-to-One with User (via user_id foreign key)

**Validation Rules:**
- Title must be present and not exceed 255 characters
- User_id must reference an existing user
- Completed field defaults to false if not specified
- All required fields must be present

### Session Entity
Represents an authenticated user session with JWT token, user ID, and expiration information for maintaining authentication state.

**Attributes:**
- id: Integer (Primary Key, Auto-increment)
- user_id: Integer (Foreign Key, Not Null) - References user associated with session
- token: String (Unique, Not Null) - JWT token identifier
- expires_at: DateTime (Not Null) - Session expiration timestamp
- created_at: DateTime (Not Null) - Session creation timestamp
- last_used_at: DateTime (Not Null) - Last activity timestamp

**Relationships:**
- Many-to-One with User (via user_id foreign key)

**Validation Rules:**
- Token must be unique across all sessions
- User_id must reference an existing user
- Expires_at must be in the future
- All required fields must be present

## Database Schema Requirements

### Users Table
- Primary key index on id
- Unique index on email
- Proper constraints for required fields

### Tasks Table
- Primary key index on id
- Index on user_id for efficient user-based queries
- Foreign key constraint linking user_id to users.id
- Proper constraints for required fields

### Sessions Table
- Primary key index on id
- Unique index on token
- Index on user_id
- Foreign key constraint linking user_id to users.id
- Proper constraints for required fields

## Data Relationships

- **Users → Tasks**: One-to-Many (One user can have many tasks)
- **Users → Sessions**: One-to-Many (One user can have many sessions)
- **Foreign Key Constraints**:
  - Tasks.user_id references Users.id
  - Sessions.user_id references Users.id

## Security Considerations

- Passwords are never stored in plaintext, only bcrypt hashes
- Session tokens are stored securely with appropriate expiration
- All database connections use SSL encryption (required for Neon)
- Foreign key constraints prevent orphaned records
- Indexes on foreign keys for efficient queries while maintaining data integrity